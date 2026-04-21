# -*- coding: utf-8 -*-
"""
Migration 001: alignment_score_v2

This script keeps the old score in alignment_score_legacy, recomputes
alignment_score_v2, and audits disagreements.

Default mode is safe:
  - recompute and store v2 scores
  - export the legacy > v2 cohort to an audit CSV
  - report whether the DB looks ratcheted

Destructive mode requires --rebuild-from-v2:
  - overwrite alignment_score from alignment_score_v2
"""

import argparse
import csv
import os
import sqlite3
import sys
from datetime import datetime

# Allow import of phase2_filter / i18n_terms from the data directory.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(_THIS_DIR)
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

from phase2_filter import score_org  # noqa: E402

DB_PATH = os.path.join(_DATA_DIR, "ecolibrium_directory.db")
AUDIT_DIR = os.path.join(_DATA_DIR, "audit")
BATCH_SIZE = 2000


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild-from-v2", action="store_true")
    return parser.parse_args()


def _col_names(cursor):
    cursor.execute("PRAGMA table_info(organizations)")
    return {row[1] for row in cursor.fetchall()}


def _score_distribution(cursor, col, label):
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


def ensure_columns(cursor):
    existing_cols = _col_names(cursor)
    if "alignment_score_legacy" not in existing_cols:
        cursor.execute("ALTER TABLE organizations ADD COLUMN alignment_score_legacy INTEGER")
    if "alignment_score_v2" not in existing_cols:
        cursor.execute("ALTER TABLE organizations ADD COLUMN alignment_score_v2 INTEGER")


def populate_scores(cursor):
    cursor.execute("SELECT COUNT(*) FROM organizations WHERE status = 'active'")
    active_count = cursor.fetchone()[0]
    print(f"\nActive orgs to process: {active_count:,}")
    if active_count == 0:
        raise RuntimeError("0 active orgs found")

    processed = 0
    last_id = 0
    while True:
        cursor.execute("""
            SELECT id, name, description, alignment_score, alignment_score_legacy
            FROM organizations
            WHERE status = 'active' AND id > ?
            ORDER BY id
            LIMIT ?
        """, (last_id, BATCH_SIZE))
        rows = cursor.fetchall()
        if not rows:
            break

        updates = []
        for org_id, name, desc, current_score, legacy_score in rows:
            legacy_value = legacy_score if legacy_score is not None else current_score
            updates.append((legacy_value, score_org(name, desc), org_id))

        cursor.executemany("""
            UPDATE organizations
            SET alignment_score_legacy = ?,
                alignment_score_v2 = ?
            WHERE id = ?
        """, updates)
        processed += len(rows)
        last_id = rows[-1][0]
        print(f"  ...{processed:,}/{active_count:,}", flush=True)


def export_disagreement_cohort(cursor):
    os.makedirs(AUDIT_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    audit_path = os.path.join(AUDIT_DIR, f"score_v2_disagreement_{timestamp}.csv")
    cursor.execute("""
        SELECT id, name, alignment_score, alignment_score_legacy, alignment_score_v2,
               country_code, source, source_id
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_legacy IS NOT NULL
          AND alignment_score_v2 IS NOT NULL
          AND alignment_score_legacy > alignment_score_v2
        ORDER BY (alignment_score_legacy - alignment_score_v2) DESC, id ASC
    """)
    rows = cursor.fetchall()
    with open(audit_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "name", "alignment_score_current", "alignment_score_legacy",
            "alignment_score_v2", "country_code", "source", "source_id"
        ])
        writer.writerows(rows)
    return audit_path, len(rows)


def count_ratcheted_rows(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_legacy IS NOT NULL
          AND alignment_score_v2 IS NOT NULL
          AND alignment_score = MAX(alignment_score_legacy, alignment_score_v2)
          AND alignment_score != alignment_score_v2
    """)
    return cursor.fetchone()[0]


def rebuild_alignment_score(cursor):
    cursor.execute("""
        UPDATE organizations
        SET alignment_score = alignment_score_v2
        WHERE status = 'active'
          AND alignment_score_v2 IS NOT NULL
    """)
    return cursor.rowcount


def run():
    args = parse_args()
    print("=== Migration 001: alignment_score_v2 ===")
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    ensure_columns(c)
    db.commit()

    _score_distribution(c, "alignment_score", "BEFORE - alignment_score")

    print("\nPopulating alignment_score_legacy and alignment_score_v2...")
    populate_scores(c)
    db.commit()

    c.execute("""
        SELECT COUNT(*) FROM organizations
        WHERE status = 'active' AND alignment_score_v2 IS NULL
    """)
    null_v2 = c.fetchone()[0]
    if null_v2:
        db.close()
        raise RuntimeError(f"{null_v2:,} active orgs still have NULL alignment_score_v2")

    audit_path, disagreement_count = export_disagreement_cohort(c)
    ratcheted_count = count_ratcheted_rows(c)
    print(f"\nAudit CSV: {audit_path}")
    print(f"legacy > v2 cohort: {disagreement_count:,}")
    print(f"Rows that look ratcheted right now: {ratcheted_count:,}")

    if not args.rebuild_from_v2:
        print("\nDry run only. alignment_score was left untouched.")
        if ratcheted_count:
            print("This DB still looks ratcheted.")
        print("Run again with --rebuild-from-v2 if you want alignment_score rebuilt from v2.")
        db.close()
        return

    print("\nRebuilding alignment_score directly from alignment_score_v2...")
    rows_touched = rebuild_alignment_score(c)
    db.commit()
    print(f"alignment_score updated for {rows_touched:,} active orgs.")

    _score_distribution(c, "alignment_score", "AFTER - alignment_score")
    _score_distribution(c, "alignment_score_v2", "AFTER - alignment_score_v2")

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
    print(f"  legacy > v2  (audit cohort)          : {row[1]:>6,}")
    print(f"  v2 == legacy (unchanged)             : {row[2]:>6,}")

    db.close()
    print("\nMigration 001 complete.\n")


if __name__ == "__main__":
    run()
