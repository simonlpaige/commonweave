#!/usr/bin/env node
/**
 * Commonweave Agent: Cartographer
 * 
 * Coverage intelligence. Runs weekly (Sun 01:00 CT).
 * - Identifies thin regions (countries, framework areas) by org count
 * - Scores gap severity (empty = critical, thin = high, sparse = medium)
 * - Recommends specific data sources for each gap
 * - Flags taxonomy fragmentation for Curator to fix
 * - Outputs cartographer-report.json consumed by Scout, Curator, Synthesizer
 * 
 * Feeds: Scout (which regions to target), Curator (what's thin + taxonomy issues),
 *        Synthesizer (where framework evidence is weak)
 */

'use strict';

const { getStats, getThinCountries, getTaxonomyFragmentation, getSuspectOrgs } = require('./shared/db-utils');
const { writeReport } = require('./shared/report-writer');
const { loadPriorityContext } = require('./shared/priority-context');

// Known rich data sources by region - for recommendations
const REGIONAL_SOURCES = {
  'latin_america': [
    { name: 'CICOPA (cooperative federation)', url: 'https://www.cicopa.coop/members/', type: 'scrape' },
    { name: 'RIPESS LAC', url: 'https://www.ripess.org/who-are-we/ripess-network/', type: 'scrape' },
    { name: 'Wikidata SPARQL - Mexico cooperatives', query: 'cooperative Mexico', type: 'wikidata' },
  ],
  'africa': [
    { name: 'ICA Africa', url: 'https://ica.coop/en/regions/africa', type: 'scrape' },
    { name: 'COOPIGAD', url: 'https://www.coopigad.org/members', type: 'scrape' },
    { name: 'Wikidata SPARQL - Nigeria cooperatives', query: 'cooperative Nigeria', type: 'wikidata' },
  ],
  'south_east_asia': [
    { name: 'ICA Asia-Pacific', url: 'https://ica.coop/en/regions/asia-pacific', type: 'scrape' },
    { name: 'Wikidata SPARQL - Philippines cooperatives', query: 'cooperative Philippines', type: 'wikidata' },
    { name: 'DGRV Asia', url: 'https://www.dgrv.coop/en/international-cooperative-work/asia.html', type: 'scrape' },
  ],
  'middle_east': [
    { name: 'ICA MENA', url: 'https://ica.coop/en/regions/mena', type: 'scrape' },
  ],
  'central_asia': [
    { name: 'Wikidata SPARQL - Central Asia cooperatives', query: 'cooperative Kazakhstan Uzbekistan', type: 'wikidata' },
  ],
  'eastern_europe': [
    { name: 'Wikidata SPARQL - Eastern Europe cooperatives', query: 'cooperative Ukraine Romania', type: 'wikidata' },
    { name: 'CECOP', url: 'https://www.cecop.coop/about-cecop/members', type: 'scrape' },
  ],
};

// Countries mapped to region keys
const COUNTRY_TO_REGION = {
  'MX': 'latin_america', 'BR': 'latin_america', 'CO': 'latin_america', 'AR': 'latin_america',
  'NG': 'africa', 'KE': 'africa', 'ZA': 'africa', 'GH': 'africa', 'ET': 'africa', 'TZ': 'africa',
  'PH': 'south_east_asia', 'ID': 'south_east_asia', 'VN': 'south_east_asia', 'TH': 'south_east_asia',
  'EG': 'middle_east', 'SA': 'middle_east', 'TR': 'middle_east', 'IR': 'middle_east',
  'KZ': 'central_asia', 'UZ': 'central_asia', 'KG': 'central_asia',
  'UA': 'eastern_europe', 'RO': 'eastern_europe', 'PL': 'eastern_europe',
};

function scoreGap(count) {
  if (count === 0) return { severity: 'critical', score: 10 };
  if (count <= 2) return { severity: 'critical', score: 9 };
  if (count <= 5) return { severity: 'high', score: 7 };
  if (count <= 15) return { severity: 'medium', score: 5 };
  if (count <= 50) return { severity: 'low', score: 2 };
  return { severity: 'ok', score: 0 };
}

async function run() {
  const ctx = loadPriorityContext('cartographer');
  const stats = getStats();
  const thinCountries = getThinCountries(15);
  const taxonomyIssues = getTaxonomyFragmentation();
  const suspectOrgs = getSuspectOrgs(500);

  // Score each thin country and recommend sources
  const gapAnalysis = thinCountries.map(({ country_code, n }) => {
    const region = COUNTRY_TO_REGION[country_code];
    const { severity, score } = scoreGap(n);
    const sources = region ? (REGIONAL_SOURCES[region] || []) : [];
    return { country_code, count: n, severity, score, region: region || 'unknown', recommended_sources: sources };
  }).sort((a, b) => b.score - a.score);

  // Framework area coverage gaps
  const areaMap = {};
  stats.byArea.forEach(({ framework_area, n }) => { areaMap[framework_area] = n; });
  const EXPECTED_AREAS = [
    'democratic_sovereignty', 'universal_sufficiency', 'ecological_equilibrium',
    'economic_democracy', 'transparency_by_default', 'healthcare', 'education',
    'food', 'housing_land', 'energy_digital'
  ];
  const areaGaps = EXPECTED_AREAS
    .map(area => ({ area, count: areaMap[area] || 0, ...scoreGap(areaMap[area] || 0) }))
    .sort((a, b) => b.score - a.score);

  // Top priority gaps to surface to other agents
  const topPriorityGaps = gapAnalysis.filter(g => g.severity === 'critical').slice(0, 20);

  const report = {
    run_at: new Date().toISOString(),
    version: '1.0',
    db_snapshot: {
      total: stats.total,
      geocoded: stats.geocoded,
      geocoded_pct: parseFloat(stats.geocodedPct),
      countries: stats.countries,
      with_website: stats.withWebsite,
    },
    country_gaps: gapAnalysis,
    top_priority_gaps: topPriorityGaps,
    framework_area_gaps: areaGaps,
    taxonomy_fragmentation: taxonomyIssues,
    suspect_orgs: {
      count: suspectOrgs.length,
      sample: suspectOrgs.slice(0, 20),
    },
    coordinator_context_used: ctx.available,
    recommendations_for_scout: topPriorityGaps.map(g => ({
      region: g.region,
      country_code: g.country_code,
      count: g.count,
      sources: g.recommended_sources,
    })),
    recommendations_for_curator: {
      geocoding_priority: 'CRITICAL - only 19% geocoded, map is 80% empty',
      taxonomy_fixes_needed: taxonomyIssues.length,
      suspect_orgs_to_quarantine: suspectOrgs.length,
    },
  };

  const outPath = writeReport('cartographer', report);
  console.log(`[cartographer] Done. ${gapAnalysis.length} thin countries, ${suspectOrgs.length} suspect orgs, ${taxonomyIssues.length} taxonomy issues.`);
  console.log(`[cartographer] Report: ${outPath}`);
}

run().catch(e => { console.error('[cartographer] ERROR:', e.message); process.exit(1); });
