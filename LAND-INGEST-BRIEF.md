# Brief: Add land trusts, sweat-equity, and construction co-ops

You are Claude Code. This brief is the source of truth. Read it once, then execute.

## Mission

Add **land trusts, sweat-equity housing programs, and construction cooperatives** to the Commonweave directory. Target: formal, country-level and regional-level orgs. ~500-1500 new orgs expected globally.

This is a follow-on to the labor unions ingest (`ingest_labor.py`). Same pipeline conventions, same rigor, different sources.

## Why we're doing this

Labor + land + housing is the triad that turns the framework from abstract to operational. Community Land Trusts already exist in ~40 countries. Sweat-equity programs (Habitat for Humanity and similar) have built ~1M homes globally. Construction co-ops quietly run in Mondragon, in the UK, in New York. Surfacing these in one place is how the next generation of these orgs finds their precedents.

## Hard rules

1. **Don't start if the unions ingest (`ingest_labor.py`, `ingest_unions.py`, `ingest_ituc.py`) is not yet committed and pushed.** Check with `git log --oneline -5` in both repos. If the unions commits aren't there, STOP and announce: `openclaw system event --text "land ingest blocked - unions not committed yet" --mode now`.
2. **Follow the existing pipeline.** Model new scripts on `ingest_wikidata_bulk.py` and `ingest_unions.py` (which should exist by the time you run).
3. **Formal orgs in v1.** `legibility=formal`. No informal squats, no tent cities, no anarchist housing collectives without legal status. Those are real but they're v2 with human review.
4. **No em dashes.** Feynman voice in all comments and docs.
5. **Surgical.** No drive-by refactors.
6. **Dedup is the existing pipeline's job.** Just ingest idempotently (upsert by source ID). Don't roll your own dedup.

## What to read first

- `commonweave/data/_common.py`
- `commonweave/data/ingest_wikidata_bulk.py`
- `commonweave/data/ingest_unions.py` (just committed by the previous run)
- `commonweave/data/ingest_ituc.py` (same)
- `commonweave/data/taxonomy.yaml`
- `commonweave/PIPELINE.md`
- `commonweave/data/migrate_legibility.py`

## Taxonomy additions

Add a `land_and_housing` top-level branch (or extend the existing `housing` branch if one already exists — check first):

```yaml
land_and_housing:
  description: Democratic ownership of land and housing
  subtypes:
    community_land_trust:
      description: Nonprofit that owns land in trust, leases homes at permanent affordability
      wikidata_ids: [Q5153359]   # Community land trust
    housing_cooperative:
      description: Residents collectively own the building, not individual units
      wikidata_ids: [Q1329546]   # Housing cooperative
    mutual_housing_association:
      description: Membership-based nonprofit owning rental housing democratically
      wikidata_ids: []   # manual curation; few Wikidata entries
    sweat_equity_program:
      description: Future owner contributes labor hours in exchange for below-market homeownership
      wikidata_ids: [Q2463356]   # Habitat for Humanity and affiliates
    construction_cooperative:
      description: Worker-owned construction and trades firms
      wikidata_ids: [Q4539]   # filter to construction-sector subtypes
    labor_for_housing_program:
      description: Orgs that tie labor contribution to housing rights (cross-cutting category)
      wikidata_ids: []   # manual + derived
```

If a `housing` branch already exists, merge gracefully instead of duplicating.

## Work items

### 1. `commonweave/data/ingest_land_trusts.py`

- Wikidata SPARQL: `Q5153359` (Community land trust) + `Q1329546` (Housing cooperative) + subclasses.
- For each org: insert with `legibility=formal`, category=`land_and_housing/<subtype>`, source=`wikidata_land_trusts`.
- Add `--dry-run` flag.
- Log to `commonweave/data/ingest-land-trusts-run.log`.

### 2. `commonweave/data/ingest_grounded_solutions.py`

Grounded Solutions Network maintains a US CLT directory. Scrape it.

- Source: https://groundedsolutions.org/tools-for-success/resource-library/us-clt-directory (verify URL; may have moved). Their members page is also a source.
- If the scrape is blocked or the structure has changed, fall back to the HUD list of CLTs or scrape Wikipedia's "Community land trust" article and its country sub-articles.
- Cache HTML to `commonweave/data/sources/grounded-solutions-cache/`.
- Polite: 1s sleep, proper User-Agent.
- Mark `legibility=formal`, source=`grounded_solutions`.

### 3. `commonweave/data/ingest_habitat.py`

Habitat for Humanity has ~1,100 affiliates globally.

- Source: https://www.habitat.org/about/affiliates (or their API if they expose one; check). International affiliates list at https://www.habitat.org/where-we-build.
- Scrape or use any available structured data.
- Each affiliate is a separate organization (local/regional chapter of a global brand). Insert each one.
- Cache HTML.
- Mark `legibility=formal`, category=`land_and_housing/sweat_equity_program`, source=`habitat_affiliates`.

### 4. `commonweave/data/ingest_construction_coops.py`

Harder because there's no single global registry.

- Wikidata: `Q4539` (cooperative) filtered by industry = construction.
- US: ICA Group's directory of worker co-ops (https://institute.coop/worker-cooperatives-directory or current URL). Filter to construction/trades.
- UK: Co-operatives UK member directory, filter to construction.
- Mondragon: Spain-based, ~15 construction-sector co-ops under the Mondragon Corporation. Manual seed list is fine if scraping is hard — document it in the script.
- Mark `legibility=formal`, category=`labor/construction_cooperative` (reuse the existing labor branch).

### 5. `commonweave/data/ingest_land_and_housing.py` dispatcher

Runs all four in order. Mirrors `ingest_labor.py`.

### 6. Documentation

- Append a "Land and housing" section to `commonweave/PIPELINE.md`. Match voice and style.
- Append to `commonweave/DATA.md` (if it lists sources).
- Skip re-rendering the PDF. Note the omission in the commit message.

### 7. Dry run

Run each script with `--dry-run` first. Total expected insert count across all four scripts: **500-1500 orgs**. If outside that range, stop and investigate.

### 8. Real run

Run all four for real. Capture summaries.

### 9. Rebuild frontend artifacts

```bash
python commonweave/data/build_map_v2.py
python commonweave/data/build_search_index.py
python commonweave/data/export_directory.py
```

Sync to live site (same pattern the `commonweave-frontend-update` cron uses).

### 10. Commit + push

Workspace repo: one commit, Feynman voice.
First line: `Add land trusts, sweat-equity, and construction co-ops to the directory`.

Live-site repo: one commit.
First line: `Update directory data: land and housing orgs added`.

Push both.

## Done checklist

- [ ] Unions commits exist in both repos (precondition check)
- [ ] `taxonomy.yaml` extended with `land_and_housing` branch
- [ ] `ingest_land_trusts.py` + `ingest_grounded_solutions.py` + `ingest_habitat.py` + `ingest_construction_coops.py` all exist with `--dry-run`
- [ ] `ingest_land_and_housing.py` dispatcher exists
- [ ] Dry-run totals are in the 500-1500 range
- [ ] Real runs completed
- [ ] `PIPELINE.md` has a "Land and housing" section
- [ ] Map + search + directory export rebuilt
- [ ] Live-site data synced
- [ ] Workspace repo committed + pushed
- [ ] Live-site repo committed + pushed
- [ ] At end, run: `openclaw system event --text "Done: Land trusts + sweat-equity + construction co-ops added. N orgs inserted. Ready for guide brief." --mode now`

## Karpathy rules

1. State assumptions. Ask when confused.
2. Minimum code. No speculative abstractions.
3. Surgical. Only touch what's needed.
4. "Done" checklist is your verifier.
