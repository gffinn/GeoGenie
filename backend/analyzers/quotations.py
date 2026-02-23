import re

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

# Quoted speech patterns: "..." said X, X said "..."
QUOTED_TEXT_RE = re.compile(r'\u201c[^"\u201d]{10,}\u201d|"[^"]{10,}"')
ATTRIBUTION_RE = re.compile(
    r"(?:said|says|stated|noted|explained|added|argued|wrote|commented|according to)\s",
    re.IGNORECASE,
)
EXPERT_TITLE_RE = re.compile(
    r"\b(?:Dr\.|Prof(?:essor)?\.?|CEO|CTO|CFO|Founder|Director|President|"
    r"Chairman|PhD|MD|Analyst|Researcher|Scientist|Expert|Specialist)\b",
    re.IGNORECASE,
)


class QuotationsAnalyzer(BaseAnalyzer):
    name = "quotations"
    score_field = "quotation_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        # Count blockquote tags
        blockquotes = soup.find_all("blockquote")
        blockquote_count = len(blockquotes)

        # Count inline quoted text
        inline_quotes = QUOTED_TEXT_RE.findall(text)
        inline_quote_count = len(inline_quotes)

        # Count attributions ("X said", "according to X")
        attributions = ATTRIBUTION_RE.findall(text)
        attribution_count = len(attributions)

        # Count expert title mentions near quotes
        expert_mentions = EXPERT_TITLE_RE.findall(text)
        expert_count = len(expert_mentions)

        total_quotes = blockquote_count + inline_quote_count

        # Scoring
        quote_score = min(50, total_quotes * 15)
        attribution_score = min(25, attribution_count * 8)
        expert_bonus = min(25, expert_count * 5)
        score = min(100.0, quote_score + attribution_score + expert_bonus)

        return {
            "score": round(score, 1),
            "blockquote_count": blockquote_count,
            "inline_quote_count": inline_quote_count,
            "total_quotes": total_quotes,
            "attribution_count": attribution_count,
            "expert_mentions": expert_count,
        }
