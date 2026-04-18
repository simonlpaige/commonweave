# Experiment Results
Run: 2026-04-17 | DB: ecolibrium_directory.db (~10MB) | All scripts read-only

Backup: `data/ecolibrium_directory.db.backup-before-experiments-2026-04-17T20-17-24Z`

---

## Experiment 1: Non-Western + semantic term expansion

**Script:** `exp1_test_nonwestern_terms.py`
**File modified:** `data/phase2_filter.py` (14 new terms appended to STRONG_POS)

### New terms added to STRONG_POS

```
ejido, cooperativa, coopérative, solidaridad,
gotong-royong, gotong royong, waqf, minga, genossenschaft,
sharikat ta'awuniya, sociedad cooperativa, société coopérative,
collective, employee-owned
```

Terms already present (skipped): `cooperative`, `worker-owned`

### Dry-run output

```
Term: 'ejido'             --> 0 potential new pickups
Term: 'cooperativa'       --> 0 potential new pickups
Term: 'cooperative'       --> 0 potential new pickups
Term: 'coopérative'       --> 0 potential new pickups
Term: 'solidaridad'       --> 0 potential new pickups
Term: 'gotong-royong'     --> 0 potential new pickups
Term: 'gotong royong'     --> 0 potential new pickups
Term: 'waqf'              --> 0 potential new pickups (1 exists in DB but already score>=2)
Term: 'minga'             --> 0 potential new pickups
Term: 'genossenschaft'    --> 0 potential new pickups
Term: 'sharikat ta'awuniya' --> 0 potential new pickups
Term: 'sociedad cooperativa' --> 0 potential new pickups
Term: 'société coopérative'  --> 0 potential new pickups
Term: 'collective'        --> 0 potential new pickups (32 exist but all score>=2)
Term: 'employee-owned'    --> 0 potential new pickups
```

### What I observed

Zero new pickups -- but this is not a failure. Two reasons:

1. **The DB has already been scored by phase2_filter.py.** Orgs containing
   `cooperative` (744), `collective` (32), and `waqf` (1) are all already
   scoring >= 2 from existing STRONG_POS terms or positive modifier stacking.
   They won't appear in the "excluded or scored < 2" bucket.

2. **The current DB is US/IRS + UK Charities heavy.** Non-Western terms like
   `ejido`, `cooperativa`, `minga`, `genossenschaft` simply don't appear yet.
   This is a data coverage gap, not a term problem.

**Impact when it matters:** These terms will activate on the NEXT ingest run
when new international data is added (Latin America, MENA, Southeast Asia,
Germany/Austria). The STRONG_POS edits are staged and ready.

---

## Experiment 2: NTEE 'Y' exclusion review

**Script:** `exp2_check_ntee_y.py`
**File modified:** `data/audit_pass3_ntee.py` (comment added confirming Y intentionally excluded)

### Dry-run output

```
Total orgs with NTEE starting 'Y' (all statuses): 0
Orgs with NTEE 'Y' that are currently kept/active: 0

Good news: NTEE 'Y' is already fully excluded from the kept set.
No orgs would be removed by the audit_pass3_ntee.py change.
```

### What I observed

'Y' was never in KEEP_NTEE -- the task description said "remove if present"
and it wasn't there. Additionally, no orgs in the current DB have NTEE codes
starting with 'Y' (the DB has 0 such records). This is likely because the
IRS data extract used didn't include Y-class (fraternal, cemetery, mutual
insurance) organizations, or they were already dropped earlier in the pipeline.

The `audit_pass3_ntee.py` file now has a clear comment documenting this was
an intentional exclusion decision (not an oversight).

**No impact on active orgs.** No further action needed unless future IRS
ingests bring in Y-class orgs.

---

## Experiment 3: Website requirement preview

**Script:** `exp3_website_required_preview.py`
**File NOT modified:** `trim_to_aligned.py` unchanged pending Simon's review

### Dry-run output

```
Active orgs with alignment_score >= 2:         24,375
Of those, with NO website:                     14,186  (58.2%)
```

**Sample orgs that would be dropped (top by score):**

| Name | Country | Framework Area | Score |
|------|---------|---------------|-------|
| ADDISON COURT HOUSING COOPERATIVE INC | US | housing_land | 10 |
| BANADIR DEVELOPMENT ORGANISATION (BANDEV) | GB | ecology | 10 |
| Environmental Monitoring Group (EMG) | ZA | ecology | 10 |
| GREATER FLINT HOUSING COOPERATIVES | US | housing_land | 10 |
| Houston Transitional Housing Cooperative | US | housing_land | 10 |
| Mutual Aid Twin Cities Housing Cooperative | US | cooperatives | 10 |
| NATIONAL ASSOCIATION OF HOUSING COOPERATIVES | US | democracy | 10 |

### What I observed

**Do NOT apply this change without further scoping.** 58% of active kept orgs
have no website -- and the highest-scoring ones (score=10) are genuine housing
cooperatives and mutual aid orgs in the US, UK, and South Africa. These are
exactly the organizations Ecolibrium exists to surface.

The "no website" pattern likely reflects two things:
- IRS data doesn't require website disclosure
- Many small cooperatives and mutual aid groups don't maintain public websites

A blunt website-required filter would drop ~14K orgs including many
mission-critical ones. Softer alternatives to consider:
- Require website only for score == 2 (borderline orgs)
- Require website only for non-cooperative model types
- Flag no-website orgs in the UI rather than dropping them
- Use website presence as a tie-breaker only, not a hard gate

---

## Experiment 4: Greenwashing penalty preview

**Script:** `exp4_greenwash_preview.py`
**File NOT modified:** Pending Simon's review

### Dry-run output

```
Total orgs flagged by heuristic: 33 (all status='active')
All 33 are UK (GB) charities.
```

**Sample flagged orgs:**

| Name | Score | Description snippet |
|------|-------|---------------------|
| Chelsea FC Foundation | 2 | Chelsea FC Foundation is the official charity affiliated... |
| THE ENERGY SAVING TRUST FOUNDATION | 2 | The Foundations object's are to promote and advance education... |
| ORPHANS SHELTER FOUNDATION | 4 | ...promote any charitable purpose for the benefit... |
| NATURALLY AFRICA FOUNDATION | 4 | ...access to basic human rights, which include food, shelter... |
| Parent Carer Foundation | 2 | ...relief, guidance, advocacy, support & counselling... |

### What I observed

**The heuristic has a critical false-positive problem in this DB.**

All 33 flagged orgs are UK charities, and the "inc" match is firing on phrases
like "including (without limitation)" in UK charity objects text -- not on
"Inc." as a corporate designator. Examples:

- "to promote and advance the education of the public, **including** (without
  limitation) by identifying, teaching..." -- matches `%, inc%`
- "The objects of the Charity are to maintain the premises, **including**..." -- same

The greenwashing signal the BOT-CRITIQUE had in mind (e.g., "Shell Foundation,
Corp.") is structurally different from what the SQL pattern is catching here.

**Recommendation:** Do NOT apply the -5 penalty as written. Refined approach:
- Match on `' inc.'` with trailing period, or `', inc.'`, or `'incorporated'`
- Add whitelist: names containing 'community foundation', 'family foundation',
  'public foundation' are exempt
- Consider a separate pattern for US orgs (where 'Inc.' is a legal designation)
  vs. UK orgs (where 'including' in description is routine legal boilerplate)

---

## Summary

| Exp | Rows affected | Safe to apply? | Notes |
|-----|--------------|----------------|-------|
| 1: STRONG_POS expansion | 0 now; future ingests | YES | Terms staged, ready for next run |
| 2: NTEE Y removal | 0 (already excluded) | YES | Comment added to source file |
| 3: Website requirement | 14,186 would drop | NO -- needs scoping | 58% of kept set; includes score=10 orgs |
| 4: Greenwashing penalty | 33 flagged (all false positives) | NO -- heuristic broken | UK "including" text matches %, inc%; needs rewrite |

---

## Verification

- `data/phase2_filter.py` parses as valid Python: PASS
- `data/audit_pass3_ntee.py` parses as valid Python: PASS
- No destructive SQL executed: CONFIRMED (all scripts use read-only URI connections)
- DB backup created before any work: `ecolibrium_directory.db.backup-before-experiments-2026-04-17T20-17-24Z`

---

## 2026-04-17 (late evening) Multilingual implementation

### What was built

- data/i18n_terms.py - concept-organized multilingual term bank. 7 concepts (worker_cooperative, mutual_aid, commons, agroecology, community_health, participatory_governance, digital_commons) across ~30 languages. 354 raw terms from MULTILINGUAL-TERMS.md, of which 338 survive the ambiguity filter for scoring use.
- data/phase2_filter.py - updated to merge STRONG_POS_MULTI, apply NFC Unicode normalization, and use word-boundary regex matching for STRONG_POS (prevents short non-English terms like 'owe', 'hima', 'mera' from false-positive matching inside English words like 'power', 'himalaya', 'numeracy'). MODERATE_POS keeps substring matching so English stems like 'education' still catch 'educational'. _count_unique_strong counts each matched term once per org, preventing the old double-count of 'cooperative' + 'coop'.
- data/run_researcher_ng.py - rewritten to use build_local_queries('NG'). Now generates 101 search queries across en/ha/yo/ig instead of 15 English-only searches. Legacy registry-specific queries preserved at top of list. Prints language breakdown at run start.
- data/experiments/exp5_i18n_dry_run.py - read-only preview script comparing stored alignment_score to the new scorer's output across all active orgs.

### Short/ambiguous terms moved from scoring to search-only

These 16 terms are short, Latin-script, and collide with English words. They remain in SEARCH_TEMPLATES (researcher-bot queries) but are excluded from STRONG_POS scoring: ayni, coop, eg, equb, ess, gojo, hima, idir, iwi, mera, owe, scic, scop, shg, sms, mi.

Honest note: 'coop' is in the original English STRONG_POS and still scores there. 'ayni' and 'minga' matter for Andean context; their exclusion from scoring is a trade-off we can revisit with better boundary logic later.

### Functional verification

- AST parse of all three modified files: PASS
- Import round-trip: PASS (phase2_filter imports i18n_terms cleanly)
- Unicode round-trip: PASS (Arabic/Chinese/Amharic/Cyrillic all survive file write + DB scan)
- build_local_queries('NG'): 101 queries in en/ha/yo/ig
- build_local_queries('BR'): 29 queries in pt
- build_local_queries('JP'): 29 queries in ja with 協同組合 present
- build_local_queries('XX'): returns [] without exception

### Score distribution under new scorer (exp5 output)

| Delta (new - old) | Count |
|---|---|
| -6 or worse | ~180 |
| -5 | 36 |
| -4 | 105 |
| -3 | 3,707 |
| -2 | 2,389 |
| -1 | 3,457 |
| 0 | 11,538 |
| +1 | 1,591 |
| +2 | 782 |
| +3 | 460 |
| +4+ | 247 |

Orgs that would cross **from alignment_score >= 2 to < 2** under the new scorer: **7,698**.

### Interpretation (honest)

The 7,698 number looks alarming but needs unpacking:

1. Part of it is correct de-inflation. 'CAMAI COMMUNITY HEALTH CENTER' was scoring +8 under the old substring matcher because 'community health center' + 'community health' + 'commun' all fired as separate STRONG hits. New scorer counts it once at +3. Still above threshold, no problem.

2. Part of it is correct rejection of labor-management cooperation committees (95+ orgs) and 'cooperation trust funds' (63+ orgs) that were false-positive matches for 'coop' inside 'cooperation'. These should NOT be in the directory.

3. Part of it (several thousand orgs) is UK homelessness/disability/advocacy charities whose stored alignment_score does NOT match the output of any version of phase2_filter.score_org, suggesting those scores came from an earlier ingest-time heuristic (possibly in run_eco1.py or ingest_gov_registry.py) that is no longer the source of truth. Example: 'LLAMAU LIMITED', 'MRS Independent Living', 'THE BRIDGE (EAST MIDLANDS)' all stored as +6 but neither old nor new phase2_filter produces that score from their text.

### What NOT to do

Do NOT run phase2_filter.py against the live DB unconditionally. It would drop 7,698 orgs, many of which are genuinely aligned UK charities that do not self-describe using framework keywords. A careful migration would:

- Snapshot current alignment_score into a new column (alignment_score_legacy)
- Run new scorer into alignment_score_v2
- Keep max(legacy, v2) during a transition period
- Audit the divergences manually, not bulk-drop

### Red-team of my own work

- **Short non-Latin term risk**: I kept all non-Latin-script terms regardless of length on the theory that Chinese '互助' (hùzhù, 2 chars) is unambiguous. That's mostly true but '公地' might match inside longer CJK compounds. Word boundary on CJK via Python re \\b doesn't cleanly handle CJK; the current regex treats all CJK chars as \\w so \\b works at script transitions. Spot-checked OK but not exhaustively.
- **French stems**: 'commun' was in the French worker_cooperative list but I filtered it out as Latin-script-under-5-chars. It was giving 9,782 false positives inside 'community', 'communities', etc. before the filter. Good riddance, but it does mean we don't score legit French 'commun' on its own. Fine trade.
- **Coverage I may have miscalibrated**: the subagent that built i18n_terms.py transcribed MULTILINGUAL-TERMS.md into data structures; I did not manually verify every language entry. Confirmed via spot-check that en, es, pt, fr, ja, zh, ar, ha, yo, ig, sw entries are present and Unicode-intact.
- **SEARCH_TEMPLATES quality**: auto-generated queries like 'Nigeria irugbin ile ogbin adayeba' may or may not actually retrieve relevant Nigerian org results from DuckDuckGo. Not tested live. The guess is that even moderately relevant Yoruba queries will surface orgs that never appear in English-only searches; the ceiling on recall is huge here.
- **No lift shown yet**: exp5 reports '0 newly passing' because most non-English terms hit orgs that already score above +2 from existing English terms. True lift requires ingesting non-US/UK data, which is a separate (bigger) job.

### Recommended next steps

1. Do NOT bulk-rerun phase2_filter. Set up a staged column migration first.
2. Ingest a non-English data source (India NGO Darpan, Brazil CNPJ, or France RNA). This is where the multilingual terms will actually earn their keep.
3. Spot-test run_researcher_ng.py against 3 queries in Yoruba and 3 in Hausa to see whether DuckDuckGo returns usable Nigerian orgs.
4. Consider whether the short-term-ambiguity filter is too aggressive for 'ayni', 'minga', 'iwi', 'whenua'. These are high-signal in context (Andean, Maori) but collide with English substrings. A per-country term activation (only apply Maori terms when country='NZ') would fix this without losing recall.
