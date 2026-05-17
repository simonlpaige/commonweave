"""
GlobalGiving Atlas ingest for Commonweave.

Downloads country-level nonprofit data from GlobalGiving Atlas and writes rows to
commonweave_directory.db with source='globalgiving' and legibility='indicated'.

The Atlas API requires a free API key. Provide it via one of:
  GLOBALGIVING_ATLAS_API_KEY, GLOBALGIVING_API_KEY, or --api-key

Usage:
  python sources/ingest_globalgiving.py US --limit 100 --dry-run
  python sources/ingest_globalgiving.py KE --format csv
  python sources/ingest_globalgiving.py --all --limit 1000
"""
import argparse
import csv
import hashlib
import io
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

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
SOURCE = 'globalgiving'
USER_AGENT = 'Commonweave/1.0 (https://commonweave.earth)'

CANDIDATE_URLS = [
    'https://api.globalgiving.org/v2/atlas/organizations/{country}.{format}',
    'https://api.globalgiving.org/v2/atlas/organizations/{country}?format={format}',
    'https://api.globalgiving.org/v2/atlas/organizations/{country}',
]

ATLAS_401_MESSAGE = (
    'GlobalGiving Atlas requires a paid license. This API key works for v1 but not Atlas v2. '
    'Register at https://www.globalgiving.org/atlas/ for Atlas access.'
)

V1_PROJECT_URLS = [
    'https://api.globalgiving.org/api/public/projectservice/countries/{country}/projects',
    'https://api.globalgiving.org/api/public/projectservice/all/projects?country={country}',
]

FRAMEWORK_KEYWORDS = {
    'healthcare': ['health', 'clinic', 'hospital', 'medical', 'medicine', 'maternal', 'hiv', 'aids'],
    'food': ['food', 'farm', 'agriculture', 'nutrition', 'hunger', 'seed'],
    'education': ['education', 'school', 'learning', 'literacy', 'teacher', 'university'],
    'ecology': ['environment', 'climate', 'conservation', 'forest', 'biodiversity', 'wildlife'],
    'housing_land': ['housing', 'shelter', 'homeless', 'land'],
    'democracy': ['rights', 'civic', 'democracy', 'justice', 'advocacy', 'community'],
    'cooperatives': ['cooperative', 'co-op', 'mutual', 'solidarity', 'credit union'],
    'energy_digital': ['energy', 'solar', 'technology', 'digital', 'internet'],
    'conflict': ['peace', 'conflict', 'reconciliation', 'restorative'],
    'recreation_arts': ['arts', 'culture', 'sport', 'music', 'heritage'],
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def stable_id(source, source_id):
    digest = hashlib.sha256(f'{source}:{source_id}'.encode('utf-8')).hexdigest()[:16]
    return f'rec_{digest}'


def api_key_from_env():
    return os.environ.get('GLOBALGIVING_ATLAS_API_KEY') or os.environ.get('GLOBALGIVING_API_KEY')


def country_name(cc):
    country = pycountry.countries.get(alpha_2=cc.upper())
    return (getattr(country, 'common_name', None) or country.name) if country else cc.upper()


def add_api_key(url, api_key):
    if not api_key:
        return url
    sep = '&' if '?' in url else '?'
    return f'{url}{sep}{urllib.parse.urlencode({"api_key": api_key})}'


def fetch_url(url, api_key=None):
    req = urllib.request.Request(add_api_key(url, api_key), headers={
        'User-Agent': USER_AGENT,
        'Accept': 'application/json,text/csv;q=0.9,*/*;q=0.1',
    })
    with urllib.request.urlopen(req, timeout=180) as resp:
        content_type = resp.headers.get('Content-Type', '')
        data = resp.read()
    return data, content_type


def download_country(cc, fmt='json', api_key=None, url_template=None):
    cc = cc.upper()
    candidates = [url_template] if url_template else CANDIDATE_URLS
    last_error = None
    for template in candidates:
        url = template.format(country=cc, format=fmt)
        try:
            body, content_type = fetch_url(url, api_key=api_key)
            return body, content_type, url
        except urllib.error.HTTPError as e:
            last_error = f'HTTP {e.code} {e.reason} for {url}'
            if e.code == 401:
                raise RuntimeError(ATLAS_401_MESSAGE) from e
            if e.code == 403:
                raise RuntimeError(f'{last_error}; GlobalGiving Atlas access denied') from e
            if e.code == 404:
                continue
            raise RuntimeError(last_error) from e
        except Exception as e:
            last_error = f'{type(e).__name__}: {e} for {url}'
            continue
    raise RuntimeError(last_error or f'No GlobalGiving Atlas endpoint worked for {cc}')


def parse_json_payload(body):
    text = body.decode('utf-8-sig')
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Some bulk APIs use NDJSON.
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ('organizations', 'data', 'results', 'items'):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    return []


def parse_csv_payload(body):
    text = body.decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(text)))


def parse_payload(body, content_type='', fmt='json'):
    if 'csv' in content_type.lower() or fmt == 'csv':
        return parse_csv_payload(body)
    return parse_json_payload(body)


def add_v1_auth(url, api_key):
    if not api_key:
        return url
    sep = '&' if '?' in url else '?'
    return f'{url}{sep}{urllib.parse.urlencode({"api_key": api_key})}'


def fetch_v1_projects(cc, api_key=None, limit=None):
    """Best-effort GlobalGiving v1 fallback for project-level data.

    v1 is not Atlas and does not provide the same comprehensive nonprofit
    registry. It can still provide project organizations for a country when the
    API key is valid for the public project service.
    """
    last_error = None
    for template in V1_PROJECT_URLS:
        url = template.format(country=cc.upper())
        req = urllib.request.Request(add_v1_auth(url, api_key), headers={
            'User-Agent': USER_AGENT,
            'Accept': 'application/json,*/*;q=0.1',
        })
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                body = resp.read()
                content_type = resp.headers.get('Content-Type', '')
            rows = parse_json_payload(body) if 'json' in content_type.lower() or body[:1] in (b'{', b'[') else []
            projects = normalize_v1_projects(rows)
            return projects[:limit] if limit else projects, url
        except urllib.error.HTTPError as e:
            last_error = f'HTTP {e.code} {e.reason} for {url}'
            if e.code == 404:
                continue
            if e.code in (401, 403):
                raise RuntimeError(f'GlobalGiving v1 project fallback access denied ({e.code}). The key may be invalid for v1 projectservice.') from e
        except Exception as e:
            last_error = f'{type(e).__name__}: {e} for {url}'
    raise RuntimeError(last_error or f'No GlobalGiving v1 project endpoint worked for {cc}')


def normalize_v1_projects(payload):
    if isinstance(payload, list):
        candidates = payload
    elif isinstance(payload, dict):
        candidates = []
        stack = [payload]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if key == 'project' and isinstance(value, list):
                        candidates.extend(value)
                    elif key == 'projects' and isinstance(value, list):
                        candidates.extend(value)
                    elif isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(item, list):
                stack.extend(item)
    else:
        candidates = []
    return [p for p in candidates if isinstance(p, dict)]


def map_v1_project(row, cc, source_url):
    org = pick(row, 'organization', 'organizationName', 'orgName')
    if isinstance(org, dict):
        org_name = str(pick(org, 'name', 'organizationName')).strip()
        website = str(pick(org, 'url', 'website')).strip()
        org_id = str(pick(org, 'id', 'organizationId')).strip()
    else:
        org_name = str(org or '').strip()
        website = ''
        org_id = ''
    name = org_name or str(pick(row, 'organizationName', 'orgName', 'contactName')).strip()
    if not name:
        title = str(pick(row, 'title', 'projectTitle')).strip()
        name = f'GlobalGiving project: {title}' if title else ''
    if not name:
        return None
    project_id = str(pick(row, 'id', 'projectId')).strip()
    source_id = org_id or project_id or f'{cc}:{hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:20]}'
    desc = str(pick(row, 'summary', 'themeName', 'title', 'projectTitle')).strip()
    return {
        'source_id': f'v1:{source_id}',
        'name': name,
        'description': desc[:2000],
        'website': website or str(pick(row, 'projectLink', 'projectUrl')).strip(),
        'city': str(pick(row, 'city')).strip(),
        'state_province': str(pick(row, 'state', 'region')).strip(),
        'country': country_name(cc),
        'country_code': cc,
        'framework_area': classify_framework(name, desc),
        'model_type': model_type(name, desc),
        'lat': None,
        'lon': None,
        'source_file': source_url,
        'raw_json': json.dumps(row, ensure_ascii=False, sort_keys=True, default=str),
    }


def pick(row, *names):
    if not isinstance(row, dict):
        return ''
    lower = {str(k).lower(): v for k, v in row.items()}
    for name in names:
        if name in row and row.get(name) not in (None, ''):
            return row.get(name)
        value = lower.get(name.lower())
        if value not in (None, ''):
            return value
    return ''


def classify_framework(name, desc):
    combined = f'{name} {desc}'.lower()
    best, best_score = 'democracy', 0
    for area, words in FRAMEWORK_KEYWORDS.items():
        score = sum(1 for w in words if w in combined)
        if score > best_score:
            best, best_score = area, score
    return best


def model_type(name, desc):
    combined = f'{name} {desc}'.lower()
    if any(x in combined for x in ('cooperative', 'co-op', 'coop', 'credit union')):
        return 'cooperative'
    if 'foundation' in combined:
        return 'foundation'
    if 'mutual aid' in combined:
        return 'mutual_aid'
    return 'nonprofit'


def map_row(row, cc, source_url):
    name = str(pick(row, 'name', 'organization_name', 'org_name', 'charity_name')).strip()
    if not name:
        return None
    reg_country = str(pick(row, 'registration_country', 'country', 'country_code')).strip().upper() or cc
    if reg_country != cc:
        # Country bulk files should be country-local; keep the caller honest.
        reg_country = cc
    atlas_id = str(pick(row, 'id')).strip()
    local_reg_id = str(pick(row, 'registration_id', 'ein', 'tax_id', 'identifier')).strip()
    reg_id = atlas_id or (f'{cc}:{local_reg_id}' if local_reg_id else '')
    if not reg_id:
        reg_id = f'{cc}:{hashlib.sha256(json.dumps(row, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:20]}'
    mission = str(pick(row, 'mission', 'description', 'summary', 'activity', 'cause')).strip()
    website = str(pick(row, 'website', 'url', 'website_url')).strip()
    city = str(pick(row, 'city', 'address_city', 'locality')).strip()
    state = str(pick(row, 'state', 'state_province', 'region', 'province')).strip()
    lat = pick(row, 'lat', 'latitude')
    lon = pick(row, 'lon', 'lng', 'longitude')
    try:
        lat = float(lat) if lat not in (None, '') else None
        lon = float(lon) if lon not in (None, '') else None
    except Exception:
        lat, lon = None, None
    return {
        'source_id': reg_id,
        'name': name,
        'description': mission[:2000],
        'website': website,
        'city': city,
        'state_province': state,
        'country': country_name(cc),
        'country_code': cc,
        'framework_area': classify_framework(name, mission),
        'model_type': model_type(name, mission),
        'lat': lat,
        'lon': lon,
        'source_file': source_url,
        'raw_json': json.dumps(row, ensure_ascii=False, sort_keys=True, default=str),
    }


def upsert_rows(rows, dry_run=False):
    mapped = [r for r in rows if r]
    if dry_run:
        return len(mapped), 0
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    now = now_iso()
    inserted = 0
    updated = 0
    for row in mapped:
        rec_id = stable_id(SOURCE, row['source_id'])
        params = (
            rec_id, row['name'], row['description'], row['website'], row['city'], row['state_province'],
            row['country'], row['country_code'], None, row['framework_area'], row['model_type'], 'B',
            SOURCE, row['source_file'], None, row['lat'], row['lon'], 'globalgiving' if row['lat'] is not None else None,
            'active', 'indicated', row['raw_json'], now, now,
        )
        cur.execute(
            """INSERT OR IGNORE INTO organizations
               (id, name, description, website, city, state_province, country, country_code,
                ntee_code, framework_area, model_type, tier, source, source_file, annual_revenue,
                lat, lon, geo_source, status, legibility, raw_json, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            params,
        )
        if cur.rowcount:
            inserted += 1
        else:
            cur.execute(
                """UPDATE organizations
                   SET name=?, description=COALESCE(NULLIF(description,''), ?),
                       website=COALESCE(NULLIF(website,''), ?), city=COALESCE(NULLIF(city,''), ?),
                       state_province=COALESCE(NULLIF(state_province,''), ?),
                       framework_area=?, model_type=?, legibility='indicated', raw_json=?, updated_at=?
                   WHERE id=?""",
                (row['name'], row['description'], row['website'], row['city'], row['state_province'],
                 row['framework_area'], row['model_type'], row['raw_json'], now, rec_id),
            )
            if cur.rowcount:
                updated += 1
    db.commit()
    db.close()
    return inserted, updated


def ingest_country(cc, fmt='json', api_key=None, limit=None, dry_run=False, url_template=None, fallback_v1=False):
    cc = cc.upper()
    if dry_run and not api_key and not url_template:
        print(f'Dry-run: GlobalGiving ingest module loads; would fetch {cc} with an Atlas API key')
        return {'country_code': cc, 'found': 0, 'inserted': 0, 'updated': 0, 'dry_run': True}
    try:
        body, content_type, source_url = download_country(cc, fmt=fmt, api_key=api_key, url_template=url_template)
        raw_rows = parse_payload(body, content_type=content_type, fmt=fmt)
        if limit:
            raw_rows = raw_rows[:limit]
        mapped = [map_row(r, cc, source_url) for r in raw_rows]
    except RuntimeError as e:
        if str(e) != ATLAS_401_MESSAGE or not fallback_v1:
            raise
        print(ATLAS_401_MESSAGE)
        print('Falling back to GlobalGiving v1 projectservice. Coverage is project-level only, not Atlas nonprofit registry coverage.')
        raw_rows, source_url = fetch_v1_projects(cc, api_key=api_key, limit=limit)
        mapped = [map_v1_project(r, cc, source_url) for r in raw_rows]
    mapped = [r for r in mapped if r]
    inserted, updated = upsert_rows(mapped, dry_run=dry_run)
    print(f'{cc}: {len(raw_rows)} downloaded, {len(mapped)} mapped, {inserted} inserted, {updated} updated')
    return {'country_code': cc, 'found': len(mapped), 'inserted': inserted, 'updated': updated, 'dry_run': dry_run}


def iter_countries():
    for c in sorted(pycountry.countries, key=lambda x: x.alpha_2):
        yield c.alpha_2


def main(argv=None):
    ap = argparse.ArgumentParser(description='Ingest GlobalGiving Atlas nonprofits by country.')
    ap.add_argument('country', nargs='?', help='ISO alpha-2 country code')
    ap.add_argument('--all', action='store_true', help='Process every pycountry country')
    ap.add_argument('--format', choices=['json', 'csv'], default='json')
    ap.add_argument('--api-key', default=api_key_from_env())
    ap.add_argument('--limit', type=int)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--url-template', help='Override Atlas bulk URL template; supports {country} and {format}')
    ap.add_argument('--fallback-v1', action='store_true', help='On Atlas 401, try GlobalGiving v1 projectservice fallback (less comprehensive project-level data)')
    ap.add_argument('--sleep', type=float, default=1.0)
    args = ap.parse_args(argv)

    if not args.country and not args.all:
        ap.print_help()
        return 2
    countries = list(iter_countries()) if args.all else [args.country.upper()]
    total = {'found': 0, 'inserted': 0, 'updated': 0}
    for cc in countries:
        try:
            result = ingest_country(
                cc, fmt=args.format, api_key=args.api_key, limit=args.limit,
                dry_run=args.dry_run, url_template=args.url_template, fallback_v1=args.fallback_v1,
            )
        except RuntimeError as e:
            print(f'ERROR: {e}', file=sys.stderr)
            return 1
        for key in total:
            total[key] += result.get(key, 0)
        time.sleep(args.sleep)
    print(json.dumps(total, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
