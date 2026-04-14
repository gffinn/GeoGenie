import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db, init_db
from .models import AnalysisResult, SiteCrawl, SiteCrawlPage
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Citation,
    CrawlPageStatus,
    CrawlRequest,
    CrawlStartResponse,
    CrawlStatusResponse,
    HealthResponse,
    Recommendation,
    ScoreBreakdown,
)
from .services.analysis import get_cached_result, run_analysis
from .services.crawler import run_site_crawl
from .services.scorer import score_to_grade
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


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_url(request: AnalyzeRequest, db: Session = Depends(get_db)):
    url = str(request.url)

    # Check cache
    cached = get_cached_result(db, url)
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
    result = run_analysis(url, html, fetch_time_ms, db)
    return _result_to_response(result, cached=False)


@app.get("/analyze/{url_encoded:path}", response_model=AnalyzeResponse)
def get_analysis(url_encoded: str, db: Session = Depends(get_db)):
    url = url_encoded if url_encoded.startswith("http") else f"https://{url_encoded}"

    # Check cache
    cached = get_cached_result(db, url)
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

    result = run_analysis(url, html, fetch_time_ms, db)
    return _result_to_response(result, cached=False)


@app.post("/crawl", response_model=CrawlStartResponse)
def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    url = str(request.url)
    domain = urlparse(url).netloc

    crawl = SiteCrawl(url=url, domain=domain, status="pending")
    db.add(crawl)
    db.commit()
    db.refresh(crawl)

    background_tasks.add_task(run_site_crawl, crawl.id)
    logger.info("Started crawl %d for %s", crawl.id, url)

    return CrawlStartResponse(crawl_id=crawl.id, status=crawl.status)


@app.get("/crawl/{crawl_id}", response_model=CrawlStatusResponse)
def get_crawl_status(crawl_id: int, db: Session = Depends(get_db)):
    crawl = db.query(SiteCrawl).filter(SiteCrawl.id == crawl_id).first()
    if not crawl:
        raise HTTPException(status_code=404, detail="Crawl not found")

    pages = (
        db.query(SiteCrawlPage)
        .filter(SiteCrawlPage.crawl_id == crawl_id)
        .order_by(SiteCrawlPage.depth, SiteCrawlPage.id)
        .all()
    )

    page_statuses = []
    for page in pages:
        page_data = CrawlPageStatus(
            url=page.url,
            status=page.status,
            depth=page.depth,
            error=page.error,
        )
        if page.result:
            page_data.total_score = page.result.total_score
            critical = {
                "crawlability_score": page.result.crawlability_score,
                "robots_score": page.result.robots_score,
                "https_score": page.result.https_score,
            }
            page_data.grade = score_to_grade(page.result.total_score, critical)
            page_data.scores = ScoreBreakdown(
                statistic_score=page.result.statistic_score,
                citation_score=page.result.citation_score,
                quotation_score=page.result.quotation_score,
                freshness_score=page.result.freshness_score,
                https_score=page.result.https_score,
                meta_tags_score=page.result.meta_tags_score,
                mobile_score=page.result.mobile_score,
                structure_score=page.result.structure_score,
                schema_score=page.result.schema_score,
                faq_score=page.result.faq_score,
                tone_score=page.result.tone_score,
                readability_score=page.result.readability_score,
                crawlability_score=page.result.crawlability_score,
                robots_score=page.result.robots_score,
                llms_txt_score=page.result.llms_txt_score,
            )
        page_statuses.append(page_data)

    return CrawlStatusResponse(
        crawl_id=crawl.id,
        url=crawl.url,
        status=crawl.status,
        pages_found=crawl.pages_found,
        pages_analyzed=crawl.pages_analyzed,
        total_score=crawl.total_score,
        grade=crawl.grade,
        pages=page_statuses,
        created_at=crawl.created_at,
        completed_at=crawl.completed_at,
    )


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
