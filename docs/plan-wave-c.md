# Commonweave Wave C Plan -- Red-Team Target

## What Commonweave Is

An open directory of ~168,629 aligned organizations (cooperatives, mutual aid, land trusts,
unions, open-source foundations, community health centers, etc.) across 183 countries.
Goal: surface these organizations for people who want to plug in locally, and eventually
auto-generate "community guides" that show people what exists near them.

Alignment score (-10..10) is the gating mechanism. Sources range from high-trust curated
lists (ICA directory, ITUC, RIPESS) to noisy mass ingests (Wikidata, IRS BMF).

## What Was Built in Wave B (already in git)

1. **post_ingest.py enforcement gate** -- runs after every ingest, removes false positives
2. **audit/index.html portal** -- human review UI (5 verdicts, keyboard shortcuts, JSON export)
3. **Outlier-weighted sampling** -- shows auditors FP risk, FN risk, scoring bugs first
4. **Open Collective ingest** (data/ingest_open_collective.py) -- GraphQL, 500 cap, score>=2 gate
5. **open_source_governance scoring** -- new keyword axis in phase2_filter.py; KNOWN_ALIGNED_NAMES whitelist
6. **Sub-national audit regions** -- gen-audit-data.py --subregion MO works, Missouri test passed
7. **Audit coverage tracker** -- data/audit-coverage.json + audit/coverage-summary.json + map pin states
8. **tools/build.py** -- single rebuild command with MANIFEST.json

## What the Red-Team Should Critique

### A. Scoring architecture

Current approach: alignment_score is a bag-of-words count (-10..10). High-trust sources
get a legal_form_bump. Known org names get a hard floor of 7. Open source governance
terms add 2 pts each.

Risks to identify:
- Is a simple keyword count the right gating mechanism at 168K+ scale?
- The KNOWN_ALIGNED_NAMES whitelist is manually curated -- what breaks when it's stale?
- Open Collective has 14K collectives but we set score >= 2 as the gate. Is that too low?
  Could it import a lot of noise (hobby projects, personal fundraisers)?
- Score axis is English-biased despite i18n_terms.py. How bad is this for non-Western orgs?

### B. Coverage and false negative rate

We removed 4,477 false positives (2.5% of the directory). But we haven't measured
the false negative rate -- how many genuinely aligned orgs were removed by the cutline?

- Scarcity protection (<=50 orgs in country exempt) is a heuristic. Is the threshold right?
- The "Real, thin docs" verdict routes to an enrichment queue -- but what if the org
  doesn't have a web presence to find? Dead end?
- World Agroforestry Centre, Kenya Human Rights Commission currently score 0-2.
  Open source governance keywords won't fix those. What will?

### C. Progressive geographic narrowing

Plan: after auditing all regions, drill down to state -> county -> city -> neighborhood.
DB has state_province (85%) and city (86%) populated.

Risks:
- US state drill-down tested (Missouri works). But state_province is a free-text field --
  some rows say "MO", some say "Missouri", some say "Kansas City, MO". Matching is fragile.
- At neighborhood level, orgs don't self-report neighborhood names. How do you get there?
- The map currently renders 29,831 geocoded pins out of 168,629 orgs. That's 18% geocoded.
  Neighborhood-level guide generation needs 80%+ geocoded. Gap.

### D. Internet-native / unregistered orgs

Open Collective is the best known source. What else is missing?
- GitHub org scraping is technically possible but quality signal is weak -- most orgs
  are individual devs, not communities
- Mastodon instances vary wildly -- some are truly community-governed, most are vanity instances
- Loomio groups are private by default
- The "internet-native" category needs a working definition: what makes a GitHub org
  "aligned" vs. just open source?

### E. Federation as a design principle

Apache, Linux Foundation, Wikimedia are canonical federations. We want to add federation_membership
as an edge type (connecting member orgs to their federating body).

Risks:
- ICA has 303 member organizations. RIPESS has ~200 networks. ITUC has 337 affiliates.
  That's ~840 high-confidence edges immediately available. Is that enough to be useful?
- Edge quality degrades fast: if we add "every org in state X that appears in the
  ICA directory is connected to ICA", we're drawing false relationships
- What's the user-facing value of showing federation edges? Is it "find your co-op's
  national body"? Or "see what networks overlap in your city"?

### F. Build pipeline

tools/build.py runs build_search_index.py, build_map_v2.py, wiki-update.py, gen-audit-data
for 3 regions, then writes MANIFEST.json.

Risks:
- Full rebuild takes how long? No timing data yet.
- If build_search_index.py fails (big script, lots of edge cases), does MANIFEST still write?
  Current design: yes, step failures are warnings not aborts. Is that right for MANIFEST?
- No CI/CD. Build is manual. Who runs it and when?
- Generated files are committed to git -- repo will grow fast as directory grows.

## Key Questions for Red-Team

1. Is the scoring architecture sound enough to scale to 500K orgs?
2. What is the #1 thing we're missing that would make this useful to a community organizer TODAY?
3. Where is the false negative risk highest? (Legitimate orgs we're excluding)
4. Is Open Collective a safe ingest source at score >= 2, or does it need a higher cutline?
5. What's the right definition of "internet-native aligned org"?
6. Is federation edge data worth building before geocoding is at 80%+?
7. What would make an auditor trust this directory enough to recommend it to their network?
