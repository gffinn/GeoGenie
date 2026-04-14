from urllib.parse import urlparse

import requests

from ..services.scraper import _is_private_host
from .base import BaseAnalyzer


class LlmsTxtAnalyzer(BaseAnalyzer):
    name = "llms_txt"
    score_field = "llms_txt_score"

    def analyze(self, html: str, url: str) -> dict:
        parsed = urlparse(url)

        if _is_private_host(parsed.hostname or ""):
            return {
                "score": 0.0,
                "llms_txt_found": False,
                "error": "Private/internal URLs are not checked",
            }

        llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"

        try:
            resp = requests.get(llms_url, timeout=8, allow_redirects=True)
            if resp.status_code == 200 and resp.text.strip():
                return {
                    "score": 100.0,
                    "llms_txt_found": True,
                    "llms_txt_url": llms_url,
                    "content_length": len(resp.text),
                }
            return {
                "score": 0.0,
                "llms_txt_found": False,
                "llms_txt_url": llms_url,
            }
        except requests.RequestException:
            return {
                "score": 0.0,
                "llms_txt_found": False,
                "llms_txt_url": llms_url,
                "error": "Could not fetch llms.txt",
            }
