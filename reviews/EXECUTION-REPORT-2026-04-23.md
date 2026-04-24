# Execution Report -- Commonweave README Fixes 2026-04-23

**Executor:** Claude Sonnet 4.6 (claude-sonnet-4-6)
**Brief:** `commonweave/reviews/CLAUDE-CODE-BRIEF-2026-04-23.md`
**Review doc:** `commonweave/reviews/README-review-2026-04-23.md`
**Date:** 2026-04-23
**Status:** All 9 fixes executed. Not pushed -- awaiting Simon's review.

---

## Files Changed

| File | Change type | Fix # |
|---|---|---|
| `README.md` | Modified | 1, 2, 3, 4, 5, 7, 9 |
| `THREAT-MODEL.md` | Created | 8 |
| `data/build_map_v2.py` | Modified | 6 |
| `map.html` | Modified | 6 |
| `data/TODO-tier-a.md` | Created | 8 (related) |

---

## Fix-by-Fix Status

### Fix 1: Promote "What Does Not Exist Yet" -- DONE
**Commit:** `eaf6dc1`

Removed from its position as `###` subsection inside "What Exists Today." Added as a top-level `##` section right after the NeighborhoodOS related-project note, before Core Principles. Now visible before the framework theory.

### Fix 2: Confidence-aware phrasing on headline number -- DONE
**Commit:** `2c4db1c`

Updated all numbers to verified DB values (filter: `WHERE merged_into IS NULL`, verified 2026-04-23):
- 24,508 → 26,022 organizations
- 60 → 61 countries
- 8,412 → 11,991 geocoded points
- 2,805 → 3,657 alignment score >= 5
- 88% → ~83% US/UK (21,559 of 26,022)

Fixed tier language: "Tier A/B verified" removed. Replaced with "15,854 are registry-backed (Tier B)" -- there are no Tier A rows in the DB.

Added legibility column note: all 26,022 currently read `unknown`; the column exists but backfill is pending.

### Fix 3: Good First Contributions -- DONE
**Commit:** `92842b0`

Added `### Good First Contributions` section inside "How to Contribute" with four subsections:
- **Data:** directory verification (45-minute country-scoped task with Larry's framing)
- **Research:** open question sourcing, org submission
- **Code:** map high-confidence toggle, edge schema, mobile
- **Design / Writing:** governance matrix cells, GLOSSARY.md

### Fix 4: Shorten README into entry point -- DONE
**Commit:** `274d238`

Replaced the full Phase 1/2/3 content (Phase 1 was already in BLUEPRINT.md, Phase 2/3 in THEORY-OF-CHANGE.md) with a 90-second framework summary. Sections removed from README:
- Detailed Phase 1 (1.1-1.4 with all checkboxes) -- preserved in BLUEPRINT.md
- Phase 2: The Transfer detail -- preserved in THEORY-OF-CHANGE.md
- Phase 3: Post-Transfer detail (3.1-3.4) -- preserved in THEORY-OF-CHANGE.md

Kept inline:
- 90-second framework summary (names Phase 1/2/3 and Mycelial Strategy)
- Mycelial Strategy with failure-modes subsection verbatim (load-bearing)
- Theory of Power Transfer condensed (not duplicated elsewhere, important enough to keep)
- Tensions and Tradeoffs condensed

README is now approximately 2,000-2,200 words.

**What moved to BLUEPRINT.md:** Nothing new moved -- Phase 1 was already there. README now explicitly links to it.

**What moved to THEORY-OF-CHANGE.md:** Nothing new moved -- Phase 2/3 were already there. README now explicitly links to it.

### Fix 5: Resource governance matrix -- DONE
**Commit:** `dae6dca`

Added six-row table to "Selective Abundance, Not Post-Scarcity" section with columns: Resource type / Examples / Constraint / Governance mode / Failure mode / Directory examples (score >= 5).

Directory examples populated from DB query (`alignment_score >= 5, merged_into IS NULL`):
- Housing/land: ADDISON COURT HOUSING COOPERATIVE INC [US], LANDWELL HOUSING COOPERATIVE [US]
- Food: PRAGYA [GB], HAYGROVE COMMUNITY GARDENS [GB]
- Cooperatives: Mutual Aid Twin Cities Housing Cooperative [US]
- Ecology: Environmental Monitoring Group (EMG) [ZA]
- Energy/digital: Centre for Renewable Energy and Action on Climate Change [NG]

Two cells marked `[NEEDS EXAMPLE]`:
- Skilled care (healthcare, childcare, eldercare) -- no good match found in `healthcare` framework area at score >= 5 that was clearly a care-work governance model rather than a general health org
- Attention and meaning -- no clear match in directory for this category

### Fix 6: Map confidence defaults + edge types -- DONE
**Commit:** `703e5ac`

**build_map_v2.py:** Edges now emit full provenance schema alongside existing compact fields:
```json
{
  "edge_type": "same_section | geographic_nearby",
  "confidence": 0.0-1.0,
  "explanation": "Both are in the housing_land section and within 12.3 km of each other",
  "created_at": "2026-04-23",
  "source_script": "data/build_map_v2.py"
}
```

**map.html changes:**
- Default `activeTiers` changed from `new Set(['A', 'B', 'C'])` to `new Set(['A', 'B'])` -- Tier C starts inactive
- "Connections" label renamed to "Shared-area links" in stats panel (removes implication of real collaboration)
- Tier C button displays as inactive (grayed out) on load
- Seven narrative presets added in new "Guided Views" sidebar section:
  1. Start with the skeptic view (Tier B only -- the honest map)
  2. High-confidence only (Tier A + B, default)
  3. Housing & land trusts
  4. Food sovereignty
  5. Participatory democracy
  6. Healthcare commons
  7. Outside US/UK (excludes US and GB records)

Presets hook into `isNodeVisible` via an `activePresetFilterFn` that manual tier/section controls can override.

**Note:** This fix requires `npm run build` or serving the files to test visually. The JS changes are syntactically correct but were not end-to-end tested because the map requires a running server and the built JSON files. The "high-confidence only" default will show fewer points when the map is first loaded -- this is the intended behavior.

### Fix 7: Issue-linked open questions -- DONE
**Commit:** `3e13c6c`

Converted 13 open questions from a numbered list to a table with columns: Question / Status / Needed expertise / Issue (if open) / Blocker.

Issue column left blank throughout -- no GitHub issues exist yet; that's Simon's decision.

Blocker column is the meaningful addition. Example: "What replaces prisons?" is not blocked on criminology expertise -- it's blocked on having a prison-abolition practitioner willing to co-author. That distinction makes the section a recruiting tool.

"Partially addressed" status used for Questions 10 and 12 where the framework or THREAT-MODEL.md has partial coverage.

### Fix 8: THREAT-MODEL.md -- DONE
**Commit:** `b55b1f1`

New file at `commonweave/THREAT-MODEL.md`. Sections:

1. **Assets** (6 rows: directory integrity, framework credibility, contributor trust, Simon's attention, Larry's output, pipeline reproducibility)
2. **Accepted tradeoffs** (state surveillance, metadata leakage, public contributor targeting)
3. **External adversaries** (grifters, greenwashers, entryists, AI-generated fake orgs, harassers)
4. **Internal adversaries** -- the load-bearing section. Four named patterns with evidence they've already happened:
   - Maintainer drift (US/UK registry skew is the residue)
   - Pipeline bias (83% US/UK, legibility backfill pending)
   - AI-assisted drift (early drafts too soft on power transfer)
   - Founder capture (nonviolence stated without comparative analysis)
5. **Attack surfaces** (6-row table)
6. **Controls matrix** (13 controls, each with adversaries defended and residual risk)
7. **Review cadence** (quarterly, Simon signs off, logged in git)

Specific tooling named as countermeasures: `pipeline_auditor.py`, `staleness_check.py`, `dedup_merge.py`, `legibility` column (intended, backfill pending), `[commonweave]` daily-memory tag.

`data/TODO-tier-a.md` also created to flag the Tier A dead code in build_map_v2.py -- no tier_a rows exist in the DB, but the code path is still there.

### Fix 9: Canonical domain line -- DONE
**Commit:** `6b8bc31`

Added `**Official site:** simonlpaige.com/commonweave/` immediately after the critique-first blockquote at the top of README.

---

## [NEEDS VERIFICATION] Markers Left in Place

| Location | Marker | Reason |
|---|---|---|
| README.md, governance matrix | `[NEEDS EXAMPLE]` for "Skilled care" row | No clean match in `healthcare` area at alignment_score >= 5 for care-work governance specifically |
| README.md, governance matrix | `[NEEDS EXAMPLE]` for "Attention and meaning" row | No clear directory category for this |

---

## Decisions Needing Simon's Sign-Off

1. **Tier A data model (data/TODO-tier-a.md):** The README now says "15,854 registry-backed (Tier B)" because Tier A produces 0 rows in the DB. Three options are listed in the TODO file. Decision: does Tier A get a real definition, or does the tier system get renamed?

2. **Domain registration:** The review recommends registering `commonweave.earth` defensively. Brief says this is Simon's call. Not acted on. Note the recommendation here in case it's useful.

3. **GitHub issues for Open Questions:** The issue column in the Open Questions table is blank throughout. Review recommended not filing all 13 as empty stubs. When/whether to file issues is a Simon decision.

4. **map.html not visually tested:** Fix 6 (map changes) is structurally correct but was not end-to-end tested against a live server. The JSON data files need to be regenerated with `python data/build_map_v2.py` to pick up the new edge schema. The default Tier C inactive state should be visually verified.

5. **Legibility backfill:** THREAT-MODEL.md lists this as the dominant data quality problem. Not in scope for this brief but flagging: the backfill is what makes the legibility column operational as a bias countermeasure.

---

## Questions for Simon

None. All ambiguous decisions were either resolved per the brief's explicit instructions or flagged above as sign-off items.

---

## Git Summary

9 commits, all on `master`. Not pushed.

```
6b8bc31 Add canonical site link near top of README
b55b1f1 Add THREAT-MODEL.md; flag Tier A dead code in data/TODO-tier-a.md
3e13c6c Convert Open Questions to work-package table with Blocker column
703e5ac Add edge provenance schema; default map to high-confidence; add presets
dae6dca Add resource governance matrix to Selective Abundance section
274d238 Shorten README to an entry point; move Phase detail to BLUEPRINT/TOC
92842b0 Add Good First Contributions section with specific 60-second tasks
2c4db1c Use verified DB numbers; fix tier language; note legibility gap
eaf6dc1 Move "What Does Not Exist Yet" above the framework theory
```
