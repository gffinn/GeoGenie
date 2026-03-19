from bs4 import BeautifulSoup

from .base import BaseAnalyzer

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]

# Points per semantic element — total possible: 43, capped at 40
SEMANTIC_WEIGHTS: dict[str, int] = {
    "main": 10,
    "header": 8,
    "nav": 7,
    "article": 8,
    "section": 5,
    "footer": 3,
    "aside": 2,
}


class StructureAnalyzer(BaseAnalyzer):
    name = "structure"
    score_field = "structure_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # ── Heading hierarchy (60 pts max) ─────────────────────────────────
        headings = []
        for tag in soup.find_all(HEADING_TAGS):
            level = int(tag.name[1])
            headings.append({"level": level, "text": tag.get_text(strip=True)})

        heading_count = len(headings)
        h1_count = sum(1 for h in headings if h["level"] == 1)
        h2_count = sum(1 for h in headings if h["level"] == 2)
        h3_count = sum(1 for h in headings if h["level"] == 3)

        nesting_errors = 0
        for i in range(1, len(headings)):
            if headings[i]["level"] > headings[i - 1]["level"] + 1:
                nesting_errors += 1

        heading_score = 60.0

        if heading_count == 0:
            heading_score = 0.0
        else:
            if h1_count == 0:
                heading_score -= 20.0
            if h1_count > 1:
                heading_score -= 15.0
            if h2_count == 0:
                heading_score -= 15.0
            heading_score -= nesting_errors * 7.0
            if h3_count > 0 and h2_count > 0:
                heading_score = min(60.0, heading_score + 7.0)

        heading_score = max(0.0, heading_score)

        # ── Semantic HTML elements (40 pts max) ────────────────────────────
        semantic_found: dict[str, bool] = {
            el: bool(soup.find(el)) for el in SEMANTIC_WEIGHTS
        }

        semantic_score = min(
            40.0,
            sum(pts for el, pts in SEMANTIC_WEIGHTS.items() if semantic_found[el]),
        )

        total_score = max(0.0, min(100.0, heading_score + semantic_score))

        return {
            "score": round(total_score, 1),
            "heading_score": round(heading_score, 1),
            "semantic_score": round(semantic_score, 1),
            "heading_count": heading_count,
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "nesting_errors": nesting_errors,
            "headings": headings[:20],
            "semantic_elements_found": semantic_found,
        }
