# ─────────────────────────────────────────────
# email_utils.py — Email finding & validation
# ─────────────────────────────────────────────

import re
import html
from urllib.parse import unquote

from bs4 import BeautifulSoup

from config import INVALID_LOCAL_PART_WORDS, INVALID_DOMAINS

# ── Regex patterns ─────────────────────────────
_EMAIL_RAW = re.compile(
    r'[a-zA-Z0-9._%+-]+\s*(?:@|\[\s*at\s*\]|\(\s*at\s*\)|\s+at\s+)\s*'
    r'[a-zA-Z0-9.-]+\s*(?:\.|\[\s*dot\s*\]|\(\s*dot\s*\)|\s+dot\s+)\s*[a-zA-Z]{2,}',
    re.IGNORECASE
)
_EMAIL_STRICT = re.compile(
    r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b',
    re.IGNORECASE
)


def decode_cfemail(cf):
    """Decode Cloudflare obfuscated email addresses."""
    try:
        cf = re.sub(r'[^0-9a-fA-F]', '', str(cf).strip().lstrip('#'))
        b  = bytes.fromhex(cf)
        return ''.join(chr(x ^ b[0]) for x in b[1:]) if b else ''
    except Exception:
        return ''


def clean_email(raw):
    """Clean and normalise a raw email string."""
    text = html.unescape(unquote(unquote(str(raw).strip())))
    tl   = text.lower()
    if re.search(r'(\[at\]|\(at\)|\{at\})', tl) and \
       re.search(r'(\[dot\]|\(dot\)|\{dot\})', tl):
        return text
    m = re.search(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}', tl)
    return m.group(0) if m else ''


def is_invalid_email(email, invalid_local_words=None):
    """Return True if email should be filtered out."""
    if not email or '@' not in email:
        return True
    if invalid_local_words is None:
        invalid_local_words = INVALID_LOCAL_PART_WORDS
    local, dom = email.split('@', 1)
    lc = re.sub(r'[^a-z0-9]', '', local.lower())
    if any(b in lc for b in invalid_local_words):
        return True
    if any(dom.lower().endswith(d) for d in INVALID_DOMAINS):
        return True
    return False


def get_domain_filter(site_url, email):
    """Check if email domain matches the site domain (Exact / Partial / Not Match)."""
    def base(v):
        v = str(v).lower().replace('http://', '').replace('https://', '') \
                  .split('/')[0].lstrip('www.')
        p = v.split('.')
        return '.'.join(p[-2:]) if len(p) >= 2 else v

    if not site_url or not email or '@' not in email:
        return 'Not Match'
    sb = base(site_url)
    eb = base(email.split('@')[-1])
    if sb == eb:
        return 'Exact'
    if sb.endswith(eb) or eb.endswith(sb):
        return 'Partial'
    if sb.split('.')[0] in eb or eb.split('.')[0] in sb:
        return 'Partial'
    return 'Not Match'


def extract_emails_from_page(html_text):
    """
    Extract all email addresses from a page's HTML.
    Handles: mailto links, Cloudflare protected emails,
             data attributes, obfuscated formats, and plain text.
    """
    emails = set()
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
    except Exception:
        return emails

    # mailto: links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if isinstance(href, str):
            if href.lower().startswith('mailto:'):
                m = href.split(':', 1)[1].split('?')[0].strip()
                if m:
                    emails.add(m.lower())
            if '/cdn-cgi/l/email-protection' in href and '#' in href:
                m = decode_cfemail(href.split('#', 1)[1])
                if m:
                    emails.add(m.lower())

    # Cloudflare protected spans
    for span in soup.find_all('span', class_='__cf_email__'):
        cf = span.get('data-cfemail')
        if cf:
            m = decode_cfemail(cf)
            if m:
                emails.add(m.lower())

    # data-cfemail attributes in raw HTML
    for m in re.findall(r'data-cfemail=["\']([0-9a-fA-F]+)["\']', html_text):
        d = decode_cfemail(m)
        if d:
            emails.add(d.lower())

    # data attributes on any tag
    for tag in soup.find_all(True):
        for attr in ('data-email', 'data-contact', 'aria-label', 'title', 'alt'):
            val = tag.get(attr)
            if val:
                for e in _EMAIL_STRICT.findall(str(val)):
                    emails.add(e.lower())

    # Plain text scan
    page_text = soup.get_text(separator=' ', strip=True)
    for m in _EMAIL_RAW.finditer(page_text):
        emails.add(m.group(0).strip())
    for e in _EMAIL_STRICT.findall(page_text):
        emails.add(e.lower())

    return emails
