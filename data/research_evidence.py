"""
Helpers for evidence-backed web research ingestion.
"""

import csv
import html
import os
import re
import urllib.request
from datetime import datetime

BAD_TITLE_PATTERNS = [
    r"\blist of\b",
    r"\btop\s+\d+\b",
    r"\bbest\b",
    r"\bpage\s+\d+\b",
    r"\bsearch results?\b",
    r"\bdirectory\b",
    r"\bdatabase\b",
    r"\bregistry\b",
    r"\bngos?\s+in\b",
]

BAD_TITLE_RE = re.compile("|".join(BAD_TITLE_PATTERNS), re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
DOMAIN_RE = re.compile(r"\b(?:www\.)?[a-z0-9.-]+\.[a-z]{2,}(?:/[^\s\"'<>]*)?\b", re.IGNORECASE)


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def normalize_result_url(url):
    url = normalize_whitespace(url)
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if DOMAIN_RE.fullmatch(url):
        return "https://" + url.lstrip("/")
    return ""


def title_looks_like_non_org(title):
    title = normalize_whitespace(title).lower()
    if not title:
        return True
    if any(token in title for token in ["wikipedia", "facebook.com", "twitter.com", "youtube", "linkedin", ".pdf"]):
        return True
    return bool(BAD_TITLE_RE.search(title))


def fetch_page_text(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "html" not in content_type and "xml" not in content_type and content_type:
            return ""
        raw = resp.read().decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style.*?>.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<[^>]+>", " ", raw)
    return normalize_whitespace(html.unescape(raw))


def extract_evidence_quote(page_text, org_name):
    page_text = normalize_whitespace(page_text)
    org_name = normalize_whitespace(org_name)
    if not page_text or not org_name:
        return ""
    lowered = page_text.lower()
    needle = org_name.lower()
    if needle not in lowered:
        return ""

    segments = re.split(r"(?<=[\.\!\?])\s+|\s{2,}", page_text)
    for segment in segments:
        candidate = normalize_whitespace(segment)
        if len(candidate) < 30:
            continue
        if needle in candidate.lower():
            return candidate[:280]
    return ""


def append_skip_audit(audit_path, reason, name, url, query, title=""):
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    needs_header = not os.path.exists(audit_path)
    with open(audit_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(["logged_at", "reason", "name", "title", "url", "query"])
        writer.writerow([
            datetime.utcnow().isoformat() + "Z",
            reason,
            name or "",
            title or "",
            url or "",
            query or "",
        ])


def validate_org_result(name, title, url, snippet, query, audit_path):
    clean_name = normalize_whitespace(name)
    clean_title = normalize_whitespace(title or name)
    if title_looks_like_non_org(clean_title):
        append_skip_audit(audit_path, "non_org_title", clean_name, url, query, clean_title)
        return None

    normalized_url = normalize_result_url(url)
    if not normalized_url:
        append_skip_audit(audit_path, "missing_url", clean_name, url, query, clean_title)
        return None

    try:
        page_text = fetch_page_text(normalized_url)
    except Exception:
        append_skip_audit(audit_path, "fetch_failed", clean_name, normalized_url, query, clean_title)
        return None

    quote = extract_evidence_quote(page_text, clean_name)
    if len(quote) < 30:
        append_skip_audit(audit_path, "missing_quote", clean_name, normalized_url, query, clean_title)
        return None

    return {
        "website": normalized_url,
        "evidence_url": normalized_url,
        "evidence_quote": quote,
        "evidence_fetched_at": datetime.utcnow().isoformat() + "Z",
        "description": normalize_whitespace(snippet)[:200],
    }


def first_url_from_text(text):
    match = URL_RE.search(text or "")
    if match:
        return normalize_result_url(match.group(0))
    domain_match = DOMAIN_RE.search(text or "")
    if domain_match:
        return normalize_result_url(domain_match.group(0))
    return ""
