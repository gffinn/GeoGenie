from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class MetaTagsAnalyzer(BaseAnalyzer):
    name = "meta_tags"
    score_field = "meta_tags_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""
        has_title = bool(title_text)

        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc_content = meta_desc.get("content", "").strip() if meta_desc else ""
        has_description = bool(desc_content)

        score = 0.0
        if has_title:
            score += 50.0
        if has_description:
            score += 50.0

        return {
            "score": score,
            "has_title": has_title,
            "title_text": title_text[:120] if title_text else "",
            "has_meta_description": has_description,
            "meta_description": desc_content[:200] if desc_content else "",
            "meta_description_length": len(desc_content),
        }
