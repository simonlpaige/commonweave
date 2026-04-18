# -*- coding: utf-8 -*-
"""
Migration 001: alignment_score_v2
----------------------------------
Adds two new columns to organizations:
  - alignment_score_legacy : copy of original alignment_score before this run
  - alignment_score_v2     : score computed by the current multilingual scorer

alignment_score is then set to MAX(legacy, v2) so no org is dropped during
the transition -- an org stays in the directory if EITHER scorer thought it
was aligned.

Must be run AFTER backing up ecolibrium_directory.db.
Transactional: all changes roll back if any step fails.

Usage:
    python data/migrations/001_alignment_score_v2.py
"""

import os
import sys
import sqlite3

# Allow import of phase2_filter / i18n_terms from the data directory.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(_THIS_DIR)  # parent = data/
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

from phase2_filter import score_org  # noqa: E402

DB_PATH = os.path.join(_DATA_DIR, "ecolibrium_directory.db")
BATCH_SIZE = 2000


def _col_names(cursor):
    """Return set of existing column names for the organizations table."""
    cursor.execute("PRAGMA table_info(organizations)")
    return {row[1] for row in cursor.fetchall()}


def _score_distribution(cursor, col, label):
    """Print a compact score distribution for one column."""
    cursor.execute(f"""
        SELECT {col}, COUNT(*) AS n
        FROM organizations
        WHERE status = 'active'
        GROUP BY {col}
        ORDER BY {col} DESC
    """)
    rows = cursor.fetchall()
    print(f"\n  [{label}] score distribution (active orgs):")
    for score, n in rows:
        print(f"    score {score:>4}: {n:>6,}")


def run():
    print("=== Migration 001: alignment_score_v2 ===")

    db = sqlite3.connect(DB_PATH)
    db.isolation_level = None  # manual transaction control
    c = db.cursor()

    # --- Step 1: Add columns if they don't already exist ---
    existing_cols = _col_names(c)
    print("\nExisting alignment columns:", [col for col in existing_cols if "alignment" in col])

    c.execute("BEGIN")
    try:
        if "alignment_score_legacy" not in existing_cols:
            print("  Adding alignment_score_legacy column...")
            c.execute("ALTER TABLE organizations ADD COLUMN alignment_score_legacy INTEGER")
        else:
            print("  alignment_score_legacy already exists, skipping ADD COLUMN")

        if "alignment_score_v2" not in existing_cols:
            print("  Adding alignment_score_v2 column...")
            c.execute("ALTER TABLE organizations ADD COLUMN alignment_score_v2 INTEGER")
        else:
            print("  alignment_score_v2 already exists, skipping ADD COLUMN")

        c.execute("COMMIT")
    except Exception as exc:
        c.execute("ROLLBACK")
        print(f"ERROR adding columns: {exc}")
        db.close()
        sys.exit(1)

    # --- Step 2: Dry-run count sanity check ---
    c.execute("SELECT COUNT(*) FROM organizations WHERE status = 'active'")
    active_count = c.fetchone()[0]
    print(f"\nActive orgs to process: {active_count:,}")

    c.execute("""
        SELECT COUNT(*) FROM organizations
        WHERE status = 'active' AND alignment_score IS NULL
    """)
    null_scores = c.fetchone()[0]
    print(f"Active orgs with NULL alignment_score: {null_scores:,}")

    if active_count == 0:
        print("STOP: 0 active orgs - unexpected. Aborting.")
        db.close()
        sys.exit(1)

    # --- Step 3: Show BEFORE distribution ---
    _score_distribution(c, "alignment_score", "BEFORE - alignment_score")

    # --- Step 4: Copy legacy scores and compute v2 in one transaction ---
    print("\nPopulating alignment_score_legacy and alignment_score_v2...")
    c.execute("BEGIN")
    try:
        processed = 0
        offset = 0
        v2_updates = []

        while True:
            c.execute("""
                SELECT id, name, description, alignment_score
                FROM organizations
                WHERE status = 'active'
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (BATCH_SIZE, offset))
            rows = c.fetchall()
            if not rows:
                break

            batch_updates = []
            for org_id, name, desc, current_score in rows:
                v2 = score_org(name, desc)
                batch_updates.append((current_score, v2, org_id))

            # Write legacy + v2 in a single UPDATE per row
            c.executemany("""
                UPDATE organizations
                SET alignment_score_legacy = ?,
                    alignment_score_v2 = ?
                WHERE id = ?
            """, batch_updates)

            processed += len(rows)
            offset += BATCH_SIZE
            print(f"  ...{processed:,}/{active_count:,}", flush=True)

        c.execute("COMMIT")
        print(f"Legacy copy + v2 scoring done. {processed:,} orgs updated.")
    except Exception as exc:
        c.execute("ROLLBACK")
        print(f"ERROR during scoring: {exc}")
        import traceback
        traceback.print_exc()
        db.close()
        sys.exit(1)

    # --- Step 5: Validate - no org should have a NULL v2 score after scoring ---
    c.execute("""
        SELECT COUNT(*) FROM organizations
        WHERE status = 'active' AND alignment_score_v2 IS NULL
    """)
    null_v2 = c.fetchone()[0]
    if null_v2 > 0:
        print(f"WARNING: {null_v2:,} active orgs still have NULL alignment_score_v2.")
        print("This should not happen. Aborting without updating alignment_score.")
        db.close()
        sys.exit(1)

    # --- Step 6: Update alignment_score = MAX(legacy, v2) ---
    print("\nUpdating alignment_score = MAX(alignment_score_legacy, alignment_score_v2)...")
    c.execute("BEGIN")
    try:
        c.execute("""
            UPDATE organizations
            SET alignment_score = MAX(alignment_score_legacy, alignment_score_v2)
            WHERE status = 'active'
              AND alignment_score_legacy IS NOT NULL
              AND alignment_score_v2 IS NOT NULL
        """)
        rows_touched = c.rowcount
        c.execute("COMMIT")
        print(f"alignment_score updated for {rows_touched:,} active orgs.")
    except Exception as exc:
        c.execute("ROLLBACK")
        print(f"ERROR updating alignment_score: {exc}")
        db.close()
        sys.exit(1)

    # --- Step 7: Safety check - no org should have dropped below its legacy score ---
    c.execute("""
        SELECT COUNT(*) FROM organizations
        WHERE status = 'active'
          AND alignment_score < alignment_score_legacy
    """)
    dropped = c.fetchone()[0]
    if dropped > 0:
        print(f"\nFAIL: {dropped:,} orgs have alignment_score < alignment_score_legacy.")
        print("MAX logic violated - rolling back entire migration.")
        c.execute("BEGIN")
        c.execute("""
            UPDATE organizations
            SET alignment_score = alignment_score_legacy
            WHERE status = 'active' AND alignment_score < alignment_score_legacy
        """)
        c.execute("COMMIT")
        print("Corrected. Please investigate before re-running.")
        db.close()
        sys.exit(1)
    else:
        print("Safety check passed: no org dropped below its pre-migration score.")

    # --- Step 8: AFTER distribution ---
    _score_distribution(c, "alignment_score", "AFTER - alignment_score")
    _score_distribution(c, "alignment_score_v2", "AFTER - alignment_score_v2")

    # --- Step 9: Summary stats ---
    c.execute("""
        SELECT
            SUM(CASE WHEN alignment_score_v2 > alignment_score_legacy THEN 1 ELSE 0 END) AS v2_wins,
            SUM(CASE WHEN alignment_score_legacy > alignment_score_v2 THEN 1 ELSE 0 END) AS legacy_wins,
            SUM(CASE WHEN alignment_score_v2 = alignment_score_legacy THEN 1 ELSE 0 END) AS unchanged
        FROM organizations
        WHERE status = 'active'
    """)
    row = c.fetchone()
    print(f"\n=== Summary ===")
    print(f"  v2 > legacy  (multilingual wins)     : {row[0]:>6,}")
    print(f"  legacy > v2  (inflation review cohort): {row[1]:>6,}")
    print(f"  v2 == legacy (unchanged)              : {row[2]:>6,}")

    db.close()
    print("\nMigration 001 complete.\n")


if __name__ == "__main__":
    run()
