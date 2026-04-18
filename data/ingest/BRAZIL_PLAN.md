# Brazil CNPJ Ingest Plan

**Status: DEFERRED - no local data, no low-cost bulk path available tonight**
**Created: 2026-04-17**

---

## What exists

The Brazilian federal business registry (CNPJ) is maintained by Receita Federal
(the Brazilian IRS). It covers all registered legal entities, including nonprofits.

### Full bulk download (Receita Federal)
- URL: https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
- Format: ZIP archives of pipe-delimited flat files (one per data type)
- **Size: 30-40 GB compressed, 100+ GB uncompressed**
- Update frequency: monthly
- Filter path: Estabelecimentos file has `natureza_juridica` field; nonprofits
  are identified by the following codes:
  - 3031: Entidade Fundacional ou Entidade de Utilidade Publica
  - 3069: Fundacao Privada
  - 3999: Associacao Privada
  - 3301, 3310, 3379, 3395: Various association subtypes
  - 3203: Servico Social Autonomo (social service)
  - EXCLUDE 3220: Organizacao Religiosa (matches existing NEGATIVE list logic)
- After filtering by those codes: estimated 400,000-600,000 entities
- After alignment scoring: a fraction; cooperatives (cooperativa, economia
  solidaria, etc.) should score >=2 via Portuguese terms in phase2_filter

**Why deferred: 30-40 GB download is outside scope for tonight's session.**

### publica.cnpj.ws API (spot lookup)
- URL: https://publica.cnpj.ws/cnpj/{14-digit-cnpj}
- Rate limit: ~3 requests/second (informal; no official published limit)
- Returns: JSON with razao_social (name), natureza_juridica, atividade_principal, socios, etc.
- **Problem: requires knowing CNPJ numbers in advance.** There is no search-by-type endpoint.
  You cannot say "give me all Associacoes Privadas" - you can only look up by ID.
- Cost: free, no auth

### Alternative: OpenCNPJ.org mirror
- URL: https://opencnpj.org (Brazilian community mirror of Receita Federal data)
- Some mirrors expose subset APIs by natureza_juridica
- Not tested tonight; worth checking for a pre-filtered nonprofits endpoint

### Alternative: Wikidata SPARQL
- Query: `?item wdt:P17 wd:Q155 ; wdt:P31 wd:Q163740` (Brazilian nonprofit orgs)
- Estimated yield: 2,000-5,000 entities with label, website, sometimes description
- Free, no rate limits for small queries
- Missing: most small cooperatives are not on Wikidata

---

## Recommended path for MVP (next session)

**Option A (best data, high effort):** Download only the Empresas + Estabelecimentos
files (~2-4 GB each), not all 14 zip files. Filter by natureza_juridica locally.
Time: 1-2 hours download + 30 min processing. Requires disk space check first.

**Option B (quick win, limited scope):** Query Wikidata SPARQL for Brazilian
nonprofits with Portuguese labels. Should return 2,000-5,000 orgs, enough to
test the Portuguese scoring pipeline. Can be done in 30 minutes.

**Option C (targeted, medium effort):** Use the publica.cnpj.ws API with a
curated seed list of known aligned orgs (cooperatives, MST, CRESOL, etc.) and
their CNPJ numbers to demonstrate Portuguese scoring. Not systematic but fast.

---

## Expected payoff from Portuguese scoring

The current phase2_filter.py includes these Portuguese terms (via i18n_terms.py):
  - cooperativa, cooperativa de trabalho, cooperativa popular
  - ajuda mutua, economia solidaria, economia popular
  - quilombo, baldios, terras de uso comum, fundo de pasto
  - agroecologia, soberania alimentar, sementes crioulas
  - saude comunitaria, agente comunitario de saude
  - orçamento participativo, assembleia popular

An English-only scorer would miss Brazilian orgs whose names/descriptions use
these terms without any English equivalent. The multilingual scorer should
show measurable lift on economia solidaria cooperatives and quilombo associations
that an English-only pipeline would score 0 or 1.

---

## Required disk space estimate

Option A (two Receita Federal zips): 5-10 GB download, 30-50 GB uncompressed.
Check disk first with: `Get-PSDrive C | Select-Object Used, Free`

Option B (Wikidata): No disk requirement beyond normal Python execution.

---

## Why not tonight

The full CNPJ download is 30-40 GB. Even the two targeted zip files (Empresas +
Estabelecimentos) are 4-8 GB each and would take 30-60 minutes to download on
a typical connection. The spot API requires known CNPJ numbers. No local Brazil
data exists in data/sources/brazil/. No half-done download was started.
