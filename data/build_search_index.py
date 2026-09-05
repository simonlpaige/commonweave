"""Build static search shards from an explicitly selected, read-only canonical DB.

Markdown research notes are candidate leads, not an independent publication store.
Promote evidence-backed corrections through stage_organizations.py first. Every
published row has a stable ID; provenance survives instead of being dropped.
"""
import argparse
import collections
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from audit_public_exports import ISO2, valid_url
from _common import normalize_us_state

US_STATES = set('AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR VI GU AS MP AA AE AP'.split())
NTEE_CATEGORIES = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', [
    'Arts & Culture', 'Education', 'Environment', 'Animal-Related', 'Health Care',
    'Mental Health', 'Disease Research', 'Medical Research', 'Crime & Legal',
    'Employment', 'Food & Agriculture', 'Housing & Shelter', 'Public Safety',
    'Recreation & Sports', 'Youth Dev', 'Human Services', 'International Affairs',
    'Civil Rights', 'Community Dev', 'Philanthropy', 'Science & Tech',
    'Social Science', 'Public Benefit', 'Religion', 'Mutual Benefit', 'Unknown']))


def compact_org(row):
    out = {'id': row['id'], 'n': row['name'], 'c': row.get('city') or '',
           't': row.get('ntee_code') or '', 'w': row.get('website') or '',
           'd': (row.get('description') or '')[:500], 'r': row.get('annual_revenue') or 0}
    for source, target in [('framework_area', 'f'), ('source', 'src'), ('tier', 'tier'),
                           ('legibility', 'legibility'), ('source_url', 'source_url'),
                           ('evidence_url', 'evidence_url'), ('last_verified_at', 'last_verified_at')]:
        if row.get(source) is not None:
            out[target] = row[source]
    return out


def build(db_path, output):
    db_path, output = Path(db_path).resolve(), Path(output).resolve()
    db = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        columns = {r[1] for r in db.execute('PRAGMA table_info(organizations)')}
        if not {'id', 'name', 'country_code', 'status'} <= columns:
            raise ValueError('Canonical identity/country/status schema missing')
        where = "status='active'"
        if 'merged_into' in columns:
            where += " AND (merged_into IS NULL OR merged_into=0 OR merged_into='')"
        rows = [dict(r) for r in db.execute('SELECT * FROM organizations WHERE '+where+' ORDER BY country_code,name,id')]
    finally:
        db.close()
    old_index_path = output / 'index.json'
    old = json.loads(old_index_path.read_text(encoding='utf-8')) if old_index_path.exists() else {}
    old_us_path = output / 'US_meta.json'
    old_us = json.loads(old_us_path.read_text(encoding='utf-8')) if old_us_path.exists() else {}
    countries, states, skipped = collections.defaultdict(list), collections.defaultdict(list), []
    sanitized = []
    for row in rows:
        code = row['country_code']
        if code not in ISO2:
            skipped.append({'id': row['id'], 'reason': 'missing_or_non_iso_country'})
            continue
        for field in ('website', 'source_url', 'evidence_url'):
            if row.get(field) and not valid_url(row[field]):
                sanitized.append({'id': row['id'], 'field': field, 'reason': 'unsafe_or_malformed_url'})
                row[field] = ''
        countries[code].append(row)
        if code == 'US':
            state = str(normalize_us_state(row.get('state_province')) or 'UNK').upper()
            # State values are data, never file paths. Unresolved values are kept searchable.
            if state not in US_STATES:
                state = 'UNK'
            states[state].append(row)
    output.mkdir(parents=True, exist_ok=True)
    files, meta = {}, {}
    for code, members in sorted(countries.items()):
        name = members[0].get('country_name') or old.get('countries', {}).get(code, {}).get('name') or code
        meta[code] = {'name': name, 'count': len(members), 'source': 'public_export', 'has_data': True}
        if code != 'US':
            files[code+'.json'] = {'country_code': code, 'country_name': name, 'source': 'Canonical database export',
                                  'count': len(members), 'orgs': [compact_org(r) for r in members]}
    us_states = {}
    for state, members in sorted(states.items()):
        name = old_us.get('states', {}).get(state, {}).get('name', 'State unknown' if state == 'UNK' else state)
        us_states[state] = {'name': name, 'count': len(members)}
        files['US_'+state+'.json'] = {'state': state, 'name': name, 'count': len(members), 'orgs': [compact_org(r) for r in members]}
    files['US_meta.json'] = {'country_code': 'US', 'country_name': 'United States', 'total': len(countries.get('US', [])),
                             'states': us_states, 'ntee_counts': dict(collections.Counter((r.get('ntee_code') or 'Z')[0] for r in countries.get('US', [])))}
    files['index.json'] = {'generated': datetime.now(timezone.utc).isoformat(), 'total_orgs': sum(len(r) for r in countries.values()),
                           'total_countries': len(countries), 'countries': meta, 'ntee_categories': NTEE_CATEGORIES,
                           'count_basis': 'Actual orgs arrays in shipped country/state JSON files; candidate rows, not verified organizations.',
                           'inventory_script': 'data/reconcile_search_index.py',
                           'provenance_note': 'generated identifies the export build time; metadata reconciliation does not reverify organizations.'}
    files['build-review.json'] = {'omitted_rows': skipped, 'sanitized_fields': sanitized,
                                  'note': 'Resolve country identity and unsafe URLs through canonical staged corrections before publication.'}
    # Write index last. Every country referred to by it is already on disk.
    for filename in sorted(files, key=lambda name: name == 'index.json'):
        path = output / filename
        temp = path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(files[filename], ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
        temp.replace(path)
    # Remove only known shard names inside the checked output directory.
    for path in output.glob('*.json'):
        if path.name not in files and (path.stem in ISO2 or (path.stem.startswith('US_') and path.stem != 'US_meta')):
            if path.resolve().parent != output:
                raise ValueError('Refusing to remove a file outside the output directory')
            path.unlink()
    return {'published': sum(len(r) for r in countries.values()), 'countries': len(countries), 'omitted_for_review': len(skipped)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=Path(os.environ.get('COMMONWEAVE_DB', str(Path(__file__).resolve().parent / 'commonweave_directory.db'))))
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'search')
    args = parser.parse_args()
    print(json.dumps(build(args.db, args.output)))


if __name__ == '__main__':
    main()
