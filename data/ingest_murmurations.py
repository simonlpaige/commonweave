"""
Murmurations index ingest (organizations schema only).

Source: https://index.murmurations.network/v2/nodes
Docs:   https://docs.murmurations.network/

Murmurations is an opt-in index: an organization (or a directory acting for
its members) publishes a profile and registers it. That makes it a better
fit than a state registry for three reasons that matter here:

  - every node carries coordinates, so rows can go on the map without a
    geocoding pass;
  - most carry a website (`primary_url`);
  - each profile names where its data came from (`metadata.sources`), so
    provenance survives the ingest.

Checked 2026-11-26: 7,242 nodes under `organizations_schema-v1.0.0`. A large
share are Co-operatives UK open-data records republished into the index.

Deliberately NOT ingested:
  - `karte_von_morgen-v1.0.0` (32,732 nodes): mixes organizations with
    places such as refill stations and rest areas. Needs its own filter.
  - `offers_wants_schema` (78,273): listings, not organizations.
  - `people_schema`: individuals.

Licence: the index does not state one licence for all nodes. Each profile
names its own upstream source. Rows are recorded with the profile URL as
evidence; do not describe this source as CC0.

Mapping:
  - source         = 'murmurations'
  - source_id      = last path segment of profile_url (stable profile id)
  - legibility     = 'unknown' (a profile does not tell us the legal form)
  - geo_source     = 'murmurations' (publisher-supplied; precision unknown)
  - framework_area = from tags, '' when no tag matches (never guessed)
  - alignment_score= 2, the floor used by other thematic ingesters

Usage:
    python ingest_murmurations.py --dry-run          # fetch + count, no DB needed
    python ingest_murmurations.py --dry-run --out rows.json
    python ingest_murmurations.py                    # write to COMMONWEAVE_DB
    python ingest_murmurations.py --refresh          # ignore cache
"""
import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from _common import DATA_DIR, ensure_column, get_db

SOURCE = 'murmurations'
SCHEMA = 'organizations_schema-v1.0.0'
INDEX_API = 'https://index.murmurations.network/v2/nodes'
PAGE_SIZE = 500
MAX_RESULTS = 10000  # hard cap enforced by the index
CACHE_DIR = os.path.join(DATA_DIR, 'sources', 'murmurations-cache')
LOG_PATH = os.path.join(DATA_DIR, 'ingest-murmurations-run.log')
USER_AGENT = 'Commonweave/1.0 directory bot (+https://commonweave.earth)'
SLEEP_BETWEEN = 1.0

TAG_TO_FRAMEWORK = [
    (re.compile(r'\b(food|farm|agri|grow|garden|csa|bakery|grocer)', re.I), 'food'),
    (re.compile(r'\b(housing|land trust|cohousing|tenant)', re.I), 'housing_land'),
    (re.compile(r'\b(energy|solar|wind|renewable|digital|software|open source|tech)', re.I), 'energy_digital'),
    (re.compile(r'\b(health|care|wellbeing|medical)', re.I), 'healthcare'),
    (re.compile(r'\b(education|school|learning|training)', re.I), 'education'),
    (re.compile(r'\b(ecolog|environment|climate|conservation|permaculture|regenerat)', re.I), 'ecology'),
    (re.compile(r'\b(arts?|culture|music|theatre|sport|recreation)', re.I), 'recreation_arts'),
    (re.compile(r'\b(co-?op|cooperative|credit union|mutual|worker.owned|solidarity)', re.I), 'cooperatives'),
    (re.compile(r'\b(democra|civic|participat|advocacy|community)', re.I), 'democracy'),
]


def derive_framework(tags):
    text = ' | '.join(tags or [])
    for rx, area in TAG_TO_FRAMEWORK:
        if rx.search(text):
            return area
    return ''


def clean_url(raw):
    """Return an http(s) URL or ''. The index stores '-' and bare domains."""
    s = (raw or '').strip()
    if not s or s == '-' or ' ' in s or '.' not in s:
        return ''
    if not re.match(r'^https?://', s, re.I):
        s = 'https://' + s
    return s


def valid_coords(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
        return None
    return lat, lon


def parse_node(node):
    """Index node -> row dict, or None when the node is unusable."""
    name = (node.get('name') or '').strip()
    profile_url = (node.get('profile_url') or '').strip()
    if not name or not profile_url or node.get('status') != 'posted':
        return None
    if SCHEMA not in (node.get('linked_schemas') or []):
        return None
    coords = valid_coords((node.get('geolocation') or {}).get('lat'),
                          (node.get('geolocation') or {}).get('lon'))
    cc = (node.get('country') or '').strip().upper()
    tags = [t.strip() for t in (node.get('tags') or []) if isinstance(t, str) and t.strip()]
    updated = node.get('last_updated')
    return {
        'name': name[:300],
        'country_code': cc if re.fullmatch(r'[A-Z]{2}', cc) else '',
        'state_province': (node.get('region') or '').strip(),
        'city': (node.get('locality') or '').strip(),
        'lat': coords[0] if coords else None,
        'lon': coords[1] if coords else None,
        'website': clean_url(node.get('primary_url')),
        'framework_area': derive_framework(tags),
        'tags': ', '.join(tags)[:500],
        'source_id': profile_url.rstrip('/').rsplit('/', 1)[-1],
        'evidence_url': profile_url,
        'source_updated_at': (datetime.fromtimestamp(updated, timezone.utc).date().isoformat()
                              if isinstance(updated, (int, float)) else ''),
    }


def fetch_page(page, refresh=False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    url = f'{INDEX_API}?schema={SCHEMA}&page_size={PAGE_SIZE}&page={page}'
    path = os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest()[:16] + f'-p{page}.json')
    if not refresh and os.path.exists(path) and os.path.getsize(path) > 32:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read()
    with open(path, 'wb') as f:
        f.write(body)
    time.sleep(SLEEP_BETWEEN)
    return json.loads(body.decode('utf-8'))


def fetch_all(refresh=False):
    nodes, page, total = [], 1, None
    while True:
        data = fetch_page(page, refresh=refresh)
        items = data.get('data') or []
        meta = data.get('meta') or {}
        total = meta.get('number_of_results', total)
        nodes.extend(items)
        print(f'  page {page}: {len(items)} nodes (index reports {total})')
        if not items or len(nodes) >= min(total or 0, MAX_RESULTS):
            break
        page += 1
    if total and total > MAX_RESULTS:
        print(f'  WARNING: index reports {total} nodes; only the first {MAX_RESULTS} are reachable.')
    return nodes, total


def upsert(db, rows):
    for col, typedef in [('evidence_url', 'TEXT'), ('evidence_fetched_at', 'TEXT'),
                         ('legibility', "TEXT DEFAULT 'unknown'")]:
        ensure_column(db, 'organizations', col, typedef)
    c = db.cursor()
    now = datetime.now(timezone.utc).isoformat()
    inserted = updated = 0
    for r in rows:
        c.execute('SELECT id FROM organizations WHERE source=? AND source_id=?', (SOURCE, r['source_id']))
        existing = c.fetchone()
        if existing:
            # Refresh publisher-supplied fields; never overwrite a reviewed
            # framework_area, description or legibility.
            c.execute(
                """UPDATE organizations
                   SET name=?, website=COALESCE(NULLIF(?, ''), website),
                       lat=COALESCE(?, lat), lon=COALESCE(?, lon),
                       city=COALESCE(NULLIF(?, ''), city),
                       state_province=COALESCE(NULLIF(?, ''), state_province),
                       tags=COALESCE(NULLIF(?, ''), tags),
                       framework_area=COALESCE(NULLIF(framework_area, ''), ?),
                       evidence_url=?, evidence_fetched_at=?
                   WHERE id=?""",
                (r['name'], r['website'], r['lat'], r['lon'], r['city'], r['state_province'],
                 r['tags'], r['framework_area'], r['evidence_url'], now, existing[0]))
            updated += 1
        else:
            c.execute(
                """INSERT INTO organizations
                   (name, country_code, state_province, city, lat, lon, geo_source,
                    website, framework_area, tags, source, source_id, alignment_score,
                    status, date_added, legibility, evidence_url, evidence_fetched_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,2,'active',?,'unknown',?,?)""",
                (r['name'], r['country_code'], r['state_province'], r['city'], r['lat'], r['lon'],
                 SOURCE if r['lat'] is not None else None,
                 r['website'], r['framework_area'], r['tags'], SOURCE, r['source_id'],
                 now, r['evidence_url'], now))
            inserted += 1
    db.commit()
    return inserted, updated


def summarize(nodes, rows, total):
    by_cc = collections.Counter(r['country_code'] or '(none)' for r in rows)
    by_area = collections.Counter(r['framework_area'] or '(unclassified)' for r in rows)
    return [
        f'Index endpoint: {INDEX_API}?schema={SCHEMA}',
        f'Nodes reported by index: {total}',
        f'Nodes fetched: {len(nodes)}',
        f'Usable rows: {len(rows)}',
        f'With coordinates: {sum(1 for r in rows if r["lat"] is not None)}',
        f'With website: {sum(1 for r in rows if r["website"])}',
        f'Countries: {len([k for k in by_cc if k != "(none)"])}',
        'Top countries: ' + ', '.join(f'{k} {v}' for k, v in by_cc.most_common(12)),
        'Framework areas: ' + ', '.join(f'{k} {v}' for k, v in by_area.most_common()),
        'Licence: not stated index-wide; see each profile\'s metadata.sources.',
    ]


def main():
    ap = argparse.ArgumentParser(description='Murmurations organizations ingest')
    ap.add_argument('--dry-run', action='store_true', help='fetch and count; never opens the database')
    ap.add_argument('--refresh', action='store_true', help='ignore cached pages')
    ap.add_argument('--out', help='also write parsed rows to this JSON file')
    args = ap.parse_args()

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Ingesting Murmurations ({SCHEMA})")
    nodes, total = fetch_all(refresh=args.refresh)
    seen, rows = set(), []
    for n in nodes:
        r = parse_node(n)
        if r and r['source_id'] not in seen:
            seen.add(r['source_id'])
            rows.append(r)

    lines = [f"Mode: {'dry-run' if args.dry_run else 'real'}"] + summarize(nodes, rows, total)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False)
        lines.append(f'Rows written: {args.out}')
    if not args.dry_run:
        db = get_db()
        inserted, updated = upsert(db, rows)
        db.close()
        lines += [f'Inserted: {inserted}', f'Updated: {updated}']
    print('\n' + '\n'.join(lines))
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"\n# ingest_murmurations run - {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%SZ}\n\n")
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
