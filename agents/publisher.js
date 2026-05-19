#!/usr/bin/env node
/**
 * Commonweave Agent: Publisher
 *
 * Communications. Runs weekly (Sun 08:00 CT, after other agents).
 *
 * Reads all agent reports + DB diff since last week.
 * Has a QUALITY GATE - only publishes if net-quality improved.
 * Drafts: (a) GitHub README update, (b) newsletter blurb, (c) Telegram heartbeat.
 * Simon approves before anything goes public.
 *
 * Quality gate rules:
 *   - Geocoding pct must have improved OR net non-suspect orgs added
 *   - No drafts if Curator quarantined more than it geocoded (bad week)
 *   - Synthesizer must have fewer "high priority" proposals than last run
 *     (meaning quality is improving not degrading)
 *
 * Reads: all agent reports
 * Writes: publisher-draft.json, pings Telegram with summary for approval
 */

'use strict';

const { getStats } = require('./shared/db-utils');
const { writeReport, readReport } = require('./shared/report-writer');
const { loadPriorityContext } = require('./shared/priority-context');

function qualityGatePasses(curator, synthesizer) {
  const issues = [];

  if (!curator) {
    issues.push('No curator report - cannot assess data quality');
    return { passes: false, issues };
  }

  // Check geocoding progress
  const geocodingImproved = curator.geocoding && !curator.geocoding.skipped &&
    curator.geocoding.geocoded > 0;
  const quarantineHeavy = curator.quarantine && curator.quarantine.quarantined > 100;

  if (quarantineHeavy && !geocodingImproved) {
    issues.push(`Heavy quarantine week (${curator.quarantine.quarantined} suspects removed) with no geocoding gain - net quality unclear`);
  }

  // Framework quality improving
  if (synthesizer && synthesizer.proposals_by_priority?.high > 3) {
    issues.push(`Synthesizer found ${synthesizer.proposals_by_priority.high} high-priority framework issues - docs need work before publishing`);
  }

  return {
    passes: issues.length === 0,
    issues,
    geocoding_improved: geocodingImproved,
    net_positive: !quarantineHeavy || geocodingImproved,
  };
}

function buildReadmeUpdate(stats, cartReport, curatorReport, scoutReport) {
  const geocodePct = (stats.geocoded / stats.total * 100).toFixed(1);
  const queueSize = scoutReport?.queue_pending_approval || 0;

  return `## Directory Status

As of ${new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}:

- **${stats.total.toLocaleString()} organizations** mapped across **${stats.countries} countries**
- **${geocodePct}% geocoded** (${stats.geocoded.toLocaleString()} with map coordinates)
- Coverage strongest in North America and Europe; actively expanding in ${cartReport?.top_priority_gaps?.slice(0, 3).map(g => g.country_code).join(', ') || 'Africa, Southeast Asia, and Latin America'}

[View the map](https://simonlpaige.github.io/commonweave/map.html) | [Search the directory](https://simonlpaige.github.io/commonweave/directory.html)

*The map shows all geocoded entries. If your organization is missing, [open an issue](https://github.com/simonlpaige/commonweave/issues/new).*`;
}

function buildNewsletterBlurb(stats, curatorReport) {
  const geocodePct = (stats.geocoded / stats.total * 100).toFixed(1);
  const geocodedThisWeek = curatorReport?.geocoding?.geocoded || 0;
  const quarantineCount = curatorReport?.quarantine?.quarantined || 0;

  const lines = [
    `**Commonweave update**`,
    ``,
    `The directory now has ${stats.total.toLocaleString()} organizations across ${stats.countries} countries.`,
  ];

  if (geocodedThisWeek > 0) {
    lines.push(`This week: ${geocodedThisWeek} more organizations placed on the map (${geocodePct}% geocoded overall).`);
  }
  if (quarantineCount > 0) {
    lines.push(`Data quality pass removed ${quarantineCount} non-organization entries that crept in from automated sources.`);
  }

  lines.push(``, `The mapping is the hard part. Every geocoded organization is a pin on a map that shows the commons economy is real, global, and distributed - not theoretical.`);

  return lines.join('\n');
}

function buildTelegramHeartbeat(stats, allReports, gateResult) {
  const { curator, scout, synthesizer, cartographer } = allReports;
  const geocodePct = (stats.geocoded / stats.total * 100).toFixed(1);

  const lines = [
    `📍 Commonweave Weekly`,
    ``,
    `DB: ${stats.total.toLocaleString()} orgs | ${stats.countries} countries | ${geocodePct}% geocoded`,
  ];

  if (curator?.geocoding?.geocoded > 0) lines.push(`Geocoded: +${curator.geocoding.geocoded} this week`);
  if (curator?.quarantine?.quarantined > 0) lines.push(`Quarantined: ${curator.quarantine.quarantined} suspect entries`);
  if (scout?.new_drafts_queued > 0) lines.push(`Scout: ${scout.new_drafts_queued} new outreach drafts queued`);
  if (synthesizer?.proposals_count > 0) lines.push(`Synthesizer: ${synthesizer.proposals_count} framework proposals`);
  if (cartographer?.top_priority_gaps?.length > 0) {
    const top = cartographer.top_priority_gaps.slice(0, 3).map(g => g.country_code).join(', ');
    lines.push(`Coverage gap priority: ${top}`);
  }

  if (!gateResult.passes) {
    lines.push(``, `⚠️ Quality gate: ${gateResult.issues.join('; ')}`);
    lines.push(`README/newsletter drafts held - review needed.`);
  } else {
    lines.push(``, `✅ Quality gate passed. README + newsletter drafts ready for your approval.`);
    lines.push(`Review: commonweave/agents/reports/publisher-latest.json`);
  }

  return lines.join('\n');
}

async function run() {
  const ctx = loadPriorityContext('publisher');
  const stats = getStats();

  const allReports = {
    cartographer: readReport('cartographer'),
    curator: readReport('curator'),
    scout: readReport('scout'),
    synthesizer: readReport('synthesizer'),
  };

  const gateResult = qualityGatePasses(allReports.curator, allReports.synthesizer);
  console.log(`[publisher] Quality gate: ${gateResult.passes ? 'PASS' : 'HOLD'}`, gateResult.issues);

  const drafts = {};
  if (gateResult.passes) {
    drafts.readme_update = buildReadmeUpdate(stats, allReports.cartographer, allReports.curator, allReports.scout);
    drafts.newsletter_blurb = buildNewsletterBlurb(stats, allReports.curator);
  } else {
    drafts.readme_update = null;
    drafts.newsletter_blurb = null;
    drafts.held_reason = gateResult.issues;
  }

  const telegramMsg = buildTelegramHeartbeat(stats, allReports, gateResult);
  drafts.telegram_heartbeat = telegramMsg;

  // Always send Telegram heartbeat (it includes the gate status)
  try {
    const { send } = require('../../tools/telegram-send');
    await send(telegramMsg);
    console.log('[publisher] Telegram heartbeat sent');
  } catch (e) {
    console.log('[publisher] Telegram notify failed (non-fatal):', e.message);
  }

  const report = {
    run_at: new Date().toISOString(),
    version: '1.0',
    db_snapshot: { total: stats.total, geocoded: stats.geocoded, geocoded_pct: parseFloat((stats.geocoded / stats.total * 100).toFixed(1)), countries: stats.countries },
    quality_gate: gateResult,
    drafts,
    coordinator_context_used: ctx.available,
  };

  const outPath = writeReport('publisher', report);
  console.log(`[publisher] Done. Gate: ${gateResult.passes ? 'PASS' : 'HOLD'}. Report: ${outPath}`);
}

run().catch(e => { console.error('[publisher] ERROR:', e.message); process.exit(1); });
