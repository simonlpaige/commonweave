-- civic-identity/schema.sql
-- Civic Identity, Trust Verification, and Federated Voting
-- SQLite. No server required. Each neighborhood node owns its own DB.
-- Designed to federate: every ID is namespaced so two nodes can merge without collision.

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
  -- Internal ID. UUID so two federated nodes can merge without conflict.
  id             TEXT PRIMARY KEY,

  -- The "handle" shown in the UI. Never the real name unless user opts in.
  handle         TEXT NOT NULL UNIQUE,

  -- Hashed contact info for verification. We store the hash, not the value.
  -- bcrypt hash of email, or null if anonymous
  email_hash     TEXT,
  -- bcrypt hash of phone, or null
  phone_hash     TEXT,

  -- Trust level: 0=anonymous, 1=self-identified, 2=email-verified,
  --              3=neighbor-vouched, 4=address-verified, 5=full-resident
  trust_level    INTEGER NOT NULL DEFAULT 0,

  -- Which neighborhood node issued this identity. Format: "slug@domain"
  -- e.g. "westwaldo@waldonet.local"
  home_node      TEXT NOT NULL,

  -- Public key for cryptographic signing (Ed25519, base64url)
  -- Used to sign votes so they're auditable without being traceable
  pubkey         TEXT,

  -- When they joined
  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  last_active    TEXT,

  -- Soft-delete. We never hard delete civic identity records.
  active         INTEGER NOT NULL DEFAULT 1
);

-- ============================================================
-- TRUST VERIFICATION EVENTS
-- Every time trust level changes, we record why.
-- This is the audit trail for the trust system.
-- ============================================================

CREATE TABLE IF NOT EXISTS trust_events (
  id             TEXT PRIMARY KEY,
  user_id        TEXT NOT NULL REFERENCES users(id),

  -- What changed
  from_level     INTEGER NOT NULL,
  to_level       INTEGER NOT NULL,

  -- How it happened
  -- 'self_register', 'email_verify', 'phone_verify', 'vouched_by',
  -- 'address_check', 'manual_admin', 'revoked'
  method         TEXT NOT NULL,

  -- For vouching: who vouched. For admin: who approved.
  actor_user_id  TEXT REFERENCES users(id),
  actor_note     TEXT,

  -- Cryptographic proof if applicable (e.g. email token hash)
  proof_hash     TEXT,

  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- VOUCHES
-- Neighbor-vouching is how trust level 3 works.
-- A resident vouches "I know this person lives in this neighborhood."
-- Requires the voucher to be at trust_level >= 4.
-- ============================================================

CREATE TABLE IF NOT EXISTS vouches (
  id             TEXT PRIMARY KEY,
  voucher_id     TEXT NOT NULL REFERENCES users(id),
  vouchee_id     TEXT NOT NULL REFERENCES users(id),

  -- Optional note from the voucher
  note           TEXT,

  -- Can be revoked
  active         INTEGER NOT NULL DEFAULT 1,
  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  revoked_at     TEXT,

  UNIQUE(voucher_id, vouchee_id)
);

-- ============================================================
-- PROPOSALS
-- A proposal is anything put to a vote: policy, budget item,
-- board decision, neighborhood priority, federation agreement.
-- ============================================================

CREATE TABLE IF NOT EXISTS proposals (
  id             TEXT PRIMARY KEY,

  -- Who created it
  author_id      TEXT NOT NULL REFERENCES users(id),
  author_node    TEXT NOT NULL,

  -- Title shown in UI
  title          TEXT NOT NULL,

  -- Full text of the proposal. Markdown.
  body           TEXT NOT NULL,

  -- Category: 'policy', 'budget', 'board', 'priority', 'federation',
  --           'constitutional', 'recall', 'survey'
  category       TEXT NOT NULL DEFAULT 'policy',

  -- Minimum trust level required to vote
  -- 0 = anyone (useful for surveys), 2 = email-verified,
  -- 4 = address-verified (meaningful civic votes)
  min_trust      INTEGER NOT NULL DEFAULT 2,

  -- Voting method: 'binary' (yes/no), 'approval' (pick any),
  --                'ranked' (1,2,3...), 'score' (1-5),
  --                'liquid' (vote or delegate)
  vote_method    TEXT NOT NULL DEFAULT 'binary',

  -- For liquid democracy: who votes proxy if not overridden
  -- JSON array of {delegate_id, scope} pairs
  default_delegates TEXT,

  -- Quorum rules (JSON): {"min_votes": 10, "min_pct_eligible": 0.1}
  quorum_rules   TEXT,

  -- Status: 'draft', 'open', 'closed', 'passed', 'failed', 'withdrawn', 'archived'
  status         TEXT NOT NULL DEFAULT 'draft',

  -- If this is a federation-level proposal, list of participating node slugs
  -- JSON array. Null means local-only.
  federation_nodes TEXT,

  -- Timestamps
  opens_at       TEXT,
  closes_at      TEXT,
  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at     TEXT NOT NULL DEFAULT (datetime('now')),

  -- Cryptographic hash of the proposal body at time of opening.
  -- Prevents retroactive edits after votes are cast.
  body_hash      TEXT
);

-- ============================================================
-- VOTES
-- The actual cast vote records.
-- Designed so the vote is verifiable but not traceable.
-- ============================================================

CREATE TABLE IF NOT EXISTS votes (
  id             TEXT PRIMARY KEY,

  proposal_id    TEXT NOT NULL REFERENCES proposals(id),

  -- Blinded voter ID: hash(user_id + proposal_id + secret_salt)
  -- Not the raw user_id. Allows verifying "this person voted once"
  -- without exposing who voted for what.
  voter_blind_id TEXT NOT NULL,

  -- For liquid democracy: if this is a delegated vote, record the chain
  -- JSON: [{delegator_blind_id, delegate_blind_id}, ...]
  delegation_chain TEXT,

  -- The actual vote value:
  -- binary: 'yes' | 'no' | 'abstain'
  -- approval: JSON array of option ids
  -- ranked: JSON array of option ids in ranked order
  -- score: JSON object {option_id: score}
  -- liquid: 'yes' | 'no' | 'delegate:<delegate_blind_id>'
  value          TEXT NOT NULL,

  -- Cryptographic signature of (voter_blind_id + proposal_id + value)
  -- using the voter's private key. Verifiable against the pubkey in users.
  signature      TEXT,

  -- When cast
  cast_at        TEXT NOT NULL DEFAULT (datetime('now')),

  -- One vote per (blinded) voter per proposal
  UNIQUE(proposal_id, voter_blind_id)
);

-- ============================================================
-- VOTE OPTIONS
-- For approval/ranked/score voting: the options to choose from.
-- Binary proposals don't need rows here (yes/no is implied).
-- ============================================================

CREATE TABLE IF NOT EXISTS vote_options (
  id             TEXT PRIMARY KEY,
  proposal_id    TEXT NOT NULL REFERENCES proposals(id),
  label          TEXT NOT NULL,
  description    TEXT,
  sort_order     INTEGER NOT NULL DEFAULT 0
);

-- ============================================================
-- FEDERATION PEERS
-- Other neighborhood nodes this node has established trust with.
-- Federation is bilateral: both sides must agree.
-- ============================================================

CREATE TABLE IF NOT EXISTS federation_peers (
  id             TEXT PRIMARY KEY,

  -- Their node slug: "brookside@waldonet.local"
  peer_node      TEXT NOT NULL UNIQUE,

  -- Human-readable name
  peer_name      TEXT,

  -- Their API endpoint (if they expose one)
  peer_url       TEXT,

  -- Their public key (for verifying signed vote bundles they send)
  peer_pubkey    TEXT NOT NULL,

  -- Our relationship:
  -- 'pending_out' = we requested, they haven't confirmed
  -- 'pending_in'  = they requested, we haven't confirmed
  -- 'active'      = mutual trust established
  -- 'suspended'   = temporarily paused
  -- 'revoked'     = terminated
  status         TEXT NOT NULL DEFAULT 'pending_out',

  -- What we share with them (JSON array):
  -- 'aggregated_votes', 'proposal_text', 'health_index', 'user_count'
  share_scope    TEXT NOT NULL DEFAULT '["aggregated_votes","user_count"]',

  -- What they share with us
  recv_scope     TEXT,

  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- SESSIONS
-- Login sessions for the web UI.
-- Short-lived. Not a social platform.
-- ============================================================

CREATE TABLE IF NOT EXISTS sessions (
  token          TEXT PRIMARY KEY,
  user_id        TEXT NOT NULL REFERENCES users(id),
  created_at     TEXT NOT NULL DEFAULT (datetime('now')),
  expires_at     TEXT NOT NULL,
  -- IP or device hint for audit
  hint           TEXT
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_users_handle       ON users(handle);
CREATE INDEX IF NOT EXISTS idx_users_home_node    ON users(home_node);
CREATE INDEX IF NOT EXISTS idx_users_trust        ON users(trust_level);
CREATE INDEX IF NOT EXISTS idx_trust_events_user  ON trust_events(user_id);
CREATE INDEX IF NOT EXISTS idx_vouches_voucher    ON vouches(voucher_id);
CREATE INDEX IF NOT EXISTS idx_vouches_vouchee    ON vouches(vouchee_id);
CREATE INDEX IF NOT EXISTS idx_proposals_status   ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_author   ON proposals(author_id);
CREATE INDEX IF NOT EXISTS idx_votes_proposal     ON votes(proposal_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user      ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires   ON sessions(expires_at);
