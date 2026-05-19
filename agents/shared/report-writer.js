/**
 * Commonweave agent report writer/reader.
 * All agents write structured JSON reports here.
 * The Coordinator reads all of them.
 */

const fs = require('fs');
const path = require('path');

const REPORTS_DIR = path.resolve(__dirname, '../reports');

function reportPath(agentName) {
  return path.join(REPORTS_DIR, `${agentName}-latest.json`);
}

function archivePath(agentName, ts) {
  const dir = path.join(REPORTS_DIR, 'archive');
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, `${agentName}-${ts}.json`);
}

/**
 * Write a report. Archives the previous one.
 * report must be a plain object with at minimum:
 *   { agent, run_at, version, ...agentSpecificFields }
 */
function writeReport(agentName, report) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
  const latest = reportPath(agentName);
  // Archive previous
  if (fs.existsSync(latest)) {
    const prev = JSON.parse(fs.readFileSync(latest, 'utf8'));
    const ts = (prev.run_at || 'unknown').replace(/[:.]/g, '-');
    fs.copyFileSync(latest, archivePath(agentName, ts));
  }
  const full = { ...report, agent: agentName, written_at: new Date().toISOString() };
  fs.writeFileSync(latest, JSON.stringify(full, null, 2));
  return latest;
}

function readReport(agentName) {
  const p = reportPath(agentName);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function readAllReports() {
  const agents = ['cartographer', 'curator', 'scout', 'synthesizer', 'publisher'];
  const out = {};
  agents.forEach(a => { out[a] = readReport(a); });
  return out;
}

module.exports = { writeReport, readReport, readAllReports };
