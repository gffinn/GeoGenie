import json
import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from ..analyzers import ALL_ANALYZERS
from ..config import settings
from ..models import AnalysisResult
from .recommender import generate_recommendations
from .scorer import calculate_total_score

logger = logging.getLogger(__name__)


def get_cached_result(db: Session, url: str) -> AnalysisResult | None:
    """Return a cached result if it exists and is less than CACHE_TTL_HOURS old."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.CACHE_TTL_HOURS)
    return (
        db.query(AnalysisResult)
        .filter(AnalysisResult.url == url, AnalysisResult.created_at >= cutoff)
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )


def run_analysis(url: str, html: str, fetch_time_ms: int, db: Session) -> AnalysisResult:
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
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
