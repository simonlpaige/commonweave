'use strict';
/**
 * enrichment-queue.js
 *
 * Reads one or more audit export JSON files (downloaded from audit/index.html
 * after a review session). Pulls out any org where audit.verdict === 'enrich'
 * and appends them to audit/enrichment-queue.json, deduped by org id.
 *
 * Usage:
 *   node tools/enrichment-queue.js path/to/audit-export.json [another.json ...]
 */

const fs   = require('fs');
const path = require('path');

const ROOT       = path.resolve(__dirname, '..');
const QUEUE_PATH = path.join(ROOT, 'audit', 'enrichment-queue.json');

// Load the existing queue (or start fresh)
function loadQueue() {
  if (fs.existsSync(QUEUE_PATH)) {
    try {
      return JSON.parse(fs.readFileSync(QUEUE_PATH, 'utf8'));
    } catch (e) {
      console.error('Warning: could not parse existing queue, starting fresh.', e.message);
    }
  }
  return [];
}

// Build a lookup map of id -> entry
function indexById(arr) {
  const map = {};
  for (const item of arr) map[item.id] = item;
  return map;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node tools/enrichment-queue.js <audit-export.json> [more.json ...]');
    process.exit(1);
  }

  const existing = loadQueue();
  const existingMap = indexById(existing);

  let added = 0;
  let skipped = 0;

  for (const filePath of args) {
    const abs = path.resolve(filePath);
    if (!fs.existsSync(abs)) {
      console.error(`File not found: ${abs}`);
      continue;
    }

    let data;
    try {
      data = JSON.parse(fs.readFileSync(abs, 'utf8'));
    } catch (e) {
      console.error(`Could not parse ${abs}: ${e.message}`);
      continue;
    }

    // The export may be an array of org objects or { orgs: [...] }
    const orgs = Array.isArray(data) ? data : (data.orgs || []);

    for (const org of orgs) {
      // Only pick orgs the reviewer tagged for enrichment
      const verdict = org.audit && org.audit.verdict;
      if (verdict !== 'enrich') continue;

      const id = String(org.id || org.org_id || '');
      if (!id) {
        console.warn('Skipping org with no id:', org.name);
        continue;
      }

      if (existingMap[id]) {
        skipped++;
        continue; // already queued
      }

      const entry = {
        id,
        name:            org.name         || null,
        country_code:    org.country_code  || null,
        city:            org.city          || null,
        source:          org.source        || null,
        framework_area:  org.framework_area || org.section || null,
        alignment_score: org.alignment_score != null ? org.alignment_score : null,
        website:         org.website       || null,
        email:           org.email         || null,
        description:     org.description   || null,
        status:          'pending',
        added_at:        new Date().toISOString(),
      };

      existingMap[id] = entry;
      existing.push(entry);
      added++;
    }

    console.log(`Processed ${abs}`);
  }

  // Write the updated queue
  fs.mkdirSync(path.dirname(QUEUE_PATH), { recursive: true });
  fs.writeFileSync(QUEUE_PATH, JSON.stringify(existing, null, 2), 'utf8');

  console.log(`\nDone. Added: ${added} | Already queued (skipped): ${skipped} | Total in queue: ${existing.length}`);
  console.log(`Queue written to: ${QUEUE_PATH}`);
}

main();
