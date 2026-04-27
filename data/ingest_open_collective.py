"""
ingest_open_collective.py

Pulls COLLECTIVE accounts from the Open Collective public GraphQL API
(https://api.opencollective.com/graphql/v2). No auth required, but we play
nice: 1 req/sec, paginate by offset, default cap of 500.

Each accepted row is scored through phase2_filter.score_org. Rows under
score 2 are skipped at ingest time so we do not pollute the DB.

Usage:
  python data/ingest_open_collective.py --limit 500
  python data/ingest_open_collective.py --limit 100 --dry-run
"""
import os
import sys
import json
import time
import argparse
import sqlite3
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print('ERROR: this script requires the "requests" package (pip install requests)')
    sys.exit(2)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DB_PATH = os.path.abspath(os.path.join(THIS_DIR, 'commonweave_directory.db'))

# Make sibling helpers importable.
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from phase2_filter import score_org  # noqa: E402

API_URL = 'https://api.opencollective.com/graphql/v2'
SOURCE = 'open_collective'
SLEEP_BETWEEN = 1.0  # seconds; Open Collective public API rate limit
MIN_SCORE = 2

QUERY = """
query Accounts($limit: Int!, $offset: Int!) {
  accounts(type: COLLECTIVE, limit: $limit, offset: $offset) {
    totalCount
    nodes {
      id
      legacyId
      slug
      name
      description
      longDescription
      website
      tags
      isActive
      isArchived
      location {
        country
        city
      }
      host {
        slug
        name
      }
    }
  }
}
"""


def ensure_column(db, table, col, typedef):
    try:
        db.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
        db.commit()
    except Exception:
        pass


def gql(session, variables, attempt=1):
    payload = {'query': QUERY, 'variables': variables}
    try:
        resp = session.post(API_URL, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        if attempt < 3:
            time.sleep(2 * attempt)
            return gql(session, variables, attempt + 1)
        print(f'  [WARN] network error after retries: {exc}')
        return None
    if resp.status_code == 429:
        # Rate-limited; back off and retry once.
        if attempt < 3:
            time.sleep(5 * attempt)
            return gql(session, variables, attempt + 1)
        print(f'  [WARN] 429 after retries')
        return None
    if resp.status_code != 200:
        print(f'  [WARN] HTTP {resp.status_code}: {resp.text[:200]}')
        return None
    try:
        body = resp.json()
    except json.JSONDecodeError:
        print(f'  [WARN] non-JSON body: {resp.text[:200]}')
        return None
    if body.get('errors'):
        print(f'  [WARN] GraphQL errors: {body["errors"]}')
    return body.get('data')


def map_node(node):
    """Translate a GraphQL account node to our DB row dict, or None to skip."""
    if not node:
        return None
    name = (node.get('name') or '').strip()
    slug = (node.get('slug') or '').strip()
    if not name or not slug:
        return None
    if node.get('isArchived'):
        return None
    if node.get('isActive') is False:
        return None
    description = (node.get('description') or '').strip()
    long_desc = (node.get('longDescription') or '').strip()
    if long_desc and len(long_desc) > len(description):
        # Truncate long_description so we do not blow up the DB column.
        description = long_desc[:2000]
    website = (node.get('website') or '').strip() or f'https://opencollective.com/{slug}'
    tags = node.get('tags') or []
    if isinstance(tags, list):
        tags_str = ', '.join(str(t) for t in tags if t)
    else:
        tags_str = str(tags)
    location = node.get('location') or {}
    country = (location.get('country') or '').strip().upper() or ''
    city = (location.get('city') or '').strip() or ''
    return {
        'source_id': slug,
        'name': name,
        'description': description,
        'website': website,
        'tags': tags_str,
        'country_code': country,
        'city': city,
    }


def upsert_rows(db, rows, dry_run=False):
    c = db.cursor()
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    updated = 0
    skipped_low_score = 0
    for r in rows:
        score = score_org(r['name'], r['description'])
        if score < MIN_SCORE:
            skipped_low_score += 1
            continue
        if dry_run:
            inserted += 1
            continue
        c.execute(
            'SELECT id, alignment_score FROM organizations '
            'WHERE source=? AND source_id=?',
            (SOURCE, r['source_id']),
        )
        existing = c.fetchone()
        if existing:
            existing_id, existing_score = existing
            c.execute(
                """UPDATE organizations
                   SET name=?,
                       description=COALESCE(NULLIF(description,''), ?),
                       website=COALESCE(NULLIF(website,''), ?),
                       tags=COALESCE(NULLIF(tags,''), ?),
                       country_code=COALESCE(NULLIF(country_code,''), ?),
                       city=COALESCE(NULLIF(city,''), ?),
                       alignment_score=MAX(COALESCE(alignment_score,0), ?),
                       legibility='formal'
                   WHERE id=?""",
                (
                    r['name'], r['description'], r['website'], r['tags'],
                    r['country_code'], r['city'], score, existing_id,
                ),
            )
            updated += 1
        else:
            c.execute(
                """INSERT INTO organizations
                   (name, country_code, city, description, website, tags,
                    source, source_id, alignment_score,
                    status, date_added, legibility)
                   VALUES (?,?,?,?,?,?,?,?,?,'active',?,?)""",
                (
                    r['name'], r['country_code'], r['city'],
                    r['description'], r['website'], r['tags'],
                    SOURCE, r['source_id'], score, now, 'formal',
                ),
            )
            if c.rowcount:
                inserted += 1
    if not dry_run:
        db.commit()
    return inserted, updated, skipped_low_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=500,
                    help='Max collectives to fetch (default 500)')
    ap.add_argument('--page-size', type=int, default=100,
                    help='Per-request page size (default 100)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'commonweave/ingest_open_collective (research)',
    })

    db = sqlite3.connect(DB_PATH)
    ensure_column(db, 'organizations', 'tags', 'TEXT')
    ensure_column(db, 'organizations', 'legibility', "TEXT DEFAULT 'unknown'")

    fetched = 0
    inserted_total = 0
    updated_total = 0
    skipped_total = 0
    page = 0
    page_size = max(10, min(args.page_size, 100))

    print(f'== ingest_open_collective ==')
    print(f'  target limit : {args.limit}')
    print(f'  page size    : {page_size}')
    print(f'  dry-run      : {args.dry_run}')

    while fetched < args.limit:
        remaining = args.limit - fetched
        this_page = min(page_size, remaining)
        offset = page * page_size
        print(f'  page {page + 1}: offset={offset} size={this_page}')
        data = gql(session, {'limit': this_page, 'offset': offset})
        if not data or not data.get('accounts'):
            print('  no data, stopping')
            break
        nodes = data['accounts'].get('nodes') or []
        if not nodes:
            print('  empty page, stopping')
            break
        rows = [r for r in (map_node(n) for n in nodes) if r]
        ins, upd, skip = upsert_rows(db, rows, dry_run=args.dry_run)
        inserted_total += ins
        updated_total += upd
        skipped_total += skip
        fetched += len(nodes)
        page += 1
        if len(nodes) < this_page:
            print('  short page, stopping')
            break
        time.sleep(SLEEP_BETWEEN)

    db.close()

    mode = '[DRY RUN] Would insert' if args.dry_run else 'Inserted'
    print('=== open_collective ingest complete ===')
    print(f'  fetched           : {fetched}')
    print(f'  {mode:24s}: {inserted_total}')
    print(f'  Updated           : {updated_total}')
    print(f'  Skipped (score<2) : {skipped_total}')


if __name__ == '__main__':
    main()
