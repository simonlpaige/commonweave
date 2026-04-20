"""
Migration: add `attestations` TEXT (JSON) column to organizations, backfill
with an ingest-provenance attestation derived from existing source+date_added.

Safe: additive column, nullable, no data rewrites to existing values.
Idempotent: skips if column already present.

Run: python migrations/2026-04-20-add-attestations.py
"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\simon\.openclaw\workspace\ecolibrium\data\ecolibrium_directory.db'


def column_exists(cursor, table, col):
    cursor.execute(f'PRAGMA table_info({table})')
    return any(r[1] == col for r in cursor.fetchall())


def main():
    if not os.path.exists(DB_PATH):
        print(f'DB not found: {DB_PATH}')
        return

    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    if column_exists(c, 'organizations', 'attestations'):
        print('attestations column already present; skipping schema change.')
    else:
        print('Adding attestations column...')
        c.execute('ALTER TABLE organizations ADD COLUMN attestations TEXT')
        db.commit()
        print('  done.')

    # Backfill: any row with NULL attestations gets a single ingest-provenance
    # attestation derived from source + date_added. Signature stays null for
    # now; when W3C VC tooling is wired up this becomes cryptographically
    # verifiable without another schema change.
    c.execute("""
        SELECT id, source, date_added
        FROM organizations
        WHERE attestations IS NULL
    """)
    rows = c.fetchall()
    print(f'Backfilling {len(rows):,} rows...')
    today = datetime.utcnow().strftime('%Y-%m-%d')
    for row_id, src, added in rows:
        issuer = src or 'unknown'
        date = (added or today)[:10]
        attestation = [{
            'issuer': issuer,
            'date': date,
            'type': 'ingest-provenance',
            'signature': None,
        }]
        c.execute(
            'UPDATE organizations SET attestations = ? WHERE id = ?',
            (json.dumps(attestation), row_id),
        )
    db.commit()
    print('Backfill complete.')

    # Report
    c.execute('SELECT COUNT(*) FROM organizations WHERE attestations IS NOT NULL')
    n = c.fetchone()[0]
    print(f'Rows with attestations: {n:,}')
    db.close()


if __name__ == '__main__':
    main()
