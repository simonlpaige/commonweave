'use strict';
/**
 * enrichment-agent.js
 *
 * Reads audit/enrichment-queue.json, finds entries with status="pending",
 * runs Brave web searches to find missing contact info (website, email,
 * description), and writes proposals to audit/enrichment-proposals.json.
 *
 * Usage:
 *   node tools/enrichment-agent.js [--limit 20] [--dry-run]
 *
 * Rate limit: 1 request/sec (Brave free tier).
 */

const fs            = require('fs');
const path          = require('path');
const { execSync }  = require('child_process');

const ROOT             = path.resolve(__dirname, '..');
const QUEUE_PATH       = path.join(ROOT, 'audit', 'enrichment-queue.json');
const PROPOSALS_PATH   = path.join(ROOT, 'audit', 'enrichment-proposals.json');
const WEB_SEARCH_TOOL  = path.join(ROOT, '..', 'tools', 'web-search.js');

// Parse CLI flags
const args    = process.argv.slice(2);
const dryRun  = args.includes('--dry-run');
const limitIdx = args.indexOf('--limit');
const limit   = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : Infinity;

// Regex to scrape email addresses out of snippet text
const EMAIL_RE = /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g;

// Sleep helper - respects the 1 req/sec Brave rate limit
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run web-search.js as a child process and return parsed JSON results
function bravSearch(query) {
  try {
    const cmd = `node "${WEB_SEARCH_TOOL}" --json --count 3 "${query.replace(/"/g, '\\"')}"`;
    const out  = execSync(cmd, { encoding: 'utf8', timeout: 15000 });
    return JSON.parse(out);
  } catch (e) {
    console.warn(`  Search failed for query "${query}": ${e.message}`);
    return [];
  }
}

// Load JSON file or return default value
function loadJson(filePath, defaultValue) {
  if (fs.existsSync(filePath)) {
    try {
      return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
      console.warn(`Could not parse ${filePath}: ${e.message}`);
    }
  }
  return defaultValue;
}

// Guess confidence level for a proposed website
function scoreConfidence(orgName, city, proposedWebsite, snippets) {
  if (!proposedWebsite && snippets.length === 0) return 'low';

  if (proposedWebsite) {
    // Strip protocol and www, check if a word from the org name appears in the domain
    const domain = proposedWebsite.replace(/^https?:\/\/(www\.)?/, '').split('/')[0].toLowerCase();
    const words  = orgName.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    if (words.some(w => domain.includes(w))) return 'high';
  }

  // Medium: snippet text mentions org name and city
  const combined = snippets.join(' ').toLowerCase();
  const nameHit  = orgName && combined.includes(orgName.toLowerCase().slice(0, 15));
  const cityHit  = city    && combined.includes(city.toLowerCase());
  if (nameHit && cityHit) return 'medium';

  return 'low';
}

// Pull the best candidate URL from a list of search result items
function extractWebsite(results) {
  for (const r of results) {
    const url = r.url || r.link || '';
    // Skip Wikipedia, social media, aggregator noise
    if (url && !/wikipedia|facebook|linkedin|twitter|x\.com|yelp|bloomberg/i.test(url)) {
      return url;
    }
  }
  return null;
}

// Pull the first email address found across all result snippets
function extractEmail(results) {
  for (const r of results) {
    const snippet = r.snippet || r.description || '';
    const matches = snippet.match(EMAIL_RE);
    if (matches && matches.length) return matches[0];
  }
  return null;
}

// Pull the best snippet as a candidate description
function extractDescription(results) {
  for (const r of results) {
    const snippet = (r.snippet || r.description || '').trim();
    if (snippet.length > 40) return snippet;
  }
  return null;
}

async function main() {
  if (!fs.existsSync(QUEUE_PATH)) {
    console.error(`Queue not found: ${QUEUE_PATH}`);
    console.error('Run enrichment-queue.js first to populate it.');
    process.exit(1);
  }

  const queue     = loadJson(QUEUE_PATH, []);
  const proposals = loadJson(PROPOSALS_PATH, []);

  // Build set of org ids already proposed
  const proposedIds = new Set(proposals.map(p => p.id));

  const pending = queue
    .filter(e => e.status === 'pending' && !proposedIds.has(e.id))
    .slice(0, isFinite(limit) ? limit : queue.length);

  if (pending.length === 0) {
    console.log('No pending entries to enrich.');
    return;
  }

  console.log(`Enriching ${pending.length} orgs${dryRun ? ' (dry-run)' : ''}...`);

  for (let i = 0; i < pending.length; i++) {
    const org = pending[i];
    console.log(`\n[${i + 1}/${pending.length}] ${org.name} (${org.country_code || '?'})`);

    // Build two targeted search queries
    const q1 = `"${org.name}" ${org.city || ''} ${org.country_code || ''} contact email website`.trim();
    const q2 = `"${org.name}" ${org.country_code || ''} ${org.framework_area || ''}`.trim();

    let allResults = [];

    if (!dryRun) {
      console.log(`  Query 1: ${q1}`);
      const r1 = bravSearch(q1);
      allResults = allResults.concat(r1);
      await sleep(1000); // 1 req/sec rate limit

      console.log(`  Query 2: ${q2}`);
      const r2 = bravSearch(q2);
      allResults = allResults.concat(r2);
      await sleep(1000);
    } else {
      console.log(`  [dry-run] Would search: "${q1}" and "${q2}"`);
    }

    const snippets        = allResults.map(r => r.snippet || r.description || '');
    const proposedWebsite = org.website || extractWebsite(allResults);
    const proposedEmail   = org.email   || extractEmail(allResults);
    const proposedDesc    = org.description || extractDescription(allResults);
    const sourceResult    = allResults[0] || null;
    const confidence      = dryRun
      ? 'low'
      : scoreConfidence(org.name, org.city, proposedWebsite, snippets);

    const proposal = {
      id:                   org.id,
      org_name:             org.name,
      country_code:         org.country_code,
      city:                 org.city,
      source:               org.source,
      framework_area:       org.framework_area,
      alignment_score:      org.alignment_score,
      proposed_website:     proposedWebsite,
      proposed_email:       proposedEmail,
      proposed_description: proposedDesc,
      source_url:           sourceResult ? (sourceResult.url || sourceResult.link || null) : null,
      search_query:         q1,
      confidence,
      status:               'pending_review',
      searched_at:          new Date().toISOString(),
    };

    console.log(`  -> confidence: ${confidence} | website: ${proposedWebsite || 'none'} | email: ${proposedEmail || 'none'}`);

    proposals.push(proposal);

    // Mark queue entry as searched
    const queueEntry = queue.find(e => e.id === org.id);
    if (queueEntry) queueEntry.status = 'searched';
  }

  if (!dryRun) {
    fs.mkdirSync(path.dirname(PROPOSALS_PATH), { recursive: true });
    fs.writeFileSync(PROPOSALS_PATH, JSON.stringify(proposals, null, 2), 'utf8');
    console.log(`\nProposals written to: ${PROPOSALS_PATH}`);

    fs.writeFileSync(QUEUE_PATH, JSON.stringify(queue, null, 2), 'utf8');
    console.log(`Queue updated at: ${QUEUE_PATH}`);
  } else {
    console.log('\n[dry-run] No files written.');
  }

  console.log(`\nDone. ${pending.length} orgs processed. Total proposals: ${proposals.length}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
