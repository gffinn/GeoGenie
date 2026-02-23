import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

CITATION_PHRASES = re.compile(
    r"(?:according to|study shows?|research (?:indicates?|suggests?|shows?|found)|"
    r"data (?:from|shows?)|survey (?:by|found)|report (?:by|from)|published (?:in|by)|"
    r"findings? (?:from|show|indicate))",
    re.IGNORECASE,
)
BRACKET_CITATION_RE = re.compile(r"\[\d+\]|\[[\w\s,]+(?:,\s*\d{4})?\]")
SOURCE_LABEL_RE = re.compile(r"\((?:Source|Ref|Citation)[^)]*\)", re.IGNORECASE)

AUTHORITY_TLDS = {".edu", ".gov"}
AUTHORITY_DOMAINS = {
    "who.int",
    "nih.gov",
    "cdc.gov",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "wiley.com",
    "pubmed.ncbi.nlm.nih.gov",
    "arxiv.org",
    "jstor.org",
    "ieee.org",
    "acm.org",
}


class CitationsAnalyzer(BaseAnalyzer):
    name = "citations"
    score_field = "citation_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        # Count textual citation patterns
        phrase_count = len(CITATION_PHRASES.findall(text))
        bracket_count = len(BRACKET_CITATION_RE.findall(text))
        source_count = len(SOURCE_LABEL_RE.findall(text))
        citation_count = phrase_count + bracket_count + source_count

        # Analyze outbound links
        page_domain = urlparse(url).netloc.lower()
        external_links = 0
        authority_links = 0

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href.startswith("http"):
                continue
            link_domain = urlparse(href).netloc.lower()
            if link_domain == page_domain:
                continue
            external_links += 1
            if any(link_domain.endswith(tld) for tld in AUTHORITY_TLDS):
                authority_links += 1
            elif any(auth in link_domain for auth in AUTHORITY_DOMAINS):
                authority_links += 1

        # Score calculation
        if word_count == 0:
            return {
                "score": 0,
                "citation_count": 0,
                "external_links": 0,
                "authority_links": 0,
            }

        density = (citation_count / word_count) * 1000  # per 1000 words
        link_score = min(40, external_links * 5)
        authority_bonus = min(20, authority_links * 10)
        density_score = min(40, density * 10)
        score = min(100.0, density_score + link_score + authority_bonus)

        return {
            "score": round(score, 1),
            "citation_count": citation_count,
            "phrase_citations": phrase_count,
            "bracket_citations": bracket_count,
            "external_links": external_links,
            "authority_links": authority_links,
            "citation_density_per_1000": round(density, 2),
        }
