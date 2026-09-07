# Published organization data audit — 5 September 2026

**Prioritize evidence repair before volume growth.** This audit checks every
row in the published search, map, and download. It does not independently
verify every organization's existence, activity, location, or services.

| Published artifact | Observable rows | Scope |
|---|---:|---|
| Search country/state files | 144,731 | 156 nonempty ISO country/territory buckets; historical timestamp 2026-04-28 |
| Downloadable release | 158,715 | Dated 2026-04-27; 177 valid ISO country codes plus missing/nonstandard values |
| Map points | 29,423 | orgs.geojson; associated stats dated 2026-05-22 |
| Map edges | 20,474 | Separate snapshot; 16,397 reference endpoints missing from those points |

The old search index advertised **168,650 rows / 183 buckets**. Reconciliation
removed 40 empty/nonexistent advertised buckets and added 13 nonempty
previously unindexed buckets. Counts now describe actual arrays; organization
records were not added, deleted, or certified. See the
[before-state record](../reports/data-audit-2026-09-05/baseline-summary.json).
Earlier v3 metadata claims 29,378 points. Circuits metadata declares 76 groups
but contains 13; the briefs generator correctly emits 13 and reports the
mismatch. These are different snapshots, not interchangeable totals.

## Findings and solutions

| Finding | Full-audit evidence | Action |
|---|---|---|
| Search drops provenance | All 144,731 search rows lack record-level source/evidence fields in this export. | Preserve stable IDs, sources and dates on rebuild; stop publishing rows parsed from research prose. |
| Release currency unknown | 158,706 of 158,715 rows lack a usable verification date; all lack an evidence excerpt in the export. | Use dated per-field review events. Build dates are not verification dates. |
| Websites incomplete/malformed | Release: 110,813 missing, 24,205 invalid under strict public-URL checks. Search: 95,680 missing, 27,017 invalid. | Queue review and render only safe URLs. Syntax failure does not establish a dead organization or site. |
| Geographic precision overstated | All map points lack explicit precision. 16,175 share coordinates with at least nine other rows; 11,399 GB points coincide. | Use recorded city/country. No travel-distance or service-radius ranking from these pins. |
| Corrupted map source tiers | 9,843 map records have values outside A/B/C/D in the tier field, mostly NTEE-style codes plus one `candidate` value. | Keep them excluded from results, disclose the count, and repair the export mapping from canonical fields. Never infer a trust tier from an activity code. |
| Edges mix inference and documentation | 16,397/20,474 have missing endpoints; 20,437 have no evidence URL. Types include 11,918 same-section proximity and 8,259 complementary-category suggestions. | Rebuild endpoints consistently; separate suggestions from sourced relationships. Never pair organizations alphabetically as a recommended collaboration. |
| Possible duplicate inflation | Release: 6,259 same-name/country groups covering 26,919 rows. Search: 632 groups / 1,882 rows. | Check identity and original source IDs. Branches and distinct same-name organizations are not automatically duplicates. |
| Strong geographic skew | Brazil/Australia: 129,484/158,715 release rows (81.6%). US/GB: 26,873/29,423 map points (91.3%). | Repair a useful pilot locality and underrepresented sources/languages. Registry volume is not representative coverage. |
| Sensitive visibility | 214 release and 82 search rows match invitation-link patterns. Release includes 4,145 mutual_aid_wiki rows. | Review discoverability and consent; do not republish invitations or precise locations merely because an upstream source did. |
| Research parsing admits non-organizations | South Africa contains a row named “283,000 civil society organizations (CSOs), NGOs, and nonprofits.” Other entries have orphaned citation markers. | Retain raw snapshots for audit, queue corrections, remove the prose-to-publication path. No automatic mass purge. |
| Pipeline trust and path errors | Shared paths targeted an old checkout; legacy enrichment overclaimed human verification; release export lacked active-status filtering. | Resolve clone-local paths, fail on missing DBs, apply evidence-backed changes only to a new review copy, and exclude inactive/merged rows at publication while recognizing empty merge markers. |

Missing website/description fields in the *map payload* do not prove they
are missing in the canonical DB; detail may be loaded separately. Automatic
checks cannot establish correct service areas or actual relationships. No
organization is removed or demoted by this audit.

The compressed queue has **380,081 review entries**, including repeated
locators for different review reasons. This is not a distinct-organization
count. It stores dataset, locator, ID and reasons rather than reproducing
sensitive contacts/invitations.

## Repairs included

- Reconciled searchable counts; distinct snapshots explained in the data notes.
- Stale-response, missing-file recovery, and safe-link fixes in the directory.
- Canonical search builder preserving identity/provenance, normalizing US
  states, retaining unresolved states, and filtering removed/merged rows.
- Proposals with expected old values, per-field evidence, reuse basis and
  visibility review. Pending proposals validate without writes; accepted
  reviews can change only a new DB copy.
- Map roles and user-selected plans, with no automatic named partnership.
- [Five OFN corrections](participation-ofn-corrections-2026-09-05.md) pending
  review and [eight corrected featured cards](featured-organizations-review-2026-09-05.md).

## Reproduce

From the repository root, Python 3.11+:

```powershell
python data/audit_public_exports.py --as-of 2026-09-05 --output reports/data-audit-2026-09-05
python data/reconcile_search_index.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
python data/stage_organizations.py data/proposals/ofn-field-review-2026-09-05.json --as-of 2026-09-05
```

Release JSON/CSV and all country/source splits match after line-ending
normalization. Input hashes, distributions and issue counts are in
[summary.json](../reports/data-audit-2026-09-05/summary.json); record locators
are in [review-queue.csv.gz](../reports/data-audit-2026-09-05/review-queue.csv.gz).
CI reruns the audit and attaches output. Audit success means the checks ran,
not that all records passed.

## Next release decision

The canonical DB is intentionally absent from GitHub. The older local
checkout has extensive staged deletions and was preserved. A trustworthy
replacement needs an explicitly selected canonical DB, queued identity and
location repairs, and search/map/edges/download rebuilt from one input. Do
not overwrite the working database with an older public export.

Start with a local food-project cohort: verify identity, public source,
role, operating area, participation route and visibility preference for
every pilot-facing record. Test the evidence workflow with the five OFN
corrections. Measure accepted corrections and useful leads, not rows added.
