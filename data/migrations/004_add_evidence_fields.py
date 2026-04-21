"""
Migration 004: add evidence fields for web-researched organizations.
"""

import os
import sqlite3

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(_THIS_DIR)
DB_PATH = os.path.join(_DATA_DIR, "ecolibrium_directory.db")


def add_column(cursor, name, sql_type):
    cursor.execute("PRAGMA table_info(organizations)")
    existing = {row[1] for row in cursor.fetchall()}
    if name in existing:
        return
    cursor.execute(f"ALTER TABLE organizations ADD COLUMN {name} {sql_type}")


def run():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    add_column(c, "evidence_url", "TEXT")
    add_column(c, "evidence_quote", "TEXT")
    add_column(c, "evidence_fetched_at", "TEXT")
    db.commit()
    db.close()
    print("Added evidence_url, evidence_quote, and evidence_fetched_at")


if __name__ == "__main__":
    run()
