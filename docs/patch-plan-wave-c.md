# Wave C Patch Plan (post red-team)

Red-teamed by: DeepSeek V4 Pro + GPT-5.5 Pro, 2026-04-27

Patches ordered by impact / urgency. Each is self-contained and shippable.

---

## Patch 1 -- Raise Open Collective ingest cutline (CRITICAL)

**Problem:** score >= 2 lets in hobby projects, personal fundraisers, birthday trips.
"community" in any description triggers MODERATE_POS and earns 1 pt. Two such words = score 2, admitted.

**Fix:**
- Raise MIN_SCORE in ingest_open_collective.py from 2 to 4
- Add hard pre-filter: skip collectives with description length < 40 chars
- Add hard pre-filter: skip collectives tagged only with ['personal'] or ['fundraiser']
- Add host check: prefer collectives with a recognized fiscal host (Open Collective Foundation,
  Open Source Collective, etc.) over self-hosted -- bump score +1 for hosted collectives

**Files:** data/ingest_open_collective.py

---

## Patch 2 -- State/province normalization (HIGH)

**Problem:** state_province is free-text. "MO" / "Missouri" / "Kansas City, MO" / "Mo." all exist.
The --subregion flag uses LIKE matching which is fragile and produces inconsistent samples.

**Fix:**
- Add data/state_province_map.json: canonical map of ISO 3166-2 codes + common variants
  e.g. {"US-MO": ["MO", "Missouri", "Mo.", "kansas city, mo"], ...}
- Update gen-audit-data.py --subregion to normalize against this map before querying
- Add a tools/normalize-state-province.py migration to standardize existing DB rows
  toward ISO 3166-2 codes where possible (dry-run default)

**Files:** data/state_province_map.json (new), tools/gen-audit-data.py, tools/normalize-state-province.py (new)

---

## Patch 3 -- False negative measurement (HIGH)

**Problem:** We measured false positive removal (4,477 removed) but have no idea how many
REAL aligned orgs were cut. Scoring is tuned in the dark.

**Fix:**
- Build tools/fn-audit.py: takes a list of orgs that SHOULD be in the DB (ground truth)
  and checks which are present/absent/removed
- Ground truth seed: all ICA members + all RIPESS affiliates + all ITUC affiliates
  (we already ingested these -- they're TRUST_SOURCES)
- Report: how many trust-source orgs are currently status='removed'? That's a direct FN count.
- Run as part of build.py --audit step; print warning if FN rate > 1%

**Files:** tools/fn-audit.py (new), tools/build.py (add step)

---

## Patch 4 -- KNOWN_ALIGNED_NAMES as external versioned file (MEDIUM)

**Problem:** Hardcoded in phase2_filter.py. Can't be edited without a code change. Curator bias baked in.
Brittle: if Apache renames a project, the old name stays, the new one never gets added.

**Fix:**
- Move to data/known_aligned.csv with columns: name, source, reason, added_by, added_date
- phase2_filter.py reads the CSV at import time (cached as a set)
- Anyone can propose additions via PR; reviewers can see the audit trail
- Add a tools/check-known-aligned.py that verifies DB matches for each row in the CSV

**Files:** data/known_aligned.csv (new), data/phase2_filter.py (read from CSV), tools/check-known-aligned.py (new)

---

## Patch 5 -- Org opt-out / edit mechanism (MEDIUM)

**Problem:** We list orgs without their knowledge or consent. In repressive contexts, being
on a public directory can be dangerous. No mechanism to request removal, correction, or obscuring.

**Fix:**
- Add a simple "Is your organization listed? Request a change" link in the directory.html card footer
- Link goes to a pre-filled GitHub Issue template: org name, request type (remove/edit/obscure), contact
- Add a data/opt-out-log.csv that records received requests and outcomes
- Any request for removal: mark status='opt_out' in DB (not deleted, not removed -- a new status
  that means "org chose not to be listed") and exclude from all exports

**Files:** directory.html (add link), .github/ISSUE_TEMPLATE/org-request.md (new), data/opt-out-log.csv (new), data/post_ingest.py (respect opt_out status)

---

## Patch 6 -- Sensitive org flag + coordinate obscuring (MEDIUM)

**Problem:** Exact coordinates on a map can be dangerous for LGBTQ+ groups, undocumented immigrant aid,
abortion funds, indigenous land rights orgs in repressive states. No threat model exists.

**Fix:**
- Add tags field check: if org has tags like ['lgbtq', 'abortion', 'undocumented', 'indigenous rights']
  AND country has a Freedom House score < 3 (Not Free), set a sensitive_flag=1 column
- In map.html: sensitive_flag=1 orgs render at city centroid only, not exact lat/lon
  (round to 2 decimal places, ~1km precision)
- Add a data/freedom-index.csv with country_code -> freedom_score for the gate condition
- Document this policy in the wiki under Data-and-Directory.md

**Files:** data/freedom-index.csv (new), data/post_ingest.py (set sensitive_flag), map.html (blur coords), wiki

---

## Patch 7 -- Legal form bump safeguard for co-opted registration types (LOW-MEDIUM)

**Problem:** In some countries, "cooperative" or "association" legal status is a sign of
state co-option, not alignment. The bump currently treats all registered coops as +3.

**Fix:**
- Add data/registration_context.json: per-country registration_type -> trust_modifier
  e.g. Cuba: cooperative -> 0 (state-dominated), China: association -> -1 (GONGO risk)
- legal_form_bump reads this file and applies the modifier
- Start with 5-10 well-documented cases; expand via community PRs
- Document the methodology clearly so it's reviewable

**Files:** data/registration_context.json (new), data/phase2_filter.py (apply modifier)

---

## Patch 8 -- Geocoding gap: city-level batch pass (LOW -- expensive but important)

**Problem:** Only 18% geocoded. Neighborhood guides need 80%+. Gap is large.

**Fix (pragmatic first step):**
- Batch geocode to city centroid (not exact address) using OpenStreetMap Nominatim (free)
  for all orgs that have city + country_code but no lat/lon
- City centroid is sufficient for regional discovery; not sufficient for neighborhood
- Rate limit: 1 req/sec (Nominatim policy). At 139K ungeococed orgs, that's ~39 hours.
  Run in a background cron over several days.
- tools/geocode-batch.py: processes 500 orgs/run, resumes from last_id, logs failures

**Files:** tools/geocode-batch.py (new)

---

## Not Patching Now (needs community decision, not code)

- **Community governance of the directory** -- who decides what gets ingested?
- **Participatory mapping** -- let orgs place themselves on the map
- **Non-English audit UI** -- requires localization, not a quick fix
- **Platform bias for WhatsApp/WeChat/Telegram orgs** -- needs a scraping strategy and legal review
- **The "alignment is political" framing** -- add a transparency page acknowledging this

---

## Execution Order

1. Patch 1 (OC cutline) -- 30 min, high ROI, run immediately before next OC ingest
2. Patch 3 (FN audit) -- 1 hr, gives us actual data on how bad the scoring is
3. Patch 4 (CSV whitelist) -- 45 min, future-proofs curation
4. Patch 2 (state normalization) -- 2 hrs, required before sub-national audits go live
5. Patch 5 (opt-out) -- 1 hr, low code, high trust signal
6. Patch 6 (sensitive flag) -- 2 hrs, requires freedom-index.csv research
7. Patch 7 (legal form context) -- 3 hrs, requires country research
8. Patch 8 (geocoding) -- 1 hr to write, 39 hrs to run
