"""
build-coverage-summary.py

Reads data/audit-coverage.json (the durable tracker) and writes
audit/coverage-summary.json -- a flat, public-facing snapshot the map.html
fetches at load time. The summary is small (only the verified bits + a
generated_at stamp), so it can ship to a CDN.

Output shape:
{
  "generated_at": "2026-04-26T22:30:00Z",
  "verified_countries": ["US", "AU", ...],
  "verified_states":    ["US/MO", "AU/VIC", ...],
  "verified_cities":    ["US/MO/St. Louis", ...],
  "counts": {
    "regions": 4, "states": 12, "cities": 38
  }
}

Usage:
  python tools/build-coverage-summary.py
  python tools/build-coverage-summary.py --out audit/coverage-summary.json
"""
import os
import json
import argparse
from datetime import datetime, timezone

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DATA_DIR = os.path.abspath(os.path.join(WORKSPACE, 'data'))
AUDIT_DIR = os.path.abspath(os.path.join(WORKSPACE, 'audit'))
COVERAGE_PATH = os.path.abspath(os.path.join(DATA_DIR, 'audit-coverage.json'))
DEFAULT_OUT = os.path.abspath(os.path.join(AUDIT_DIR, 'coverage-summary.json'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    if not os.path.isfile(COVERAGE_PATH):
        print(f'ERROR: missing {COVERAGE_PATH}. Run record-audit-coverage.py first.')
        return

    with open(COVERAGE_PATH, 'r', encoding='utf-8') as f:
        cov = json.load(f)

    verified_countries = sorted(
        k for k, v in (cov.get('regions') or {}).items() if v.get('verified')
    )
    verified_states = sorted(
        k for k, v in (cov.get('states') or {}).items() if v.get('verified')
    )
    verified_cities = sorted(
        k for k, v in (cov.get('cities') or {}).items() if v.get('verified')
    )

    summary = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'verified_countries': verified_countries,
        'verified_states': verified_states,
        'verified_cities': verified_cities,
        'counts': {
            'regions': len(verified_countries),
            'states': len(verified_states),
            'cities': len(verified_cities),
        },
        'thresholds': cov.get('thresholds', {}),
    }

    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f'Wrote {out_path}')
    print(
        f'  regions={summary["counts"]["regions"]} '
        f'states={summary["counts"]["states"]} '
        f'cities={summary["counts"]["cities"]}'
    )


if __name__ == '__main__':
    main()
