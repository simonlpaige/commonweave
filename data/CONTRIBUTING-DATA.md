# Contributing organization data

Read [AGENTS.md](../AGENTS.md) and the [published-list audit](../docs/DATA-AUDIT-2026-09-05.md). A listing is a candidate for investigation, not an endorsement, verified service, or partnership. Preserve uncertainty and source terms.

## A correction without coding

Use [the contribution form](../participate.html) to prepare an addition, correction, connection, or protection request. Download the draft or review it on GitHub before posting. Issues are public. For removal or location protection, a listing name or ID and the requested change are enough; no personal explanation or proof of ownership is required.

## One durable path

The canonical store is `data/commonweave_directory.db`, intentionally absent from GitHub. Set `COMMONWEAVE_DB` or pass `--db` to an explicit existing file. Shared paths now resolve within the current clone. Missing databases fail instead of creating an empty file or using another checkout.

Search and map files are generated artifacts. Do not edit a country JSON file as the sole correction record: rebuilding would erase it. Do not insert comments or change a generated file's top-level shape. Research prose, scraped text, and AI output are leads, not publishable organization records.

1. Find a public organization page or source record; preserve source identity and identifiers. Prefer documented feeds/APIs to scraping presentation pages.
2. Check reuse terms and discoverability. Public access does not make a dataset CC0. Use original factual summaries, compatible open licenses, or explicit permission; do not copy restricted directories.
3. Separate identity, role, locality and service area. Software and federations are not local providers. Unknown is a valid value.
4. Prepare proposal JSON with evidence and expected old values. See [five pending OFN corrections](proposals/ofn-field-review-2026-09-05.json).
5. Validate without writes, review against the current DB, apply accepted changes to a new review copy, and inspect a coherent release before publication.

## Proposal contract

A document contains a `proposals` array. Each proposal has:

- Unique `proposal_id`, `operation` (`add`/`update`), and `changes`. Updates require `organization_id` and `expected` old values for every changed field.
- `evidence`: public HTTP(S) URL, supported `fields`, short excerpt or explicitly labeled reviewer summary, and `checked_at` (`YYYY-MM-DD`). Evidence must be within 180 days of validation and not future-dated.
- `visibility_review`: decision (`public`, `country_only`, `withhold`) and reason. Withheld groups cannot enter the public pipeline. Country-only changes must clear existing detailed location.
- `reuse`: basis (`open_license`, `permission`, `original_factual_summary`) and supporting URL. Software checks structure; reviewers check whether the basis is true.
- `review`: decision (`pending`/`accepted`), with a named `reviewer` for acceptance. Pending proposals cannot be applied.

Supported changes include name, description, website, `country_code`, city, state/province, `framework_area`, model type, source, legibility and paired `lat`/`lon`. Country uses ISO alpha-2; GLOBAL is not a country. Coordinates require source-supported `location_precision`. Do not add personal addresses or private invitations. Scores, status and verification tiers cannot be promoted through this tool. New records enter as `status=candidate`, `tier=D`, unpublished until a separate maintainer decision.

```powershell
# Historical packet validation; no writes.
python data/stage_organizations.py data/proposals/ofn-field-review-2026-09-05.json --as-of 2026-09-05

# Check current DB expected values; no writes.
python data/stage_organizations.py reviewed-proposals.json --db C:/path/to/commonweave_directory.db

# Accepted reviews only; output must be a new file.
python data/stage_organizations.py reviewed-proposals.json --db C:/path/to/commonweave_directory.db --output-db C:/path/to/new-review-copy.db

# Generate into a separate directory for inspection.
python data/build_search_index.py --db C:/path/to/new-review-copy.db --output C:/path/to/search-review
```

The copy operation checks expected values against the actual backed-up snapshot, applies a batch transactionally, saves `organization_evidence`, rejects replay, and never overwrites the source. It cannot verify a source's truth or a reviewer's authority. Field-level evidence is stored separately; not every review event is yet exported into map tooltips. Keep the linked review packet until that exporter exists.

`apply-enrichments.py` uses this new interface. Legacy files and old `--file`/`--dry-run` invocations must migrate; they are rejected rather than silently promoted as human-verified. Historical ingest adapters have not all migrated. Do not run their default write paths against a live database; use saved inputs and an isolated review copy.

## Interpretation and safety

Legacy sources use inconsistent A/B/C/D and tier_a-style values. Treat these as source metadata, not an independent confidence score. The map's A/B filter is source-backed, not proof of services, alignment or availability. Legibility (`formal`, `hybrid`, `informal`, `unknown`) describes how a group is documented, not legitimacy.

For vulnerable informal groups, survivor support, labor organizing, migrant support or hostile contexts, prefer minimal/country-level information and unknown legibility unless public discoverability is clearly intended. Do not enrich a sensitive group just because details are obtainable. Protection/removal requests take priority.

Name/country coincidence alone does not establish duplicate identity. Check branches, locality, original IDs and sources before merging. Broken websites are review signals, not closure decisions. Never use an export date as a verification date or a keyword score as evidence of impact.

## Checks and next contribution

```powershell
python data/reconcile_search_index.py --check
python data/audit_public_exports.py --as-of 2026-09-05 --output reports/data-audit-2026-09-05
python -m unittest discover -s tests -p 'test_*.py' -v
```

Submit proposal/script, review note, input snapshot and validation results. Do not commit a database or private source cache. Next: export `organization_evidence` into consistent per-field provenance and reconcile map edges to the same release's point IDs. Acceptance: a rendered claim links to its source, field, review date and decision without guesswork.
