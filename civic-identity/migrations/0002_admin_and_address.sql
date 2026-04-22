-- 0002_admin_and_address.sql
-- Per-admin token table and two-operator address verification table.
-- Both modules also have ensureX functions for back-compat with nodes that
-- skip migrations, but from 0002 onward the migration is the source of truth.

-- label is not UNIQUE so rotated tokens can coexist with their revoked
-- predecessors for audit. addAdminToken() enforces "at most one active
-- token per label" in application code.
CREATE TABLE IF NOT EXISTS admin_tokens (
  id            TEXT PRIMARY KEY,
  label         TEXT NOT NULL,
  token_prefix  TEXT NOT NULL,
  token_hash    TEXT NOT NULL,
  scope         TEXT NOT NULL DEFAULT 'full',
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  last_used_at  TEXT,
  revoked_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_admin_tokens_prefix ON admin_tokens(token_prefix);
CREATE INDEX IF NOT EXISTS idx_admin_tokens_label  ON admin_tokens(label);

CREATE TABLE IF NOT EXISTS address_approvals (
  id              TEXT PRIMARY KEY,
  target_user_id  TEXT NOT NULL,
  requester_id    TEXT NOT NULL,
  requester_note  TEXT,
  approver_id     TEXT,
  approver_note   TEXT,
  status          TEXT NOT NULL DEFAULT 'pending',
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_addr_appr_status ON address_approvals(status);
CREATE INDEX IF NOT EXISTS idx_addr_appr_target ON address_approvals(target_user_id);

-- Federation result reporting, to support the aggregation module. A single
-- row per (proposal, participating_node) tracks whether that node has
-- submitted its tally yet, or been marked timed out.
CREATE TABLE IF NOT EXISTS federation_reports (
  id              TEXT PRIMARY KEY,
  proposal_id     TEXT NOT NULL,
  peer_node       TEXT NOT NULL,
  status          TEXT NOT NULL DEFAULT 'pending',
  eligible        INTEGER,
  tally_json      TEXT,
  reported_at     TEXT,
  UNIQUE(proposal_id, peer_node)
);
CREATE INDEX IF NOT EXISTS idx_fed_reports_status ON federation_reports(status);
