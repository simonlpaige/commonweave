// connectors/ecolibrium-directory.js
// Bridge between NeighborhoodOS and the Ecolibrium global directory.
// Lets a neighborhood ask: "Who's already working on what we care about, near us?"
//
// The Ecolibrium directory lives at ecolibrium/data/ecolibrium_directory.db
// This connector reads it (read-only) to surface relevant orgs.

import Database from 'better-sqlite3';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
// Path to the main Ecolibrium directory DB (relative to this file)
const DIRECTORY_DB_PATH = join(__dir, '../../data/ecolibrium_directory.db');

// ----------------------------------------------------------------
// TOPIC -> ECOLIBRIUM CATEGORY MAPPING
// Maps NeighborhoodOS topic tags to Ecolibrium taxonomy categories
// ----------------------------------------------------------------

const TOPIC_TO_CATEGORIES = {
  housing:        ['housing', 'community_land_trust', 'affordable_housing', 'cooperative_housing'],
  traffic:        ['transportation', 'bicycle', 'pedestrian', 'transit'],
  crime:          ['safety', 'community_safety', 'restorative_justice'],
  parks:          ['parks', 'green_space', 'urban_ecology', 'environmental'],
  infrastructure: ['infrastructure', 'utilities', 'public_works'],
  events:         ['community_organizing', 'civic_engagement', 'neighborhood'],
  city_hall:      ['civic_tech', 'democracy', 'government_accountability'],
  business:       ['cooperative', 'local_economy', 'credit_union', 'food_system'],
  food:           ['food_system', 'food_cooperative', 'community_garden', 'food_bank'],
  mutual_aid:     ['mutual_aid', 'community_care', 'solidarity']
};

// ----------------------------------------------------------------
// QUERIES
// ----------------------------------------------------------------

function openDirectoryDB() {
  try {
    const db = new Database(DIRECTORY_DB_PATH, { readonly: true });
    return db;
  } catch (err) {
    return null; // Directory DB not available - degrade gracefully
  }
}

// Find organizations near a neighborhood boundary (bbox search)
export function getOrgsNearNeighborhood(bounds, { limit = 20, categories = null } = {}) {
  const db = openDirectoryDB();
  if (!db) return { orgs: [], note: 'Ecolibrium directory not available locally' };

  try {
    let query = `
      SELECT name, description, website, categories, city, state, country,
             latitude, longitude
      FROM organizations
      WHERE latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
        AND active = 1
    `;
    const params = [bounds.south, bounds.north, bounds.west, bounds.east];

    if (categories && categories.length > 0) {
      const catFilter = categories.map(() => `categories LIKE ?`).join(' OR ');
      query += ` AND (${catFilter})`;
      categories.forEach(c => params.push(`%${c}%`));
    }

    query += ` ORDER BY name LIMIT ?`;
    params.push(limit);

    const orgs = db.prepare(query).all(...params);
    return { orgs, count: orgs.length };

  } finally {
    db.close();
  }
}

// Find orgs relevant to the neighborhood's top-discussed topics
export function getOrgsForTopics(topicTags, bounds, { limit = 15 } = {}) {
  const db = openDirectoryDB();
  if (!db) return { orgs: [], note: 'Ecolibrium directory not available locally' };

  // Map topic tags to directory categories
  const categories = new Set();
  for (const tag of topicTags) {
    const mapped = TOPIC_TO_CATEGORIES[tag] || [];
    mapped.forEach(c => categories.add(c));
  }

  if (categories.size === 0) return { orgs: [], topics: topicTags };

  return {
    ...getOrgsNearNeighborhood(bounds, { limit, categories: [...categories] }),
    topics: topicTags,
    categories: [...categories]
  };
}

// Get orgs that are already federated (using NeighborhoodOS or Ecolibrium tools)
export function getFederatedNeighborhoods(bounds) {
  const db = openDirectoryDB();
  if (!db) return [];

  try {
    return db.prepare(`
      SELECT name, description, website, city, state, latitude, longitude,
             ecolibrium_node_url
      FROM organizations
      WHERE ecolibrium_node_url IS NOT NULL
        AND latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
      ORDER BY name
    `).all(bounds.south, bounds.north, bounds.west, bounds.east);
  } catch {
    // Column may not exist yet - the schema evolves
    return [];
  } finally {
    db.close();
  }
}

// The "Who's working on this near me?" query
// Takes the neighborhood's active social topics and surfaces the most relevant orgs
export async function getEcosystemRecommendations(neighborhoodDb, neighborhood, bounds) {
  const { getTopTopics } = await import('./social.js');
  const topics = getTopTopics(neighborhoodDb, neighborhood, { days: 30, limit: 8 });
  const topTags = topics.map(t => t.tag);

  const result = getOrgsForTopics(topTags, bounds);

  return {
    neighborhood,
    topDiscussedTopics: topTags,
    recommendedOrgs: result.orgs,
    matchedCategories: result.categories,
    note: result.orgs.length === 0
      ? 'No orgs found near this neighborhood in the Ecolibrium directory. This is a gap - consider adding local orgs.'
      : `${result.orgs.length} organizations found working on issues your neighbors are discussing.`
  };
}

// ----------------------------------------------------------------
// REGISTRATION
// Lets a neighborhood register itself in the Ecolibrium directory
// so other neighborhoods can find and federate with it.
// This writes to the directory DB (requires write access).
// ----------------------------------------------------------------

export function registerNeighborhoodNode(nodeInfo) {
  // nodeInfo: { name, slug, bounds, nodeUrl, contactEmail, city, state }
  // This is a placeholder - in production this would call the Ecolibrium
  // directory API to register the node, or submit a PR to the open-source
  // directory data file.
  return {
    status: 'pending',
    message: 'Node registration submitted. To register in the Ecolibrium directory, ' +
             'open an issue at github.com/simonlpaige/ecolibrium with your node details.',
    nodeInfo
  };
}
