# Directory Methodology

How organizations get into the Commonweave directory, how they're classified, what "legibility" means, and what the quality standards are.

---

## Who Gets In

An organization belongs in the directory if it is **commons-oriented** in at least one of these ways:

- **Cooperative structure** - worker co-ops, consumer co-ops, housing co-ops, credit unions, producer co-ops
- **Mutual aid** - community-organized resource sharing, savings circles, ROSCAs, solidarity networks
- **Commons governance** - organizations that govern shared resources (water, land, energy, data) on behalf of a community rather than extracting profit from them
- **Transition infrastructure** - organizations building the systems a post-extraction economy needs (open source tools, democratic governance platforms, community land trusts, universal basic services pilots)

The test is not ideology. An organization doesn't need to self-identify as part of any movement. The test is structure and practice.

---

## What Gets Excluded

- Corporations with CSR programs (structure is extractive even if some programs are good)
- Think tanks and advocacy organizations with no operational commons (they study the alternatives, they don't run them)
- Government agencies (included only when they directly operate a commons, e.g. a municipal energy cooperative)
- Roads, infrastructure, Wikipedia articles, Reddit threads (these have appeared in automated ingests and are quarantined)

---

## Legibility Tiers

Every organization has a `legibility` field. This tracks *how we found it* so the bias in coverage is visible.

| Value | Meaning |
|-------|---------|
| `formal` | Found in formal registries (Wikidata, ICA, government cooperative lists). Verifiable. |
| `hybrid` | Found through a mix of formal and informal sources. Partially verifiable. |
| `informal` | Community-documented, social media, word of mouth. Exists but harder to verify. |
| `unknown` | Source unknown or unclear. Needs review. |

**Why this matters:** Formal registries have a strong bias toward organizations that can afford registration, operate in countries with cooperative law, and communicate in English. The legibility field makes that bias visible rather than hiding it. An organization documented by its own community as `informal` is not less valid - it's differently documented.

---

## Framework Area Classification

Each organization is tagged with its primary framework area:

| Area | Description |
|------|-------------|
| `democratic_sovereignty` | Voting, governance, civic participation, unions |
| `universal_sufficiency` | Food, housing, healthcare, education access |
| `ecological_equilibrium` | Environmental commons, land stewardship |
| `economic_democracy` | Cooperatives, worker ownership, solidarity economy |
| `transparency_by_default` | Open data, open government, accountability orgs |
| `healthcare` | Community health, mutual aid health |
| `education` | Community education, open learning |
| `food` | Food cooperatives, community gardens, food sovereignty |
| `housing_land` | Community land trusts, housing cooperatives, land commons |
| `energy_digital` | Community energy, digital commons |

**Known taxonomy issues:** Some entries use variant spellings (`democratic sovereignty` vs `democratic_sovereignty`, `land commons` vs `housing_land`). The Curator agent normalizes these on each run.

---

## Sources

Current primary sources:

- **Wikidata** - bulk SPARQL pulls for cooperative, mutual-aid, and credit union classes. High legibility, formal bias.
- **ICA (International Cooperative Alliance)** - regional member federations. Formal, well-structured.
- **Source discovery loop** - automated web search for aligned organizations. Variable quality - generates candidates that need Curator review.
- **Manual contributions** - organizations added by contributors via pull requests or issues.

Known gaps in current sourcing:
- Informal savings circles and ROSCAs (especially Africa, Southeast Asia)
- Indigenous resource governance organizations
- Neighborhood mutual aid networks (especially Global South)
- Caste-community mutual aid networks (India) - documented as out-of-scope for automated ingest, requires human knowledge

---

## Geocoding

Organizations need a `lat/lon` to appear on the map. Current geocoding rate: **~19%** (as of May 2026).

The Curator agent geocodes 50 organizations per day using Nominatim (OpenStreetMap, free, no key required). At this rate:
- 70% geocoding: approximately 300 days from current state
- This is being improved - geocoding batch size and frequency will increase

**Priority:** Organizations with a city and country are geocoded first. Organizations with only a country get a country-centroid approximation.

---

## Quality Standards

An organization passes quality review if:
1. Name is the organization's actual name (not a road, URL, or article title)
2. Country code is correct
3. Framework area is one of the canonical values
4. Source is documented

Organizations failing any check are moved to `status = 'quarantine'` for review - not deleted. Quarantined orgs are excluded from public directory but retained in DB.
