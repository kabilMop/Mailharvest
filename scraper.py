# ─────────────────────────────────────────────
# scraper.py — Core site crawling & extraction
# ─────────────────────────────────────────────

import os
import time
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

from config import (
    REQUEST_TIMEOUT, PER_DOMAIN_DELAY, MAX_DEPTH1_PAGES,
    PRIORITY_KEYWORDS, SKIP_PATH_KEYWORDS, BLACKLISTED_EXT, AVOID_DOMAINS
)
from network import robust_fetch
from email_utils import extract_emails_from_page, clean_email, is_invalid_email, get_domain_filter


# ── URL helpers ────────────────────────────────

def normalize_url(u):
    u = str(u).strip()
    if not urlparse(u).scheme:
        u = 'http://' + u
    return u


def domain_of(url):
    try:
        return urlparse(url).netloc.lower().split(':')[0]
    except Exception:
        return ''


def registered_domain(url):
    try:
        netloc = domain_of(url).lstrip('www.')
        parts  = netloc.split('.')
        return '.'.join(parts[-2:]) if len(parts) >= 2 else netloc
    except Exception:
        return ''


def same_domain(a, b):
    d1, d2 = registered_domain(a), registered_domain(b)
    return bool(d1 and d2 and d1 == d2)


def is_avoid(host):
    hr = registered_domain('http://' + host)
    return any(hr == registered_domain('http://' + b) for b in AVOID_DOMAINS)


# ── Core extraction ────────────────────────────

def extract_site(site_url, session, log_fn, yield_fn, invalid_local_words=None):
    """
    Crawl a website and extract all email addresses found.
    Returns a list of result dicts with url, email, status, location, etc.
    """
    results  = []
    site_url = normalize_url(site_url)
    last_hit = {}

    def rate_limit(url):
        """Wait between requests to the same domain."""
        dom  = domain_of(url)
        last = last_hit.get(dom, 0)
        wait = PER_DOMAIN_DELAY - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        last_hit[dom] = time.time()

    def fetch(url):
        rate_limit(url)
        return robust_fetch(url, session, REQUEST_TIMEOUT)

    # ── Step 1: Fetch homepage ─────────────────
    log_fn(f"  Fetching homepage: {site_url}")
    yield_fn()

    html_text, final_url = fetch(site_url)
    if not html_text:
        log_fn(f"  [BLOCKED] Could not reach: {site_url}")
        yield_fn()
        return [{'url': site_url, 'email': '', 'status': 'Blocked',
                 'location': site_url, 'navigation': 'Home', 'domain_filter': '-'}]

    log_fn(f"  Homepage loaded successfully")
    yield_fn()

    # ── Step 2: Collect internal links ────────
    links, seen = [], set()
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if not href or href.startswith(('javascript:', 'mailto:', '#')):
                continue
            full   = urljoin(final_url, href)
            parsed = urlparse(full)
            full   = urlunparse(parsed._replace(fragment=''))
            if full in seen:
                continue
            ext = os.path.splitext(parsed.path.lower())[1]
            if ext in BLACKLISTED_EXT:
                continue
            if is_avoid(parsed.netloc.lower()):
                continue
            if not same_domain(site_url, full):
                continue
            anchor = a.get_text(strip=True) or parsed.path.split('/')[-1] or 'Link'
            seen.add(full)
            links.append((full, anchor))
    except Exception as e:
        log_fn(f"  [WARN] Link extraction error: {e}")

    # ── Step 3: Score & prioritise pages ──────
    def score(url):
        path = urlparse(url).path.lower()
        s    = sum(10 for kw in PRIORITY_KEYWORDS if kw in path)
        s   -= sum(100 for sk in SKIP_PATH_KEYWORDS if sk in path)
        return s

    filtered = [(l, a) for l, a in links
                if not any(sk in urlparse(l).path.lower() for sk in SKIP_PATH_KEYWORDS)]
    scored   = sorted(filtered, key=lambda x: score(x[0]), reverse=True)
    pages    = scored[:MAX_DEPTH1_PAGES - 1]

    seen_p, unique = {final_url}, [(final_url, 'Home')]
    for url, anchor in pages:
        if url not in seen_p:
            seen_p.add(url)
            unique.append((url, anchor))

    log_fn(f"  Scanning {len(unique)} page(s)")
    yield_fn()

    # ── Step 4: Scan each page for emails ─────
    found_any = False

    for page_url, anchor in unique:
        nav = 'Home' if page_url == final_url else f"Home > {anchor}"
        log_fn(f"  Scanning: {page_url}")
        yield_fn()

        page_html = html_text if page_url == final_url else None
        if page_html is None:
            page_html, _ = fetch(page_url)
            if not page_html:
                log_fn(f"  [SKIP] Fetch failed: {page_url}")
                yield_fn()
                continue

        for raw_email in extract_emails_from_page(page_html):
            cleaned = clean_email(raw_email)
            if not cleaned:
                continue
            status = 'Invalid' if is_invalid_email(cleaned, invalid_local_words) else 'Valid'
            df     = get_domain_filter(site_url, cleaned)
            log_fn(f"  [{'VALID' if status == 'Valid' else 'INVALID'}] {cleaned} ({df})")
            yield_fn()
            results.append({
                'url':           site_url,
                'email':         cleaned,
                'status':        status,
                'location':      page_url,
                'navigation':    nav,
                'domain_filter': df,
            })
            found_any = True

        time.sleep(0.2)

    if not found_any:
        log_fn(f"  [NOT FOUND] No emails: {site_url}")
        yield_fn()
        results.append({'url': site_url, 'email': '', 'status': 'Not Found',
                        'location': site_url, 'navigation': 'Home', 'domain_filter': '-'})
    return results
