import ipaddress
import logging
import re
import socket
import time
from urllib.parse import urlparse

import requests

from ..config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Patterns that indicate JS-rendered content (empty shell)
JS_SHELL_PATTERNS = [
    re.compile(r'<div\s+id=["\'](?:root|app|__next|__nuxt)["\']>\s*</div>', re.IGNORECASE),
    re.compile(r"<body[^>]*>\s*<(?:div|noscript|script)", re.IGNORECASE),
]

MIN_CONTENT_LENGTH = 500  # Minimum body text to consider page as rendered


class FetchError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _is_private_host(hostname: str) -> bool:
    """Check if a hostname resolves to a private/internal IP address."""
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
    except (socket.gaierror, ValueError):
        return True  # Can't resolve — treat as unsafe
    return False


def validate_url(url: str) -> str:
    """Validate and normalize the URL. Blocks private/internal targets."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError("URL must use http or https scheme")
    if not parsed.netloc:
        raise FetchError("Invalid URL: no domain found")

    hostname = parsed.hostname or ""
    if _is_private_host(hostname):
        raise FetchError("URLs targeting private or internal networks are not allowed")

    return url


def _looks_js_rendered(html: str) -> bool:
    """Check if the HTML looks like an empty JS shell."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    if not body:
        return True

    # Strip scripts/styles and check text length
    for tag in body(["script", "style"]):
        tag.decompose()
    text = body.get_text(strip=True)

    if len(text) < MIN_CONTENT_LENGTH:
        return True

    for pattern in JS_SHELL_PATTERNS:
        if pattern.search(html):
            if len(text) < MIN_CONTENT_LENGTH:
                return True

    return False


def _fetch_with_requests(url: str) -> tuple[str, int]:
    """Fast fetch with requests (no JS execution)."""
    start = time.time()
    resp = requests.get(
        url,
        headers=HEADERS,
        timeout=settings.REQUEST_TIMEOUT,
        allow_redirects=True,
    )
    fetch_time_ms = int((time.time() - start) * 1000)

    if resp.status_code >= 400:
        raise FetchError(
            f"HTTP {resp.status_code}: {resp.reason}",
            status_code=resp.status_code,
        )

    content_length = len(resp.content)
    if content_length > settings.MAX_CONTENT_LENGTH:
        raise FetchError(
            f"Content too large: {content_length} bytes "
            f"(max {settings.MAX_CONTENT_LENGTH})"
        )

    resp.encoding = resp.apparent_encoding or "utf-8"
    return resp.text, fetch_time_ms


def _fetch_with_playwright(url: str) -> tuple[str, int]:
    """Fallback fetch with headless browser for JS-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise FetchError("Playwright is not installed — run: pip install playwright && playwright install chromium")

    start = time.time()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent=HEADERS["User-Agent"],
            )
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                html = page.content()
                fetch_time_ms = int((time.time() - start) * 1000)
                return html, fetch_time_ms
            finally:
                browser.close()
    except FetchError:
        raise
    except Exception as e:
        raise FetchError(f"Playwright browser failed: {e}")


def fetch_page(url: str) -> tuple[str, int]:
    """Fetch a page. Tries requests first, falls back to Playwright for JS sites."""
    url = validate_url(url)

    try:
        html, fetch_time_ms = _fetch_with_requests(url)

        if not _looks_js_rendered(html):
            return html, fetch_time_ms

        # Page looks JS-rendered, try Playwright
        logger.info("Page appears JS-rendered, falling back to Playwright: %s", url)
        try:
            return _fetch_with_playwright(url)
        except Exception:
            logger.warning("Playwright fallback failed for %s, using static HTML", url)
            return html, fetch_time_ms

    except FetchError:
        raise
    except requests.Timeout:
        raise FetchError(f"Request timed out after {settings.REQUEST_TIMEOUT}s")
    except requests.ConnectionError:
        raise FetchError(f"Could not connect to {urlparse(url).netloc}")
    except requests.RequestException as e:
        raise FetchError(f"Request failed: {e}")
