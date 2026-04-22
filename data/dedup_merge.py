"""
Fuzzy dedup/merge pass for the Commonweave directory.

Groups orgs by normalized name + country_code. Within each group with 2+
rows: picks the best row as canonical, merges missing fields from others,
then soft-deletes the duplicates (status='merged').

New DB column: merged_into INTEGER NULL REFERENCES organizations(id)

Usage:
    python dedup_merge.py                    # run against full DB
    python dedup_merge.py --dry-run          # report counts without writing
    python dedup_merge.py --country IN       # scope to one country
    python dedup_merge.py --dry-run --country GB
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from _common import DB_PATH, TRIM_AUDIT_DIR, ensure_column, normalize_name, trim_audit_path


def run_migration(db):
    ensure_column(db, 'organizations', 'merged_into', 'INTEGER')


def score_row(row):
    """Score a row's completeness. Higher = more complete = better canonical."""
    fields = [
        row['description'], row['website'], row['email'],
        row['lat'], row['lon'], row['framework_area'],
    ]
    filled = sum(1 for f in fields if f)
    desc_len = len(row['description'] or '')
    return filled * 10 + desc_len


def merge_fields(canonical, dup, c, dry_run):
    """Copy fields from dup into canonical where canonical is missing them."""
    updates = {}
    for field in ('website', 'email', 'lat', 'lon', 'description', 'phone', 'city', 'state_province'):
        canon_val = canonical[field]
        dup_val = dup[field]
        if not canon_val and dup_val:
            updates[field] = dup_val
    if updates and not dry_run:
        set_clause = ', '.join(f'{k}=?' for k in updates)
        vals = list(updates.values()) + [canonical['id']]
        c.execute(f'UPDATE organizations SET {set_clause} WHERE id=?', vals)
    return updates


def process_country(db, cc, dry_run, log_lines):
    c = db.cursor()
    where = "WHERE status != 'merged' AND status != 'removed'"
    params = []
    if cc:
        where += ' AND country_code = ?'
        params.append(cc)

    c.execute(f'SELECT * FROM organizations {where}', params)
    rows = c.fetchall()
    if not rows:
        return 0, 0

    # Group by (normalized_name, country_code)
    groups = {}
    for row in rows:
        key = (normalize_name(row['name']), (row['country_code'] or '').upper())
        groups.setdefault(key, []).append(row)

    merged_count = 0
    groups_deduped = 0

    for (norm_name, group_cc), group in groups.items():
        if len(group) < 2:
            continue
        # Sort by completeness descending; pick best as canonical
        group_sorted = sorted(group, key=score_row, reverse=True)
        canonical = group_sorted[0]
        duplicates = group_sorted[1:]

        groups_deduped += 1
        for dup in duplicates:
            updates = merge_fields(canonical, dup, c, dry_run)
            if not dry_run:
                c.execute(
                    "UPDATE organizations SET status='merged', merged_into=? WHERE id=?",
                    (canonical['id'], dup['id'])
                )
            merged_count += 1
            log_lines.append(
                f"  merge: [{group_cc}] '{dup['name']}' (id={dup['id']}) "
                f"-> canonical '{canonical['name']}' (id={canonical['id']}) "
                f"copied={list(updates.keys())}"
            )

    if not dry_run:
        db.commit()

    return groups_deduped, merged_count


def main():
    ap = argparse.ArgumentParser(description='Fuzzy dedup/merge for Commonweave directory')
    ap.add_argument('--dry-run', action='store_true', help='Report without writing changes')
    ap.add_argument('--country', help='Limit to one country code, e.g. IN')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    run_migration(db)

    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'merged' AND status != 'removed'")
    before_total = c.fetchone()[0]
    print(f'Before: {before_total:,} active/stale orgs')

    log_lines = []
    countries = []
    if args.country:
        countries = [args.country.upper()]
    else:
        c.execute("SELECT DISTINCT country_code FROM organizations WHERE status != 'merged' AND status != 'removed'")
        countries = [r[0] for r in c.fetchall()]

    total_groups = 0
    total_merged = 0
    country_stats = []

    for cc in countries:
        groups, merged = process_country(db, cc, args.dry_run, log_lines)
        if merged:
            country_stats.append((cc, merged))
        total_groups += groups
        total_merged += merged

    c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'merged' AND status != 'removed'")
    after_total = c.fetchone()[0]
    db.close()

    mode = '[DRY RUN]' if args.dry_run else 'DONE'
    print(f'{mode}: {total_groups} duplicate groups found, {total_merged} rows soft-deleted')
    print(f'After: {after_total:,} active/stale orgs (was {before_total:,})')

    # Write audit log
    log_path = trim_audit_path('dedup')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f'# Dedup/Merge Audit - {today}\n\n')
        f.write(f'**Mode:** {"dry-run" if args.dry_run else "applied"}\n\n')
        f.write(f'| Metric | Value |\n|---|---|\n')
        f.write(f'| Before | {before_total:,} |\n')
        f.write(f'| After  | {after_total:,} |\n')
        f.write(f'| Duplicate groups | {total_groups:,} |\n')
        f.write(f'| Rows merged | {total_merged:,} |\n\n')
        if country_stats:
            f.write('## Per-country merges\n\n')
            f.write('| Country | Merged |\n|---|---|\n')
            for cc, n in sorted(country_stats, key=lambda x: -x[1]):
                f.write(f'| {cc} | {n} |\n')
            f.write('\n')
        if log_lines:
            f.write('## Merge log (first 200 entries)\n\n```\n')
            for line in log_lines[:200]:
                f.write(line + '\n')
            if len(log_lines) > 200:
                f.write(f'... and {len(log_lines) - 200} more\n')
            f.write('```\n')

    print(f'Log written: {log_path}')


if __name__ == '__main__':
    main()
