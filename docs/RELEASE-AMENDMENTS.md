# Reviewed public release amendments

The October 19, 2026 amendment corrects four fields across three Maine records:

| Release ID | Correction | Evidence |
|---|---|---|
| 909540 | Decode the ampersand in Belfast Cohousing & Ecovillage; link to the community homepage. | [Community website](https://www.mainecohousing.org/), reviewed October 19. |
| 909562 | Normalize `Blue  Hill` to `Blue Hill`. | Duplicate whitespace in the existing release and its exact corresponding directory row; checked October 19. No new activity or legal-form claim. |
| 910476 | Link Two Echo Cohousing to its community homepage. | [Community website](https://twoecho.org/), reviewed October 17. The October 19 fetch timed out; the earlier dated source evidence is retained. |

These are a separately reviewed subset of the September Maine proposals. Description and model-type changes remain pending. Review was automated by Codex under the project owner's existing authorization; no organization endorsement, external acceptance, legal-form verification or current housing availability is asserted.

The downloadable JSON, CSV, US split, `ic_directory` split and Maine directory shard contain the same accepted values. Their record counts and other record fields are preserved. A bounded check found no matching map feature under the three known source-profile URLs or recovered IDs, so this amendment does not add or alter a map point.

## Durable evidence and reproduction

[`releases/AMENDMENTS.json`](../releases/AMENDMENTS.json) contains the accepted field subset, source identities, exact old values, field evidence dates, input hashes and output hashes. [`data/proposals/maine-contact-format-2026-10-19.json`](../data/proposals/maine-contact-format-2026-10-19.json) is the review input. The April extraction date and original source/provenance fields remain historical; an amendment does not reverify the whole directory.

To reproduce, use a clean checkout at parent `d8c900423151a860c46fa228df107169c29fe3b8`, then run the new tool and review input from this revision against that parent checkout:

```powershell
python -B data/amend_maine_release.py data/proposals/maine-contact-format-2026-10-19.json --root C:/path/to/parent-checkout --output C:/path/to/new-amendment-output
```

The output must be a new directory outside the source checkout. The tool reads no database and performs no network requests. It validates the complete batch before creating output. Compressed inputs are pinned byte-for-byte; text input hashes normalize CRLF to LF for cross-platform reproduction. All affected representations must pass their original-ID, source-ID and expected-value checks. Id-less directory rows require exact name, city and original source-URL matches. Missing or ambiguous matches fail.

The output is a reviewed partial overlay, not a full export. Copy its seven generated files together into the release-review checkout and verify them before publication. Other countries, sources, search metadata and map snapshots must not be regenerated from the older download. Pending review, unsupported promotion fields, old/future evidence, changed input hashes and existing amendment ledgers are refused. Extending an existing ledger requires an explicit reviewed implementation; this tool does not silently replace a prior amendment.

## Rebuild protection and next task

`export_to_releases.py` refuses to overwrite a release directory containing `AMENDMENTS.json`. Generate a fresh database export into a separate directory, reconcile the field evidence and identities, and review the resulting amendment chain before replacing the public files. This prevents an ordinary export from silently erasing these corrections.

The operational database and these public snapshots still have different identities and provenance. The next task is a source-preserving adapter that reconciles reviewed amendments into a new canonical export, with conflict handling and tests proving that prior corrections survive. Until then, keep the public ledger and its exact input/output hashes with any redistribution. This amendment conveys no new license over upstream data.
