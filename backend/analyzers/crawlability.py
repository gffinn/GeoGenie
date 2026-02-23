import re

from bs4 import BeautifulSoup

from .base import BaseAnalyzer

JS_FRAMEWORK_INDICATORS = [
    re.compile(r'<div\s+id=["\'](?:root|app|__next|__nuxt)["\']', re.IGNORECASE),
    re.compile(r"<noscript>.*?enable javascript", re.IGNORECASE | re.DOTALL),
]

JS_PLACEHOLDER_PATTERNS = [
    re.compile(r"loading\.{0,3}", re.IGNORECASE),
    re.compile(r"please enable javascript", re.IGNORECASE),
    re.compile(r"this app requires javascript", re.IGNORECASE),
    re.compile(r"you need to enable javascript", re.IGNORECASE),
]


class CrawlabilityAnalyzer(BaseAnalyzer):
    name = "crawlability"
    score_field = "crawlability_score"

    def analyze(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "lxml")
        body = soup.find("body")

        if not body:
            return {
                "score": 0,
                "has_body": False,
                "body_text_length": 0,
                "js_rendering_likely": True,
            }

        # Remove script/style from body text analysis
        body_copy = BeautifulSoup(str(body), "lxml")
        for tag in body_copy(["script", "style"]):
            tag.decompose()
        body_text = body_copy.get_text(separator=" ", strip=True)
        text_length = len(body_text)

        # Check for JS framework root elements with no content
        js_framework_detected = False
        for pattern in JS_FRAMEWORK_INDICATORS:
            if pattern.search(html):
                js_framework_detected = True
                break

        # Check for loading/placeholder text
        js_placeholder = False
        for pattern in JS_PLACEHOLDER_PATTERNS:
            if pattern.search(body_text):
                js_placeholder = True
                break

        # Count meaningful HTML elements
        content_elements = len(
            body.find_all(["p", "article", "section", "table", "ul", "ol", "dl"])
        )

        # Scoring
        if text_length < 100:
            score = 0.0
            js_rendering_likely = True
        elif text_length < 500:
            score = 40.0
            js_rendering_likely = js_framework_detected or js_placeholder
        else:
            score = 100.0
            js_rendering_likely = False

        if js_placeholder and score > 0:
            score = max(0, score - 50)

        if js_framework_detected and text_length < 500:
            score = max(0, score - 30)

        # Bonus for rich content
        if content_elements >= 5 and text_length >= 500:
            score = min(100.0, score + 10)

        return {
            "score": round(max(0.0, min(100.0, score)), 1),
            "has_body": True,
            "body_text_length": text_length,
            "content_element_count": content_elements,
            "js_framework_detected": js_framework_detected,
            "js_placeholder_detected": js_placeholder,
            "js_rendering_likely": js_rendering_likely,
        }
