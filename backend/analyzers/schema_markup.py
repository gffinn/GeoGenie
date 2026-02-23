import json

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

HIGH_VALUE_TYPES = {"Article", "NewsArticle", "BlogPosting", "FAQ", "HowTo"}
MEDIUM_VALUE_TYPES = {
    "Organization",
    "Person",
    "Product",
    "WebPage",
    "WebSite",
    "BreadcrumbList",
    "LocalBusiness",
}

# Key properties that indicate a well-populated schema
ARTICLE_PROPS = {"headline", "datePublished", "author", "dateModified", "description"}
FAQ_PROPS = {"mainEntity"}


class SchemaMarkupAnalyzer(BaseAnalyzer):
    name = "schema_markup"
    score_field = "schema_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        ld_scripts = soup.find_all("script", {"type": "application/ld+json"})

        if not ld_scripts:
            return {
                "score": 0,
                "schema_count": 0,
                "schema_types": [],
                "has_article_schema": False,
                "has_faq_schema": False,
            }

        schemas = []
        schema_types = []

        for script in ld_scripts:
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    schemas.extend(data)
                elif isinstance(data, dict):
                    # Handle @graph
                    if "@graph" in data:
                        schemas.extend(data["@graph"])
                    else:
                        schemas.append(data)
            except (json.JSONDecodeError, TypeError):
                continue

        for schema in schemas:
            if isinstance(schema, dict) and "@type" in schema:
                s_type = schema["@type"]
                if isinstance(s_type, list):
                    schema_types.extend(s_type)
                else:
                    schema_types.append(s_type)

        type_set = set(schema_types)
        has_high_value = bool(type_set & HIGH_VALUE_TYPES)
        has_medium_value = bool(type_set & MEDIUM_VALUE_TYPES)
        has_article = bool(type_set & {"Article", "NewsArticle", "BlogPosting"})
        has_faq = "FAQ" in type_set or "FAQPage" in type_set

        # Check property completeness for articles
        completeness = 0.0
        if has_article:
            for schema in schemas:
                s_type = schema.get("@type", "")
                if s_type in {"Article", "NewsArticle", "BlogPosting"} or (
                    isinstance(s_type, list) and set(s_type) & HIGH_VALUE_TYPES
                ):
                    present = sum(1 for p in ARTICLE_PROPS if schema.get(p))
                    completeness = present / len(ARTICLE_PROPS)
                    break

        # Scoring
        if has_high_value:
            base = 70
            if completeness >= 0.8:
                base = 100
            elif completeness >= 0.5:
                base = 85
            score = base
        elif has_medium_value:
            score = 50
        else:
            score = 30  # Has schema but not high-value types

        if has_faq:
            score = min(100, score + 15)

        return {
            "score": round(min(100.0, score), 1),
            "schema_count": len(schemas),
            "schema_types": list(type_set),
            "has_article_schema": has_article,
            "has_faq_schema": has_faq,
            "property_completeness": round(completeness, 2),
        }
