import re
from urllib.parse import urlparse

import requests

from ..services.scraper import _is_private_host
from .base import BaseAnalyzer

# Full crawler list from Liu et al. (2025) IMC and vendor documentation.
# Organized by purpose: training vs. retrieval/search.
AI_CRAWLERS = {
    # OpenAI
    "GPTBot": {"company": "OpenAI", "purpose": "training", "block_reason": "You don't want content used to train models."},
    "ChatGPT-User": {"company": "OpenAI", "purpose": "retrieval", "block_reason": "You don't want to appear in ChatGPT answers."},
    "OAI-SearchBot": {"company": "OpenAI", "purpose": "search", "block_reason": "You don't want to appear in ChatGPT Search."},
    # Anthropic
    "ClaudeBot": {"company": "Anthropic", "purpose": "training", "block_reason": "You don't want content used to train Claude."},
    "Claude-SearchBot": {"company": "Anthropic", "purpose": "search", "block_reason": "You don't want to appear in Claude answers."},
    # Google
    "Google-Extended": {"company": "Google", "purpose": "training", "block_reason": "You want to block AI training but keep Search."},
    # ByteDance
    "Bytespider": {"company": "ByteDance", "purpose": "training", "block_reason": "You don't want content used by TikTok/ByteDance AI."},
    # Perplexity
    "PerplexityBot": {"company": "Perplexity", "purpose": "retrieval", "block_reason": "You don't want to appear in Perplexity."},
    # Common Crawl
    "CCBot": {"company": "Common Crawl", "purpose": "dataset", "block_reason": "You don't want content in public AI datasets."},
}

# Matches "User-agent: <name>" followed by Disallow/Allow rules
USER_AGENT_BLOCK_RE = re.compile(
    r"User-agent:\s*(\S+)\s*\n((?:(?:Disallow|Allow|Crawl-delay|Sitemap)[^\n]*\n?)*)",
    re.IGNORECASE,
)


class RobotsAnalyzer(BaseAnalyzer):
    name = "robots"
    score_field = "robots_score"

    def analyze(self, html: str, url: str) -> dict:
        parsed = urlparse(url)
        crawler_names = list(AI_CRAWLERS.keys())

        if _is_private_host(parsed.hostname or ""):
            return {
                "score": 100,
                "robots_found": False,
                "crawler_status": {c: "not specified" for c in crawler_names},
                "crawler_details": AI_CRAWLERS,
                "error": "Private/internal URLs are not allowed",
            }

        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            resp = requests.get(robots_url, timeout=10)
            if resp.status_code != 200:
                return {
                    "score": 100,
                    "robots_found": False,
                    "crawler_status": {c: "not specified" for c in crawler_names},
                    "crawler_details": AI_CRAWLERS,
                }
            robots_text = resp.text
        except requests.RequestException:
            return {
                "score": 100,
                "robots_found": False,
                "crawler_status": {c: "not specified" for c in crawler_names},
                "crawler_details": AI_CRAWLERS,
                "error": "Could not fetch robots.txt",
            }

        # Parse robots.txt blocks
        blocks: dict[str, str] = {}
        for match in USER_AGENT_BLOCK_RE.finditer(robots_text):
            agent = match.group(1).strip()
            rules = match.group(2).strip()
            blocks[agent.lower()] = rules

        # Check wildcard block
        wildcard_rules = blocks.get("*", "")
        wildcard_blocks_all = bool(
            re.search(r"Disallow:\s*/\s*$", wildcard_rules, re.MULTILINE)
        )

        crawler_status: dict[str, str] = {}
        for crawler in crawler_names:
            crawler_lower = crawler.lower()
            if crawler_lower in blocks:
                rules = blocks[crawler_lower]
                if re.search(r"Disallow:\s*/\s*$", rules, re.MULTILINE):
                    crawler_status[crawler] = "blocked"
                elif re.search(r"Allow:\s*/\s*$", rules, re.MULTILINE):
                    crawler_status[crawler] = "allowed"
                else:
                    crawler_status[crawler] = "partially blocked"
            elif wildcard_blocks_all:
                crawler_status[crawler] = "blocked"
            else:
                crawler_status[crawler] = "not specified"

        # Score: percentage of crawlers that are allowed/not blocked
        allowed = sum(
            1 for s in crawler_status.values() if s in ("allowed", "not specified")
        )
        score = (allowed / len(crawler_names)) * 100

        # Build detailed status with company/purpose metadata
        detailed_status = {}
        for crawler, status in crawler_status.items():
            meta = AI_CRAWLERS[crawler]
            detailed_status[crawler] = {
                "status": status,
                "company": meta["company"],
                "purpose": meta["purpose"],
            }

        return {
            "score": round(score, 1),
            "robots_found": True,
            "crawler_status": crawler_status,
            "crawler_details": detailed_status,
            "blocked_crawlers": [
                c for c, s in crawler_status.items() if s == "blocked"
            ],
            "allowed_crawlers": [
                c
                for c, s in crawler_status.items()
                if s in ("allowed", "not specified")
            ],
        }
