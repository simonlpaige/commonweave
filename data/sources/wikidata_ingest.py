"""
Wikidata SPARQL ingest for Commonweave.

Layer 1/2 foundation script:
- validates ISO country codes with pycountry
- loads ISO alpha-2 -> Wikidata QID from wikidata_qid_map.json
- supports --all to process every mapped pycountry country
- writes to the current commonweave_directory.db schema
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import pycountry

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
QID_MAP_PATH = os.path.join(THIS_DIR, 'wikidata_qid_map.json')
WIKIDATA_ENDPOINT = 'https://query.wikidata.org/sparql'
SOURCE = 'wikidata'

# Wikidata queries tuned for Commonweave-relevant orgs.
SPARQL_QUERIES = [
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      VALUES ?type {{ wd:Q163740 wd:Q1127126 wd:Q157031 wd:Q38026614 wd:Q476068 }}
      ?org wdt:P31/wdt:P279* ?type .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 500
    """,
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      ?org wdt:P31/wdt:P279* wd:Q15911314 .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 500
    """,
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      VALUES ?type {{ wd:Q708676 wd:Q178790 }}
      ?org wdt:P31/wdt:P279* ?type .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 500
    """,
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      VALUES ?type {{ wd:Q31855 wd:Q3918 wd:Q1664720 }}
      ?org wdt:P31/wdt:P279* ?type .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 300
    """,
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      VALUES ?type {{ wd:Q49773 wd:Q7210356 wd:Q15925165 }}
      ?org wdt:P31/wdt:P279* ?type .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 300
    """,
    """
    SELECT DISTINCT ?org ?orgLabel ?desc ?website ?lat ?lon ?inception WHERE {{
      VALUES ?type {{ wd:Q16917 wd:Q7075 wd:Q35535 }}
      ?org wdt:P31/wdt:P279* ?type .
      ?org wdt:P17 wd:{qid} .
      OPTIONAL {{ ?org schema:description ?desc . FILTER(LANG(?desc) = "en") }}
      OPTIONAL {{ ?org wdt:P856 ?website }}
      OPTIONAL {{ ?org p:P625 ?coordStmt . ?coordStmt psv:P625 ?coordNode .
                  ?coordNode wikibase:geoLatitude ?lat . ?coordNode wikibase:geoLongitude ?lon . }}
      OPTIONAL {{ ?org wdt:P571 ?inception }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es,fr,pt,de" }}
    }} LIMIT 300
    """,
]

FRAMEWORK_KEYWORDS = {
    'healthcare': ['health','clinic','hospital','medical','medicine','nurse','hiv','aids','malaria','maternal','salud'],
    'food': ['food','farm','agri','seed','nutrition','hunger','crop','agroecol','permaculture','harvest','aliment'],
    'education': ['education','school','learn','literacy','teach','library','university','college','training','escuela','universidad'],
    'ecology': ['environment','ecology','conservation','climate','biodiversity','forest','ocean','wildlife','restoration','ambiente','naturaleza'],
    'housing_land': ['housing','shelter','land trust','tenure','homeless','affordable housing','vivienda','tierra'],
    'democracy': ['democracy','civic','governance','participat','voting','election','human rights','civil liberties','derechos','democracia'],
    'cooperatives': ['cooperative','co-op','worker-owned','mutual','solidarity','credit union','cooperativa','solidaria'],
    'energy_digital': ['energy','solar','wind','renewable','digital','open source','internet','data','technology','energia'],
    'conflict': ['justice','conflict','mediation','reconciliation','peace','restorative','prison','justicia','paz'],
    'recreation_arts': ['arts','culture','recreation','sport','music','theater','museum','heritage','creative','cultura','arte'],
}

FILTER_KEYWORDS = [
    'football club', 'soccer club', 'basketball club', 'rugby club', 'cricket club',
    'association football', 'f.c.', ' fc ', 'cf ', 'sport club', 'sports club',
    'country club', 'golf club', 'yacht club', 'polo club', 'diocese', 'archdiocese',
    'parish', 'cathedral', 'political party', 'military', 'armed forces',
    'national team', 'olympic committee', 'beauty pageant',
]

try:
    sys.path.insert(0, THIS_DIR)
    from i18n_align import alignment_score_multilingual as _alignment_score
except Exception:  # import should never block ingest
    def _alignment_score(name, desc):
        combined = f'{name} {desc}'.lower()
        return sum(1 for words in FRAMEWORK_KEYWORDS.values() for kw in words if kw in combined)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def stable_id(source, source_id):
    digest = hashlib.sha256(f'{source}:{source_id}'.encode('utf-8')).hexdigest()[:16]
    return f'rec_{digest}'


def load_qid_map():
    with open(QID_MAP_PATH, encoding='utf-8') as f:
        data = json.load(f)
    return {k.upper(): v for k, v in data.items()}


def country_for_code(cc):
    country = pycountry.countries.get(alpha_2=cc.upper())
    if not country:
        raise ValueError(f'Unknown ISO alpha-2 country code: {cc}')
    return getattr(country, 'common_name', None) or country.name


def mapped_countries():
    qids = load_qid_map()
    for c in sorted(pycountry.countries, key=lambda x: x.alpha_2):
        qid = qids.get(c.alpha_2)
        if qid:
            yield c.alpha_2, (getattr(c, 'common_name', None) or c.name), qid


def is_relevant_org(name, desc):
    combined = f'{name} {desc}'.lower()
    return not any(kw in combined for kw in FILTER_KEYWORDS)


def classify_framework(name, desc):
    combined = f'{name} {desc}'.lower()
    best_area, best_score = 'democracy', 0
    for area, keywords in FRAMEWORK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > best_score:
            best_area, best_score = area, score
    return best_area


def classify_model(name, desc):
    combined = f'{name} {desc}'.lower()
    if any(x in combined for x in ('cooperative', 'co-op', 'coop', 'cooperativa', 'credit union')):
        return 'cooperative'
    if 'foundation' in combined or 'stiftung' in combined:
        return 'foundation'
    if 'union' in combined or 'trade union' in combined:
        return 'labor_union'
    if 'mutual aid' in combined:
        return 'mutual_aid'
    return 'nonprofit'


def run_sparql(query, retries=1):
    params = urllib.parse.urlencode({'format': 'json', 'query': query})
    req = urllib.request.Request(f'{WIKIDATA_ENDPOINT}?{params}', headers={
        'User-Agent': 'Commonweave/1.0 (https://commonweave.earth)',
        'Accept': 'application/sparql-results+json',
    })
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            return data.get('results', {}).get('bindings', [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                print('  Rate limited, waiting 30s...')
                time.sleep(30)
                continue
            print(f'  SPARQL error: HTTP {e.code} {e.reason}')
            return []
        except Exception as e:
            print(f'  SPARQL error: {e}')
            return []
    return []


def get_val(binding, key):
    return binding.get(key, {}).get('value', '')


def fetch_country(cc, country_name=None, delay=3, query_index=None):
    cc = cc.upper()
    country_name = country_name or country_for_code(cc)
    qid = load_qid_map().get(cc)
    if not qid:
        print(f'  No Wikidata QID for {cc}, skipping')
        return []

    all_orgs = {}
    queries = list(enumerate(SPARQL_QUERIES, start=1))
    if query_index is not None:
        if query_index < 1 or query_index > len(SPARQL_QUERIES):
            raise ValueError(f'--query-index must be 1..{len(SPARQL_QUERIES)}')
        queries = [(query_index, SPARQL_QUERIES[query_index - 1])]

    for i, query_template in queries:
        print(f'  Query {i}/{len(SPARQL_QUERIES)}...')
        results = run_sparql(query_template.format(qid=qid), retries=1)
        print(f'    Got {len(results)} results')
        for r in results:
            name = get_val(r, 'orgLabel').strip()
            if not name or (name.startswith('Q') and name[1:].isdigit()):
                continue
            desc = get_val(r, 'desc').strip()
            if not is_relevant_org(name, desc):
                continue
            wikidata_id = get_val(r, 'org').rsplit('/', 1)[-1]
            if wikidata_id in all_orgs:
                continue
            lat = get_val(r, 'lat')
            lon = get_val(r, 'lon')
            all_orgs[wikidata_id] = {
                'wikidata_id': wikidata_id,
                'name': name,
                'description': desc[:2000],
                'website': get_val(r, 'website').strip(),
                'lat': float(lat) if lat else None,
                'lon': float(lon) if lon else None,
                'country_code': cc,
                'country': country_name,
                'framework_area': classify_framework(name, desc),
                'model_type': classify_model(name, desc),
                'inception': get_val(r, 'inception'),
            }
        time.sleep(delay)
    return list(all_orgs.values())


def ingest_to_db(orgs, cc, country_name, dry_run=False):
    if not orgs:
        return 0
    if dry_run:
        print(f'  Dry-run: would insert/update up to {len(orgs)} Wikidata orgs')
        return len(orgs)

    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    now = now_iso()
    inserted = 0
    updated = 0
    rejected = 0

    for org in orgs:
        score = _alignment_score(org['name'], org.get('description', ''))
        c.execute("SELECT COUNT(*) FROM organizations WHERE country_code=? AND status != 'removed'", (cc,))
        existing_count = c.fetchone()[0]
        min_score = 0 if existing_count < 50 else 2
        if score < min_score:
            rejected += 1
            continue

        rec_id = stable_id(SOURCE, org['wikidata_id'])
        raw = json.dumps({**org, 'alignment_score': score}, ensure_ascii=False, sort_keys=True)
        params = (
            rec_id, org['name'], org.get('description', ''), org.get('website', ''),
            None, None, country_name, cc, None, org.get('framework_area'), org.get('model_type'),
            'B', SOURCE, f'https://www.wikidata.org/wiki/{org["wikidata_id"]}', None,
            org.get('lat'), org.get('lon'), 'wikidata' if org.get('lat') is not None else None,
            'active', 'indicated', raw, now, now,
        )
        c.execute(
            """INSERT OR IGNORE INTO organizations
               (id, name, description, website, city, state_province, country, country_code,
                ntee_code, framework_area, model_type, tier, source, source_file,
                annual_revenue, lat, lon, geo_source, status, legibility, raw_json,
                created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            params,
        )
        if c.rowcount:
            inserted += 1
        else:
            c.execute(
                """UPDATE organizations
                   SET name=?, description=COALESCE(NULLIF(description,''), ?),
                       website=COALESCE(NULLIF(website,''), ?), framework_area=?, model_type=?,
                       lat=COALESCE(lat, ?), lon=COALESCE(lon, ?), geo_source=COALESCE(geo_source, ?),
                       legibility='indicated', raw_json=?, updated_at=?
                   WHERE id=?""",
                (
                    org['name'], org.get('description', ''), org.get('website', ''),
                    org.get('framework_area'), org.get('model_type'), org.get('lat'), org.get('lon'),
                    'wikidata' if org.get('lat') is not None else None, raw, now, rec_id,
                ),
            )
            if c.rowcount:
                updated += 1

    db.commit()
    c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'removed'")
    total = c.fetchone()[0]
    db.close()
    if rejected:
        print(f'  Rejected {rejected} low-signal orgs before DB insert')
    print(f'  DB: +{inserted} new, {updated} updated from Wikidata, total active={total:,}')
    return inserted + updated


def run_one(cc, country_name=None, dry_run=False, delay=3, query_index=None):
    cc = cc.upper()
    country_name = country_name or country_for_code(cc)
    print(f'\n=== Wikidata ingest: {country_name} ({cc}) ===')
    orgs = fetch_country(cc, country_name, delay=delay, query_index=query_index)
    print(f'Found {len(orgs)} unique organizations')
    changed = ingest_to_db(orgs, cc, country_name, dry_run=dry_run)
    print(f'Done: {changed} orgs inserted/updated')
    for org in orgs[:10]:
        print(f"  - {org['name']}: {org.get('description','')[:80]}")
    return {'country_code': cc, 'country': country_name, 'found': len(orgs), 'changed': changed}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Ingest Commonweave-relevant organizations from Wikidata.')
    ap.add_argument('country', nargs='?', help='ISO alpha-2 code, or ALL for legacy all-country mode')
    ap.add_argument('country_name', nargs='?', help='Optional display name override')
    ap.add_argument('--all', action='store_true', help='Process every pycountry country with a QID')
    ap.add_argument('--dry-run', action='store_true', help='Fetch and score but do not write DB')
    ap.add_argument('--delay', type=float, default=3.0, help='Delay between SPARQL queries/countries')
    ap.add_argument('--query-index', type=int, help='Run only one SPARQL query (1-6), useful for endpoint smoke tests')
    args = ap.parse_args(argv)

    run_all = args.all or (args.country and args.country.upper() == 'ALL')
    if run_all:
        total = {'found': 0, 'changed': 0, 'countries': 0}
        for cc, country_name, _qid in mapped_countries():
            result = run_one(cc, country_name, dry_run=args.dry_run, delay=args.delay, query_index=args.query_index)
            total['found'] += result['found']
            total['changed'] += result['changed']
            total['countries'] += 1
            time.sleep(args.delay)
        print(f"\nTotal: {total['countries']} countries, {total['found']} found, {total['changed']} inserted/updated")
        return 0

    if not args.country:
        ap.print_help()
        return 2
    run_one(args.country, args.country_name, dry_run=args.dry_run, delay=args.delay, query_index=args.query_index)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
