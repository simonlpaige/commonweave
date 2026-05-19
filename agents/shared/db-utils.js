/**
 * Commonweave agent shared DB utilities.
 * Uses the same sqlite3.exe pattern as the existing tools (no better-sqlite3 dep).
 */

'use strict';

const path = require('path');
const { execFileSync } = require('child_process');

const DB_PATH = path.resolve(__dirname, '../../data/commonweave_directory.db');
// workspace root is 3 levels up from agents/shared/
const WORKSPACE = path.resolve(__dirname, '../../..');
const SQLITE = path.join(WORKSPACE, 'tools', 'bin', 'sqlite3.exe');

function query(sql, params) {
  // sqlite3 CLI doesn't support parameterized queries - caller must sanitize
  const out = execFileSync(SQLITE, [DB_PATH, '-json', sql], { encoding: 'utf8' });
  return out.trim() ? JSON.parse(out) : [];
}

function run(sql) {
  execFileSync(SQLITE, [DB_PATH, sql], { encoding: 'utf8' });
}

function getStats() {
  const total = query('SELECT COUNT(*) as n FROM organizations')[0].n;
  const geocoded = query('SELECT COUNT(*) as n FROM organizations WHERE lat IS NOT NULL')[0].n;
  const countries = query('SELECT COUNT(DISTINCT country_code) as n FROM organizations')[0].n;
  const withWebsite = query("SELECT COUNT(*) as n FROM organizations WHERE website IS NOT NULL AND website != ''")[0].n;
  const byArea = query('SELECT framework_area, COUNT(*) as n FROM organizations GROUP BY framework_area ORDER BY n DESC LIMIT 20');
  return { total, geocoded, geocodedPct: (geocoded / total * 100).toFixed(1), countries, withWebsite, byArea };
}

function getThinCountries(threshold = 5) {
  return query(`SELECT country_code, COUNT(*) as n FROM organizations GROUP BY country_code HAVING n <= ${threshold} ORDER BY n ASC`);
}

function getUngeocodedSample(limit = 100) {
  return query(`SELECT id, name, city, state_province, country_code FROM organizations WHERE lat IS NULL ORDER BY RANDOM() LIMIT ${limit}`);
}

function getTaxonomyFragmentation() {
  const areas = query('SELECT DISTINCT framework_area FROM organizations WHERE framework_area IS NOT NULL');
  const normalized = {};
  areas.forEach(({ framework_area }) => {
    const key = framework_area.toLowerCase().replace(/[\s-]+/g, '_').trim();
    if (!normalized[key]) normalized[key] = [];
    normalized[key].push(framework_area);
  });
  return Object.entries(normalized)
    .filter(([, variants]) => variants.length > 1)
    .map(([key, variants]) => ({ key, variants }));
}

function getSuspectOrgs(limit = 200) {
  const sql = `
    SELECT id, name, description, source, country_code
    FROM organizations
    WHERE (
      name LIKE '% road' OR name LIKE 'M% road' OR name LIKE 'M% Road' OR
      lower(name) LIKE 'r/%' OR
      lower(source) LIKE '%reddit%' OR
      (lower(description) LIKE '%road between%' OR lower(description) LIKE '% highway %')
    )
    AND status != 'quarantine'
    LIMIT ${limit}
  `.trim().replace(/\s+/g, ' ');
  return query(sql);
}

function getRecentInserts(hours = 24) {
  return query(`SELECT id, name, country_code, source, created_at FROM organizations WHERE created_at >= datetime('now', '-${hours} hours') ORDER BY created_at DESC LIMIT 200`);
}

function updateOrgField(id, field, value) {
  const escaped = String(value).replace(/'/g, "''");
  run(`UPDATE organizations SET ${field} = '${escaped}', updated_at = datetime('now') WHERE id = '${id}'`);
}

function quarantineOrg(id) {
  run(`UPDATE organizations SET status = 'quarantine', updated_at = datetime('now') WHERE id = '${id}'`);
}

module.exports = { query, run, getStats, getThinCountries, getUngeocodedSample, getTaxonomyFragmentation, getSuspectOrgs, getRecentInserts, updateOrgField, quarantineOrg };
