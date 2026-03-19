import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .analyzers import ALL_ANALYZERS
from .config import settings
from .database import get_db, init_db
from .models import AnalysisResult
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Citation,
    HealthResponse,
    Recommendation,
    ScoreBreakdown,
)
from .services.recommender import generate_recommendations
from .services.scorer import calculate_total_score, score_to_grade
from .services.scraper import FetchError, fetch_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="GEO Diagnostic Tool",
    description="Generative Engine Optimization analyzer based on peer-reviewed research",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_cached_result(
    db: Session, url: str
) -> AnalysisResult | None:
    """Return a cached result if it exists and is less than CACHE_TTL_HOURS old."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.CACHE_TTL_HOURS)
    return (
        db.query(AnalysisResult)
        .filter(AnalysisResult.url == url, AnalysisResult.created_at >= cutoff)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )


def _result_to_response(result: AnalysisResult, cached: bool) -> AnalyzeResponse:
    """Convert a DB model to API response."""
    scores = ScoreBreakdown(
        statistic_score=result.statistic_score,
        citation_score=result.citation_score,
        quotation_score=result.quotation_score,
        freshness_score=result.freshness_score,
        https_score=result.https_score,
        meta_tags_score=result.meta_tags_score,
        mobile_score=result.mobile_score,
        structure_score=result.structure_score,
        schema_score=result.schema_score,
        faq_score=result.faq_score,
        tone_score=result.tone_score,
        readability_score=result.readability_score,
        crawlability_score=result.crawlability_score,
        robots_score=result.robots_score,
        llms_txt_score=result.llms_txt_score,
    )
    critical_scores = {
        "crawlability_score": result.crawlability_score,
        "robots_score": result.robots_score,
        "https_score": result.https_score,
    }
    return AnalyzeResponse(
        url=result.url,
        total_score=result.total_score,
        grade=score_to_grade(result.total_score, critical_scores),
        scores=scores,
        raw_metrics=result.get_raw_metrics(),
        recommendations=[
            Recommendation(**r) for r in result.get_recommendations()
        ],
        cached=cached,
        analyzed_at=result.created_at,
    )


def _run_analysis(url: str, html: str, fetch_time_ms: int, db: Session) -> AnalysisResult:
    """Run all analyzers and persist results."""
    domain = urlparse(url).netloc
    scores: dict[str, float] = {}
    raw_metrics: dict[str, dict] = {}

    for analyzer_cls in ALL_ANALYZERS:
        analyzer = analyzer_cls()
        try:
            result = analyzer.analyze(html, url)
            scores[analyzer.score_field] = result.get("score", 0.0)
            raw_metrics[analyzer.name] = result
        except Exception:
            logger.exception("Analyzer %s failed for %s", analyzer.name, url)
            scores[analyzer.score_field] = 0.0
            raw_metrics[analyzer.name] = {"score": 0, "error": "analyzer failed"}

    total_score = calculate_total_score(scores)
    recommendations = generate_recommendations(scores)

    record = AnalysisResult(
        url=url,
        domain=domain,
        total_score=total_score,
        statistic_score=scores.get("statistic_score", 0),
        citation_score=scores.get("citation_score", 0),
        quotation_score=scores.get("quotation_score", 0),
        freshness_score=scores.get("freshness_score", 0),
        https_score=scores.get("https_score", 0),
        meta_tags_score=scores.get("meta_tags_score", 0),
        mobile_score=scores.get("mobile_score", 0),
        structure_score=scores.get("structure_score", 0),
        schema_score=scores.get("schema_score", 0),
        faq_score=scores.get("faq_score", 0),
        readability_score=scores.get("readability_score", 0),
        tone_score=scores.get("tone_score", 0),
        crawlability_score=scores.get("crawlability_score", 0),
        robots_score=scores.get("robots_score", 0),
        llms_txt_score=scores.get("llms_txt_score", 0),
        raw_metrics=json.dumps(raw_metrics),
        recommendations=json.dumps([r.model_dump() for r in recommendations]),
        fetch_time_ms=fetch_time_ms,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to save analysis for %s", url)
        raise HTTPException(status_code=500, detail="Failed to save analysis results")
    return record


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(request: AnalyzeRequest, db: Session = Depends(get_db)):
    url = str(request.url)

    # Check cache
    cached = _get_cached_result(db, url)
    if cached:
        logger.info("Cache hit for %s", url)
        return _result_to_response(cached, cached=True)

    # Fetch and analyze
    try:
        html, fetch_time_ms = fetch_page(url)
    except FetchError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not fetch URL: {e.message}",
        )

    logger.info("Analyzing %s (%d ms fetch)", url, fetch_time_ms)
    result = _run_analysis(url, html, fetch_time_ms, db)
    return _result_to_response(result, cached=False)


@app.get("/analyze/{url_encoded:path}", response_model=AnalyzeResponse)
def get_analysis(url_encoded: str, db: Session = Depends(get_db)):
    url = url_encoded if url_encoded.startswith("http") else f"https://{url_encoded}"

    # Check cache
    cached = _get_cached_result(db, url)
    if cached:
        return _result_to_response(cached, cached=True)

    # No cache — run fresh analysis
    try:
        html, fetch_time_ms = fetch_page(url)
    except FetchError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not fetch URL: {e.message}",
        )

    result = _run_analysis(url, html, fetch_time_ms, db)
    return _result_to_response(result, cached=False)


CITATIONS = [
    Citation(
        authors="Aggarwal, P., Murahari, V., Rajpurohit, T., Kalyan, A., Narasimhan, K., & Deshpande, A.",
        year=2024,
        title="GEO: Generative Engine Optimization",
        venue="Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD '24)",
        doi="https://doi.org/10.1145/3637528.3671882",
        note="Primary reference. Coined 'GEO' and tested 9 optimization strategies across BingChat, Perplexity, and NeevaAI. Source for scoring weights and effect sizes (+40-41% statistics, +38-40% quotations, +30-40% citations, +15-30% fluency).",
    ),
    Citation(
        authors="Thompson, S., et al.",
        year=2025,
        title="The Crawl Before the Fall: Understanding AI's Impact on Content Providers",
        venue="ACM Internet Measurement Conference (IMC 2025). Cloudflare Research.",
        doi="https://doi.org/10.1145/3646547.3688428",
        note="Quantified crawl-to-referral ratios: Google 14:1, OpenAI 1,700:1, Anthropic 73,000:1. Evidence of the extraction problem where AI companies crawl far more than they refer back.",
    ),
    Citation(
        authors="Longpre, S., Mahari, R., Lee, A., et al.",
        year=2024,
        title="Consent in Crisis: The Rapid Decline of the AI Data Commons",
        venue="Advances in Neural Information Processing Systems 37, Datasets and Benchmarks Track (NeurIPS 2024). MIT Data Provenance Initiative.",
        doi="https://doi.org/10.48550/arXiv.2407.14933",
        note="First large-scale longitudinal audit of web domain consent protocols. Documented that ~5%+ of C4 tokens became restricted in one year, with 45% restricted by Terms of Service.",
    ),
    Citation(
        authors="Liu, E., et al.",
        year=2025,
        title="Somesite I Used To Crawl: Awareness, Agency and Efficacy in Protecting Content Creators From AI Crawlers",
        venue="ACM Internet Measurement Conference (IMC 2025)",
        doi="https://doi.org/10.1145/3646547.3688435",
        note="User study of 203 professional artists on awareness and accessibility of defensive tools. Measured which AI crawlers respect robots.txt and efficacy of active blocking techniques.",
    ),
    Citation(
        authors="Zhao, H. & Berman, R.",
        year=2025,
        title="Large Language Models and News Publishing",
        venue="Working Paper. Rutgers Business School & The Wharton School.",
        doi="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4767297",
        note="Found that blocking AI crawlers reduced total traffic by 23% and human traffic by 14% for large publishers. Documents the unintended consequences of AI protection strategies.",
    ),
    Citation(
        authors="SE Ranking",
        year=2025,
        title="400K URL Study: Content Structure and AI Visibility",
        venue="SE Ranking Research",
        doi="https://seranking.com/blog/ai-overview-study/",
        note="Industry validation of structural optimization strategies. Source for +28-40% visibility improvement from structured formatting (H2/H3 hierarchy, bullet points, logical sections).",
    ),
    Citation(
        authors="Search Engine Land",
        year=2025,
        title="Content Freshness and AI Citations Study",
        venue="Search Engine Land",
        doi="https://searchengineland.com/how-llms-retrieve-rank-information-452553",
        note="Source for the 3.2x citation multiplier for content updated within 30 days. Demonstrates strong AI preference for fresh content.",
    ),
]


@app.get("/citations", response_model=list[Citation])
def get_citations():
    return CITATIONS


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version="1.0.0")
