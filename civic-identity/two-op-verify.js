// civic-identity/two-op-verify.js
// Two-operator address verification (review recommendation #16).
//
// The original verifyAddress() in identity.js lets a single trust-4+ user
// promote someone to trust 4. One compromised or careless coordinator can
// then mint fake residents. This module adds a second-signature gate.
//
// Flow:
//   1. Coordinator A calls requestAddressVerification(target, proofNote).
//      A pending_address_approval row is written with approverA recorded.
//   2. Coordinator B calls approveAddressVerification(requestId).
//      If B is a different trust-4+ user, the target is promoted and the
//      row is marked completed.
//   3. Either operator can reject the request, which leaves the target at
//      their current trust level.
//
// If FORCE_TWO_OP is false (env: CIVIC_REQUIRE_TWO_OP=0), the original
// single-signature verifyAddress path still exists. The recommendation in
// the review was to REQUIRE two signatures, so the default here is on.

import crypto from 'crypto';
import { getUser } from './identity.js';

const REQUIRE_TWO_OP = process.env.CIVIC_REQUIRE_TWO_OP !== '0';

export function ensureAddressApprovalsTable(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS address_approvals (
      id              TEXT PRIMARY KEY,
      target_user_id  TEXT NOT NULL REFERENCES users(id),
      requester_id    TEXT NOT NULL REFERENCES users(id),
      requester_note  TEXT,
      approver_id     TEXT REFERENCES users(id),
      approver_note   TEXT,
      status          TEXT NOT NULL DEFAULT 'pending',
      created_at      TEXT NOT NULL DEFAULT (datetime('now')),
      completed_at    TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_addr_appr_status ON address_approvals(status);
    CREATE INDEX IF NOT EXISTS idx_addr_appr_target ON address_approvals(target_user_id);
  `);
}

// Coordinator A opens a request. Does not change trust yet.
export function requestAddressVerification(db, { requesterId, targetUserId, note = null }) {
  const requester = getUser(db, requesterId);
  if (!requester || requester.trust_level < 4) {
    throw new Error('Only trust-4+ coordinators can request address verification');
  }
  const target = getUser(db, targetUserId);
  if (!target) throw new Error('Target user not found');
  if (requesterId === targetUserId) throw new Error('Cannot verify your own address');

  // No duplicate pending requests for the same target.
  const existing = db.prepare(`
    SELECT id FROM address_approvals WHERE target_user_id = ? AND status = 'pending'
  `).get(targetUserId);
  if (existing) throw new Error('A pending address verification already exists for this user');

  const id = crypto.randomUUID();
  db.prepare(`
    INSERT INTO address_approvals (id, target_user_id, requester_id, requester_note)
    VALUES (?, ?, ?, ?)
  `).run(id, targetUserId, requesterId, note || null);

  return getRequest(db, id);
}

// Coordinator B approves. Must be a different trust-4+ user.
// When REQUIRE_TWO_OP is off (dev), the requester can approve themselves,
// which collapses the flow back to a single-signature promotion. That mode
// exists only for development and is not the default.
export function approveAddressVerification(db, { requestId, approverId, note = null }) {
  const approver = getUser(db, approverId);
  if (!approver || approver.trust_level < 4) {
    throw new Error('Only trust-4+ coordinators can approve address verification');
  }

  const req = getRequest(db, requestId);
  if (!req) throw new Error('Request not found');
  if (req.status !== 'pending') throw new Error(`Request is ${req.status}, not pending`);

  if (REQUIRE_TWO_OP && approverId === req.requester_id) {
    throw new Error('Approver must be a different coordinator than the requester');
  }

  // Promote the target to trust 4 atomically with the approval write.
  db.transaction(() => {
    const target = getUser(db, req.target_user_id);
    const newLevel = Math.max(target.trust_level, 4);

    db.prepare(`UPDATE users SET trust_level = ? WHERE id = ?`).run(newLevel, req.target_user_id);

    // Log both signatures in trust_events so the audit trail shows the pair.
    const id1 = crypto.randomUUID();
    const id2 = crypto.randomUUID();
    db.prepare(`
      INSERT INTO trust_events
        (id, user_id, from_level, to_level, method, actor_user_id, actor_note, created_at)
      VALUES
        (?, ?, ?, ?, 'address_check_request', ?, ?, datetime('now')),
        (?, ?, ?, ?, 'address_check_approve', ?, ?, datetime('now'))
    `).run(
      id1, req.target_user_id, target.trust_level, newLevel, req.requester_id, req.requester_note || null,
      id2, req.target_user_id, target.trust_level, newLevel, approverId,       note || null
    );

    db.prepare(`
      UPDATE address_approvals
      SET status = 'completed', approver_id = ?, approver_note = ?, completed_at = datetime('now')
      WHERE id = ?
    `).run(approverId, note || null, requestId);
  })();

  return { request: getRequest(db, requestId), user: getUser(db, req.target_user_id) };
}

export function rejectAddressVerification(db, { requestId, actorUserId, note = null }) {
  const req = getRequest(db, requestId);
  if (!req) throw new Error('Request not found');
  if (req.status !== 'pending') throw new Error(`Request is ${req.status}, not pending`);

  const actor = getUser(db, actorUserId);
  if (!actor || actor.trust_level < 4) throw new Error('Trust 4+ required to reject');

  db.prepare(`
    UPDATE address_approvals
    SET status = 'rejected', approver_id = ?, approver_note = ?, completed_at = datetime('now')
    WHERE id = ?
  `).run(actorUserId, note || null, requestId);
  return getRequest(db, requestId);
}

export function listPendingAddressVerifications(db) {
  return db.prepare(`
    SELECT a.*, tu.handle as target_handle, ru.handle as requester_handle
    FROM address_approvals a
    JOIN users tu ON a.target_user_id = tu.id
    JOIN users ru ON a.requester_id = ru.id
    WHERE a.status = 'pending'
    ORDER BY a.created_at ASC
  `).all();
}

function getRequest(db, id) {
  return db.prepare(`SELECT * FROM address_approvals WHERE id = ?`).get(id);
}

export function isTwoOpRequired() { return REQUIRE_TWO_OP; }
