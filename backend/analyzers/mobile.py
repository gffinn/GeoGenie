from bs4 import BeautifulSoup

from .base import BaseAnalyzer


class MobileAnalyzer(BaseAnalyzer):
    name = "mobile"
    score_field = "mobile_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")

        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            return {
                "score": 0.0,
                "has_viewport": False,
                "is_mobile_responsive": False,
                "viewport_content": "",
            }

        content = viewport.get("content", "").strip()
        is_responsive = "width=device-width" in content

        return {
            "score": 100.0 if is_responsive else 50.0,
            "has_viewport": True,
            "is_mobile_responsive": is_responsive,
            "viewport_content": content,
        }
