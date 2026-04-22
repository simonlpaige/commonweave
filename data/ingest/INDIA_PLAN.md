# India NGO Ingest Plan

**Status: DEFERRED - NGO Darpan no longer scrapeable; Wikidata viable but needs query tuning**
**Created: 2026-04-17**

---

## TL;DR

1. **NGO Darpan (original target) is no longer scrapeable.** The NITI Aayog site
   was rebuilt as an Angular single-page application (SPA). All URL paths now
   return the same HTML shell; data loads via JavaScript after page render.
   The old CSRF token + CodeIgniter endpoint flow documented on StackOverflow
   no longer exists. A headless browser (Playwright) would be required.

2. **Wikidata SPARQL is live and working**, but the obvious query
   (non-profit organization in India) returns mostly universities because
   Q163740 has broad transitive subclasses. Needs narrower query targets.

3. **Recommended tonight-to-tomorrow path: Wikidata SPARQL with refined
   query**, targeting cooperative society (Q200796), self-help group (Q3478540),
   NGO (Q79913), and a handful of India-specific subclasses. Expected yield:
   500-2000 usable orgs with labels in Hindi/Tamil/Bengali where available.

---

## What was probed tonight

### NGO Darpan (ngodarpan.gov.in)

Probe script: `data/ingest/india_darpan/probe_darpan.py`

Results:
- `https://ngodarpan.gov.in/` returns `<title>NPODARPAN</title>` + Angular shell HTML
- `https://ngodarpan.gov.in/index.php/ajaxcontroller/get_csrf` (old CSRF endpoint)
  returns the SAME HTML shell, not JSON
- `https://ngodarpan.gov.in/index.php/home/statewise_ngo/10/0` (old statewise
  endpoint for Maharashtra) returns the SAME HTML shell, not JSON
- Zero cookies set on initial request
- Response content-type is `text/html` everywhere, not `application/json`

**Conclusion: Darpan migrated from CodeIgniter to a JavaScript SPA. The old
scrapeable API endpoints are gone. New API endpoints exist but are called
from client-side JavaScript only. Accessing them requires either:**

- A headless browser (Playwright, Puppeteer) to render the page and capture
  the in-flight XHR/fetch calls, then replay them
- Reverse-engineering the new Angular app to find the REST API base URL
  (usually `/api/v1/...` or similar) and authentication scheme

Either path is 4-8 hours of work. Out of scope for tonight.

### Wikidata SPARQL (query.wikidata.org)

Probe script: `data/ingest/india_darpan/probe_wikidata.py`
Query: `?org wdt:P31/wdt:P279* wd:Q163740 . ?org wdt:P17 wd:Q668`

Results:
- 20 results returned successfully in < 5 seconds
- All 20 had websites (100%)
- 0/20 had non-ASCII labels (Hindi/Tamil/Bengali missing)
- Content was ALL universities (Q163740 subclass transitive closure includes
  university). Not what we want for nonprofit directory.

**Conclusion: Wikidata is responsive and returns real data, but the query
needs to be narrowed to exclude educational institutions and focus on
civic/cooperative/NGO types.**

---

## Recommended Wikidata query refinements for next session

```sparql
SELECT ?org ?orgLabel ?orgDescription ?website ?stateLabel ?typeLabel WHERE {
  VALUES ?type {
    wd:Q79913        # non-governmental organization
    wd:Q200796       # cooperative
    wd:Q3478540      # self-help group
    wd:Q48204        # cooperative society
    wd:Q163740       # nonprofit organization (with manual UNIVERSITY exclusion)
    wd:Q15932383     # charitable organization
  }
  ?org wdt:P31 ?type .
  ?org wdt:P17 wd:Q668 .

  # Exclude clearly-scoped-out types
  FILTER NOT EXISTS { ?org wdt:P31/wdt:P279* wd:Q3918 }   # university
  FILTER NOT EXISTS { ?org wdt:P31/wdt:P279* wd:Q9842 }   # primary school
  FILTER NOT EXISTS { ?org wdt:P31/wdt:P279* wd:Q9826 }   # secondary school
  FILTER NOT EXISTS { ?org wdt:P31/wdt:P279* wd:Q7188 }   # government

  OPTIONAL { ?org wdt:P856 ?website }
  OPTIONAL { ?org wdt:P131 ?state }

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "hi,ta,bn,te,ml,mr,pa,en"
  }
}
LIMIT 2000
```

Note: language preference reversed so Hindi/Tamil/Bengali/etc. labels are
selected first if available.

Expected yield: 500-1500 orgs (rough estimate; Wikidata coverage of Indian
civil society is patchy but growing).

---

## Alternative sources

### GuideStar India (now part of Candid)
- URL: https://candid.org/
- Historically had a free search UI but no public bulk download
- Candid API requires paid subscription ($500+/month for API access)
- **Not viable for Commonweave's open-data model without budget.**

### ILO SEIS (Social Economy Information System)
- Covers cooperatives and mutual societies globally
- India coverage: SEWA (Self-Employed Women's Association), IFFCO, NAFED, and
  major apex cooperatives. Tens to low hundreds of records, not thousands.
- Format: unknown; may require data request via ILO
- Worth pursuing for high-quality apex-level records, not mass ingest

### Indian government open data portal (data.gov.in)
- URL: https://data.gov.in
- Host for Receita Federal equivalents in India
- Has several registry-adjacent datasets; most are state-level
- Quality varies. Requires per-state exploration.

### Darpan via headless browser (last resort)
- Playwright or Puppeteer session against ngodarpan.gov.in
- 2-second sleeps, proper User-Agent, respect robots.txt
- Estimated 30-60 minutes of engineering + 3-5 hours of crawl time for a
  50-state sample at 1000 orgs each
- Produces ~500K records - the actual full NGO Darpan corpus
- Risk: they may add bot detection if rebuilt recently. Probe first.

---

## Payoff if ingest succeeds

The multilingual phase2_filter already has these Hindi/Tamil/Bengali terms:

Hindi (hi):
- सहकारी समिति (sahkari samiti) - cooperative society
- श्रमिक सहकारी - worker cooperative
- परस्पर सहायता (paraspar sahayata) - mutual aid
- स्वयं सहायता समूह (SHG) - self-help group
- देसी बीज (desi beej) - native seeds
- सामुदायिक स्वास्थ्य - community health
- आशा कार्यकर्ता (ASHA worker) - community health worker
- साझा भूमि (sajha bhoomi) - common land
- गोचर (gochar) - village grazing commons

Tamil (ta):
- உணவு இறையாண்மை - food sovereignty

Bengali (bn):
- সমবায় সমিতি (samabay samiti) - cooperative society
- স্বনির্ভর গোষ্ঠী (swanirbhar goshthi) - self-help group

Expected lift vs English-only scoring: significant. Indian SHG/cooperative
names often use native-script suffixes (-समिति, -সমিতি) that English
substring matching would miss entirely. The 700K NGO Darpan corpus would
give the clearest multilingual lift signal available.

---

## Recommended next steps

**Existing tooling to reuse**: `data/sources/wikidata_ingest.py` already has
full SPARQL ingest logic, country code to QID mapping (IN is already mapped),
and a set of broad ORG_TYPES queries. Starting point is there.

1. **Extend wikidata_ingest.py language handling** to prefer Hindi/Tamil/Bengali
   labels over English when available (currently it likely defaults to English).
2. **Add the narrower org-type targets** from the query above (Q79913, Q200796,
   Q3478540, etc.) and exclusion filters for universities/schools.
3. **Run the existing pipeline** against country='IN' only, with LIMIT 2000.
4. **Audit by term origin**: for each score >= 2, identify which terms fired
   (English vs Hindi/Tamil/Bengali) to quantify multilingual lift.
5. **If yield is low or duplicates are high**, revisit Darpan via Playwright
   or contact NITI Aayog for bulk data access (researcher media-relations path).
