import json
import re

from bs4 import BeautifulSoup, Tag

from .base import BaseAnalyzer

QUESTION_RE = re.compile(
    r"^(?:What|How|Why|When|Where|Who|Which|Can|Do|Does|Is|Are|Should|Will|Would)\b.+\?$",
    re.IGNORECASE,
)


def _count_answer_blocks(soup: BeautifulSoup) -> int:
    """Detect 40-60 word Q&A answer blocks that can be directly extracted by LLMs.

    Source: GEO Strategies doc — "Create 40-60 word Q&A blocks that can be
    directly extracted. LLM preferred format."
    """
    count = 0
    for heading in soup.find_all(["h2", "h3", "h4"]):
        heading_text = heading.get_text(strip=True)
        if not (QUESTION_RE.match(heading_text) or heading_text.endswith("?")):
            continue

        # Collect text from siblings until next heading
        answer_text = []
        sibling = heading.find_next_sibling()
        while sibling and isinstance(sibling, Tag):
            if sibling.name and sibling.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                break
            answer_text.append(sibling.get_text(separator=" ", strip=True))
            sibling = sibling.find_next_sibling()

        combined = " ".join(answer_text)
        word_count = len(combined.split())
        if 30 <= word_count <= 80:
            count += 1

    return count


class FAQFormatAnalyzer(BaseAnalyzer):
    name = "faq_format"
    score_field = "faq_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        # 1. Check for FAQ schema markup
        faq_schema_items = 0
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "")
                items = [data] if isinstance(data, dict) else data
                if isinstance(data, dict) and "@graph" in data:
                    items = data["@graph"]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    s_type = item.get("@type", "")
                    if s_type in ("FAQPage", "FAQ"):
                        entities = item.get("mainEntity", [])
                        if isinstance(entities, list):
                            faq_schema_items += len(entities)
            except (json.JSONDecodeError, TypeError):
                continue

        # 2. Check for <details>/<summary> elements
        details_count = len(soup.find_all("details"))

        # 3. Check headings for question patterns
        question_headings = 0
        for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
            heading_text = tag.get_text(strip=True)
            if QUESTION_RE.match(heading_text) or heading_text.endswith("?"):
                question_headings += 1

        # 4. Check for elements with FAQ-related classes/IDs
        faq_elements = len(
            soup.find_all(
                attrs={
                    "class": re.compile(r"faq|accordion|question", re.IGNORECASE),
                }
            )
        )

        # 5. Detect answer blocks (40-60 word Q&A blocks, LLM preferred format)
        answer_blocks = _count_answer_blocks(soup)

        total_faq_signals = (
            faq_schema_items + details_count + question_headings
            + faq_elements + answer_blocks
        )

        # Scoring
        score = 0.0
        if faq_schema_items > 0:
            score += min(40, faq_schema_items * 12)
        if details_count > 0:
            score += min(15, details_count * 5)
        if question_headings > 0:
            score += min(15, question_headings * 5)
        if faq_elements > 0:
            score += min(10, faq_elements * 3)
        if answer_blocks > 0:
            score += min(20, answer_blocks * 7)

        score = min(100.0, score)

        return {
            "score": round(score, 1),
            "faq_schema_items": faq_schema_items,
            "details_summary_count": details_count,
            "question_headings": question_headings,
            "faq_elements": faq_elements,
            "answer_blocks": answer_blocks,
            "total_faq_signals": total_faq_signals,
        }
