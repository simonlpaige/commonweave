"""
ICA Cooperatives Connect ingest for Commonweave.

The public ICA page describes Cooperatives Connect and links to the ICA/SEA
linked-data directory. This ingester is conservative: it fetches the directory
page(s), extracts organization-looking links/cards/JSON-LD when available, and
inserts rows as source='ica_coops'. If the public directory renders mostly via
client-side code, the run exits cleanly with found=0 and a note instead of
pretending coverage exists.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser

import pycountry

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
SOURCE = 'ica_coops'
USER_AGENT = 'Commonweave/1.0 (https://commonweave.earth)'
ICA_PAGE = 'https://ica.coop/en/cooperatives-connect'
DIRECTORY_URLS = [
    'https://ica.solidarityeconomy.coop/?language=EN',
    'https://identity.coop/directory/',
]


class LinkTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._buf = []
        self.scripts = []
        self._script = False
        self._script_buf = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'):
            self._href = attrs.get('href')
            self._buf = []
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self._script = True
            self._script_buf = []

    def handle_endtag(self, tag):
        if tag == 'a' and self._href:
            text = ' '.join(''.join(self._buf).split())
            self.links.append((self._href, html.unescape(text)))
            self._href = None
            self._buf = []
        if tag == 'script' and self._script:
            self.scripts.append(''.join(self._script_buf))
            self._script = False
            self._script_buf = []

    def handle_data(self, data):
        if self._href:
            self._buf.append(data)
        if self._script:
            self._script_buf.append(data)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def stable_id(source, source_id):
    digest = hashlib.sha256(f'{source}:{source_id}'.encode('utf-8')).hexdigest()[:16]
    return f'rec_{digest}'


def country_name(cc):
    country = pycountry.countries.get(alpha_2=cc.upper())
    return (getattr(country, 'common_name', None) or country.name) if country else cc.upper()


def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode('utf-8', 'replace'), resp.geturl()


def looks_like_org(text, href):
    blob = f'{text} {href}'.lower()
    if len(text.strip()) < 3:
        return False
    bad = ('facebook.com', 'twitter.com', 'youtube.com', 'linkedin.com', 'instagram.com', 'newsletter', 'search', 'about-us')
    if any(x in blob for x in bad):
        return False
    good = ('coop', 'co-op', 'cooperative', 'co-operative', 'credit union', 'federation', 'alliance', 'society')
    return any(x in blob for x in good)


def country_matches(blob, cc):
    cc = cc.upper()
    name = country_name(cc).lower()
    blob = blob.lower()
    return cc.lower() in blob or name in blob


def extract_jsonld_orgs(parser, cc, source_url):
    rows = []
    for script in parser.scripts:
        try:
            data = json.loads(script)
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
                continue
            if not isinstance(item, dict):
                continue
            stack.extend(v for v in item.values() if isinstance(v, (dict, list)))
            typ = item.get('@type') or item.get('type') or ''
            name = item.get('name') or ''
            url = item.get('url') or item.get('@id') or source_url
            blob = json.dumps(item, ensure_ascii=False)
            if name and 'organization' in str(typ).lower() and country_matches(blob, cc):
                rows.append(make_row(name, url, cc, source_url, item))
    return rows


def make_row(name, url, cc, source_url, raw):
    return {
        'source_id': url or f'{cc}:{name}',
        'name': name.strip()[:300],
        'description': 'ICA Cooperatives Connect / cooperative directory hit',
        'website': url if str(url).startswith('http') else '',
        'city': '',
        'state_province': '',
        'country': country_name(cc),
        'country_code': cc.upper(),
        'framework_area': 'cooperatives',
        'model_type': 'cooperative',
        'source_file': source_url,
        'raw_json': json.dumps(raw, ensure_ascii=False, sort_keys=True, default=str),
    }


def scrape_url(url, cc):
    body, final_url = fetch_html(url)
    parser = LinkTextParser()
    parser.feed(body)
    rows = extract_jsonld_orgs(parser, cc, final_url)
    for href, text in parser.links:
        absolute = urllib.parse.urljoin(final_url, href)
        blob = f'{text} {absolute}'
        if looks_like_org(text, absolute) and country_matches(blob, cc):
            rows.append(make_row(text, absolute, cc, final_url, {'href': absolute, 'text': text}))
    # Last-resort: some map apps hydrate data into JS variables. Extract small
    # name/url/country-looking fragments without collecting personal data.
    for match in re.finditer(r'"name"\s*:\s*"([^"]{3,200})".{0,500}?"(?:country|countryCode)"\s*:\s*"([^"]{2,80})"', body, re.I | re.S):
        name, country = match.groups()
        if cc.lower() == country.lower() or country_name(cc).lower() == country.lower():
            rows.append(make_row(html.unescape(name), final_url, cc, final_url, {'fragment': match.group(0)[:800]}))
    dedup = {}
    for row in rows:
        dedup[row['source_id']] = row
    return list(dedup.values()), final_url


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
            row['country'], row['country_code'], None, row['framework_area'], row['model_type'], 'B', SOURCE,
            row['source_file'], None, None, None, None, 'active', 'indicated', row['raw_json'], now, now,
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
                   SET name=?, website=COALESCE(NULLIF(website,''), ?), legibility='indicated', raw_json=?, updated_at=?
                   WHERE id=?""",
                (row['name'], row['website'], row['raw_json'], now, rec_id),
            )
            if cur.rowcount:
                updated += 1
    db.commit()
    db.close()
    return inserted, updated


def ingest_country(cc, urls=None, dry_run=False):
    cc = cc.upper()
    urls = urls or DIRECTORY_URLS
    rows = []
    checked = []
    errors = []
    for url in urls:
        try:
            got, final_url = scrape_url(url, cc)
            checked.append(final_url)
            rows.extend(got)
            print(f'{cc}: {final_url} yielded {len(got)} candidate rows')
        except Exception as e:
            errors.append(f'{url}: {type(e).__name__}: {e}')
            print(f'{cc}: {url} failed: {e}')
    dedup = {r['source_id']: r for r in rows}
    inserted, updated = upsert_rows(list(dedup.values()), dry_run=dry_run)
    result = {'country_code': cc, 'found': len(dedup), 'inserted': inserted, 'updated': updated, 'checked': checked, 'errors': errors, 'dry_run': dry_run}
    if not dedup:
        result['note'] = 'No parseable public ICA directory rows found; page may require client-side/API-specific extraction or data request.'
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description='Ingest ICA Cooperatives Connect directory rows by country.')
    ap.add_argument('country', help='ISO alpha-2 country code')
    ap.add_argument('--url', action='append', dest='urls', help='Directory URL to scrape; can repeat')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args(argv)
    ingest_country(args.country, urls=args.urls, dry_run=args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
