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

    # Site crawl settings
    MAX_CRAWL_PAGES: int = 20
    MAX_CRAWL_DEPTH: int = 2       # 0 = seed page, 1 = linked from seed
    CRAWL_DELAY_SECONDS: float = 1.0  # politeness delay between fetches

    # Scoring weights — GEO research signals (Aggarwal et al. KDD 2024,
    # SE Ranking 2025, Search Engine Land 2025) plus technical infrastructure
    # rubric (v2). Total = 1.0.
    WEIGHTS: dict[str, float] = {
        # ── GEO Content Signals (research-backed) ──────────────────────────
        "statistic_score": 0.13,      # +40-41% visibility — Aggarwal et al. (2024)
        "quotation_score": 0.11,      # +38-40% visibility — Aggarwal et al. (2024)
        "citation_score": 0.10,       # +30-40% visibility — Aggarwal et al. (2024)
        "freshness_score": 0.09,      # 3.2x more citations — Search Engine Land (2025)
        # ── Technical Infrastructure ────────────────────────────────────────
        "https_score": 0.09,          # Security prerequisite; critical failure if absent
        "meta_tags_score": 0.07,      # Title + meta description discoverability
        "mobile_score": 0.05,         # Viewport / mobile responsiveness
        # ── Content & Structure ─────────────────────────────────────────────
        "structure_score": 0.08,      # Heading hierarchy + semantic HTML — SE Ranking (2025)
        "schema_score": 0.06,         # +28% visibility — industry consensus
        "faq_score": 0.04,            # High citation rate — multiple sources
        "tone_score": 0.04,           # Variable effect — Aggarwal et al. (2024)
        "readability_score": 0.02,    # +15-30% visibility — Aggarwal et al. (2024)
        # ── AI Access ───────────────────────────────────────────────────────
        "crawlability_score": 0.05,   # Technical prerequisite; critical failure if 0
        "robots_score": 0.04,         # AI crawler access; critical failure if 0
        "llms_txt_score": 0.03,       # /llms.txt presence — emerging standard
    }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
