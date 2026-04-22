// civic-identity/config.js
// Per-node configuration loader.
//
// One JSON file defines everything that differs between neighborhood nodes:
// the slug, geographic bounds, topic keywords, social handles, contact info.
// Before this file existed, those values were hardcoded to West Waldo in
// the connector source. Node two would have required a code fork.
//
// Resolution order:
//   1. NOS_CONFIG_PATH environment variable (explicit override)
//   2. ./node.config.json in the process cwd
//   3. ./node.config.json next to this module
//   4. built-in defaults (West Waldo, for back-compat)
//
// The loader validates shape but does not enforce anything beyond that.
// Values you omit fall through to the defaults. A missing config file is
// not an error; a malformed one is.

import { readFileSync, existsSync } from 'fs';
import { join, dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));

// Built-in defaults. These match the original hardcoded West Waldo values
// so a node that never writes a config file keeps working.
const DEFAULTS = Object.freeze({
  slug: 'local@waldonet.local',
  name: 'Local Neighborhood',
  contactEmail: null,
  bounds: {
    north: 38.9920,
    south: 38.9540,
    east:  -94.5890,
    west:  -94.6140
  },
  nextdoor: {
    publicSlug: 'westwaldomo',
    enablePostScrape: false // Must be explicitly opted in per review
  },
  facebook: {
    groupId: null
  },
  topicKeywords: {
    // Used by social connector to tag posts by topic. Lowercase substrings.
    infrastructure: ['pothole', 'streetlight', 'sidewalk', 'sewer', 'drainage'],
    safety:         ['crime', 'police', 'theft', 'suspicious'],
    neighbor:       ['neighbor', 'block party', 'welcome'],
    policy:         ['council', 'ordinance', 'meeting', 'vote'],
    environment:    ['tree', 'garden', 'trash', 'recycling', 'compost']
  },
  geoPatterns: {
    // Optional regex strings for matching street names in free text.
    // Keep them simple. Callers can compile with new RegExp(..., 'i').
    streetRegex: '\\b(\\d+(?:th|st|nd|rd)?\\s+(?:st|ave|street|avenue))\\b'
  },
  retention: {
    socialDays: 90,
    federationDays: 365
  }
});

let _cached = null;

export function loadConfig({ path = null, reload = false } = {}) {
  if (_cached && !reload && !path) return _cached;

  const candidates = [
    path,
    process.env.NOS_CONFIG_PATH || null,
    resolve(process.cwd(), 'node.config.json'),
    join(__dir, '..', 'node.config.json'),
    join(__dir, 'node.config.json')
  ].filter(Boolean);

  let raw = null;
  let loadedPath = null;
  for (const p of candidates) {
    if (existsSync(p)) {
      try {
        raw = JSON.parse(readFileSync(p, 'utf8'));
        loadedPath = p;
        break;
      } catch (err) {
        throw new Error(`Invalid JSON in ${p}: ${err.message}`);
      }
    }
  }

  const merged = mergeConfig(DEFAULTS, raw || {});
  validateConfig(merged);
  merged._source = loadedPath || 'built-in defaults';
  _cached = merged;
  return merged;
}

// Shallow-merge for top-level keys, recursive for the nested objects we
// expect. We do not blindly deep-merge because that can mask typos.
function mergeConfig(base, override) {
  const out = { ...base };
  for (const [k, v] of Object.entries(override)) {
    if (v && typeof v === 'object' && !Array.isArray(v) && base[k] && typeof base[k] === 'object') {
      out[k] = { ...base[k], ...v };
    } else {
      out[k] = v;
    }
  }
  return out;
}

function validateConfig(cfg) {
  if (typeof cfg.slug !== 'string' || !/^[a-z0-9_-]+@[a-z0-9.\-]+$/i.test(cfg.slug)) {
    throw new Error(`config.slug must look like "slug@domain", got ${JSON.stringify(cfg.slug)}`);
  }
  const b = cfg.bounds || {};
  for (const k of ['north', 'south', 'east', 'west']) {
    if (!Number.isFinite(b[k])) throw new Error(`config.bounds.${k} must be a number`);
  }
  if (b.north <= b.south) throw new Error('config.bounds.north must be greater than south');
  if (b.east  <= b.west)  throw new Error('config.bounds.east must be greater than west');
  if (cfg.retention) {
    for (const k of ['socialDays', 'federationDays']) {
      if (cfg.retention[k] != null && !Number.isFinite(cfg.retention[k])) {
        throw new Error(`config.retention.${k} must be a number`);
      }
    }
  }
}

// Reset internal cache. Used by tests.
export function _resetConfigCache() { _cached = null; }

// Convenience accessors.
export const config = () => loadConfig();
