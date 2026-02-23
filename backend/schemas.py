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
    statistic_score: float
    citation_score: float
    quotation_score: float
    structure_score: float
    schema_score: float
    freshness_score: float
    faq_score: float
    readability_score: float
    tone_score: float
    robots_score: float
    crawlability_score: float


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


class HealthResponse(BaseModel):
    status: str
    version: str
