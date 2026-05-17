"""
Append source coverage metadata for the Commonweave ingest pipeline.

Writes a durable JSON state file at coverage_logs/source_discovery_state.json.
The file keeps per-country/source rollups plus an append-only runs list so gaps
and retries are honest instead of trapped in terminal scrollback.
"""
import argparse
import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
COVERAGE_DIR = os.path.join(DATA_DIR, 'coverage_logs')
STATE_PATH = os.path.join(COVERAGE_DIR, 'source_discovery_state.json')


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_state(path=STATE_PATH):
    try:
        with open(path, encoding='utf-8') as f:
            state = json.load(f)
        if isinstance(state, dict):
            state.setdefault('countries', {})
            state.setdefault('runs', [])
            return state
    except FileNotFoundError:
        pass
    return {'countries': {}, 'runs': []}


def write_state(state, path=STATE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, path)


def append_coverage(country_code, country_name, source, status, found=0, inserted=0, notes='', gaps=None, extra=None):
    cc = country_code.upper()
    source = source.strip()
    ts = now_iso()
    gaps = gaps or []
    extra = extra or {}
    state = load_state()
    country = state['countries'].setdefault(cc, {
        'country_name': country_name,
        'sources': {},
        'last_updated': ts,
    })
    country['country_name'] = country_name or country.get('country_name') or cc
    country['last_updated'] = ts
    country['sources'][source] = {
        'status': status,
        'found': int(found or 0),
        'inserted': int(inserted or 0),
        'notes': notes,
        'gaps': gaps,
        'last_run_at': ts,
        **extra,
    }
    run = {
        'timestamp': ts,
        'country_code': cc,
        'country_name': country['country_name'],
        'source': source,
        'status': status,
        'found': int(found or 0),
        'inserted': int(inserted or 0),
        'notes': notes,
        'gaps': gaps,
    }
    if extra:
        run['extra'] = extra
    state['runs'].append(run)
    write_state(state)
    return run


def main(argv=None):
    ap = argparse.ArgumentParser(description='Append Commonweave coverage metadata.')
    ap.add_argument('--country-code', required=True)
    ap.add_argument('--country-name', required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--status', required=True, choices=['pending', 'running', 'complete', 'error', 'skipped', 'no_data'])
    ap.add_argument('--found', type=int, default=0)
    ap.add_argument('--inserted', type=int, default=0)
    ap.add_argument('--notes', default='')
    ap.add_argument('--gap', action='append', default=[])
    args = ap.parse_args(argv)
    run = append_coverage(
        args.country_code, args.country_name, args.source, args.status,
        found=args.found, inserted=args.inserted, notes=args.notes, gaps=args.gap,
    )
    print(json.dumps(run, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
