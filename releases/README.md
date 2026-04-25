# Commonweave Directory: Release Artifacts

This folder is the public-facing snapshot of the Commonweave directory database.
Anyone can grab a CSV or JSON here without rebuilding the database from source.

## Files

| File | What it is |
|------|------------|
| `organizations.csv.gz` | All aligned organizations, one row per org. Gzipped (~6MB) for fast cloning. `gunzip` to use. |
| `organizations.json.gz` | Same data as a JSON array, gzipped. |
| `by-country/<ISO2>.csv` | Country splits, uncompressed so you can browse them on GitHub directly. |
| `by-source/<name>.csv` | Source splits (IRS, UK Charity Commission, Wikidata, etc.), uncompressed. |
| `MANIFEST.json` | Generation timestamp, row counts, schema version, git commit hash. |

Quick start:

```
gunzip -k organizations.csv.gz   # produces organizations.csv
```

## What counts as "aligned"

Each organization has an alignment score from a multi-pass keyword scan against
the Commonweave framework areas (community land trusts, worker cooperatives,
mutual aid, food sovereignty, restorative justice, community health, open
source, and so on). Rows with `alignment_score >= 2` are included by default.

The full scoring methodology is in [`../DATA.md`](../DATA.md).

## How fresh is this?

`MANIFEST.json` carries the exact timestamp and git commit. The export is
regenerated whenever the underlying database changes. Best-effort weekly
refresh on Sunday nights.

## Rebuild it yourself

The source database lives at `../data/commonweave_directory.db` and is
gitignored on purpose (it is a build artifact, not source code). To rebuild
from scratch, see the ingest scripts in `../data/ingest_*.py` plus the registry
fetchers documented in [`../DATA.md`](../DATA.md). To regenerate just the
release files from an existing database:

```
python ../data/export_to_releases.py
```

## Schema

See `MANIFEST.json` for the column list. Internal scoring, audit, and
deduplication fields are intentionally omitted from the public export.
