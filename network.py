# ─────────────────────────────────────────────
# network.py — HTTP fetching & session handling
# ─────────────────────────────────────────────

import random

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    import cloudscraper
except Exception:
    cloudscraper = None

from config import USER_AGENTS, CLOUDFLARE_STRINGS


def random_headers():
    """Return randomised browser-like headers to avoid bot detection."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }


def create_session():
    """Create a requests Session with automatic retry logic."""
    s = requests.Session()
    retry = Retry(
        total=3, read=3, connect=3, backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(['GET', 'HEAD', 'OPTIONS'])
    )
    s.mount('http://',  HTTPAdapter(max_retries=retry))
    s.mount('https://', HTTPAdapter(max_retries=retry))
    return s


def is_cf_block(text):
    """Detect if the page is a Cloudflare challenge/block page."""
    if not text:
        return False
    tl = text.lower()
    if any(s in tl for s in CLOUDFLARE_STRINGS):
        return True
    if len(text.strip()) < 200 and ("cloudflare" in tl or "checking" in tl):
        return True
    return False


def fetch_requests(url, session, timeout):
    """Fetch a URL using the requests library."""
    try:
        session.headers.update(random_headers())
        r = session.get(url, timeout=timeout, allow_redirects=True)
        if r.status_code >= 400:
            return None, None
        ct = r.headers.get('Content-Type', '')
        if 'html' not in ct and 'text' not in ct:
            return None, None
        if is_cf_block(r.text):
            return None, r.url
        return r.text, r.url
    except Exception:
        return None, None


def fetch_cloudscraper_fn(url, timeout):
    """Fallback fetch using cloudscraper (bypasses some Cloudflare blocks)."""
    if not cloudscraper:
        return None, None
    try:
        scr = cloudscraper.create_scraper()
        scr.headers.update(random_headers())
        r = scr.get(url, timeout=timeout)
        if r.status_code >= 400:
            return None, None
        ct = r.headers.get('Content-Type', '')
        if 'html' not in ct and 'text' not in ct:
            return None, None
        if is_cf_block(r.text):
            return None, r.url
        return r.text, r.url
    except Exception:
        return None, None


def robust_fetch(url, session, timeout):
    """
    Try requests first, fall back to cloudscraper if blocked.
    Returns (html_text, final_url) or (None, None) if both fail.
    """
    h, f = fetch_requests(url, session, timeout)
    if h:
        return h, f or url
    h, f = fetch_cloudscraper_fn(url, timeout)
    if h:
        return h, f or url
    return None, None
