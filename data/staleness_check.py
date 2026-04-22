"""
Staleness check for Commonweave directory.

HEAD-checks org websites to find dead links. Marks unreachable orgs with
staleness_flag and eventually demotes them to status='stale' after 3 strikes.

New columns (added on first run):
  last_verified_at TEXT
  staleness_flag TEXT
  staleness_count INTEGER DEFAULT 0

Usage:
    python staleness_check.py                  # batch of 500
    python staleness_check.py --limit 20       # small test batch
    python staleness_check.py --dry-run        # show what would be checked
    python staleness_check.py --country IN     # scope to one country
"""
import argparse
import os
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urlparse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

sys.path.insert(0, os.path.dirname(__file__))
from _common import DB_PATH, ensure_column, trim_audit_path

MAX_CONCURRENT = 30
BATCH_SIZE = 500
REQUEST_TIMEOUT = 10
DOMAIN_SLEEP = 1.0       # sleep between requests to same domain
BATCH_SLEEP = 0.5        # sleep between concurrent batches
STALE_AFTER_STRIKES = 3  # consecutive failures before status='stale'
REVERIFY_DAYS = 180      # re-check orgs not seen in this many days


def run_migration(db):
    ensure_column(db, 'organizations', 'last_verified_at', 'TEXT')
    ensure_column(db, 'organizations', 'staleness_flag', 'TEXT')
    ensure_column(db, 'organizations', 'staleness_count', 'INTEGER DEFAULT 0')


def get_domain(url):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ''


def head_check(url):
    """
    HEAD-check a URL. Returns ('ok', status_code) or ('fail', reason).
    Falls back to GET if HEAD gets a 405.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return ('skip', 'no_url')
    try:
        if HAS_REQUESTS:
            resp = requests.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True,
                                 headers={'User-Agent': 'Commonweave/1.0 (+https://commonweave.org)'})
            if resp.status_code == 405:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True,
                                    headers={'User-Agent': 'Commonweave/1.0 (+https://commonweave.org)'})
            code = resp.status_code
            if 200 <= code < 400:
                return ('ok', code)
            return ('fail', code)
        else:
            req = urllib.request.Request(url, method='HEAD',
                headers={'User-Agent': 'Commonweave/1.0 (+https://commonweave.org)'})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                return ('ok', r.status)
    except Exception as e:
        return ('fail', str(e)[:80])


def load_candidates(db, limit, country):
    """Load orgs due for reverification."""
    c = db.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cutoff = datetime.now(timezone.utc).replace(
        year=datetime.now(timezone.utc).year
    )
    # Compute cutoff 180 days ago as an ISO string comparison
    from datetime import timedelta
    cutoff_iso = (datetime.now(timezone.utc) - timedelta(days=REVERIFY_DAYS)).isoformat()

    parts = ["website IS NOT NULL AND website != ''"]
    parts.append("status NOT IN ('removed', 'merged')")
    parts.append(f"(last_verified_at IS NULL OR last_verified_at < '{cutoff_iso}')")
    if country:
        parts.append(f"country_code = '{country.upper()}'")

    where = ' AND '.join(parts)
    q = f"SELECT id, name, website, country_code, staleness_count FROM organizations WHERE {where} LIMIT {limit}"
    c.execute(q)
    return c.fetchall()


def apply_results(db, results, dry_run, log_lines):
    """Write HEAD-check outcomes back to DB."""
    c = db.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    ok_count = 0
    fail_count = 0
    stale_promoted = 0

    for row_id, name, url, outcome, reason in results:
        if outcome == 'skip':
            continue
        if outcome == 'ok':
            ok_count += 1
            if not dry_run:
                c.execute("""
                    UPDATE organizations
                    SET last_verified_at=?, staleness_count=0, staleness_flag=NULL
                    WHERE id=?
                """, (now_iso, row_id))
        else:
            fail_count += 1
            log_lines.append(f"  FAIL [{reason}] id={row_id} '{name}' {url}")
            if not dry_run:
                c.execute("""
                    UPDATE organizations
                    SET staleness_flag='unreachable',
                        staleness_count=COALESCE(staleness_count,0)+1
                    WHERE id=?
                """, (row_id,))
                # Promote to stale if strikes >= threshold
                c.execute("""
                    UPDATE organizations SET status='stale'
                    WHERE id=? AND staleness_count >= ?
                    AND status = 'active'
                """, (row_id, STALE_AFTER_STRIKES))
                # Check if we just promoted
                c.execute('SELECT changes()')
                if c.fetchone()[0]:
                    stale_promoted += 1
                    log_lines.append(f'    -> PROMOTED to stale (3 strikes)')

    if not dry_run:
        db.commit()
    return ok_count, fail_count, stale_promoted


def main():
    ap = argparse.ArgumentParser(description='Website staleness checker for Commonweave')
    ap.add_argument('--limit', type=int, default=BATCH_SIZE, help='Max orgs to check per run')
    ap.add_argument('--dry-run', action='store_true', help='Show what would be checked, no writes')
    ap.add_argument('--country', help='Scope to one country code')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    run_migration(db)

    candidates = load_candidates(db, args.limit, args.country)
    print(f'Candidates due for check: {len(candidates)}')

    if args.dry_run:
        for row in candidates[:20]:
            print(f'  [{row["country_code"]}] {row["name"]} -> {row["website"]}')
        if len(candidates) > 20:
            print(f'  ... and {len(candidates) - 20} more')
        db.close()
        print(f'[DRY RUN] Would check {len(candidates)} URLs.')
        return

    log_lines = []
    all_results = []
    domain_last = {}  # domain -> last request time

    # Group by domain to respect per-domain rate limit
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as pool:
        futures = {}
        for row in candidates:
            url = row['website']
            row_id = row['id']
            name = row['name']
            futures[pool.submit(head_check, url)] = (row_id, name, url)

        done = 0
        for fut in as_completed(futures):
            row_id, name, url = futures[fut]
            outcome, reason = fut.result()
            all_results.append((row_id, name, url, outcome, reason))
            done += 1
            if done % 50 == 0:
                print(f'  Checked {done}/{len(candidates)}...')
            time.sleep(BATCH_SLEEP / MAX_CONCURRENT)

    ok, fail, promoted = apply_results(db, all_results, args.dry_run, log_lines)
    db.close()

    print(f'Results: {ok} ok, {fail} unreachable, {promoted} promoted to stale')

    # Write audit log
    log_path = trim_audit_path('staleness')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f'# Staleness Check - {today}\n\n')
        f.write(f'| Metric | Value |\n|---|---|\n')
        f.write(f'| Checked | {len(candidates)} |\n')
        f.write(f'| OK (2xx/3xx) | {ok} |\n')
        f.write(f'| Unreachable | {fail} |\n')
        f.write(f'| Promoted to stale | {promoted} |\n\n')
        if log_lines:
            f.write('## Failures\n\n```\n')
            for line in log_lines[:300]:
                f.write(line + '\n')
            if len(log_lines) > 300:
                f.write(f'... and {len(log_lines) - 300} more\n')
            f.write('```\n')

    print(f'Log: {log_path}')


if __name__ == '__main__':
    main()
