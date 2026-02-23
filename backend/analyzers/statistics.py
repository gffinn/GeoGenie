import re

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

# Patterns for statistical content
PERCENTAGE_RE = re.compile(r"\d+\.?\d*\s*%")
DOLLAR_RE = re.compile(r"\$[\d,]+\.?\d*")
MULTIPLIER_RE = re.compile(r"\b\d+(\.\d+)?x\b", re.IGNORECASE)
LARGE_NUMBER_RE = re.compile(r"\b\d{1,3}(,\d{3})+\b")
WORD_NUMBER_RE = re.compile(
    r"\b\d+(\.\d+)?\s*(million|billion|trillion|thousand)\b", re.IGNORECASE
)


class StatisticsAnalyzer(BaseAnalyzer):
    name = "statistics"
    score_field = "statistic_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        if word_count == 0:
            return {"score": 0, "stat_count": 0, "word_count": 0, "density": 0.0}

        stats = set()
        for pattern in [
            PERCENTAGE_RE,
            DOLLAR_RE,
            MULTIPLIER_RE,
            LARGE_NUMBER_RE,
            WORD_NUMBER_RE,
        ]:
            for match in pattern.finditer(text):
                stats.add(match.start())

        stat_count = len(stats)
        density = (stat_count / word_count) * 100  # per 100 words

        # Score: 0 stats = 0, density >= 2 per 100 words = 100
        if density == 0:
            score = 0.0
        elif density >= 2.0:
            score = 100.0
        else:
            score = min(100.0, (density / 2.0) * 100)

        return {
            "score": round(score, 1),
            "stat_count": stat_count,
            "word_count": word_count,
            "density_per_100_words": round(density, 2),
        }
