#!/usr/bin/env node
/**
 * Commonweave Agent: Scout
 *
 * Outreach intelligence. Runs Mon/Wed/Fri 09:00 CT.
 * 
 * Philosophy (learned from first-round failures):
 *   - Lead with CONTRIBUTION, not invitation
 *   - Target thin-coverage regions from Cartographer report
 *   - Find projects that need the directory (not flagship projects that don't care)
 *   - Queue drafts for Simon approval - NEVER auto-send
 *   - Telegram notification when queue has items
 *
 * What it does:
 *   1. Reads Cartographer's top_priority_gaps for target regions
 *   2. Searches GitHub for aligned repos in those regions
 *   3. Searches for regional cooperative federations needing a directory
 *   4. Generates contribution-first draft messages
 *   5. Writes to outreach-queue.json (Simon approves before anything sends)
 *   6. Pings Telegram if queue has new items
 *
 * Reads: cartographer report
 * Writes: scout-report.json, outreach-queue.json
 */

'use strict';

const https = require('https');
const fs = require('fs');
const path = require('path');
const { writeReport, readReport } = require('./shared/report-writer');
const { loadPriorityContext } = require('./shared/priority-context');

const QUEUE_PATH = path.resolve(__dirname, '../data/outreach-queue.json');

// GitHub search helper
function githubSearch(query) {
  return new Promise((resolve) => {
    const q = encodeURIComponent(query);
    const opts = {
      hostname: 'api.github.com',
      path: `/search/repositories?q=${q}&sort=updated&order=desc&per_page=10`,
      headers: {
        'User-Agent': 'Commonweave-Scout/1.0',
        'Accept': 'application/vnd.github.v3+json',
      },
    };
    const req = https.get(opts, (res) => {
      let data = '';
      res.on('data', d => { data += d; });
      res.on('end', () => {
        try { resolve(JSON.parse(data).items || []); }
        catch { resolve([]); }
      });
    });
    req.on('error', () => resolve([]));
    req.setTimeout(8000, () => { req.destroy(); resolve([]); });
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Target search queries by region - contribution-angle framing
// Extended country-to-region map covering more codes
const EXTENDED_COUNTRY_REGION = {
  'MX': 'latin_america', 'BR': 'latin_america', 'CO': 'latin_america', 'AR': 'latin_america',
  'PE': 'latin_america', 'CL': 'latin_america', 'VE': 'latin_america', 'EC': 'latin_america',
  'BZ': 'latin_america', 'GT': 'latin_america', 'HN': 'latin_america', 'NI': 'latin_america',
  'NG': 'africa', 'KE': 'africa', 'ZA': 'africa', 'GH': 'africa', 'ET': 'africa',
  'TZ': 'africa', 'UG': 'africa', 'RW': 'africa', 'SN': 'africa', 'GW': 'africa',
  'MW': 'africa', 'MZ': 'africa', 'CI': 'africa', 'CM': 'africa', 'ZW': 'africa',
  'PH': 'south_east_asia', 'ID': 'south_east_asia', 'VN': 'south_east_asia', 'TH': 'south_east_asia',
  'MM': 'south_east_asia', 'KH': 'south_east_asia', 'LA': 'south_east_asia', 'MY': 'south_east_asia',
  'EG': 'middle_east', 'SA': 'middle_east', 'TR': 'middle_east', 'IR': 'middle_east',
  'OM': 'middle_east', 'BH': 'middle_east', 'KW': 'middle_east', 'JO': 'middle_east',
  'KZ': 'central_asia', 'UZ': 'central_asia', 'KG': 'central_asia', 'TJ': 'central_asia',
  'UA': 'eastern_europe', 'RO': 'eastern_europe', 'PL': 'eastern_europe', 'HU': 'eastern_europe',
  'AG': 'latin_america', // Antigua and Barbuda - Caribbean/Americas
};

function inferRegion(code) {
  return EXTENDED_COUNTRY_REGION[code] || null;
}

const REGION_QUERIES = {
  latin_america: [
    'cooperativa solidarity economy Latin America',
    'economia solidaria cooperative open data',
    'mutual aid network Mexico Brazil Argentina',
  ],
  africa: [
    'cooperative mutual aid Africa open data',
    'savings circle ROSCA community finance Africa',
    'sacco saccos cooperative Kenya Nigeria',
  ],
  south_east_asia: [
    'cooperative solidarity economy Philippines Indonesia',
    'mutual aid community finance Southeast Asia',
  ],
  middle_east: [
    'cooperative solidarity economy Middle East',
    'community organization directory MENA',
  ],
  central_asia: [
    'cooperative organization Central Asia directory',
  ],
  general: [
    'commons cooperative directory open data',
    'solidarity economy network mapping',
    'mutual aid directory tools community',
  ],
};

function generateDraftMessage(repo, targetRegion, commonweaveAngle) {
  return {
    to: repo.full_name,
    platform: 'github',
    channel: 'issues',
    subject: `Data contribution offer - Commonweave commons directory`,
    body: `Hi ${repo.owner?.login || 'team'},

I maintain Commonweave (github.com/simonlpaige/commonweave), an open directory of cooperative, mutual-aid, and commons-based organizations. We currently have thin coverage in ${targetRegion} and noticed ${repo.name} has work in this space.

I'm not here to pitch you on joining anything. I have a specific offer: if there are organizations in your network that would benefit from being in an open, searchable global directory, I'd like to add them with proper attribution to your project as the source.

Two questions if you have a moment:
1. Is there a public list of organizations in your network we could reference?
2. Is anything in our ${targetRegion} coverage wrong or missing that you'd want corrected?

Our directory: https://github.com/simonlpaige/commonweave
Our current ${targetRegion} coverage: ${commonweaveAngle}

No response needed if this isn't useful. Thanks for the work you do.

- Simon Paige, Commonweave`,
    angle: commonweaveAngle,
    target_region: targetRegion,
    repo_url: repo.html_url,
    repo_stars: repo.stargazers_count,
    repo_description: repo.description,
  };
}

function loadQueue() {
  if (!fs.existsSync(QUEUE_PATH)) return [];
  return JSON.parse(fs.readFileSync(QUEUE_PATH, 'utf8'));
}

function saveQueue(queue) {
  fs.writeFileSync(QUEUE_PATH, JSON.stringify(queue, null, 2));
}

async function run() {
  const ctx = loadPriorityContext('scout');
  const cartReport = readReport('cartographer');

  // Determine target regions from Cartographer (or use defaults)
  let targetRegions = ['general'];
  if (cartReport && cartReport.recommendations_for_scout) {
    const regionCounts = {};
    cartReport.recommendations_for_scout.forEach(({ region, country_code }) => {
      // Fall back to broad region inference from country_code if region is unknown
      const effectiveRegion = region !== 'unknown' ? region : inferRegion(country_code);
      if (effectiveRegion) regionCounts[effectiveRegion] = (regionCounts[effectiveRegion] || 0) + 1;
    });
    const detected = Object.keys(regionCounts).sort((a, b) => regionCounts[b] - regionCounts[a]).slice(0, 3);
    if (detected.length > 0) targetRegions = detected;
  }
  if (ctx.agentGuidance.target_regions) {
    targetRegions = ctx.agentGuidance.target_regions;
  }

  console.log('[scout] Target regions:', targetRegions);

  const foundRepos = [];
  const newDrafts = [];

  for (const region of targetRegions) {
    const queries = REGION_QUERIES[region] || REGION_QUERIES.general;
    for (const q of queries.slice(0, 2)) {
      const results = await githubSearch(q);
      await sleep(2000); // GitHub rate limit
      for (const repo of results.slice(0, 3)) {
        if (repo.stargazers_count < 2) continue; // skip truly abandoned
        if (repo.pushed_at < '2022-01-01') continue; // skip stale repos
        foundRepos.push({ region, query: q, repo });
      }
    }
  }

  // Deduplicate by repo full_name
  const seen = new Set();
  const existing = loadQueue().map(d => d.to);
  const existingSet = new Set(existing);

  for (const { region, repo } of foundRepos) {
    if (seen.has(repo.full_name)) continue;
    if (existingSet.has(repo.full_name)) continue;
    seen.add(repo.full_name);

    const gapCount = cartReport?.recommendations_for_scout?.find(g => g.region === region)?.count || 'few';
    const angle = `${gapCount} orgs in ${region} - expanding coverage`;
    const draft = generateDraftMessage(repo, region, angle);
    draft.status = 'pending_approval';
    draft.queued_at = new Date().toISOString();
    draft.scout_run_id = new Date().toISOString().slice(0, 10);
    newDrafts.push(draft);
  }

  // Add new drafts to queue
  if (newDrafts.length > 0) {
    const queue = loadQueue();
    queue.push(...newDrafts);
    saveQueue(queue);
    console.log(`[scout] Added ${newDrafts.length} new drafts to outreach queue`);
  }

  const queue = loadQueue();
  const pendingCount = queue.filter(d => d.status === 'pending_approval').length;

  // Telegram notification if pending items exist
  if (pendingCount > 0) {
    try {
      const { send } = require('../../tools/telegram-send');
      await send(`🪱 Commonweave Scout: ${pendingCount} outreach draft${pendingCount > 1 ? 's' : ''} pending your approval.\nReview: C:\\Users\\simon\\.openclaw\\workspace\\commonweave\\data\\outreach-queue.json\nApprove each draft by setting status to "approved" then run the send script.`);
    } catch (e) {
      console.log('[scout] Telegram notify failed (non-fatal):', e.message);
    }
  }

  const report = {
    run_at: new Date().toISOString(),
    version: '1.0',
    target_regions: targetRegions,
    repos_found: foundRepos.length,
    new_drafts_queued: newDrafts.length,
    queue_pending_approval: pendingCount,
    sample_drafts: newDrafts.slice(0, 3).map(d => ({ to: d.to, region: d.target_region, subject: d.subject })),
    cartographer_input_used: !!cartReport,
    coordinator_context_used: ctx.available,
  };

  const outPath = writeReport('scout', report);
  console.log(`[scout] Done. ${newDrafts.length} new drafts, ${pendingCount} pending. Report: ${outPath}`);
}

run().catch(e => { console.error('[scout] ERROR:', e.message); process.exit(1); });
