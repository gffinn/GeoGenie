import textstat
from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class ReadabilityAnalyzer(BaseAnalyzer):
    name = "readability"
    score_field = "readability_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        words = text.split()
        word_count = len(words)

        if word_count < 30:
            return {
                "score": 0,
                "flesch_reading_ease": 0,
                "word_count": word_count,
                "sentence_count": 0,
                "avg_sentence_length": 0,
            }

        flesch = textstat.flesch_reading_ease(text)
        sentence_count = textstat.sentence_count(text)
        avg_sentence_length = word_count / max(1, sentence_count)

        # Score: Flesch 60-70 is optimal (100 points)
        # Below 30 or above 80 gets penalized
        if 60 <= flesch <= 70:
            score = 100.0
        elif 50 <= flesch < 60:
            score = 80.0
        elif 70 < flesch <= 80:
            score = 80.0
        elif 40 <= flesch < 50:
            score = 60.0
        elif 80 < flesch <= 90:
            score = 60.0
        elif 30 <= flesch < 40:
            score = 40.0
        elif flesch > 90:
            score = 40.0
        else:
            # Below 30
            score = 20.0

        return {
            "score": round(score, 1),
            "flesch_reading_ease": round(flesch, 1),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
        }
