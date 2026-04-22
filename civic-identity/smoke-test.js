// civic-identity/smoke-test.js
// Fast sanity check. Runs the main flows end-to-end against a temp DB.
// Not a full test suite; just the path the deep-dive review flagged as
// most likely to break on a fresh box.
//
// Usage: node civic-identity/smoke-test.js

import { existsSync, unlinkSync } from 'fs';
import { openDB, registerAnonymous, addEmail, verifyEmail, vouchFor,
         verifyAddress, createSession, resolveSession } from './identity.js';
import { createProposal, openProposal, castVote, tallyVotes,
         delegateVote, closeProposal, verifyBody } from './voting.js';
import { createIssue, acknowledgeIssue, resolveIssue } from './issues.js';
import { addCommitment, resolveCommitment, followThroughScores } from './commitments.js';
import { logAction, recentAudit } from './audit.js';
import { rateLimitCheck, LIMITS } from './rate-limit.js';
import { runRetention } from './retention.js';
import { currentVersion } from './migrations.js';
import { ensureAdminTokensTable, addAdminToken, verifyAdminToken,
         revokeAdminToken, rotateAdminToken } from './admin-tokens.js';
import { ensureAddressApprovalsTable, requestAddressVerification,
         approveAddressVerification } from './two-op-verify.js';
import { loadConfig, _resetConfigCache } from './config.js';
import { combineFederationResults } from './federation-aggregate.js';
import { renderBallotPdf } from './ballot-pdf.js';
import { renderDigest } from './digest.js';

const DB_PATH = './smoke-test.db';
if (existsSync(DB_PATH)) unlinkSync(DB_PATH);
if (existsSync(DB_PATH + '-shm')) unlinkSync(DB_PATH + '-shm');
if (existsSync(DB_PATH + '-wal')) unlinkSync(DB_PATH + '-wal');

let passed = 0;
let failed = 0;
async function check(name, fn) {
  try {
    const maybe = fn();
    if (maybe && typeof maybe.then === 'function') await maybe;
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.log(`  ✗ ${name}: ${err.message}`);
    failed++;
  }
}

console.log('\nSmoke test: civic-identity\n');

const db = openDB(DB_PATH);

check('migrations applied', () => {
  const v = currentVersion(db);
  if (v < 1) throw new Error(`expected version >= 1, got ${v}`);
});

check('register returns one-time private key', () => {
  const alice = registerAnonymous(db, 'alice', 'test@local');
  if (!alice._oneTimePrivateKey) throw new Error('missing _oneTimePrivateKey');
  if (!alice.pubkey) throw new Error('missing pubkey in user row');
});

const alice = db.prepare(`SELECT * FROM users WHERE handle = 'alice'`).get();
const bob   = registerAnonymous(db, 'bob', 'test@local');
const carol = registerAnonymous(db, 'carol', 'test@local');
const dave  = registerAnonymous(db, 'dave', 'test@local');

check('duplicate handle rejected', () => {
  try { registerAnonymous(db, 'alice', 'test@local'); throw new Error('should have rejected'); }
  catch (e) { if (!/already taken/.test(e.message)) throw e; }
});

// Email flow
check('email verify flow', () => {
  const token = addEmail(db, alice.id, 'alice@example.com');
  verifyEmail(db, alice.id, token);
  const a = db.prepare(`SELECT trust_level FROM users WHERE id = ?`).get(alice.id);
  if (a.trust_level < 2) throw new Error(`expected trust >= 2, got ${a.trust_level}`);
});

check('used email token cannot be replayed', () => {
  try {
    const token = addEmail(db, bob.id, 'bob@example.com');
    verifyEmail(db, bob.id, token);
    verifyEmail(db, bob.id, token); // second try
    throw new Error('should have rejected replay');
  } catch (e) {
    if (!/No pending|Invalid verification/.test(e.message)) throw e;
  }
});

// Elevate carol to trust 4 (admin-seeded for test), then she can vouch and verify.
db.prepare(`UPDATE users SET trust_level = 4 WHERE id = ?`).run(carol.id);

check('vouch raises to trust 3', () => {
  vouchFor(db, carol.id, dave.id, 'neighbor');
  const d = db.prepare(`SELECT trust_level FROM users WHERE id = ?`).get(dave.id);
  if (d.trust_level !== 3) throw new Error(`expected 3, got ${d.trust_level}`);
});

check('address verification raises to trust 4', () => {
  verifyAddress(db, carol.id, dave.id, 'lease on file');
  const d = db.prepare(`SELECT trust_level FROM users WHERE id = ?`).get(dave.id);
  if (d.trust_level !== 4) throw new Error(`expected 4, got ${d.trust_level}`);
});

// Proposals + voting
const proposal = createProposal(db, {
  authorId: alice.id,
  authorNode: 'test@local',
  title: 'Should we do the thing?',
  body: 'This is the body of the proposal that is long enough to pass validation.',
  category: 'policy',
  minTrust: 0,
  voteMethod: 'binary'
});

check('cannot open as random user', () => {
  try {
    openProposal(db, proposal.id, bob.id);
    throw new Error('should have rejected');
  } catch (e) {
    if (!/Only the author/.test(e.message)) throw e;
  }
});

check('author can open proposal', () => {
  openProposal(db, proposal.id, alice.id);
  const p = db.prepare(`SELECT status, voting_salt, body_hash FROM proposals WHERE id = ?`).get(proposal.id);
  if (p.status !== 'open') throw new Error(`status ${p.status}`);
  if (!p.voting_salt) throw new Error('voting_salt not set');
  if (p.body_hash.includes(':')) throw new Error('body_hash contaminated with salt');
});

check('body verification works', () => {
  const result = verifyBody(db, proposal.id);
  if (!result.verified) throw new Error('body should verify cleanly');
});

check('cast binary votes', () => {
  castVote(db, { userId: alice.id, proposalId: proposal.id, value: 'yes' });
  castVote(db, { userId: bob.id,   proposalId: proposal.id, value: 'yes' });
  castVote(db, { userId: carol.id, proposalId: proposal.id, value: 'no' });
  const t = tallyVotes(db, proposal.id);
  if (t.counts.yes !== 2 || t.counts.no !== 1) throw new Error(JSON.stringify(t));
});

check('double-vote blocked', () => {
  try {
    castVote(db, { userId: alice.id, proposalId: proposal.id, value: 'yes' });
    throw new Error('should have blocked');
  } catch (e) {
    if (!/already voted/.test(e.message)) throw e;
  }
});

check('close proposal', () => {
  const r = closeProposal(db, proposal.id, alice.id);
  if (!r.passed) throw new Error('expected passed');
});

// Liquid delegation - the previously broken path
const lq = createProposal(db, {
  authorId: alice.id,
  authorNode: 'test@local',
  title: 'Liquid test proposal',
  body: 'This is a liquid democracy test proposal to verify the delegation chain resolver actually works in blind-space now.',
  category: 'policy',
  minTrust: 0,
  voteMethod: 'liquid'
});
openProposal(db, lq.id, alice.id);

check('liquid: A delegates to B who delegates to C who votes yes => C gets weight 3', () => {
  // dave delegates to bob
  delegateVote(db, { delegatorId: dave.id, delegateId: bob.id, proposalId: lq.id });
  // bob delegates to carol
  delegateVote(db, { delegatorId: bob.id, delegateId: carol.id, proposalId: lq.id });
  // carol votes yes
  castVote(db, { userId: carol.id, proposalId: lq.id, value: 'yes' });
  const t = tallyVotes(db, lq.id);
  // carol has weight 3: her own + bob's + dave's (via bob)
  if (t.counts.yes !== 3) throw new Error(`expected yes=3, got ${JSON.stringify(t.counts)}`);
  if (t.directVoters !== 1) throw new Error(`expected directVoters=1, got ${t.directVoters}`);
  if (t.delegators !== 2) throw new Error(`expected delegators=2, got ${t.delegators}`);
});

// Issues
check('file issue', () => {
  const i = createIssue(db, {
    reporterUserId: alice.id, category: 'infrastructure',
    title: 'Potholes on 79th', body: 'Several deep ones at the bus stop.'
  });
  if (i.status !== 'open') throw new Error(`status ${i.status}`);
});

check('acknowledge needs trust 3', () => {
  const i = createIssue(db, {
    reporterUserId: alice.id, category: 'safety',
    title: 'Broken streetlight', body: 'The one at 80th and Wornall is out.'
  });
  try {
    acknowledgeIssue(db, i.id, bob.id); // bob has trust 2
    throw new Error('should have rejected');
  } catch (e) { if (!/trust level 3/i.test(e.message)) throw e; }
  // dave has trust 4 via vouching+address
  acknowledgeIssue(db, i.id, dave.id);
});

// Commitments
check('commitment lifecycle', () => {
  const c = addCommitment(db, {
    description: 'Fix the pothole at 79th and Wornall', committedBy: 'Public Works',
    dueDate: '2026-05-01'
  });
  if (c.status !== 'open') throw new Error('status');
  const r = resolveCommitment(db, c.id, carol.id, 'Filled.');
  if (r.status !== 'resolved') throw new Error('status');
});

check('follow-through scores', () => {
  const scores = followThroughScores(db);
  if (!Array.isArray(scores)) throw new Error('expected array');
});

// Rate limiter
check('rate limit burst rejects after max', () => {
  const results = [];
  for (let i = 0; i < 7; i++) {
    results.push(rateLimitCheck(db, 'test:burst', { max: 5, windowMs: 60_000 }).allowed);
  }
  const allowed = results.filter(Boolean).length;
  if (allowed !== 5) throw new Error(`allowed=${allowed}, expected 5`);
});

// Audit log
check('audit log writes and reads', () => {
  logAction(db, { actorUserId: alice.id, actorIp: '127.0.0.1',
                  action: 'test.action', targetType: 'test', targetId: 'abc' });
  const entries = recentAudit(db, { action: 'test.action' });
  if (entries.length === 0) throw new Error('no audit entries');
  if (entries[0].actor_ip_hash === '127.0.0.1') throw new Error('IP not hashed');
});

// Sessions + retention
check('session create/resolve/destroy', () => {
  const tok = createSession(db, alice.id);
  const s = resolveSession(db, tok);
  if (!s || s.userId !== alice.id) throw new Error('bad session');
});

check('retention job runs', () => {
  const r = runRetention(db);
  if (typeof r.sessionsDropped !== 'number') throw new Error('retention shape');
});

// Per-admin tokens
ensureAdminTokensTable(db);
let simonToken, adminPrincipal;
check('admin token add', () => {
  const created = addAdminToken(db, { label: 'simon@waldonet' });
  simonToken = created.token;
  if (!simonToken || simonToken.length < 20) throw new Error('short token');
});
check('admin token verify', () => {
  adminPrincipal = verifyAdminToken(db, simonToken);
  if (!adminPrincipal || adminPrincipal.label !== 'simon@waldonet') throw new Error('principal mismatch');
});
check('admin token bad token rejected', () => {
  const p = verifyAdminToken(db, 'not-a-real-token-but-long-enough-to-pass');
  if (p !== null) throw new Error('bad token accepted');
});
check('admin token revoke', () => {
  revokeAdminToken(db, 'simon@waldonet');
  const p = verifyAdminToken(db, simonToken);
  if (p !== null) throw new Error('revoked token still works');
});
check('admin token rotate', () => {
  addAdminToken(db, { label: 'backup@waldonet' });
  const newOne = rotateAdminToken(db, 'backup@waldonet');
  const p = verifyAdminToken(db, newOne.token);
  if (!p) throw new Error('rotated token does not verify');
});

// Two-operator address verification
ensureAddressApprovalsTable(db);
check('two-op: single coordinator cannot self-approve', () => {
  const rookie = registerAnonymous(db, 'rookie1', 'test@local');
  const req = requestAddressVerification(db, {
    requesterId: carol.id, targetUserId: rookie.id, note: 'lease'
  });
  try {
    approveAddressVerification(db, { requestId: req.id, approverId: carol.id });
    throw new Error('should have rejected same-coordinator approval');
  } catch (e) {
    if (!/different coordinator/.test(e.message)) throw e;
  }
});

check('two-op: second coordinator approves and promotes', () => {
  // Need a second trust-4+ coordinator. Dave is trust 4 via earlier test.
  const rookie = registerAnonymous(db, 'rookie2', 'test@local');
  const req = requestAddressVerification(db, {
    requesterId: carol.id, targetUserId: rookie.id, note: 'lease'
  });
  const result = approveAddressVerification(db, {
    requestId: req.id, approverId: dave.id, note: 'second op ok'
  });
  if (result.user.trust_level !== 4) throw new Error('not promoted');
});

// Federation aggregation
check('federation aggregation: one_person_one_vote', () => {
  const result = combineFederationResults([
    { nodeSlug: 'a', status: 'received', tally: { counts: { yes: 300, no: 120, abstain: 5 } } },
    { nodeSlug: 'b', status: 'received', tally: { counts: { yes:  20, no:  45, abstain: 2 } } }
  ]);
  if (!result.complete) throw new Error('should be complete');
  if (!result.passed) throw new Error('expected passed (320 > 165)');
});

check('federation aggregation: one_node_one_vote', () => {
  const result = combineFederationResults([
    { nodeSlug: 'a', status: 'received', tally: { counts: { yes: 300, no: 120 } } },
    { nodeSlug: 'b', status: 'received', tally: { counts: { yes:  20, no:  45 } } },
    { nodeSlug: 'c', status: 'received', tally: { counts: { yes:  10, no:  40 } } }
  ], { mode: 'one_node_one_vote' });
  if (!result.complete) throw new Error('should be complete');
  // node a yes, nodes b and c no -> federation no
  if (result.passed) throw new Error('expected caucus failure');
  if (result.yesNodes !== 1 || result.noNodes !== 2) throw new Error('node counts wrong');
});

check('federation aggregation: refuses to complete if missing', () => {
  const result = combineFederationResults([
    { nodeSlug: 'a', status: 'received', tally: { counts: { yes: 10, no: 5 } } },
    { nodeSlug: 'b', status: 'pending' }
  ]);
  if (result.complete) throw new Error('should have refused');
});

// Config loader
check('config loader returns defaults without a file', () => {
  _resetConfigCache();
  const cfg = loadConfig();
  if (!cfg.slug || !cfg.bounds) throw new Error('missing defaults');
});

// Ballot PDF (just make sure it returns bytes without throwing)
await check('ballot PDF generates bytes', async () => {
  const bytes = await renderBallotPdf(db, lq.id, { baseUrl: 'http://localhost:4242' });
  if (!bytes || bytes.length < 1000) throw new Error('tiny or empty PDF');
});

// Digest render
check('digest renders markdown', () => {
  const md = renderDigest(db, { days: 7 });
  if (!md.includes('weekly digest')) throw new Error('digest missing header');
});

db.close();

console.log(`\n${passed} passed, ${failed} failed\n`);
if (existsSync(DB_PATH)) unlinkSync(DB_PATH);
if (existsSync(DB_PATH + '-shm')) unlinkSync(DB_PATH + '-shm');
if (existsSync(DB_PATH + '-wal')) unlinkSync(DB_PATH + '-wal');
process.exit(failed > 0 ? 1 : 0);
