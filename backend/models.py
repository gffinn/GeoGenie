import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(2048), index=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)

    # GEO content signals
    statistic_score: Mapped[float] = mapped_column(Float, default=0.0)
    citation_score: Mapped[float] = mapped_column(Float, default=0.0)
    quotation_score: Mapped[float] = mapped_column(Float, default=0.0)
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)
    # Technical infrastructure
    https_score: Mapped[float] = mapped_column(Float, default=0.0)
    meta_tags_score: Mapped[float] = mapped_column(Float, default=0.0)
    mobile_score: Mapped[float] = mapped_column(Float, default=0.0)
    # Content & structure
    structure_score: Mapped[float] = mapped_column(Float, default=0.0)
    schema_score: Mapped[float] = mapped_column(Float, default=0.0)
    faq_score: Mapped[float] = mapped_column(Float, default=0.0)
    readability_score: Mapped[float] = mapped_column(Float, default=0.0)
    tone_score: Mapped[float] = mapped_column(Float, default=0.0)
    # AI access
    crawlability_score: Mapped[float] = mapped_column(Float, default=0.0)
    robots_score: Mapped[float] = mapped_column(Float, default=0.0)
    llms_txt_score: Mapped[float] = mapped_column(Float, default=0.0)

    raw_metrics: Mapped[str] = mapped_column(Text, default="{}")
    recommendations: Mapped[str] = mapped_column(Text, default="[]")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    fetch_time_ms: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (Index("ix_url_created", "url", "created_at"),)

    def get_raw_metrics(self) -> dict:
        return json.loads(self.raw_metrics)

    def get_recommendations(self) -> list:
        return json.loads(self.recommendations)
