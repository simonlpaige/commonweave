"""
record-audit-coverage.py

Reads an audit export (the JSON written by tools/audit-sample.py or the
review portal's exported verdict file) and updates data/audit-coverage.json
with verified flags for each region / state / city covered by the audit.

A region/state/city is marked verified when at least 80% (configurable in
audit-coverage.json under thresholds.verdicted_pct_required) of the orgs
covered by that scope have a non-null verdict.

Usage:
  python tools/record-audit-coverage.py path/to/audit-export.json
  python tools/record-audit-coverage.py audit/usa-mo.json --threshold 0.75
  python tools/record-audit-coverage.py audit/world.json --dry-run
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DATA_DIR = os.path.abspath(os.path.join(WORKSPACE, 'data'))
COVERAGE_PATH = os.path.abspath(os.path.join(DATA_DIR, 'audit-coverage.json'))


def load_coverage():
    if not os.path.isfile(COVERAGE_PATH):
        return {
            'schema': 1,
            'thresholds': {'verdicted_pct_required': 0.80},
            'regions': {}, 'states': {}, 'cities': {},
        }
    with open(COVERAGE_PATH, 'r', encoding='utf-8') as f:
        cov = json.load(f)
    cov.setdefault('regions', {})
    cov.setdefault('states', {})
    cov.setdefault('cities', {})
    cov.setdefault('thresholds', {'verdicted_pct_required': 0.80})
    return cov


def save_coverage(cov):
    with open(COVERAGE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cov, f, indent=2, ensure_ascii=False)


def has_verdict(org):
    """Treat any non-empty verdict / status / decision field as a verdict."""
    for k in ('verdict', 'status', 'decision', 'review_status'):
        v = org.get(k)
        if v and str(v).strip().lower() not in ('', 'none', 'pending', 'unreviewed'):
            return True
    return False


def update_scope(scope_dict, key, total, verdicted, threshold, now_iso):
    if not key:
        return False
    pct = (verdicted / total) if total else 0.0
    verified = pct >= threshold
    entry = scope_dict.get(key) or {}
    entry.update({
        'total': total,
        'verdicted': verdicted,
        'pct': round(pct, 3),
        'verified': bool(verified),
        'last_recorded_at': now_iso,
    })
    if verified and not entry.get('first_verified_at'):
        entry['first_verified_at'] = now_iso
    scope_dict[key] = entry
    return verified


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audit_path', help='Path to audit JSON export')
    ap.add_argument('--threshold', type=float, default=None,
                    help='Override pct threshold for verified (default 0.80)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    audit_path = os.path.abspath(args.audit_path)
    if not os.path.isfile(audit_path):
        print(f'ERROR: audit file not found: {audit_path}')
        sys.exit(1)

    with open(audit_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    orgs = payload.get('orgs') or payload.get('items') or []
    if not orgs:
        print('No orgs in audit file. Nothing to do.')
        return

    cov = load_coverage()
    threshold = args.threshold if args.threshold is not None else \
        cov.get('thresholds', {}).get('verdicted_pct_required', 0.80)
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Group by region (cc), state (cc/state), city (cc/state/city).
    region_totals = {}    # cc -> [total, verdicted]
    state_totals = {}     # 'CC/ST' -> [total, verdicted]
    city_totals = {}      # 'CC/ST/CITY' -> [total, verdicted]
    region_label = (payload.get('region') or '').strip().lower()
    subregion = (payload.get('subregion') or '').strip()

    for o in orgs:
        cc = (o.get('country_code') or o.get('cc') or '').strip().upper()
        st = (o.get('state_province') or o.get('st') or '').strip()
        ci = (o.get('city') or o.get('ci') or '').strip()
        v = 1 if has_verdict(o) else 0
        if cc:
            region_totals.setdefault(cc, [0, 0])
            region_totals[cc][0] += 1
            region_totals[cc][1] += v
            if st:
                k = f'{cc}/{st}'
                state_totals.setdefault(k, [0, 0])
                state_totals[k][0] += 1
                state_totals[k][1] += v
                if ci:
                    k2 = f'{cc}/{st}/{ci}'
                    city_totals.setdefault(k2, [0, 0])
                    city_totals[k2][0] += 1
                    city_totals[k2][1] += v

    newly_verified = []
    for cc, (tot, ver) in sorted(region_totals.items()):
        was = (cov['regions'].get(cc) or {}).get('verified', False)
        is_now = update_scope(cov['regions'], cc, tot, ver, threshold, now_iso)
        if is_now and not was:
            newly_verified.append(('region', cc))
    for key, (tot, ver) in sorted(state_totals.items()):
        was = (cov['states'].get(key) or {}).get('verified', False)
        is_now = update_scope(cov['states'], key, tot, ver, threshold, now_iso)
        if is_now and not was:
            newly_verified.append(('state', key))
    for key, (tot, ver) in sorted(city_totals.items()):
        was = (cov['cities'].get(key) or {}).get('verified', False)
        is_now = update_scope(cov['cities'], key, tot, ver, threshold, now_iso)
        if is_now and not was:
            newly_verified.append(('city', key))

    # Stamp top-level scope marker (helpful for review trails)
    cov.setdefault('history', []).append({
        'audit_path': os.path.relpath(audit_path, WORKSPACE).replace('\\', '/'),
        'recorded_at': now_iso,
        'region_label': region_label,
        'subregion': subregion or None,
        'orgs_seen': len(orgs),
        'threshold': threshold,
    })
    # Trim history to last 200 entries to keep the file manageable.
    cov['history'] = cov['history'][-200:]

    if args.dry_run:
        print('[dry-run] would update audit-coverage.json')
    else:
        save_coverage(cov)
        print(f'Updated {COVERAGE_PATH}')

    print(f'  regions touched : {len(region_totals)}')
    print(f'  states touched  : {len(state_totals)}')
    print(f'  cities touched  : {len(city_totals)}')
    print(f'  threshold       : {threshold:.0%}')
    if newly_verified:
        print(f'  newly verified  : {len(newly_verified)}')
        for kind, key in newly_verified[:20]:
            print(f'    + {kind:6s} {key}')
    else:
        print('  newly verified  : 0')


if __name__ == '__main__':
    main()
