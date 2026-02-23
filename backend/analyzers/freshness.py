import json
import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

DATE_TEXT_RE = re.compile(
    r"(?:Updated|Last modified|Modified|Published|Posted|Edited|Revised)"
    r"[:\s]*(\w+ \d{1,2},?\s*\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})",
    re.IGNORECASE,
)

DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%B %d, %Y",
    "%B %d %Y",
    "%b %d, %Y",
    "%m/%d/%Y",
]


def _parse_date(date_str: str) -> datetime | None:
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


class FreshnessAnalyzer(BaseAnalyzer):
    name = "freshness"
    score_field = "freshness_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        now = datetime.now(timezone.utc)
        dates_found = []

        # 1. Check JSON-LD schema for dateModified/datePublished
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "")
                items = [data] if isinstance(data, dict) else data
                if isinstance(data, dict) and "@graph" in data:
                    items = data["@graph"]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    for field in ("dateModified", "datePublished"):
                        dt = _parse_date(item.get(field, ""))
                        if dt:
                            dates_found.append(("schema_" + field, dt))
            except (json.JSONDecodeError, TypeError):
                continue

        # 2. Check meta tags
        meta_names = [
            "article:modified_time",
            "article:published_time",
            "og:updated_time",
            "last-modified",
        ]
        for name in meta_names:
            tag = soup.find("meta", {"property": name}) or soup.find(
                "meta", {"name": name}
            )
            if tag and tag.get("content"):
                dt = _parse_date(tag["content"])
                if dt:
                    dates_found.append(("meta_" + name, dt))

        # 3. Check visible text patterns
        text = soup.get_text(separator=" ", strip=True)
        for match in DATE_TEXT_RE.finditer(text):
            dt = _parse_date(match.group(1))
            if dt:
                dates_found.append(("text_pattern", dt))

        if not dates_found:
            return {
                "score": 0,
                "days_since_update": None,
                "most_recent_date": None,
                "date_sources": [],
            }

        # Use most recent date
        most_recent = max(dates_found, key=lambda x: x[1])
        days_since = (now - most_recent[1]).days

        # Score based on age
        if days_since < 0:
            days_since = 0
        if days_since <= 30:
            score = 100.0
        elif days_since <= 90:
            score = 70.0
        elif days_since <= 180:
            score = 40.0
        elif days_since <= 365:
            score = 20.0
        else:
            score = 0.0

        return {
            "score": score,
            "days_since_update": days_since,
            "most_recent_date": most_recent[1].isoformat(),
            "date_source": most_recent[0],
            "date_sources": [
                {"source": s, "date": d.isoformat()} for s, d in dates_found
            ],
        }
