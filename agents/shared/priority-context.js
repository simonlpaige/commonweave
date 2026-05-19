/**
 * Priority context loader.
 * Every agent calls loadPriorityContext() at startup to receive
 * the Coordinator's latest guidance. If no synthesis exists yet,
 * returns defaults so agents can still run cold.
 */

const { readReport } = require('./report-writer');

function loadPriorityContext(agentName) {
  const synthesis = readReport('coordinator');
  if (!synthesis) {
    return {
      available: false,
      priorities: [],
      agentGuidance: {},
      simonDecision: null,
    };
  }

  return {
    available: true,
    run_at: synthesis.run_at,
    globalPriorities: synthesis.global_priorities || [],
    agentGuidance: (synthesis.agent_guidance || {})[agentName] || {},
    simonDecision: synthesis.simon_decision || null,
    patterns: synthesis.patterns || [],
    qualityScore: synthesis.quality_score || null,
  };
}

module.exports = { loadPriorityContext };
