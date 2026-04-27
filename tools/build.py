"""
build.py -- single-command rebuild for the Commonweave site/data layer.

Steps (in order):
  1. data/build_search_index.py
  2. data/build_map_v2.py
  3. tools/wiki-update.py        (skip with --skip-wiki)
  4. tools/gen-audit-data.py --region usa
  5. tools/gen-audit-data.py --region india
  6. tools/gen-audit-data.py --region latam
     (skip 4-6 with --skip-audit)
  7. Write data/generated/MANIFEST.json with built_at, org_count,
     country_count, geocoded_count, files_generated, db_path.

Each step prints its wall-clock duration. A failing step is logged as a
warning but the build continues, so an audit slowdown does not block a
search-index publish.

Usage:
  python tools/build.py
  python tools/build.py --skip-wiki --skip-audit
  python tools/build.py --dry-run
"""
import os
import sys
import argparse
import sqlite3
import subprocess
import time
import json
from datetime import datetime, timezone

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DATA_DIR = os.path.abspath(os.path.join(WORKSPACE, 'data'))
TOOLS_DIR = THIS_DIR
DB_PATH = os.path.abspath(os.path.join(DATA_DIR, 'commonweave_directory.db'))
GENERATED_DIR = os.path.abspath(os.path.join(DATA_DIR, 'generated'))


def fmt_secs(secs):
    if secs < 1:
        return f'{secs * 1000:.0f}ms'
    if secs < 60:
        return f'{secs:.1f}s'
    m, s = divmod(secs, 60)
    return f'{int(m)}m{int(s):02d}s'


def run_step(label, args, dry_run=False, results=None):
    """Run a python sub-script. Never abort on failure, just warn."""
    print(f'\n>>> [{label}] {" ".join(args)}')
    if dry_run:
        print('    (dry-run, skipped)')
        if results is not None:
            results.append({'step': label, 'status': 'dry-run', 'duration_s': 0.0})
        return 0
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable] + args,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        elapsed = time.time() - t0
        # Stream a compact tail of stdout so build logs stay readable.
        out = (proc.stdout or '').rstrip()
        err = (proc.stderr or '').rstrip()
        if out:
            tail = '\n'.join(out.splitlines()[-12:])
            print(tail)
        if proc.returncode != 0:
            print(f'    [WARN] {label} exited {proc.returncode} (continuing)')
            if err:
                print('    stderr tail:')
                print('\n'.join(err.splitlines()[-8:]))
            status = 'fail'
        else:
            status = 'ok'
        print(f'    [{label}] done in {fmt_secs(elapsed)}')
    except Exception as exc:
        elapsed = time.time() - t0
        print(f'    [WARN] {label} crashed: {exc} (continuing)')
        status = 'crash'
    if results is not None:
        results.append({'step': label, 'status': status, 'duration_s': round(elapsed, 2)})
    return 0


def db_stats():
    """Return (org_count, country_count, geocoded_count) or zeros if DB unreadable."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM organizations WHERE status='active'")
        org_count = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(DISTINCT country_code) FROM organizations "
            "WHERE status='active' AND country_code != ''"
        )
        country_count = c.fetchone()[0]
        c.execute(
            "SELECT COUNT(*) FROM organizations "
            "WHERE status='active' AND lat IS NOT NULL AND lon IS NOT NULL"
        )
        geocoded_count = c.fetchone()[0]
        conn.close()
        return org_count, country_count, geocoded_count
    except Exception as exc:
        print(f'    [WARN] db_stats failed: {exc}')
        return 0, 0, 0


def list_generated_files():
    """Snapshot of search/, map/, audit/ output trees."""
    targets = [
        os.path.join(DATA_DIR, 'search'),
        os.path.join(DATA_DIR, 'map'),
        os.path.abspath(os.path.join(WORKSPACE, 'audit')),
    ]
    files = []
    for root in targets:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.startswith('.'):
                    continue
                full = os.path.abspath(os.path.join(dirpath, fn))
                rel = os.path.relpath(full, WORKSPACE).replace('\\', '/')
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = 0
                files.append({'path': rel, 'bytes': size})
    files.sort(key=lambda f: f['path'])
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-wiki', action='store_true')
    ap.add_argument('--skip-audit', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    overall_t0 = time.time()
    results = []

    print(f'== Commonweave build ==')
    print(f'  workspace : {WORKSPACE}')
    print(f'  db        : {DB_PATH}')
    print(f'  dry-run   : {args.dry_run}')

    # 1. search index
    run_step(
        'build_search_index',
        [os.path.abspath(os.path.join(DATA_DIR, 'build_search_index.py'))],
        dry_run=args.dry_run,
        results=results,
    )

    # 2. map v2
    run_step(
        'build_map_v2',
        [os.path.abspath(os.path.join(DATA_DIR, 'build_map_v2.py'))],
        dry_run=args.dry_run,
        results=results,
    )

    # 3. wiki update
    if args.skip_wiki:
        print('\n>>> [wiki-update] skipped (--skip-wiki)')
        results.append({'step': 'wiki-update', 'status': 'skipped', 'duration_s': 0.0})
    else:
        run_step(
            'wiki-update',
            [os.path.abspath(os.path.join(TOOLS_DIR, 'wiki-update.py'))],
            dry_run=args.dry_run,
            results=results,
        )

    # 4-6. audit data per region
    if args.skip_audit:
        print('\n>>> [gen-audit-data] skipped (--skip-audit)')
        for region in ('usa', 'india', 'latam'):
            results.append({
                'step': f'gen-audit-{region}',
                'status': 'skipped',
                'duration_s': 0.0,
            })
    else:
        for region in ('usa', 'india', 'latam'):
            run_step(
                f'gen-audit-{region}',
                [os.path.abspath(os.path.join(TOOLS_DIR, 'gen-audit-data.py')),
                 '--region', region],
                dry_run=args.dry_run,
                results=results,
            )

    # 7. manifest
    org_count, country_count, geocoded_count = db_stats()
    files = list_generated_files()
    manifest = {
        'built_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'org_count': org_count,
        'country_count': country_count,
        'geocoded_count': geocoded_count,
        'files_generated': files,
        'db_path': DB_PATH,
        'steps': results,
        'flags': {
            'skip_wiki': args.skip_wiki,
            'skip_audit': args.skip_audit,
            'dry_run': args.dry_run,
        },
    }

    if args.dry_run:
        print('\n>>> [manifest] dry-run, not writing')
    else:
        os.makedirs(GENERATED_DIR, exist_ok=True)
        manifest_path = os.path.abspath(os.path.join(GENERATED_DIR, 'MANIFEST.json'))
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        print(f'\n>>> [manifest] wrote {manifest_path}')
        print(
            f'    orgs={org_count:,}  countries={country_count}  '
            f'geocoded={geocoded_count:,}  files={len(files)}'
        )

    print(f'\n== build complete in {fmt_secs(time.time() - overall_t0)} ==')
    print('Step summary:')
    for r in results:
        print(f'  {r["step"]:24s} {r["status"]:8s} {fmt_secs(r["duration_s"])}')


if __name__ == '__main__':
    main()
