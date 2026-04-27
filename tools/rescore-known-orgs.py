"""
rescore-known-orgs.py

Walks KNOWN_ALIGNED_NAMES from data/phase2_filter.py and rescores any
matching DB rows up to KNOWN_ALIGNED_MIN_SCORE. Idempotent: rows that are
already at or above the floor are left alone.

Usage:
  python tools/rescore-known-orgs.py            # apply
  python tools/rescore-known-orgs.py --dry-run  # report only
"""
import os
import sys
import sqlite3
import argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DATA_DIR = os.path.abspath(os.path.join(WORKSPACE, 'data'))
DB_PATH = os.path.abspath(os.path.join(DATA_DIR, 'commonweave_directory.db'))

# Make data/phase2_filter.py importable.
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)

from phase2_filter import (
    KNOWN_ALIGNED_NAMES,
    KNOWN_ALIGNED_MIN_SCORE,
    _normalize_known_name,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    updated = 0
    matched = 0
    skipped = 0
    examples = []

    # Pre-build LIKE clauses against name. We do a coarse LIKE pull for each
    # KNOWN name to keep the scan cheap, then re-verify against the
    # normalized form in Python.
    for canonical in sorted(KNOWN_ALIGNED_NAMES):
        like = '%' + canonical.replace(' ', '%') + '%'
        c.execute(
            "SELECT id, name, alignment_score FROM organizations "
            "WHERE LOWER(name) LIKE ? AND status='active'",
            (like,),
        )
        for row in c.fetchall():
            norm = _normalize_known_name(row['name'])
            if norm != canonical:
                continue
            matched += 1
            current = row['alignment_score'] or 0
            if current >= KNOWN_ALIGNED_MIN_SCORE:
                skipped += 1
                continue
            if not args.dry_run:
                c.execute(
                    "UPDATE organizations SET alignment_score=?, scored_pass=1 "
                    "WHERE id=?",
                    (KNOWN_ALIGNED_MIN_SCORE, row['id']),
                )
            updated += 1
            if len(examples) < 12:
                examples.append((row['id'], row['name'], current, KNOWN_ALIGNED_MIN_SCORE))

    if not args.dry_run:
        db.commit()
    db.close()

    print('=== rescore-known-orgs ===')
    print(f'  KNOWN names checked : {len(KNOWN_ALIGNED_NAMES)}')
    print(f'  DB rows matched     : {matched}')
    print(f'  Already at floor    : {skipped}')
    print(f'  Updated             : {updated}{" (dry-run)" if args.dry_run else ""}')
    if examples:
        print('  Examples:')
        for eid, name, before, after in examples:
            print(f'    [{eid}] {name}: {before} -> {after}')


if __name__ == '__main__':
    main()
