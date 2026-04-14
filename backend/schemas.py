from datetime import datetime

from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class Recommendation(BaseModel):
    priority: int
    category: str
    message: str
    impact: str  # "high", "medium", "low"


class ScoreBreakdown(BaseModel):
    # GEO content signals
    statistic_score: float
    citation_score: float
    quotation_score: float
    freshness_score: float
    # Technical infrastructure
    https_score: float
    meta_tags_score: float
    mobile_score: float
    # Content & structure
    structure_score: float
    schema_score: float
    faq_score: float
    tone_score: float
    readability_score: float
    # AI access
    crawlability_score: float
    robots_score: float
    llms_txt_score: float


class AnalyzeResponse(BaseModel):
    url: str
    total_score: float
    grade: str
    scores: ScoreBreakdown
    raw_metrics: dict
    recommendations: list[Recommendation]
    cached: bool
    analyzed_at: datetime


class Citation(BaseModel):
    authors: str
    year: int
    title: str
    venue: str
    doi: str
    note: str


class CrawlRequest(BaseModel):
    url: HttpUrl


class CrawlStartResponse(BaseModel):
    crawl_id: int
    status: str


class CrawlPageStatus(BaseModel):
    url: str
    status: str
    depth: int
    total_score: float | None = None
    grade: str | None = None
    scores: ScoreBreakdown | None = None
    error: str | None = None


class CrawlStatusResponse(BaseModel):
    crawl_id: int
    url: str
    status: str
    pages_found: int
    pages_analyzed: int
    total_score: float | None = None
    grade: str | None = None
    pages: list[CrawlPageStatus]
    created_at: datetime
    completed_at: datetime | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
