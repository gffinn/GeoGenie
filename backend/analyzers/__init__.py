from .citations import CitationsAnalyzer
from .crawlability import CrawlabilityAnalyzer
from .faq_format import FAQFormatAnalyzer
from .freshness import FreshnessAnalyzer
from .quotations import QuotationsAnalyzer
from .readability import ReadabilityAnalyzer
from .robots import RobotsAnalyzer
from .schema_markup import SchemaMarkupAnalyzer
from .statistics import StatisticsAnalyzer
from .structure import StructureAnalyzer
from .tone import ToneAnalyzer

ALL_ANALYZERS = [
    StatisticsAnalyzer,
    CitationsAnalyzer,
    StructureAnalyzer,
    QuotationsAnalyzer,
    SchemaMarkupAnalyzer,
    FreshnessAnalyzer,
    FAQFormatAnalyzer,
    ReadabilityAnalyzer,
    ToneAnalyzer,
    RobotsAnalyzer,
    CrawlabilityAnalyzer,
]

__all__ = [
    "ALL_ANALYZERS",
    "StatisticsAnalyzer",
    "CitationsAnalyzer",
    "QuotationsAnalyzer",
    "StructureAnalyzer",
    "SchemaMarkupAnalyzer",
    "FreshnessAnalyzer",
    "FAQFormatAnalyzer",
    "ReadabilityAnalyzer",
    "ToneAnalyzer",
    "RobotsAnalyzer",
    "CrawlabilityAnalyzer",
]
