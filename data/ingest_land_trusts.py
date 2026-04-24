"""
Wikidata SPARQL bulk ingest for land trusts and housing cooperatives.

Models on ingest_unions.py. Pulls two classes:

  * Q3278937  community land trust  (~6 direct instances + subclasses)
  * Q562166   housing cooperative   (~550 instances globally)

The brief cited Q5153359 for community land trust and Q1329546 for housing
cooperative. Both were wrong. Q5153359 resolves to "municipality of the
Czech Republic" and Q1329546 resolves to an American journalist named Elinor
Burkett. The correct IDs above were found by searching Wikidata labels and
confirmed by counting instances. The taxonomy file still lists the wrong IDs
alongside this correction so the mistake is recoverable.

Every row inserted is tagged legibility=formal (Wikidata-notable = registered
and documented by definition), category=land_and_housing/<subtype>, with the
Wikidata item URL as evidence_url. source='wikidata_land_trusts'. Re-runs are
idempotent via UPDATE-or-INSERT on (source, source_id).

The housing-cooperative class is also present in ingest_wikidata_bulk.py with
source='wikidata_bulk', so the same org may appear twice across sources with
different source strings. That is fine: dedup_merge.py collapses cross-source
duplicates later whenever the location agrees. Do not roll dedup here.

Usage:
    python ingest_land_trusts.py --dry-run    # count, no writes
    python ingest_land_trusts.py              # real run
    python ingest_land_trusts.py --limit 1000 # per-class cap (default 1000)
"""
import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from _common import DB_PATH, DATA_DIR, ensure_column

WIKIDATA_ENDPOINT = 'https://query.wikidata.org/sparql'
SLEEP_BETWEEN = 2
LOG_PATH = os.path.join(DATA_DIR, 'ingest-land-trusts-run.log')

# (wikidata_class_qid, taxonomy_subtype, model_type)
# Subclasses are included via wdt:P279*, so variants land in the same bucket.
LAND_CLASSES = [
    ('Q3278937', 'community_land_trust', 'nonprofit'),
    ('Q562166',  'housing_cooperative',  'cooperative'),
]

SPARQL = """
SELECT DISTINCT ?org ?orgLabel ?desc ?website ?country ?countryLabel ?countryCode ?inceptionYear ?hqLabel WHERE {{
  ?org wdt:P31/wdt:P279* wd:{class_qid} .
  OPTIONAL {{ ?org wdt:P17 ?country }}
  OPTIONAL {{ ?country wdt:P297 ?countryCode }}
  OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
  OPTIONAL {{ ?org wdt:P856 ?website }}
  OPTIONAL {{ ?org wdt:P571 ?inception }}
  BIND(YEAR(?inception) AS ?inceptionYear)
  OPTIONAL {{ ?org wdt:P159 ?hq }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,es,fr,pt,de,it,nl,sv,da,no".
    ?org rdfs:label ?orgLabel .
    ?country rdfs:label ?countryLabel .
    ?hq rdfs:label ?hqLabel .
  }}
}} LIMIT {limit}
"""


def sparql_query(sparql, timeout=120):
    url = WIKIDATA_ENDPOINT + '?' + urllib.parse.urlencode({
        'query': sparql,
        'format': 'json',
    })
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Commonweave/1.0 (https://commonweave.earth; directory@commonweave.earth)',
        'Accept': 'application/sparql-results+json',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('results', {}).get('bindings', [])
    except urllib.error.HTTPError as e:
        print(f'  SPARQL HTTP {e.code}: {e.reason}')
        return []
    except Exception as e:
        print(f'  SPARQL error: {e}')
        return []


def bindings_to_orgs(bindings, subtype, model_type):
    orgs = []
    for b in bindings:
        qid_url = b.get('org', {}).get('value', '')
        qid = qid_url.split('/')[-1] if qid_url else ''
        name = b.get('orgLabel', {}).get('value', '')
        if not qid or not name or name.startswith('Q'):
            continue
        orgs.append({
            'source_id': qid,
            'evidence_url': qid_url,
            'name': name,
            'description': b.get('desc', {}).get('value', ''),
            'website': b.get('website', {}).get('value', ''),
            'country_code': (b.get('countryCode', {}).get('value', '') or '').upper(),
            'country_name': b.get('countryLabel', {}).get('value', ''),
            'city': b.get('hqLabel', {}).get('value', ''),
            'last_filing_year': b.get('inceptionYear', {}).get('value', ''),
            'registration_type': f'land_and_housing/{subtype}',
            'model_type': model_type,
            'subtype': subtype,
        })
    return orgs


def run_migration(db):
    for col, typedef in [
        ('evidence_url', 'TEXT'),
        ('evidence_quote', 'TEXT'),
        ('evidence_fetched_at', 'TEXT'),
        ('legibility', "TEXT DEFAULT 'unknown'"),
    ]:
        ensure_column(db, 'organizations', col, typedef)


def upsert_orgs(db, orgs, dry_run=False):
    if not orgs:
        return 0, 0, 0

    try:
        from ingest_gov_registry import classify_org_ml
    except Exception:
        classify_org_ml = None

    c = db.cursor()
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    updated = 0
    skipped_excluded = 0

    for org in orgs:
        name = (org.get('name') or '').strip()
        qid = org.get('source_id') or ''
        if not name or not qid:
            continue

        # Run the classifier mostly to catch hard exclusions. Land and housing
        # orgs are inherently in scope, so we force framework_area='housing_land'
        # and a minimum alignment_score of 2 to survive trim_to_aligned.py.
        area = 'housing_land'
        score = 2
        exclude = False
        if classify_org_ml:
            try:
                a, s, x = classify_org_ml(name, org.get('description', ''))
                exclude = bool(x)
                if not exclude:
                    # Prefer housing_land but do not override a strong keyword
                    # hit on something different (e.g. a row classified as
                    # cooperatives with a high score).
                    if a and int(s or 0) >= 3:
                        area = a
                    score = max(int(s or 0), 2)
            except Exception:
                pass
        if exclude:
            skipped_excluded += 1
            continue

        if dry_run:
            inserted += 1
            continue

        c.execute(
            "SELECT id FROM organizations WHERE source=? AND source_id=?",
            ('wikidata_land_trusts', qid),
        )
        existing = c.fetchone()

        if existing:
            c.execute(
                """UPDATE organizations
                   SET name=?, description=COALESCE(NULLIF(description,''), ?),
                       website=COALESCE(NULLIF(website,''), ?),
                       country_code=COALESCE(NULLIF(country_code,''), ?),
                       country_name=COALESCE(NULLIF(country_name,''), ?),
                       city=COALESCE(NULLIF(city,''), ?),
                       registration_type=?,
                       model_type=?,
                       framework_area=COALESCE(NULLIF(framework_area,''), ?),
                       alignment_score=MAX(COALESCE(alignment_score,0), ?),
                       evidence_url=?,
                       evidence_fetched_at=?,
                       legibility='formal'
                   WHERE id=?""",
                (
                    name,
                    org.get('description', ''),
                    org.get('website', ''),
                    org.get('country_code', ''),
                    org.get('country_name', ''),
                    org.get('city', ''),
                    org.get('registration_type', ''),
                    org.get('model_type', 'nonprofit'),
                    area,
                    score,
                    org.get('evidence_url', ''),
                    now,
                    existing[0],
                ),
            )
            updated += 1
        else:
            c.execute(
                """INSERT OR IGNORE INTO organizations
                   (name, country_code, country_name, city, description, website,
                    source, source_id, registration_type, model_type,
                    framework_area, alignment_score, status, date_added,
                    last_filing_year, legibility, evidence_url, evidence_fetched_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'active',?,?,?,?,?)""",
                (
                    name,
                    org.get('country_code', ''),
                    org.get('country_name', ''),
                    org.get('city', ''),
                    org.get('description', ''),
                    org.get('website', ''),
                    'wikidata_land_trusts',
                    qid,
                    org.get('registration_type', ''),
                    org.get('model_type', 'nonprofit'),
                    area,
                    score,
                    now,
                    org.get('last_filing_year', ''),
                    'formal',
                    org.get('evidence_url', ''),
                    now,
                ),
            )
            if c.rowcount:
                inserted += 1

    if not dry_run:
        db.commit()

    return inserted, updated, skipped_excluded


def write_log(lines):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f'\n# ingest_land_trusts run - {today}\n\n')
        for line in lines:
            f.write(line + '\n')


def main():
    ap = argparse.ArgumentParser(
        description='Ingest community land trusts and housing cooperatives from Wikidata'
    )
    ap.add_argument('--dry-run', action='store_true',
                    help='Query Wikidata and count what would be inserted, no writes')
    ap.add_argument('--limit', type=int, default=1000,
                    help='Max results per SPARQL class (default 1000)')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    run_migration(db)

    totals = {'queried': 0, 'inserted': 0, 'updated': 0, 'skipped_excluded': 0}
    per_subtype = {}

    mode_tag = '[DRY RUN] ' if args.dry_run else ''
    print(f'{mode_tag}Ingesting land trusts and housing cooperatives from Wikidata')
    print(f'  Target subtypes: {sorted(set(s[1] for s in LAND_CLASSES))}')
    print(f'  Per-class limit: {args.limit}')

    for class_qid, subtype, model_type in LAND_CLASSES:
        sparql = SPARQL.format(class_qid=class_qid, limit=args.limit)
        print(f'\n  SPARQL: class={class_qid} subtype={subtype}')
        bindings = sparql_query(sparql)
        print(f'    -> {len(bindings)} results')
        orgs = bindings_to_orgs(bindings, subtype, model_type)
        totals['queried'] += len(orgs)

        inserted, updated, skipped = upsert_orgs(db, orgs, dry_run=args.dry_run)
        totals['inserted'] += inserted
        totals['updated'] += updated
        totals['skipped_excluded'] += skipped

        per_subtype.setdefault(subtype, {'queried': 0, 'inserted': 0, 'updated': 0, 'skipped_excluded': 0})
        per_subtype[subtype]['queried'] += len(orgs)
        per_subtype[subtype]['inserted'] += inserted
        per_subtype[subtype]['updated'] += updated
        per_subtype[subtype]['skipped_excluded'] += skipped

        print(f'    inserted={inserted} updated={updated} excluded={skipped}')
        time.sleep(SLEEP_BETWEEN)

    db.close()

    mode = '[DRY RUN] Would insert' if args.dry_run else 'Inserted'
    lines = [
        f"Mode: {'dry-run' if args.dry_run else 'real'}",
        f"Per-class SPARQL limit: {args.limit}",
        '',
        f"Queried total:  {totals['queried']}",
        f"{mode}: {totals['inserted']}",
        f"Updated:        {totals['updated']}",
        f"Excluded:       {totals['skipped_excluded']}",
        '',
        'Per subtype:',
    ]
    for st, d in sorted(per_subtype.items()):
        lines.append(f"  {st:25s} queried={d['queried']:4d} inserted={d['inserted']:4d} "
                     f"updated={d['updated']:4d} excluded={d['skipped_excluded']:4d}")

    print('\n' + '\n'.join(lines))
    write_log(lines)
    print(f'\nLog appended: {LOG_PATH}')


if __name__ == '__main__':
    main()
