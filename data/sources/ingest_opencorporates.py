"""
OpenCorporates ingest for Commonweave.

Queries the OpenCorporates REST API by jurisdiction and cooperative/nonprofit
legal-form search terms, then writes indicated Commonweave candidates to the
shared directory DB.

API key/token can be supplied by OPENCORPORATES_API_KEY or --api-key.
The current OpenCorporates API returns 401 without a valid token.
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
SOURCE = 'opencorporates'
API_BASE = 'https://api.opencorporates.com/v0.4/companies/search'
USER_AGENT = 'Commonweave/1.0 (https://commonweave.earth)'
DEFAULT_TERMS = [
    'nonprofit', 'non-profit', 'not for profit', 'cooperative', 'co-operative',
    'coop', 'mutual', 'community interest company', 'benefit corporation',
    'sociedad cooperativa', 'association', 'foundation',
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def stable_id(source, source_id):
    digest = hashlib.sha256(f'{source}:{source_id}'.encode('utf-8')).hexdigest()[:16]
    return f'rec_{digest}'


def country_name(cc):
    country = pycountry.countries.get(alpha_2=cc.upper())
    return (getattr(country, 'common_name', None) or country.name) if country else cc.upper()


def api_key_from_env():
    return os.environ.get('OPENCORPORATES_API_KEY') or os.environ.get('OPENCORPORATES_API_TOKEN')


def fetch_page(cc, term, api_key=None, page=1, per_page=30):
    params = {
        'q': term,
        'jurisdiction_code': cc.lower(),
        'page': page,
        'per_page': min(max(per_page, 1), 100),
    }
    if api_key:
        # OpenCorporates docs historically used api_token; some accounts expose
        # the value as an API key. Keep the CLI/env name generic but send token.
        params['api_token'] = api_key
    url = f'{API_BASE}?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode('utf-8')), url
    except urllib.error.HTTPError as e:
        body = ''
        try:
            body = e.read().decode('utf-8', 'replace')[:500]
        except Exception:
            pass
        if e.code == 401:
            raise RuntimeError('OpenCorporates API requires a valid API key/token. Set OPENCORPORATES_API_KEY or pass --api-key. Response: 401 Unauthorized') from e
        if e.code == 429:
            raise RuntimeError('OpenCorporates rate limit hit (429). Retry later or lower --pages/--sleep.') from e
        raise RuntimeError(f'OpenCorporates HTTP {e.code}: {body}') from e


def iter_companies(payload):
    companies = payload.get('results', {}).get('companies', []) if isinstance(payload, dict) else []
    for item in companies:
        company = item.get('company') if isinstance(item, dict) else None
        if isinstance(company, dict):
            yield company


def map_company(company, cc, term, source_url):
    name = (company.get('name') or '').strip()
    number = (company.get('company_number') or '').strip()
    jurisdiction = (company.get('jurisdiction_code') or cc.lower()).lower()
    if not name or not number:
        return None
    ctype = (company.get('company_type') or '').strip()
    status = (company.get('current_status') or '').strip()
    address = (company.get('registered_address_in_full') or '').strip()
    inactive = bool(company.get('inactive'))
    description = '; '.join(x for x in [ctype, status, address] if x)[:2000]
    model = 'cooperative' if 'coop' in f'{term} {ctype}'.lower() else 'nonprofit'
    if 'mutual' in f'{term} {ctype}'.lower():
        model = 'mutual_aid'
    if 'foundation' in f'{term} {ctype}'.lower():
        model = 'foundation'
    return {
        'source_id': f'{jurisdiction}:{number}',
        'name': name,
        'description': description,
        'website': company.get('opencorporates_url') or '',
        'city': '',
        'state_province': '',
        'country': country_name(cc),
        'country_code': cc.upper(),
        'framework_area': 'cooperatives' if model == 'cooperative' else 'democracy',
        'model_type': model,
        'source_file': source_url,
        'raw_json': json.dumps({**company, 'matched_term': term}, ensure_ascii=False, sort_keys=True, default=str),
        'status': 'inactive' if inactive else 'active',
    }


def upsert_rows(rows, dry_run=False):
    rows = [r for r in rows if r]
    if dry_run:
        return len(rows), 0
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    now = now_iso()
    inserted = updated = 0
    for row in rows:
        rec_id = stable_id(SOURCE, row['source_id'])
        params = (
            rec_id, row['name'], row['description'], row['website'], row['city'], row['state_province'],
            row['country'], row['country_code'], None, row['framework_area'], row['model_type'], 'B',
            SOURCE, row['source_file'], None, None, None, None, row['status'], 'indicated', row['raw_json'], now, now,
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
                       website=COALESCE(NULLIF(website,''), ?), framework_area=?, model_type=?,
                       legibility='indicated', raw_json=?, updated_at=?
                   WHERE id=?""",
                (row['name'], row['description'], row['website'], row['framework_area'], row['model_type'], row['raw_json'], now, rec_id),
            )
            if cur.rowcount:
                updated += 1
    db.commit()
    db.close()
    return inserted, updated


def ingest_country(cc, api_key=None, terms=None, pages=1, per_page=30, sleep=1.0, dry_run=False):
    cc = cc.upper()
    terms = terms or DEFAULT_TERMS
    if dry_run and not api_key:
        print(f'Dry-run: OpenCorporates module loads; would query {cc}. No OPENCORPORATES_API_KEY found.')
        return {'country_code': cc, 'found': 0, 'inserted': 0, 'updated': 0, 'dry_run': True, 'blocked': 'missing_api_key'}
    all_rows = []
    seen = set()
    for term in terms:
        for page in range(1, pages + 1):
            payload, url = fetch_page(cc, term, api_key=api_key, page=page, per_page=per_page)
            companies = list(iter_companies(payload))
            print(f'{cc}: term={term!r} page={page} got {len(companies)}')
            for company in companies:
                key = (company.get('jurisdiction_code'), company.get('company_number'))
                if key in seen:
                    continue
                seen.add(key)
                all_rows.append(map_company(company, cc, term, url))
            if len(companies) < per_page:
                break
            time.sleep(sleep)
    inserted, updated = upsert_rows(all_rows, dry_run=dry_run)
    print(f'{cc}: {len([r for r in all_rows if r])} mapped, {inserted} inserted, {updated} updated')
    return {'country_code': cc, 'found': len([r for r in all_rows if r]), 'inserted': inserted, 'updated': updated, 'dry_run': dry_run}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Ingest cooperative/nonprofit legal-form candidates from OpenCorporates.')
    ap.add_argument('country', help='ISO alpha-2 country code')
    ap.add_argument('--api-key', default=api_key_from_env(), help='OpenCorporates API key/token; default OPENCORPORATES_API_KEY')
    ap.add_argument('--term', action='append', dest='terms', help='Search term; can repeat. Defaults to nonprofit/cooperative legal-form terms.')
    ap.add_argument('--pages', type=int, default=1, help='Pages per term (default 1; API max page is 100)')
    ap.add_argument('--per-page', type=int, default=30, help='Results per page, max 100')
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args(argv)
    try:
        result = ingest_country(args.country, api_key=args.api_key, terms=args.terms, pages=args.pages, per_page=args.per_page, sleep=args.sleep, dry_run=args.dry_run)
    except RuntimeError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
