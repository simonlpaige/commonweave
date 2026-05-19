#!/usr/bin/env node
/**
 * Commonweave Agent: Curator
 *
 * Data quality. Runs daily (03:00 CT).
 * Priority order (from Coordinator + red-team):
 *   1. QUARANTINE suspect non-orgs (roads, Reddit posts, Wikipedia articles)
 *   2. GEOCODE ungeocoded orgs until rate >= 70% (uses Nominatim, free)
 *   3. FIX taxonomy fragmentation (normalize framework_area variants)
 *   4. ENRICH thin records (missing model_type, framework_area classification)
 *
 * Reads: cartographer report (for taxonomy issues + suspect list)
 * Writes: curator-report.json consumed by Publisher + Coordinator
 */

'use strict';

const https = require('https');
const { getStats, getSuspectOrgs, getUngeocodedSample, getTaxonomyFragmentation, quarantineOrg, updateOrgField, run: dbRun } = require('./shared/db-utils');
const { writeReport, readReport } = require('./shared/report-writer');
const { loadPriorityContext } = require('./shared/priority-context');

// Nominatim geocoding (free, no key, strict 1 req/sec - be a good citizen)
let lastNominatimCall = 0;

function geocodeWithNominatim(name, city, countryCode) {
  return new Promise((resolve) => {
    // Use just city + country for the query - org name often confuses Nominatim
    const parts = [city, countryCode].filter(Boolean);
    if (parts.length === 0) return resolve(null); // no location data
    const q = encodeURIComponent(parts.join(', '));
    const opts = {
      hostname: 'nominatim.openstreetmap.org',
      path: `/search?q=${q}&format=json&limit=1`,
      headers: { 'User-Agent': 'Commonweave-Directory/1.0 (simonlpaige@gmail.com)' },
    };
    const req = https.get(opts, (res) => {
      let data = '';
      if (res.statusCode === 429) {
        console.log('[curator] Nominatim rate limited - backing off 30s');
        setTimeout(() => resolve(null), 30000);
        return;
      }
      res.on('data', d => { data += d; });
      res.on('end', () => {
        try {
          const results = JSON.parse(data);
          if (results.length > 0) {
            resolve({ lat: parseFloat(results[0].lat), lon: parseFloat(results[0].lon), source: 'nominatim' });
          } else {
            resolve(null);
          }
        } catch { resolve(null); }
      });
    });
    req.on('error', () => resolve(null));
    req.setTimeout(8000, () => { req.destroy(); resolve(null); });
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// Known taxonomy normalizations
const TAXONOMY_NORMALIZATION = {
  'democratic sovereignty': 'democratic_sovereignty',
  'democratic-sovereignty': 'democratic_sovereignty',
  'land commons': 'housing_land',
  'land_commons': 'housing_land',
  'cooperatives': 'economic_democracy',
  'coverage repair': null, // remove/reclassify these
  'unknown': null,
  'democracy': 'democratic_sovereignty',
  'conflict': 'democratic_sovereignty',
};

async function quarantineSuspects() {
  const suspects = getSuspectOrgs(2000);
  if (suspects.length === 0) return { quarantined: 0 };

  // Mark as status='quarantine' rather than deleting - preserves data for review
  let count = 0;
  for (const org of suspects) {
    quarantineOrg(org.id);
    count++;
  }
  return { quarantined: count, sample: suspects.slice(0, 10).map(o => o.name) };
}

async function fixTaxonomy() {
  let fixed = 0;
  for (const [from, to] of Object.entries(TAXONOMY_NORMALIZATION)) {
    if (to === null) continue; // skip nulls for now - need human decision
    const fromEsc = from.replace(/'/g, "''");
    const toEsc = to.replace(/'/g, "''");
    dbRun(`UPDATE organizations SET framework_area = '${toEsc}', updated_at = datetime('now') WHERE framework_area = '${fromEsc}'`);
    fixed++; // sqlite3 CLI doesn't return changes count easily; just count executed
  }
  return { fixed };
}

async function geocodeBatch(batchSize = 50) {
  const sample = getUngeocodedSample(batchSize);
  let geocoded = 0;
  let failed = 0;

  for (const org of sample) {
    const result = await geocodeWithNominatim(org.name, org.city, org.country_code);
    if (result) {
      updateOrgField(org.id, 'lat', result.lat);
      updateOrgField(org.id, 'lon', result.lon);
      updateOrgField(org.id, 'geo_source', result.source);
      geocoded++;
    } else {
      failed++;
    }
    await sleep(1500); // Nominatim: be a good citizen, max ~40/min but we do 1/1.5s to be safe
  }
  return { attempted: sample.length, geocoded, failed };
}

async function run() {
  const ctx = loadPriorityContext('curator');
  const cartReport = readReport('cartographer');

  const statsBefore = getStats();
  const results = {};

  // 1. Quarantine suspects
  console.log('[curator] Step 1: Quarantine suspect non-orgs...');
  results.quarantine = await quarantineSuspects();
  console.log(`[curator] Quarantined ${results.quarantine.quarantined} suspect entries`);

  // 2. Fix taxonomy
  console.log('[curator] Step 2: Fix taxonomy fragmentation...');
  results.taxonomy = await fixTaxonomy();
  console.log(`[curator] Fixed ${results.taxonomy.fixed} taxonomy entries`);

  // 3. Geocode batch (50 per run = ~1 min, safe for daily cron)
  const geocodePct = statsBefore.geocoded / statsBefore.total * 100;
  let geocodeResult = { skipped: true, reason: 'geocode rate already >70%' };
  if (geocodePct < 70) {
    console.log(`[curator] Step 3: Geocoding (current: ${geocodePct.toFixed(1)}%)...`);
    geocodeResult = await geocodeBatch(50);
    console.log(`[curator] Geocoded ${geocodeResult.geocoded}/${geocodeResult.attempted}`);
  } else {
    console.log('[curator] Geocoding complete (>70%), skipping batch');
  }
  results.geocoding = geocodeResult;

  const statsAfter = getStats();
  const taxonomyIssues = getTaxonomyFragmentation();

  const report = {
    run_at: new Date().toISOString(),
    version: '1.0',
    before: { total: statsBefore.total, geocoded: statsBefore.geocoded, geocoded_pct: parseFloat(statsBefore.geocodedPct) },
    after: { total: statsAfter.total, geocoded: statsAfter.geocoded, geocoded_pct: parseFloat(statsAfter.geocodedPct) },
    quarantine: results.quarantine,
    taxonomy_fixes: results.taxonomy,
    geocoding: results.geocoding,
    remaining_taxonomy_issues: taxonomyIssues.length,
    geocoding_to_70pct: {
      needed: Math.max(0, Math.round(statsAfter.total * 0.70) - statsAfter.geocoded),
      at_50_per_day_days: Math.ceil(Math.max(0, Math.round(statsAfter.total * 0.70) - statsAfter.geocoded) / 50),
    },
    coordinator_context_used: ctx.available,
    cartographer_input_used: !!cartReport,
  };

  const outPath = writeReport('curator', report);
  console.log(`[curator] Done. Report: ${outPath}`);
}

run().catch(e => { console.error('[curator] ERROR:', e.message); process.exit(1); });
