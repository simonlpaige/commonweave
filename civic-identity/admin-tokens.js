// civic-identity/admin-tokens.js
// Per-admin API tokens, hashed at rest, revocable without a server restart.
//
// The deep-dive review flagged the single shared ADMIN_TOKEN env var as a
// single point of compromise and a painful rotation path: to rotate, you
// had to restart the server, update every operator's copy, and there was
// no way to tell who acted.
//
// This module stores a short label ("simon@waldonet", "brookside-backup")
// alongside a bcrypt hash of the token. Raw tokens are returned once at
// creation and never again. Revocation is a column flip, no restart.
//
// Admin routes now call verifyAdminToken(db, raw). If it returns a
// principal object, the request is authorized and the principal's label
// can be written into the audit log. If it returns null, fall through to
// the legacy ADMIN_TOKEN or deny.

import bcrypt from 'bcrypt';
import crypto from 'crypto';

const BCRYPT_ROUNDS = 10;

export function ensureAdminTokensTable(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS admin_tokens (
      id            TEXT PRIMARY KEY,
      label         TEXT NOT NULL UNIQUE,
      token_prefix  TEXT NOT NULL,
      token_hash    TEXT NOT NULL,
      scope         TEXT NOT NULL DEFAULT 'full',
      created_at    TEXT NOT NULL DEFAULT (datetime('now')),
      last_used_at  TEXT,
      revoked_at    TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_admin_tokens_prefix ON admin_tokens(token_prefix);
  `);
}

export function addAdminToken(db, { label, scope = 'full' } = {}) {
  if (!label || !/^[\w@.\-]{3,64}$/.test(label)) {
    throw new Error('label must be 3-64 chars, letters/digits/@.-_');
  }
  const existing = db.prepare(`SELECT 1 FROM admin_tokens WHERE label = ? AND revoked_at IS NULL`).get(label);
  if (existing) throw new Error('An active token with that label already exists');

  const raw = crypto.randomBytes(32).toString('base64url');
  const prefix = raw.slice(0, 8);
  const hash = bcrypt.hashSync(raw, BCRYPT_ROUNDS);
  const id = crypto.randomUUID();

  db.prepare(`
    INSERT INTO admin_tokens (id, label, token_prefix, token_hash, scope)
    VALUES (?, ?, ?, ?, ?)
  `).run(id, label, prefix, hash, scope);

  return { id, label, scope, token: raw, notice: 'Copy this token now. It is never stored server-side and cannot be retrieved again.' };
}

// Resolve a raw bearer token to a principal, or null.
// Uses a prefix index so we only do one bcrypt per call in the common case.
export function verifyAdminToken(db, raw) {
  if (!raw || typeof raw !== 'string' || raw.length < 20) return null;
  const prefix = raw.slice(0, 8);
  const candidates = db.prepare(`
    SELECT * FROM admin_tokens WHERE token_prefix = ? AND revoked_at IS NULL
  `).all(prefix);

  for (const c of candidates) {
    try {
      if (bcrypt.compareSync(raw, c.token_hash)) {
        db.prepare(`UPDATE admin_tokens SET last_used_at = datetime('now') WHERE id = ?`).run(c.id);
        return { id: c.id, label: c.label, scope: c.scope };
      }
    } catch { /* ignore malformed rows */ }
  }
  return null;
}

export function listAdminTokens(db) {
  return db.prepare(`
    SELECT id, label, token_prefix, scope, created_at, last_used_at, revoked_at
    FROM admin_tokens ORDER BY created_at DESC
  `).all();
}

export function revokeAdminToken(db, label) {
  const res = db.prepare(`
    UPDATE admin_tokens SET revoked_at = datetime('now')
    WHERE label = ? AND revoked_at IS NULL
  `).run(label);
  if (res.changes === 0) throw new Error('No active admin token with that label');
  return true;
}

export function rotateAdminToken(db, label, scope = null) {
  // A rotation is revoke + add with the same label. We use a transaction so
  // we never end up with zero active admin tokens mid-rotation.
  return db.transaction(() => {
    const current = db.prepare(`SELECT scope FROM admin_tokens WHERE label = ? AND revoked_at IS NULL`).get(label);
    if (!current) throw new Error('No active admin token with that label');
    db.prepare(`UPDATE admin_tokens SET revoked_at = datetime('now') WHERE label = ? AND revoked_at IS NULL`).run(label);
    return addAdminToken(db, { label, scope: scope || current.scope });
  })();
}
