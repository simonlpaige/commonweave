"""
fn-audit.py -- False Negative audit.

Measures how many trust-source orgs (which should NEVER be removed by score alone)
are currently status='removed'. These are direct false negatives in the pipeline.

Also checks the known_aligned.csv whitelist against the DB.

Usage:
  python tools/fn-audit.py
  python tools/fn-audit.py --fix   (restore removed trust-source orgs to active)
"""
import os
import sys
import csv
import argparse
import sqlite3

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(THIS_DIR, '..'))
DB_PATH = os.path.abspath(os.path.join(WORKSPACE, 'data', 'commonweave_directory.db'))
KNOWN_CSV = os.path.abspath(os.path.join(WORKSPACE, 'data', 'known_aligned.csv'))

# Sources that should never be removed by score alone
TRUST_SOURCES = {
    'ica_directory', 'ituc_affiliates', 'construction_coops', 'susy_map',
    'clt_world_map', 'nec_members', 'mutual_aid_hub', 'transition_network',
    'ripess_family', 'habitat_affiliates', 'grounded_solutions',
    'manual_curation', 'ic_directory', 'wikidata_land_trusts',
    'wikidata_unions', 'web_research',
}


def run(fix=False):
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    # -- Trust source false negatives --
    placeholders = ','.join('?' for _ in TRUST_SOURCES)
    c.execute(
        f"SELECT source, COUNT(id) FROM organizations WHERE status='removed' AND source IN ({placeholders}) GROUP BY source ORDER BY COUNT(id) DESC",
        list(TRUST_SOURCES)
    )
    rows = c.fetchall()

    c.execute(
        f"SELECT COUNT(id) FROM organizations WHERE status='removed' AND source IN ({placeholders})",
        list(TRUST_SOURCES)
    )
    total_removed_trust = c.fetchone()[0]

    c.execute(
        f"SELECT COUNT(id) FROM organizations WHERE source IN ({placeholders})",
        list(TRUST_SOURCES)
    )
    total_trust = c.fetchone()[0]

    print('=== Trust-Source False Negatives ===')
    print(f'Total trust-source orgs in DB: {total_trust:,}')
    print(f'Currently removed:             {total_removed_trust:,}')
    fn_rate = total_removed_trust / total_trust * 100 if total_trust else 0
    print(f'FN rate:                       {fn_rate:.1f}%')
    if rows:
        print('\nBreakdown by source:')
        for source, count in rows:
            print(f'  {source}: {count}')
    else:
        print('No trust-source orgs removed. FN rate is 0%.')

    if fn_rate > 1:
        print('\nWARNING: FN rate > 1%. Trust-source orgs should never be removed by score alone.')

    if fix and total_removed_trust > 0:
        print(f'\nFixing: restoring {total_removed_trust} trust-source orgs to active...')
        c.execute(
            f"UPDATE organizations SET status='active' WHERE status='removed' AND source IN ({placeholders})",
            list(TRUST_SOURCES)
        )
        db.commit()
        print('Done.')

    # -- Known aligned CSV check --
    print('\n=== KNOWN_ALIGNED_NAMES DB Check ===')
    if not os.path.exists(KNOWN_CSV):
        print(f'known_aligned.csv not found at {KNOWN_CSV}. Skipping.')
        db.close()
        return

    with open(KNOWN_CSV, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows_csv = list(reader)

    found = 0
    missing = 0
    removed = 0
    for row in rows_csv:
        name = row.get('name', '').strip()
        if not name:
            continue
        c.execute(
            "SELECT status FROM organizations WHERE lower(name) = lower(?) LIMIT 1",
            (name,)
        )
        result = c.fetchone()
        if result is None:
            print(f'  NOT IN DB: {name}')
            missing += 1
        elif result[0] == 'removed':
            print(f'  REMOVED:   {name}')
            removed += 1
            if fix:
                c.execute(
                    "UPDATE organizations SET status='active', alignment_score=7 WHERE lower(name)=lower(?)",
                    (name,)
                )
        else:
            found += 1

    if fix:
        db.commit()

    print(f'\nKNOWN_ALIGNED_NAMES: {found} found active, {removed} removed, {missing} not in DB at all.')
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Audit false negatives in the pipeline')
    parser.add_argument('--fix', action='store_true', help='Restore removed trust-source orgs to active')
    args = parser.parse_args()
    run(fix=args.fix)
