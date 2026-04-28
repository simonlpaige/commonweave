"""
fix_state_province.py - One-time migration: normalize US state names to 2-letter codes.

Wave B ingesters wrote full state names (e.g. "Alabama") instead of codes ("AL").
build_search_index.py then emitted orphaned US_Alabama.json files.

Run once: python data/fix_state_province.py
Safe to re-run (idempotent - only updates rows with length > 2).
"""

import sqlite3
import os
import glob
import re

STATE_MAP = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN',
    'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE',
    'nevada': 'NV', 'new hampshire': 'NH', 'new jersey': 'NJ',
    'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC',
    'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR',
    'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA',
    'west virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
    'district of columbia': 'DC', 'puerto rico': 'PR', 'virgin islands': 'VI',
    'guam': 'GU', 'american samoa': 'AS', 'northern mariana islands': 'MP',
}

DB_PATH = os.path.join(os.path.dirname(__file__), 'commonweave_directory.db')
SEARCH_DIR = os.path.join(os.path.dirname(__file__), 'search')


def fix_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    rows = c.execute(
        "SELECT id, state_province FROM organizations WHERE country_code='US' AND length(state_province) > 2"
    ).fetchall()

    print(f"Found {len(rows)} US rows with full state names")

    fixed = 0
    unresolved = []
    for row_id, sp in rows:
        code = STATE_MAP.get(sp.strip().lower())
        if code:
            c.execute('UPDATE organizations SET state_province=? WHERE id=?', (code, row_id))
            fixed += 1
        else:
            unresolved.append((row_id, sp))

    conn.commit()
    conn.close()

    print(f"Fixed: {fixed} rows")
    if unresolved:
        print(f"Could not resolve {len(unresolved)} values:")
        for row_id, sp in unresolved[:20]:
            print(f"  id={row_id} state_province={repr(sp)}")
    return fixed


def list_orphaned_search_files():
    """Find US_<FullName>.json files - orphaned by the old full-name writes."""
    if not os.path.isdir(SEARCH_DIR):
        print(f"Search dir not found: {SEARCH_DIR}")
        return []

    files = glob.glob(os.path.join(SEARCH_DIR, 'US_*.json'))
    # Orphaned = has a lowercase letter after US_ (codes are always 2-char uppercase)
    orphaned = []
    for f in files:
        basename = os.path.basename(f)
        state_part = basename[3:-5]  # strip US_ and .json
        if len(state_part) > 2 or (len(state_part) == 2 and state_part != state_part.upper()):
            orphaned.append(f)
    return orphaned


if __name__ == '__main__':
    print("=== fix_state_province.py ===\n")
    fixed = fix_db()

    orphaned = list_orphaned_search_files()
    print(f"\nOrphaned search files: {len(orphaned)}")
    for f in orphaned:
        print(f"  {os.path.basename(f)}")

    if orphaned:
        resp = input("\nDelete these orphaned files? (y/N): ").strip().lower()
        if resp == 'y':
            for f in orphaned:
                os.remove(f)
                print(f"  Deleted: {os.path.basename(f)}")
            print("Done. Re-run build_search_index.py to regenerate clean files.")
        else:
            print("Skipped deletion. Run with 'y' when ready.")
    else:
        print("No orphaned search files found.")
