import logging
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..config import settings
from ..database import SessionLocal
from ..models import SiteCrawl, SiteCrawlPage
from .analysis import get_cached_result, run_analysis
from .scorer import score_to_grade
from .scraper import FetchError, fetch_page

logger = logging.getLogger(__name__)

# File extensions to skip when discovering links
_SKIP_EXTENSIONS = re.compile(
    r"\.(?:pdf|jpg|jpeg|png|gif|svg|webp|ico|css|js|zip|tar|gz|mp4|mp3|woff2?|ttf|eot)$",
    re.IGNORECASE,
)

# Common non-content paths to skip
_SKIP_PATHS = re.compile(
    r"(?:^/(?:login|logout|signin|signup|register|admin|wp-admin|wp-login|cart|checkout|account|api/))",
    re.IGNORECASE,
)


def _normalize_url(url: str) -> str:
    """Normalize a URL for deduplication: lowercase scheme+host, strip fragment and trailing slash."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    # Drop fragment, keep query
    return f"{scheme}://{netloc}{path}"


def extract_internal_links(html: str, base_url: str) -> list[str]:
    """Extract and deduplicate same-domain internal links from HTML."""
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc.lower()
    seen: set[str] = set()
    links: list[str] = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()

        # Skip non-HTTP links
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        # Resolve relative URLs
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only same domain
        if parsed.netloc.lower() != base_domain:
            continue

        # Only http(s)
        if parsed.scheme not in ("http", "https"):
            continue

        # Skip file extensions
        if _SKIP_EXTENSIONS.search(parsed.path):
            continue

        # Skip non-content paths
        if _SKIP_PATHS.search(parsed.path):
            continue

        normalized = _normalize_url(full_url)
        if normalized not in seen:
            seen.add(normalized)
            links.append(full_url.split("#")[0])  # strip fragment from actual URL

    return sorted(links)


def run_site_crawl(crawl_id: int) -> None:
    """Background task: crawl a site and analyze each page."""
    db = SessionLocal()
    try:
        crawl = db.query(SiteCrawl).filter(SiteCrawl.id == crawl_id).first()
        if not crawl:
            logger.error("Crawl job %d not found", crawl_id)
            return

        crawl.status = "crawling"
        db.commit()

        seed_url = crawl.url
        max_pages = settings.MAX_CRAWL_PAGES

        # ── Step 1: Fetch and analyze the seed page ──────────────────────
        try:
            html, fetch_time_ms = fetch_page(seed_url)
        except FetchError as e:
            crawl.status = "failed"
            crawl.error = f"Could not fetch seed URL: {e.message}"
            crawl.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        # Check cache for the seed
        cached = get_cached_result(db, seed_url)
        if cached:
            seed_result = cached
        else:
            seed_result = run_analysis(seed_url, html, fetch_time_ms, db)

        seed_page = SiteCrawlPage(
            crawl_id=crawl_id,
            url=seed_url,
            depth=0,
            status="completed",
            result_id=seed_result.id,
        )
        db.add(seed_page)
        crawl.pages_found = 1
        crawl.pages_analyzed = 1
        db.commit()

        # ── Step 2: Extract internal links ───────────────────────────────
        discovered_links = extract_internal_links(html, seed_url)

        # Exclude the seed URL itself
        seed_normalized = _normalize_url(seed_url)
        discovered_links = [
            link for link in discovered_links
            if _normalize_url(link) != seed_normalized
        ]

        # Cap at max_pages - 1 (seed already counted)
        discovered_links = discovered_links[: max_pages - 1]

        # Create page rows
        for link in discovered_links:
            page = SiteCrawlPage(
                crawl_id=crawl_id,
                url=link,
                depth=1,
                status="pending",
            )
            db.add(page)

        crawl.pages_found = 1 + len(discovered_links)
        db.commit()

        # ── Step 3: Analyze each discovered page ─────────────────────────
        pending_pages = (
            db.query(SiteCrawlPage)
            .filter(
                SiteCrawlPage.crawl_id == crawl_id,
                SiteCrawlPage.status == "pending",
            )
            .all()
        )

        for page in pending_pages:
            page.status = "analyzing"
            db.commit()

            try:
                # Check cache first
                cached = get_cached_result(db, page.url)
                if cached:
                    result = cached
                else:
                    page_html, page_fetch_time = fetch_page(page.url)
                    result = run_analysis(page.url, page_html, page_fetch_time, db)

                page.result_id = result.id
                page.status = "completed"
            except FetchError as e:
                page.status = "failed"
                page.error = e.message
                logger.warning("Failed to fetch %s: %s", page.url, e.message)
            except Exception:
                page.status = "failed"
                page.error = "Analysis failed"
                logger.exception("Unexpected error analyzing %s", page.url)

            crawl.pages_analyzed += 1
            db.commit()

            # Politeness delay
            time.sleep(settings.CRAWL_DELAY_SECONDS)

        # ── Step 4: Compute aggregate score ──────────────────────────────
        completed_pages = (
            db.query(SiteCrawlPage)
            .filter(
                SiteCrawlPage.crawl_id == crawl_id,
                SiteCrawlPage.status == "completed",
            )
            .all()
        )

        if completed_pages:
            total = sum(p.result.total_score for p in completed_pages)
            avg_score = round(total / len(completed_pages), 1)
            crawl.total_score = avg_score
            crawl.grade = score_to_grade(avg_score)
        else:
            crawl.total_score = 0.0
            crawl.grade = "F"

        crawl.status = "completed"
        crawl.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            "Crawl %d completed: %d pages, score=%.1f, grade=%s",
            crawl_id,
            len(completed_pages),
            crawl.total_score,
            crawl.grade,
        )

    except Exception:
        logger.exception("Crawl %d failed with unexpected error", crawl_id)
        try:
            crawl = db.query(SiteCrawl).filter(SiteCrawl.id == crawl_id).first()
            if crawl:
                crawl.status = "failed"
                crawl.error = "Unexpected server error during crawl"
                crawl.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception:
            logger.exception("Failed to update crawl %d status to failed", crawl_id)
    finally:
        db.close()
