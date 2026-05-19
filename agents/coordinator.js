#!/usr/bin/env node
/**
 * Commonweave Agent: Coordinator
 *
 * Cross-agent synthesis. Runs weekly (Sun 10:00 CT - last of all agents).
 * Uses gemma4:26b local (or DeepSeek flash as fallback) - NOT GPT-5.5.
 *
 * Reads all 5 agent reports from this week.
 * Produces coordinator-synthesis.json that every agent reads before their next run.
 * Surfaces exactly ONE "Simon needs to decide" item to Telegram per week.
 *
 * The feedback loop:
 *   Coordinator writes → agents read priority-context.js → behavior adjusts next cycle
 *
 * Output schema:
 * {
 *   run_at, version,
 *   global_priorities: string[],   // what matters most this cycle
 *   agent_guidance: {              // per-agent priorities for next run
 *     cartographer: { ... },
 *     curator: { ... },
 *     scout: { ... },
 *     synthesizer: { ... },
 *     publisher: { ... }
 *   },
 *   patterns: string[],            // cross-agent observations
 *   quality_score: number,         // 0-100 overall project health
 *   simon_decision: string|null,   // ONE thing Simon needs to decide
 *   contradictions: string[],      // conflicting signals across agents
 * }
 */

'use strict';

const https = require('https');
const { getStats } = require('./shared/db-utils');
const { writeReport, readAllReports } = require('./shared/report-writer');

// Ollama local (gemma4:26b) - free, no API key
function callOllama(prompt) {
  return new Promise((resolve) => {
    const body = JSON.stringify({
      model: 'gemma4:26b',
      prompt,
      stream: false,
      options: { num_ctx: 4096, temperature: 0.3 },
    });
    const req = https.request({
      hostname: 'localhost',
      port: 11434,
      path: '/api/generate',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    }, (res) => {
      let data = '';
      res.on('data', d => { data += d; });
      res.on('end', () => {
        try { resolve(JSON.parse(data).response || ''); }
        catch { resolve(''); }
      });
    });
    req.on('error', () => resolve(''));
    req.setTimeout(120000, () => { req.destroy(); resolve(''); });
    req.write(body);
    req.end();
  });
}

// DeepSeek flash fallback (cheap: $0.14/1M tokens)
function callDeepSeekFallback(prompt) {
  return new Promise((resolve) => {
    try {
      const { execSync } = require('child_process');
      const dsPath = require('path').resolve(__dirname, '../../tools/deepseek.js');
      const safePrompt = prompt.slice(0, 3000).replace(/"/g, "'").replace(/\n/g, ' ');
      const result = execSync(
        `node "${dsPath}" --model flash "${safePrompt}"`,
        { timeout: 60000, encoding: 'utf8' }
      );
      resolve(result.trim());
    } catch (e) { console.log('[coordinator] DeepSeek error:', e.message.slice(0, 100)); resolve(''); }
  });
}

function buildSynthesisPrompt(reports, stats) {
  const { cartographer, curator, scout, synthesizer, publisher } = reports;

  return `You are analyzing weekly reports from 5 agents maintaining the Commonweave directory (${stats.total} organizations, ${stats.countries} countries, ${(stats.geocoded/stats.total*100).toFixed(1)}% geocoded).

CARTOGRAPHER: Found ${cartographer?.top_priority_gaps?.length || 0} critical country gaps, ${cartographer?.taxonomy_fragmentation?.length || 0} taxonomy issues, ${cartographer?.suspect_orgs?.count || 0} suspect entries.

CURATOR: Quarantined ${curator?.quarantine?.quarantined || 0} suspect orgs, fixed ${curator?.taxonomy_fixes?.fixed || 0} taxonomy entries, geocoded ${curator?.geocoding?.geocoded || 0} orgs. Geocoded pct: ${curator?.after?.geocoded_pct || 'unknown'}%.

SCOUT: Queued ${scout?.new_drafts_queued || 0} outreach drafts, ${scout?.queue_pending_approval || 0} pending approval. Target regions: ${scout?.target_regions?.join(', ') || 'none'}.

SYNTHESIZER: ${synthesizer?.proposals_count || 0} framework proposals (${synthesizer?.proposals_by_priority?.high || 0} high priority). Areas needing hedges: ${synthesizer?.areas_needing_hedges?.join(', ') || 'none'}.

PUBLISHER: Quality gate ${publisher?.quality_gate?.passes ? 'PASSED' : 'HELD'}. ${publisher?.quality_gate?.issues?.join('; ') || 'No issues'}.

Based on this, respond with a JSON object (no markdown, just JSON) with these exact keys:
- global_priorities: array of 3 strings (most important things for all agents next week)
- agent_guidance: object with keys cartographer/curator/scout/synthesizer/publisher, each with a "focus" string and optional "target_regions" or other specifics
- patterns: array of 2-3 cross-agent observation strings
- quality_score: integer 0-100 based on geocoding%, data quality, outreach momentum
- simon_decision: single string - ONE thing only Simon can decide (or null if nothing urgent)
- contradictions: array of conflicting signals (empty if none)

Respond with ONLY the JSON object.`;
}

function buildFallbackSynthesis(reports, stats) {
  // Deterministic synthesis when LLM is unavailable
  const { cartographer, curator, scout, synthesizer } = reports;
  const geocodePct = stats.geocoded / stats.total * 100;

  const global_priorities = [];
  if (geocodePct < 30) global_priorities.push('Geocoding is critical - less than 30% of orgs on the map');
  if (cartographer?.suspect_orgs?.count > 50) global_priorities.push('Data quality: quarantine suspect non-org entries');
  if (scout?.queue_pending_approval > 0) global_priorities.push(`Review ${scout.queue_pending_approval} outreach drafts pending approval`);
  if (global_priorities.length < 3) global_priorities.push('Expand coverage in Africa, Southeast Asia, Latin America');

  return {
    global_priorities,
    agent_guidance: {
      cartographer: { focus: 'Continue gap analysis, prioritize Africa and Southeast Asia' },
      curator: { focus: `Geocoding priority until ${Math.min(geocodePct + 5, 70).toFixed(0)}% reached` },
      scout: { focus: 'Target thin-coverage regions with contribution-first outreach' },
      synthesizer: { focus: 'Review high-priority proposals from previous week' },
      publisher: { focus: 'Hold publish until quality gate passes consistently' },
    },
    patterns: [
      `Geocoding at ${geocodePct.toFixed(1)}% - map shows ${(geocodePct).toFixed(0)}% of real coverage`,
      'Formal org bias in Wikidata sources - informal networks still underrepresented',
    ],
    quality_score: Math.round(
      (geocodePct * 0.4) +
      (Math.min(stats.countries / 200 * 100, 100) * 0.3) +
      ((scout?.queue_pending_approval > 0 ? 20 : 0)) +
      ((curator?.quarantine?.quarantined > 0 ? 10 : 0))
    ),
    simon_decision: scout?.queue_pending_approval > 0
      ? `${scout.queue_pending_approval} outreach drafts in queue need your review before Scout can track responses`
      : null,
    contradictions: [],
  };
}

async function run() {
  const stats = getStats();

  const reports = readAllReports();
  const hasReports = Object.values(reports).some(r => r !== null);

  if (!hasReports) {
    console.log('[coordinator] No agent reports found yet. Run other agents first.');
    process.exit(0);
  }

  console.log('[coordinator] Building synthesis from agent reports...');
  const prompt = buildSynthesisPrompt(reports, stats);

  let synthesis = null;

  // Try Ollama first (free, local)
  console.log('[coordinator] Calling gemma4:26b (local)...');
  const ollamaResponse = await callOllama(prompt);
  if (ollamaResponse) {
    try {
      const cleaned = ollamaResponse.replace(/^```json\s*/i, '').replace(/```\s*$/i, '').trim();
      synthesis = JSON.parse(cleaned);
      console.log('[coordinator] Ollama synthesis successful');
    } catch {
      console.log('[coordinator] Ollama response unparseable, trying DeepSeek fallback...');
    }
  }

  // Fallback to DeepSeek flash
  if (!synthesis) {
    const dsResponse = await callDeepSeekFallback(prompt);
    if (dsResponse) {
      try {
        const cleaned = dsResponse.replace(/^```json\s*/i, '').replace(/```\s*$/i, '').trim();
        synthesis = JSON.parse(cleaned);
        console.log('[coordinator] DeepSeek fallback synthesis successful');
      } catch {
        console.log('[coordinator] DeepSeek response unparseable, using deterministic fallback');
      }
    }
  }

  // Final deterministic fallback
  if (!synthesis) {
    synthesis = buildFallbackSynthesis(reports, stats);
    console.log('[coordinator] Using deterministic fallback synthesis');
  }

  // Surface Simon decision to Telegram
  if (synthesis.simon_decision) {
    try {
      const { send } = require('../../tools/telegram-send');
      await send(`🪱 Commonweave Coordinator\n\n📋 This week's synthesis ready.\n\n🔴 One thing for you:\n${synthesis.simon_decision}\n\nQuality score: ${synthesis.quality_score}/100\nTop priority: ${synthesis.global_priorities?.[0] || 'see report'}`);
    } catch (e) {
      console.log('[coordinator] Telegram notify failed (non-fatal):', e.message);
    }
  }

  const report = {
    run_at: new Date().toISOString(),
    version: '1.0',
    ...synthesis,
    db_snapshot: { total: stats.total, geocoded: stats.geocoded, geocoded_pct: parseFloat((stats.geocoded / stats.total * 100).toFixed(1)), countries: stats.countries },
    synthesis_method: synthesis._method || 'llm',
  };

  const outPath = writeReport('coordinator', report);
  console.log(`[coordinator] Done. Quality score: ${synthesis.quality_score}/100. Report: ${outPath}`);
}

run().catch(e => { console.error('[coordinator] ERROR:', e.message); process.exit(1); });
