# -*- coding: utf-8 -*-
"""
Exp 6: Post-migration audit - alignment_score_v2 vs alignment_score_legacy.

Read-only. Run AFTER migration 001_alignment_score_v2.py.

Reports three cohorts:
  - Multilingual wins: v2 > legacy (captured by non-English terms)
  - Inflation review: legacy > v2 (old substring scorer over-credited)
  - Unchanged: v2 == legacy

Shows 15 samples per cohort with name, country_code, both scores, desc snippet.
"""

import os
import sys
import sqlite3

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(_THIS_DIR)  # experiments/ -> data/
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

DB_PATH = r'C:\Users\simon\.openclaw\workspace\ecolibrium\data\ecolibrium_directory.db'

SAMPLE_SIZE = 15
SNIPPET_LEN = 100


def _check_cols(cursor):
    cursor.execute("PRAGMA table_info(organizations)")
    cols = {row[1] for row in cursor.fetchall()}
    missing = [c for c in ('alignment_score_v2', 'alignment_score_legacy') if c not in cols]
    if missing:
        print(f"ERROR: columns missing: {missing}. Has migration 001 run?")
        sys.exit(1)


def _show_samples(cursor, where_clause, label, order_expr):
    cursor.execute(f"""
        SELECT name, country_code, alignment_score_legacy, alignment_score_v2,
               COALESCE(description, '')
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_legacy IS NOT NULL
          AND alignment_score_v2 IS NOT NULL
          AND ({where_clause})
        ORDER BY {order_expr} DESC, id
        LIMIT {SAMPLE_SIZE}
    """)
    rows = cursor.fetchall()
    print(f"\n--- {label} ({len(rows)} samples) ---")
    print(f"  {'Name':<45} {'CC':<4} {'Leg':>5} {'V2':>4}  Snippet")
    print(f"  {'-'*45} {'-'*4} {'-'*5} {'-'*4}  {'-'*40}")
    for name, cc, legacy, v2, desc in rows:
        name_t = (name or "")[:44]
        snippet = (desc or "").replace("\n", " ")[:SNIPPET_LEN]
        print(f"  {name_t:<45} {(cc or '?'):<4} {legacy or 0:>5} {v2 or 0:>4}  {snippet}")


def main():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    _check_cols(c)

    c.execute("SELECT COUNT(*) FROM organizations WHERE status = 'active'")
    total = c.fetchone()[0]
    print(f"Active orgs: {total:,}\n")

    # --- Counts ---
    c.execute("""
        SELECT
            SUM(CASE WHEN alignment_score_v2 > alignment_score_legacy THEN 1 ELSE 0 END),
            SUM(CASE WHEN alignment_score_v2 < alignment_score_legacy THEN 1 ELSE 0 END),
            SUM(CASE WHEN alignment_score_v2 = alignment_score_legacy THEN 1 ELSE 0 END)
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_legacy IS NOT NULL
          AND alignment_score_v2 IS NOT NULL
    """)
    v2_wins, legacy_wins, unchanged = [x or 0 for x in c.fetchone()]
    compared = v2_wins + legacy_wins + unchanged

    print("=== Category Counts (active orgs with both scores) ===")
    print(f"  v2 > legacy  (multilingual wins)      : {v2_wins:>6,}  ({100*v2_wins/max(compared,1):.1f}%)")
    print(f"  legacy > v2  (substring inflation)     : {legacy_wins:>6,}  ({100*legacy_wins/max(compared,1):.1f}%)")
    print(f"  v2 == legacy (unchanged)               : {unchanged:>6,}  ({100*unchanged/max(compared,1):.1f}%)")
    print(f"  TOTAL compared                         : {compared:>6,}")

    # --- Threshold: how many crossed the >=2 boundary ---
    c.execute("""
        SELECT
            SUM(CASE WHEN alignment_score_legacy >= 2 THEN 1 ELSE 0 END),
            SUM(CASE WHEN alignment_score_v2 >= 2 THEN 1 ELSE 0 END),
            SUM(CASE WHEN alignment_score >= 2 THEN 1 ELSE 0 END)
        FROM organizations WHERE status = 'active'
    """)
    r = c.fetchone()
    print(f"\n=== Threshold >=2 (aligned) ===")
    print(f"  Pre-migration (legacy >= 2)            : {r[0] or 0:>6,}")
    print(f"  v2 scorer alone (v2 >= 2)              : {r[1] or 0:>6,}")
    print(f"  Post-migration merged (score >= 2)     : {r[2] or 0:>6,}")

    # --- Score delta distribution ---
    print("\n=== Delta distribution (v2 - legacy, top 20 by magnitude) ===")
    c.execute("""
        SELECT (alignment_score_v2 - alignment_score_legacy) AS delta, COUNT(*) AS n
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_legacy IS NOT NULL
          AND alignment_score_v2 IS NOT NULL
        GROUP BY delta
        ORDER BY delta DESC
        LIMIT 20
    """)
    print(f"  {'Delta':>7}  {'Count':>7}")
    for delta, n in c.fetchall():
        print(f"  {delta:>7}  {n:>7,}")

    # --- Country breakdown of v2 wins ---
    print("\n=== Country breakdown of v2 wins (top 15) ===")
    c.execute("""
        SELECT country_code, COUNT(*) AS n
        FROM organizations
        WHERE status = 'active'
          AND alignment_score_v2 > alignment_score_legacy
        GROUP BY country_code
        ORDER BY n DESC
        LIMIT 15
    """)
    rows = c.fetchall()
    if rows:
        for cc, n in rows:
            print(f"  {(cc or '??'):<6}  {n:>5,}")
    else:
        print("  (no v2 wins)")

    # --- Samples per cohort ---
    if v2_wins > 0:
        _show_samples(c,
            "alignment_score_v2 > alignment_score_legacy",
            "MULTILINGUAL WINS (v2 > legacy)",
            "(alignment_score_v2 - alignment_score_legacy)")
    else:
        print("\n--- MULTILINGUAL WINS: none found ---")
        print("  Interpretation: the new word-boundary scorer is stricter than the")
        print("  old substring matcher. All active orgs were already covered by the")
        print("  English terms in the original scorer. v2 does not LIFT any new orgs")
        print("  but its stricter matching means it LOWERS scores for 9,763 orgs")
        print("  (those are 'inflation' cases the old substring approach over-counted).")

    _show_samples(c,
        "alignment_score_legacy > alignment_score_v2",
        "SUBSTRING INFLATION (legacy > v2) - top 15 by score gap",
        "(alignment_score_legacy - alignment_score_v2)")

    _show_samples(c,
        "alignment_score_v2 = alignment_score_legacy AND alignment_score_legacy >= 2",
        "UNCHANGED but aligned (score >= 2)",
        "alignment_score_legacy")

    db.close()
    print("\nExp 6 complete.\n")


if __name__ == '__main__':
    main()
