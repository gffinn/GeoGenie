from pydantic import field_validator
from pydantic_settings import BaseSettings

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://localhost/neondb"
    CACHE_TTL_HOURS: int = 24
    REQUEST_TIMEOUT: int = 15
    MAX_CONTENT_LENGTH: int = 5_000_000  # 5MB
    CORS_ORIGINS: list[str] = _DEFAULT_CORS_ORIGINS

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Scoring weights derived from Aggarwal et al. (2024) KDD effect sizes,
    # SE Ranking (2025), and Search Engine Land (2025)
    WEIGHTS: dict[str, float] = {
        "statistic_score": 0.17,      # +40-41% visibility — Aggarwal et al. (2024)
        "quotation_score": 0.15,      # +38-40% visibility — Aggarwal et al. (2024)
        "citation_score": 0.14,       # +30-40% visibility — Aggarwal et al. (2024)
        "freshness_score": 0.12,      # 3.2x more citations — Search Engine Land (2025)
        "structure_score": 0.10,      # +28-40% visibility — SE Ranking (2025)
        "schema_score": 0.08,         # +28% visibility — industry consensus
        "tone_score": 0.05,           # Variable effect — Aggarwal et al. (2024)
        "faq_score": 0.05,            # High citation rate — multiple sources
        "crawlability_score": 0.07,   # Technical prerequisite
        "robots_score": 0.05,         # Technical prerequisite
        "readability_score": 0.02,    # +15-30% visibility — Aggarwal et al. (2024)
    }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
