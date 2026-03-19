from .base import BaseAnalyzer


class HttpsAnalyzer(BaseAnalyzer):
    name = "https"
    score_field = "https_score"

    def analyze(self, html: str, url: str) -> dict:
        is_https = url.lower().startswith("https://")
        return {
            "score": 100.0 if is_https else 0.0,
            "uses_https": is_https,
            "scheme": "https" if is_https else "http",
        }
