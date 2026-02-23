from bs4 import BeautifulSoup

from .base import BaseAnalyzer

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]


class StructureAnalyzer(BaseAnalyzer):
    name = "structure"
    score_field = "structure_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        headings = []
        for tag in soup.find_all(HEADING_TAGS):
            level = int(tag.name[1])
            headings.append({"level": level, "text": tag.get_text(strip=True)})

        heading_count = len(headings)
        h1_count = sum(1 for h in headings if h["level"] == 1)
        h2_count = sum(1 for h in headings if h["level"] == 2)
        h3_count = sum(1 for h in headings if h["level"] == 3)

        nesting_errors = 0
        if headings:
            for i in range(1, len(headings)):
                prev_level = headings[i - 1]["level"]
                curr_level = headings[i]["level"]
                # Skipping levels (e.g., H1 -> H3 without H2)
                if curr_level > prev_level + 1:
                    nesting_errors += 1

        # Scoring
        score = 100.0

        # No headings at all
        if heading_count == 0:
            return {
                "score": 0,
                "heading_count": 0,
                "h1_count": 0,
                "h2_count": 0,
                "h3_count": 0,
                "nesting_errors": 0,
            }

        # Penalize missing H1
        if h1_count == 0:
            score -= 30

        # Penalize multiple H1s
        if h1_count > 1:
            score -= 20

        # Penalize no H2s (flat structure)
        if h2_count == 0:
            score -= 20

        # Penalize nesting errors
        score -= nesting_errors * 10

        # Bonus for having H3s (deeper structure)
        if h3_count > 0 and h2_count > 0:
            score = min(100.0, score + 10)

        score = max(0.0, min(100.0, score))

        return {
            "score": round(score, 1),
            "heading_count": heading_count,
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "nesting_errors": nesting_errors,
            "headings": headings[:20],  # Cap for storage
        }
