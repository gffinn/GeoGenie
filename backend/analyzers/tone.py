import re

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

# Hedging/qualifying words that weaken authoritative tone
# Source: Aggarwal et al. (2024) — authoritative tone strategy, variable effect size
HEDGING_WORDS = re.compile(
    r"\b(?:might|could|possibly|perhaps|maybe|seems?|appear(?:s|ed)? to|"
    r"somewhat|arguably|generally|usually|often|tends? to|likely|unlikely|"
    r"it is (?:believed|thought|possible|probable)|in some cases|"
    r"to some extent|more or less|sort of|kind of|a bit|rather|fairly|"
    r"quite possibly|may or may not|not necessarily)\b",
    re.IGNORECASE,
)

# Strong authoritative markers
CONFIDENCE_MARKERS = re.compile(
    r"\b(?:clearly|evidently|undoubtedly|certainly|definitively|"
    r"demonstrates?|proves?|confirms?|establishes?|shows? that|"
    r"the (?:data|evidence|research|findings?) (?:shows?|indicates?|confirms?|proves?)|"
    r"in fact|notably|significantly|crucially|importantly)\b",
    re.IGNORECASE,
)


class ToneAnalyzer(BaseAnalyzer):
    name = "tone"
    score_field = "tone_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        if word_count < 30:
            return {
                "score": 0,
                "hedging_count": 0,
                "confidence_count": 0,
                "word_count": word_count,
                "hedging_density_per_1000": 0,
                "confidence_density_per_1000": 0,
            }

        hedging_matches = HEDGING_WORDS.findall(text)
        confidence_matches = CONFIDENCE_MARKERS.findall(text)

        hedging_count = len(hedging_matches)
        confidence_count = len(confidence_matches)

        hedging_density = (hedging_count / word_count) * 1000
        confidence_density = (confidence_count / word_count) * 1000

        # Scoring: penalize hedging, reward confidence markers
        # Start at 70 (neutral), deduct for hedging, add for confidence
        score = 70.0

        # Penalize hedging: >5 per 1000 words starts hurting
        if hedging_density > 10:
            score -= 40
        elif hedging_density > 5:
            score -= 20
        elif hedging_density > 2:
            score -= 10

        # Reward confidence markers
        if confidence_density > 3:
            score += 30
        elif confidence_density > 1.5:
            score += 20
        elif confidence_density > 0.5:
            score += 10

        score = max(0.0, min(100.0, score))

        return {
            "score": round(score, 1),
            "hedging_count": hedging_count,
            "confidence_count": confidence_count,
            "word_count": word_count,
            "hedging_density_per_1000": round(hedging_density, 2),
            "confidence_density_per_1000": round(confidence_density, 2),
        }
