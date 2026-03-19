from .citations import CitationsAnalyzer
from .crawlability import CrawlabilityAnalyzer
from .faq_format import FAQFormatAnalyzer
from .freshness import FreshnessAnalyzer
from .https_analyzer import HttpsAnalyzer
from .llms_txt import LlmsTxtAnalyzer
from .meta_tags import MetaTagsAnalyzer
from .mobile import MobileAnalyzer
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
    QuotationsAnalyzer,
    StructureAnalyzer,
    SchemaMarkupAnalyzer,
    FreshnessAnalyzer,
    FAQFormatAnalyzer,
    ReadabilityAnalyzer,
    ToneAnalyzer,
    RobotsAnalyzer,
    CrawlabilityAnalyzer,
    HttpsAnalyzer,
    MetaTagsAnalyzer,
    MobileAnalyzer,
    LlmsTxtAnalyzer,
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
    "HttpsAnalyzer",
    "MetaTagsAnalyzer",
    "MobileAnalyzer",
    "LlmsTxtAnalyzer",
]
