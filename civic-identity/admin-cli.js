#!/usr/bin/env node
// civic-identity/admin-cli.js
// Provision and rotate per-admin tokens without the server running.
//
// Usage:
//   node admin-cli.js list
//   node admin-cli.js add <label> [--scope full]
//   node admin-cli.js rotate <label>
//   node admin-cli.js revoke <label>
//
// Env:
//   DB_PATH  default ./civic-identity.db

import { openDB } from './identity.js';
import {
  ensureAdminTokensTable, addAdminToken, listAdminTokens,
  revokeAdminToken, rotateAdminToken
} from './admin-tokens.js';

const DB_PATH = process.env.DB_PATH || './civic-identity.db';
const args = process.argv.slice(2);
const cmd = args[0];

function usage() {
  console.log(`Usage:
  admin-cli.js list
  admin-cli.js add <label> [--scope full]
  admin-cli.js rotate <label> [--scope full]
  admin-cli.js revoke <label>
`);
  process.exit(1);
}

if (!cmd) usage();

const db = openDB(DB_PATH);
ensureAdminTokensTable(db);

try {
  switch (cmd) {
    case 'list': {
      const rows = listAdminTokens(db);
      if (!rows.length) { console.log('(no admin tokens)'); break; }
      for (const r of rows) {
        const status = r.revoked_at ? 'REVOKED' : 'active';
        console.log(
          `${r.label.padEnd(30)} ${r.token_prefix}… ${r.scope.padEnd(8)} ` +
          `${status.padEnd(8)} last_used=${r.last_used_at || '-'} created=${r.created_at}`
        );
      }
      break;
    }
    case 'add': {
      const label = args[1];
      if (!label) usage();
      const scopeIdx = args.indexOf('--scope');
      const scope = scopeIdx > -1 ? args[scopeIdx + 1] : 'full';
      const created = addAdminToken(db, { label, scope });
      console.log(`Label:   ${created.label}`);
      console.log(`Scope:   ${created.scope}`);
      console.log(`Token:   ${created.token}`);
      console.log(`\n${created.notice}`);
      break;
    }
    case 'rotate': {
      const label = args[1];
      if (!label) usage();
      const scopeIdx = args.indexOf('--scope');
      const scope = scopeIdx > -1 ? args[scopeIdx + 1] : null;
      const created = rotateAdminToken(db, label, scope);
      console.log(`Rotated ${created.label}. New token:`);
      console.log(`  ${created.token}`);
      console.log(`\n${created.notice}`);
      break;
    }
    case 'revoke': {
      const label = args[1];
      if (!label) usage();
      revokeAdminToken(db, label);
      console.log(`Revoked ${label}`);
      break;
    }
    default:
      usage();
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
} finally {
  db.close();
}
