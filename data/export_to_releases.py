"""
Export the Commonweave directory database to release files in commonweave/releases/.

Why this exists:
- The SQLite DB is a build artifact and stays gitignored.
- People should still be able to download the directory without rebuilding it.
- Flat files (CSV + JSON) play nice with grep, spreadsheets, and notebooks.

What it produces (overwrites every run):
- releases/organizations.csv         all aligned orgs, one row per org
- releases/organizations.json        same data, JSON array
- releases/by-country/<ISO2>.csv     country splits
- releases/by-source/<source>.csv    source splits
- releases/MANIFEST.json             counts + generated-at + schema version + git hash

Run from the workspace root or from commonweave/data/. It auto-locates the DB.

Usage:
    python commonweave/data/export_to_releases.py
    python commonweave/data/export_to_releases.py --include-unaligned
    python commonweave/data/export_to_releases.py --min-score 3
"""

import argparse
import csv
import gzip
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Columns we expose in the public export. Internal scoring/audit fields are
# omitted to keep the schema stable and easy to read.
PUBLIC_COLUMNS = [
    "id",
    "name",
    "country_code",
    "country_name",
    "state_province",
    "city",
    "registration_id",
    "registration_type",
    "description",
    "website",
    "email",
    "phone",
    "framework_area",
    "ntee_code",
    "icnpo_code",
    "source",
    "source_id",
    "last_filing_year",
    "annual_revenue",
    "employee_count",
    "lat",
    "lon",
    "model_type",
    "tags",
    "alignment_score",
    "evidence_url",
    "evidence_quote",
    "last_verified_at",
]

SCHEMA_VERSION = "1.0.0"


def find_db():
    here = Path(__file__).resolve().parent
    candidate = here / "commonweave_directory.db"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Database not found at {candidate}")


def find_releases_dir(db_path):
    # commonweave/data/foo.db -> commonweave/releases/
    return db_path.parent.parent / "releases"


def safe_filename(s):
    s = (s or "unknown").strip()
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
    return s[:80] or "unknown"


def fetch_rows(db_path, min_score):
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    placeholders = ", ".join(PUBLIC_COLUMNS)
    where = []
    params = []
    if min_score is not None:
        # alignment_score is the v2 score per recent migrations.
        where.append("(alignment_score IS NOT NULL AND alignment_score >= ?)")
        params.append(min_score)
    # Filter merged-out duplicates.
    where.append("(merged_into IS NULL OR merged_into = 0)")

    sql = f"SELECT {placeholders} FROM organizations"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY country_code, name"
    cur.execute(sql, params)
    for row in cur:
        yield dict(row)
    db.close()


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=PUBLIC_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_json(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2, default=str)


def get_git_hash(repo_dir):
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(description="Export Commonweave directory to releases/")
    ap.add_argument("--min-score", type=int, default=2,
                    help="minimum alignment_score to include (default 2 = aligned)")
    ap.add_argument("--include-unaligned", action="store_true",
                    help="include all rows regardless of alignment_score")
    ap.add_argument("--by-country", action="store_true", default=True,
                    help="generate per-country split files (default on)")
    ap.add_argument("--by-source", action="store_true", default=True,
                    help="generate per-source split files (default on)")
    args = ap.parse_args()

    min_score = None if args.include_unaligned else args.min_score

    db_path = find_db()
    releases = find_releases_dir(db_path)
    releases.mkdir(parents=True, exist_ok=True)

    print(f"Reading from: {db_path}")
    print(f"Writing to:   {releases}")
    print(f"Filter:       alignment_score >= {min_score}" if min_score else "Filter: include all")

    all_rows = list(fetch_rows(db_path, min_score))
    print(f"Rows to export: {len(all_rows)}")

    # Top-level files. We write to temp paths then gzip, because the full
    # CSV/JSON together are ~32MB and bloat clones. Splits stay uncompressed
    # so people can browse them on GitHub directly.
    full_csv = releases / "organizations.csv"
    full_json = releases / "organizations.json"
    write_csv(all_rows, full_csv)
    write_json(all_rows, full_json)
    for p in (full_csv, full_json):
        gz = p.with_suffix(p.suffix + ".gz")
        with p.open("rb") as src, gzip.open(gz, "wb", compresslevel=9) as dst:
            shutil.copyfileobj(src, dst)
        p.unlink()
        print(f"  gzipped {p.name} -> {gz.name}")

    # By country.
    if args.by_country:
        by_country = {}
        for r in all_rows:
            cc = (r.get("country_code") or "ZZ").upper()
            by_country.setdefault(cc, []).append(r)
        bc_dir = releases / "by-country"
        # Wipe stale country files so disappearing countries don't leave junk.
        if bc_dir.exists():
            for old in bc_dir.glob("*.csv"):
                old.unlink()
        for cc, rows in by_country.items():
            write_csv(rows, bc_dir / f"{safe_filename(cc)}.csv")
        print(f"Wrote {len(by_country)} country files to {bc_dir}")

    # By source.
    if args.by_source:
        by_source = {}
        for r in all_rows:
            src = r.get("source") or "unknown"
            by_source.setdefault(src, []).append(r)
        bs_dir = releases / "by-source"
        if bs_dir.exists():
            for old in bs_dir.glob("*.csv"):
                old.unlink()
        for src, rows in by_source.items():
            write_csv(rows, bs_dir / f"{safe_filename(src)}.csv")
        print(f"Wrote {len(by_source)} source files to {bs_dir}")

    # Manifest.
    repo_dir = db_path.parent.parent  # commonweave/
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(all_rows),
        "country_count": len({(r.get("country_code") or "").upper() for r in all_rows}),
        "source_count": len({r.get("source") or "" for r in all_rows}),
        "min_alignment_score": min_score,
        "git_commit": get_git_hash(repo_dir),
        "columns": PUBLIC_COLUMNS,
        "files": {
            "organizations.csv.gz": "all rows, one per org (gzipped CSV)",
            "organizations.json.gz": "all rows, JSON array (gzipped)",
            "by-country/<ISO2>.csv": "rows split by country_code (uncompressed)",
            "by-source/<source>.csv": "rows split by source (uncompressed)",
        },
        "notes": [
            "Built from commonweave/data/commonweave_directory.db.",
            "DB itself stays gitignored; this folder is the public artifact.",
            "Regenerate with: python commonweave/data/export_to_releases.py",
        ],
    }
    with (releases / "MANIFEST.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Manifest written. {manifest['row_count']} rows across {manifest['country_count']} countries.")


if __name__ == "__main__":
    main()
