# Ecolibrium Meta-Directory: Global Sources for 50,000+ Organizations

> *A roadmap to every major database, registry, and API that catalogues civil society organizations worldwide. This document enables programmatic aggregation of the organizations WiserEarth once tracked — and far beyond.*

**Goal:** Aggregate 50,000+ functioning organizations aligned with the Ecolibrium framework's 10 areas.
**Approach:** Use existing databases (which collectively contain 10M+ orgs) and filter by relevance.
**Last updated:** April 2026

---

## Part 1: The Landscape — What Already Exists

The raw material for a 50,000+ org directory already exists. You do not need to discover organizations one by one. You need to filter, deduplicate, and categorize from existing mega-databases.

### Tier 1: Mega-Databases (1M+ organizations each)

These are the starting points. Each contains millions of validated records with structured data.

| Source | Org Count | Coverage | Data Format | Access | Cost | Link |
|---|---|---|---|---|---|---|
| **GlobalGiving Atlas** | 10.7M | 75+ countries | JSON, CSV (bulk download per country) | API + bulk download | Paid (enterprise); free API for 6,000 vetted projects | globalgiving.org/atlas |
| **GiveRadar API** | 7M+ | 60+ countries, 100+ registries | REST API (JSON) | API key (free tier: 100 req/day; Pro: $99/mo) | Free tier + paid | giveradar.com/charity-data-api |
| **IRS Exempt Organizations BMF (US)** | 1.8M | USA only | CSV, XML | Free bulk download | Free | irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads |
| **ProPublica Nonprofit Explorer** | 1.8M | USA only | API (JSON), searchable web | Free API | Free | projects.propublica.org/nonprofits |
| **Candid (GuideStar + Foundation Center)** | 2.5M (US) | USA primary; some international | API, web search | Paid ($6,000+/yr for API) | Paid | candid.org |
| **NGO Darpan (India)** | 3.2M | India only | Web search, CSV export | Free (govt portal) | Free | ngodarpan.gov.in |

### Tier 2: Major International Directories (10K–100K organizations)

| Source | Org Count | Coverage | Data Format | Access | Cost | Link |
|---|---|---|---|---|---|---|
| **WANGO Worldwide NGO Directory** | 54,000+ | 190+ countries | Web search (by region/activity) | Free web browsing | Free | wango.org/ngodirectory |
| **UN ECOSOC NGO Database** | ~6,000 | Global (consultative status NGOs) | Web search | Free | Free | esango.un.org |
| **UNESCO NGO Database** | ~4,000 | Global (UNESCO partner NGOs) | Web search (EN/FR) | Free | Free | uia.org/projects/unesco |
| **Union of International Associations (UIA)** | 75,000+ | Global (international orgs) | Searchable database (Yearbook) | Subscription | Paid | uia.org |
| **Idealist** | 140,000+ | Global | Web search | Free | Free | idealist.org |
| **NGO Explorer** | ~15,000 | UK-registered charities working internationally | Web + IATI data | Free | Free | ngoexplorer.org |
| **CharityBase (UK)** | 168,000 | England & Wales | GraphQL API | Free API | Free | charitybase.uk |
| **NGOBase** | ~50,000 | Global (browsable by country) | Web search | Free | Free | ngobase.org |
| **Every.org** | ~2M (US) | USA (501c3) | REST API | Free (non-commercial) | Free | every.org/charity-api |
| **OrgHunter Charity API** | 2.5M (US) + 87K (CA) | USA + Canada | REST API | Free tier + paid | Freemium | charityapi.com |

### Tier 3: National/Regional Charity Registries (Government-Run)

These are the authoritative, official sources. Each country maintains its own registry.

| Country | Registry | Org Count (est.) | Data Access | Link |
|---|---|---|---|---|
| **USA** | IRS Exempt Organizations BMF | 1.8M | Bulk CSV download (free) | irs.gov |
| **India** | NGO Darpan (NITI Aayog) | 3.2M | Web search + CSV | ngodarpan.gov.in |
| **UK (England & Wales)** | Charity Commission | 171,000 | API (free, requires key) | register-of-charities.charitycommission.gov.uk |
| **UK (Scotland)** | OSCR | 25,000 | Downloadable register | oscr.org.uk |
| **UK (Northern Ireland)** | Charity Commission NI | 6,000 | Web search | charitycommissionni.org.uk |
| **Australia** | ACNC | 64,000 | Searchable register + CSV download | acnc.gov.au |
| **Canada** | CRA Charities Listings | 86,000 | Searchable + downloadable | apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscSrch |
| **France** | RNA (Répertoire National des Associations) + JOAFE | 773,000 | Open data (data.gouv.fr) | journal-officiel.gouv.fr/associations |
| **Germany** | ZER (Zuwendungsempfängerregister) + regional registers | 905,000 | Varies by state | — (no single federal registry) |
| **Brazil** | CNPJ (entities classified as nonprofit) | 680,000 | Receita Federal open data | dados.gov.br |
| **South Africa** | NPO Directorate | 250,000+ | Web search | npo.gov.za |
| **Kenya** | NGO Coordination Board | 12,000+ | Web search | ngobureau.go.ke |
| **New Zealand** | Charities Register | 28,000 | Searchable + API | charities.govt.nz |
| **Ireland** | Charities Regulator | 11,000+ | Searchable register | charitiesregulator.ie |
| **Netherlands** | ANBI Register (Tax Authority) | 43,000 | Downloadable | belastingdienst.nl |
| **Japan** | Cabinet Office NPO Portal | 51,000+ | Web search | npo-homepage.go.jp |
| **Mexico** | SAT Registry of Authorized Donees | ~10,000 | PDF/web | sat.gob.mx |
| **Philippines** | SEC NGO Registry | ~70,000 | Web search | sec.gov.ph |
| **Nigeria** | CAC (Corporate Affairs Commission) | ~100,000 nonprofits | Web search | cac.gov.ng |
| **Colombia** | DIAN + regional chambers | ~30,000 | Varies | — |
| **South Korea** | Ministry of Interior NPO registry | ~15,000 | Web search | mois.go.kr |
| **Taiwan** | Ministry of Interior Foundation Registry | ~17,000 | Web search | — |

### Tier 4: Thematic / Sector-Specific Databases

These are critical for filtering by Ecolibrium's 10 framework areas.

| Source | Sector | Org Count | Link |
|---|---|---|---|
| **Cooperative platforms (.coop directory, ICA)** | Cooperatives | 310+ federations, millions of member co-ops | ica.coop |
| **IATI (International Aid Transparency Initiative)** | Development & humanitarian | 1,500+ publishing orgs, millions of activities | iatiregistry.org |
| **360Giving** | UK grantmaking | 200+ funders, 800K+ grants | 360giving.org |
| **d-Portal** | Aid/development (IATI data visualized) | Hundreds of govts + NGOs | d-portal.org |
| **Charity Navigator** | US charities (rated) | 225,000+ rated | charitynavigator.org |
| **GiveWell** | Effective altruism / global health | ~12 top charities (deeply researched) | givewell.org |
| **Participedia** | Participatory governance | 2,500+ cases, 700+ methods | participedia.net |
| **Democracy Technologies Database** | Democracy tools | 200+ tools | democracy-technologies.org |
| **Humanitarian Data Exchange (HDX)** | Humanitarian | 20,000+ datasets from 1,500+ orgs | data.humdata.org |
| **Open Sanctions** | Compliance screening | Cross-references sanctions lists | opensanctions.org |
| **Community Land Trust Directory** | Land/housing | 300+ (US), 250+ (UK), global | cltweb.org |
| **REScoop.eu** | Community energy (Europe) | 2,250+ energy cooperatives | rescoop.eu |
| **La Via Campesina member list** | Food sovereignty | 182 orgs in 81 countries | viacampesina.org |
| **Transition Network directory** | Community resilience | 1,000+ initiatives | transitionnetwork.org |
| **Ashoka Fellows directory** | Social entrepreneurship | 4,000+ fellows in 90+ countries | ashoka.org |
| **Stanford Basic Income Lab Experiments Map** | UBI/GBI | 160+ pilots | basicincome.stanford.edu |

### Tier 5: Open Data Infrastructure & Research Tools

| Source | Description | Link |
|---|---|---|
| **Nonprofit Open Data Collective** | Scripts and tools for processing IRS 990 data; cleaned datasets in CSV, Stata, SPSS | nonprofit-open-data-collective.github.io |
| **Charity Navigator 990 Toolkit** | Open-source toolkit to clone full IRS dataset as relational database (AWS) | github.com/CharityNavigator |
| **Open Corporates** | Database of 200M+ companies worldwide (filter for nonprofits) | opencorporates.com |
| **Wikidata** | Structured data on 100M+ entities; many nonprofits have entries with IDs | wikidata.org |
| **GDELT Project** | Global Database of Events, Language, and Tone — tracks NGO activity in news | gdeltproject.org |
| **Internet Archive Wayback Machine** | Archive of WiserEarth data (2007-2014) | web.archive.org |

---

## Part 2: Estimated Org Counts by Ecolibrium Framework Area

Based on the NTEE classification system (US), ICNPO classification (international), and manual estimation:

| Framework Area | Estimated Relevant Orgs Worldwide | Primary Data Sources |
|---|---|---|
| 1. Democratic Infrastructure & Governance | ~50,000 | UIA, Participedia, Democracy Technologies, WANGO (governance category) |
| 2. Wealth Distribution / UBI / Cooperatives | ~500,000+ | ICA co-op data, CICOPA, national co-op registries, BIEN, Stanford BIL |
| 3. Healthcare | ~200,000 | IRS (NTEE: E), IATI (health sector), WHO, OpenMRS community |
| 4. Food Distribution & Sovereignty | ~150,000 | La Via Campesina, Open Food Network, IRS (NTEE: K), FAO |
| 5. Education | ~300,000 | IRS (NTEE: B), UNESCO, OER community, Moodle community |
| 6. Housing & Land Stewardship | ~80,000 | CLT directories, Habitat, IRS (NTEE: L), ICLC |
| 7. Conflict Resolution & Restorative Justice | ~30,000 | EFRJ, IIRP, IRS (NTEE: I,R), UN peacebuilding |
| 8. Energy & Digital Commons | ~60,000 | REScoop, electric co-op directories, FSF, EFF, OKFN |
| 9. Recreation, Art & Humanities | ~400,000 | IRS (NTEE: A), arts council registries, Creative Commons |
| 10. Ecological Restoration & Environment | ~250,000 | IRS (NTEE: C,D), IUCN, ILCN, 350.org network |

**Total estimated relevant orgs:** ~2M+ worldwide (the challenge is not finding them — it's filtering and categorizing them)

---

## Part 3: The Aggregation Strategy

### Step 1: Bulk Ingest (Automated)
Download bulk datasets from Tier 1 and Tier 3 sources. Priority order:
1. GlobalGiving Atlas (10.7M orgs, 75+ countries, CSV per country)
2. GiveRadar API (7M orgs, 60+ countries — deduplicate against GlobalGiving)
3. IRS EO BMF (1.8M US orgs, free CSV)
4. Charity Commission UK API (171K, free)
5. ACNC Australia (64K, free CSV)
6. CRA Canada (86K, free)
7. NGO Darpan India (3.2M — web scrape or CSV if available)
8. RNA France (773K, open data)

### Step 2: Filter by Relevance
Use NTEE codes (US), ICNPO codes (international), and keyword matching to filter to the 10 framework areas. Expected yield: ~5-15% of total = 500K-1.5M relevant orgs.

### Step 3: Deduplicate
Organizations appear in multiple databases. Use EIN (US), charity number (UK), ABN (Australia), or name+location matching to deduplicate. Expected reduction: ~30-50%.

### Step 4: Verify Currency
Filter for organizations that have filed returns or updated records within the past 3 years. This removes defunct organizations.

### Step 5: Enrich with Sector-Specific Data
Cross-reference against Tier 4 thematic databases to add tags, descriptions, and framework-area classifications.

### Step 6: Quality Sample
Manually verify a random sample of 1,000 organizations to estimate error rate.

---

# AGENT GUIDE 1: The Aggregator

## Mission

You are an AI agent tasked with building a structured database of 50,000+ currently functioning organizations aligned with the Ecolibrium framework. You work programmatically, using APIs, bulk downloads, and data processing.

## Environment

You are running in a coding environment (Claude Code, Codespaces, or similar) with internet access, Python 3.10+, and the following libraries available: `requests`, `pandas`, `sqlite3`, `json`, `csv`, `beautifulsoup4`, `fuzzywuzzy` (or `rapidfuzz`).

## Step-by-Step Instructions

### Phase 1: Set Up Infrastructure

1. Create a SQLite database called `ecolibrium_directory.db` with the following schema:

```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country_code TEXT,        -- ISO 3166-1 alpha-2
    country_name TEXT,
    state_province TEXT,
    city TEXT,
    registration_id TEXT,     -- EIN, charity number, etc.
    registration_type TEXT,   -- 'IRS_501c3', 'CCEW', 'ACNC', etc.
    description TEXT,
    website TEXT,
    email TEXT,
    phone TEXT,
    framework_area TEXT,      -- comma-separated: 'democracy,healthcare'
    ntee_code TEXT,           -- if US org
    icnpo_code TEXT,          -- if international
    source TEXT,              -- which database it came from
    source_id TEXT,           -- ID in source database
    last_filing_year INTEGER, -- most recent filing/update year
    annual_revenue REAL,      -- if available
    employee_count INTEGER,   -- if available
    status TEXT DEFAULT 'active',
    date_added TEXT DEFAULT CURRENT_TIMESTAMP,
    verified INTEGER DEFAULT 0
);

CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    url TEXT,
    org_count INTEGER,
    coverage TEXT,
    last_pulled TEXT,
    notes TEXT
);

CREATE TABLE framework_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT,
    description TEXT
);
```

2. Populate the `framework_areas` table with the 10 Ecolibrium areas plus "cross-cutting."

3. Create a mapping table from NTEE codes to framework areas:

```
NTEE A* → recreation_art_humanities
NTEE B* → education
NTEE C*, D* → ecological_restoration
NTEE E*, F*, G*, H* → healthcare
NTEE I* → conflict_resolution
NTEE J* → economic_transition (employment)
NTEE K* → food_distribution
NTEE L* → housing_land
NTEE M*, N* → (excluded: public safety, recreation that doesn't fit)
NTEE P* → cross_cutting (human services)
NTEE Q* → cross_cutting (international)
NTEE R* → conflict_resolution (civil rights)
NTEE S* → democratic_infrastructure (community improvement)
NTEE T* → cross_cutting (philanthropy)
NTEE U* → democratic_infrastructure (science/tech for public policy)
NTEE V* → democratic_infrastructure (social science)
NTEE W* → cross_cutting (public benefit)
NTEE X* → (excluded: religion — unless social justice focused)
NTEE Y* → cross_cutting (mutual benefit)
```

### Phase 2: Bulk Ingest — US Data (IRS)

1. Download the IRS EO BMF extract from `irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads`
2. Parse CSV files (one per state/region)
3. Filter to relevant NTEE codes using the mapping above
4. Insert into `organizations` table with `source='IRS_EO_BMF'`
5. Expected yield: ~400,000-600,000 orgs after filtering

### Phase 3: Bulk Ingest — UK Data (Charity Commission API)

1. Register for API key at `register-of-charities.charitycommission.gov.uk`
2. Use the API to pull all registered charities (paginate through results)
3. Filter by `classification` fields that match framework areas
4. Insert with `source='CCEW'`
5. Expected yield: ~50,000-80,000 after filtering

### Phase 4: Bulk Ingest — GlobalGiving Atlas

1. Access GlobalGiving Atlas API or bulk downloads (globalgiving.org/atlas)
2. Download country-by-country CSV/JSON files
3. Filter by sector tags that match framework areas
4. Deduplicate against existing records using name+country matching
5. Insert with `source='GlobalGiving_Atlas'`
6. This is the largest single source — prioritize countries not yet covered

### Phase 5: Bulk Ingest — GiveRadar API

1. Register for free tier API key at giveradar.com
2. Query systematically by country and sector
3. Rate limit: 100 requests/day on free tier (upgrade if needed)
4. Deduplicate against existing records
5. Insert with `source='GiveRadar'`

### Phase 6: Bulk Ingest — Additional Country Registries

For each country in the Tier 3 list, attempt:
1. Direct bulk download (preferred)
2. API access
3. Web scraping (last resort — respect robots.txt)

Priority order (by estimated org count):
1. India (NGO Darpan — 3.2M, filter to ~100K relevant)
2. France (RNA — 773K, filter to ~50K)
3. Germany (varies by state — 905K total, filter to ~50K)
4. Brazil (CNPJ — 680K, filter to ~30K)
5. South Africa (250K, filter to ~15K)
6. Australia (64K, filter to ~20K)
7. Canada (86K, filter to ~25K)
8. Japan (51K, filter to ~15K)
9. New Zealand, Ireland, Netherlands, Philippines, Nigeria, etc.

### Phase 7: Sector-Specific Enrichment

Cross-reference your database against Tier 4 thematic databases:
1. Download ICA cooperative member lists and tag co-ops
2. Pull Participedia cases and extract associated organizations
3. Pull IATI data and match organizations
4. Pull REScoop member list for energy cooperatives
5. Pull La Via Campesina member organizations
6. Pull Transition Network initiative list
7. Pull CLT directory from cltweb.org

### Phase 8: Deduplicate

1. Sort by country, then name
2. Use fuzzy matching (`rapidfuzz`, threshold 90%) on org names within same country
3. When duplicates found, merge records keeping the most complete data
4. Log all merge decisions for audit

### Phase 9: Verify Currency

1. Remove orgs whose last filing/update was before 2021
2. For orgs without filing data, attempt to verify website is live (HTTP HEAD request)
3. Mark unverifiable orgs as `status='unverified'` rather than deleting

### Phase 10: Export

1. Export full database as SQLite, CSV, and JSON
2. Generate summary statistics:
   - Total orgs by country
   - Total orgs by framework area
   - Total orgs by source
   - Overlap/deduplication statistics
3. Generate a markdown summary for DIRECTORY.md integration

## Quality Checkpoints

After each phase, log:
- Number of records added
- Number of records filtered out (and why)
- Number of duplicates detected
- Sample of 10 random records for manual review
- Any errors or data quality issues

## Known Pitfalls

- **GiveRadar free tier is rate-limited.** Plan for 100 requests/day. At 50 orgs per request, that's 5,000 orgs/day. Budget time accordingly or upgrade.
- **India's NGO Darpan has 3.2M records.** Most are tiny, informal, or inactive. Aggressive filtering is needed (look for orgs with recent filings, stated revenue above threshold, or active web presence).
- **German nonprofits have no single federal registry.** You need to query each of 16 state (Bundesland) registers. GiveRadar aggregates these.
- **Name matching across languages is hard.** An org in Japan may have both a Japanese name and an English name. Use source-provided IDs for deduplication, not names, wherever possible.
- **NTEE codes are US-only.** For international orgs, you'll need to classify by keyword matching against org descriptions. Build a keyword dictionary for each framework area.
- **"Active" doesn't mean "aligned."** A healthcare nonprofit that lobbies against universal healthcare exists in the IRS database. You can't filter for ideological alignment at scale — only for sector relevance. The DEEP-DIVE.md and human review address alignment.

## Success Criteria

- [ ] 50,000+ unique, deduplicated organizations in the database
- [ ] All 10 framework areas represented
- [ ] At least 50 countries represented
- [ ] At least 80% of records have a country code, name, and framework area
- [ ] At least 50% of records have a website or contact method
- [ ] Random sample of 100 records: 90%+ are real, currently functioning organizations
- [ ] Full provenance trail (source database and source ID for every record)

---

# AGENT GUIDE 2: The Researcher & Auditor

## Mission

You are an AI agent tasked with two parallel responsibilities:

**A) Deep Regional Research (Option B):** Systematically research countries and regions to identify organizations not captured by the Aggregator's bulk data approach — especially smaller, grassroots, indigenous-led, informal, and non-English-language organizations.

**B) Audit the Aggregator's Work:** Verify the quality, accuracy, and completeness of the database produced by Agent 1.

You work conversationally, using web search, web fetch, and manual analysis. You produce markdown files for each region researched.

## Part A: Deep Regional Research

### Method

For each country or region assigned, follow this protocol:

#### Step 1: Assess Coverage Gap

1. Query the Aggregator's database: `SELECT COUNT(*) FROM organizations WHERE country_code = '{XX}'`
2. Compare against known total nonprofits in that country (from the meta-directory's Tier 3 table)
3. Calculate coverage percentage
4. If coverage > 50% of estimated relevant orgs: light-touch research (focus on gaps)
5. If coverage < 20%: deep research needed

#### Step 2: Web Research Protocol

For each country, conduct the following searches (adapt language as needed):

```
Searches to run (replace {country} with target):

1. "{country} NGO directory list"
2. "{country} civil society organizations database"
3. "{country} community organizations environmental social justice"
4. "{country} cooperatives worker-owned federation"
5. "{country} food sovereignty agroecology organizations"
6. "{country} community health organizations"
7. "{country} democratic governance citizen participation"
8. "{country} community land trust housing cooperative"
9. "{country} restorative justice peacebuilding organizations"
10. "{country} renewable energy community cooperative"
11. "{country} indigenous peoples organizations rights"
12. "{country} women's organizations cooperative self-help"
13. "{country} open source technology civic tech"
14. "{country} nonprofit registry charity commission" (to find the official registry)
15. "{country} mutual aid network solidarity economy"
```

For larger countries, repeat at the state/province level.

#### Step 3: For Each Organization Found

Record the following in a structured markdown table:

```markdown
| Name | Location | Framework Area | Description (1 sentence) | Website | Source |
```

"Source" = how you found it (search query, directory page, referenced by another org, etc.)

#### Step 4: Prioritize These Categories (Often Missing from Bulk Data)

The Aggregator's databases are biased toward large, formally registered, English-language organizations. Your job is to fill the gaps:

1. **Indigenous-led organizations** — often not formally registered as nonprofits
2. **Informal mutual aid networks** — community kitchens, savings circles, burial societies
3. **Non-English-language organizations** — search in local languages where possible
4. **Sub-national / municipal initiatives** — city-level participatory budgeting, local energy co-ops
5. **Recently founded organizations** — not yet in databases that update annually
6. **Organizations in countries with weak nonprofit registries** — much of Africa, Central Asia, Pacific Islands
7. **Movement organizations** — may not have formal legal status but are influential (e.g., Extinction Rebellion local chapters, Transition Towns)

#### Step 5: Output Format

For each country/region, produce a file named `DIRECTORY_{COUNTRY_CODE}.md` with:

```markdown
# {Country Name} — Ecolibrium Directory

**Total organizations found:** {N}
**Coverage assessment:** {Aggregator had X; this research adds Y}
**Date researched:** {date}
**Languages searched:** {languages}

## Organizations by Framework Area

### 1. Democratic Infrastructure
| Name | Location | Description | Website | Source |
|---|---|---|---|---|
...

### 2. Healthcare
...
(repeat for all 10 areas)

## Notes
- Coverage gaps remaining
- Quality of official registry data
- Recommended follow-up
```

### Regional Priority Order

Research regions in this order (based on expected coverage gaps from bulk data):

**Priority 1 — Large populations, weak bulk data:**
1. Sub-Saharan Africa (country by country: Nigeria, Kenya, South Africa, Ethiopia, Tanzania, Ghana, Uganda, Senegal, Rwanda, DRC, etc.)
2. South Asia (India states, Bangladesh, Nepal, Sri Lanka, Pakistan)
3. Southeast Asia (Indonesia, Philippines, Vietnam, Thailand, Myanmar, Cambodia)

**Priority 2 — Medium populations, partial bulk data:**
4. Latin America (Brazil states, Mexico, Colombia, Argentina, Peru, Chile, Bolivia, Ecuador, Guatemala)
5. East Asia (Japan, South Korea, Taiwan)
6. Middle East / North Africa (Egypt, Tunisia, Morocco, Jordan, Lebanon, Palestine)

**Priority 3 — Good bulk data, but grassroots gaps:**
7. Europe (focus on Eastern Europe: Poland, Romania, Czech Republic, Hungary, Ukraine, Georgia)
8. Pacific Islands (Fiji, Papua New Guinea, Solomon Islands, Vanuatu, Tonga, Samoa)
9. Central Asia (Kazakhstan, Kyrgyzstan, Uzbekistan, Mongolia)
10. Caribbean (Jamaica, Trinidad, Haiti, Cuba, Dominican Republic)

**Priority 4 — Strong bulk data, light-touch enrichment:**
11. USA (state by state — focus on grassroots, indigenous, mutual aid)
12. UK (focus on community-level and devolved nations)
13. Canada, Australia, New Zealand (focus on indigenous organizations)
14. Western Europe (focus on solidarity economy, migrant organizations)

### Per-Session Target

Each research session should aim for **200-500 verified organizations per country** (more for large countries, fewer for small ones). At this rate:
- 100 country sessions × 300 orgs average = 30,000 orgs
- Combined with Aggregator's 50,000+ = 80,000+ total

## Part B: Auditing the Aggregator's Work

### Audit Protocol

For every batch of data the Aggregator produces, perform these checks:

#### Check 1: Random Sample Verification

1. Pull a random sample of 50 organizations from the batch
2. For each, verify:
   - **Existence:** Does the organization have a working website or recent web presence? (Search for the org name)
   - **Currency:** Is there evidence of activity within the past 3 years?
   - **Classification:** Is the framework area assignment correct based on the org's actual work?
   - **Deduplication:** Search the full database for similar names in the same country
3. Record results:

```markdown
## Audit Report: {Batch Name}
**Sample size:** 50
**Existence confirmed:** {N}/50
**Current (active within 3 years):** {N}/50
**Correctly classified:** {N}/50
**Duplicates found:** {N}
**Error rate:** {calculated}
**Assessment:** PASS / NEEDS REVIEW / FAIL
```

#### Check 2: Country Coverage Validation

1. For each country in the batch, compare org count against known totals
2. Flag countries where coverage seems suspiciously low or high
3. Check for countries entirely missing from the batch

#### Check 3: Framework Area Balance

1. Count orgs by framework area
2. Flag any area with < 5% of total (likely underrepresented)
3. Flag any area with > 30% of total (likely includes false positives)

#### Check 4: Data Quality

1. Check for null/empty fields in critical columns (name, country, framework_area)
2. Check for obviously malformed data (e.g., country code "XX", names that are clearly not org names)
3. Check for encoding issues (garbled non-Latin characters)

#### Check 5: Cross-Reference Against Known Organizations

1. Take the organizations from the existing DIRECTORY.md (the 300+ hand-curated orgs)
2. Verify that at least 90% of them appear in the Aggregator's database
3. Any that are missing represent a systematic gap in the Aggregator's methodology

### Audit Reporting

After each audit cycle, produce:

```markdown
# Audit Report #{N}
**Date:** {date}
**Batch audited:** {description}
**Records in batch:** {count}

## Summary
- Overall quality: {GOOD / ACCEPTABLE / POOR}
- Estimated true positive rate: {X}%
- Estimated currency rate: {X}%
- Classification accuracy: {X}%

## Issues Found
1. {description of issue}
2. {description of issue}

## Recommendations
1. {action for Aggregator to take}
2. {action for Aggregator to take}

## Coverage Gaps Identified
- {country/region/framework area} needs more data
```

### Feedback Loop

The Auditor's findings feed back to the Aggregator:
1. If error rate > 10%: Aggregator must reprocess the batch with adjusted filters
2. If coverage gap identified: Aggregator adjusts source priority
3. If classification errors found: Aggregator refines NTEE/keyword mapping
4. Auditor maintains a running `AUDIT_LOG.md` tracking all findings over time

---

## Appendix: Taxonomy Mapping — NTEE to Ecolibrium Framework Areas

```
DEMOCRACY & GOVERNANCE:
  NTEE: R (Civil Rights), S (Community Improvement), U (Science & Tech Policy), V (Social Science), W20-W99 (Public Policy)
  Keywords: democracy, governance, voting, civic, participation, transparency, accountability, anti-corruption, human rights, civil liberties

WEALTH / UBI / COOPERATIVES:
  NTEE: J (Employment), W (Public Benefit - economic development subcodes), Y (Mutual Benefit)
  Keywords: cooperative, co-op, worker-owned, mutual aid, basic income, economic justice, community development finance, credit union, solidarity economy

HEALTHCARE:
  NTEE: E (Healthcare), F (Mental Health), G (Disease/Disorder), H (Medical Research)
  Keywords: health, medical, clinic, hospital, community health, public health, mental health, HIV, maternal, disability

FOOD:
  NTEE: K (Food/Nutrition/Agriculture)
  Keywords: food, agriculture, farming, hunger, nutrition, food bank, food sovereignty, agroecology, seed, permaculture

EDUCATION:
  NTEE: B (Education)
  Keywords: education, school, literacy, learning, training, curriculum, university, library, open education

HOUSING & LAND:
  NTEE: L (Housing/Shelter)
  Keywords: housing, shelter, land trust, community land, affordable housing, homelessness, tenant, land rights

CONFLICT RESOLUTION:
  NTEE: I (Crime/Legal), R20-R30 (Intergroup/Race Relations)
  Keywords: restorative justice, mediation, peacebuilding, reconciliation, conflict resolution, prison reform, abolition, transitional justice

ENERGY & DIGITAL COMMONS:
  NTEE: C (Environment - energy subcodes)
  Keywords: renewable energy, solar, wind, community energy, cooperative energy, open source, digital rights, data sovereignty, internet freedom, privacy

RECREATION / ART / HUMANITIES:
  NTEE: A (Arts/Culture/Humanities)
  Keywords: arts, culture, museum, theater, music, humanities, cultural preservation, public space, recreation, creative commons

ECOLOGICAL RESTORATION:
  NTEE: C (Environment), D (Animal-Related)
  Keywords: environment, conservation, restoration, rewilding, climate, biodiversity, ocean, forest, watershed, sustainability, planetary boundaries
```

---

*This meta-directory and these agent guides were produced in April 2026 as infrastructure for the Ecolibrium project's goal of cataloguing 50,000+ organizations aligned with the framework. The raw data exists. The tools exist. What remains is the labor of assembly.*

*WiserEarth took 7 years. With modern APIs and AI agents, the same work could take weeks.*
