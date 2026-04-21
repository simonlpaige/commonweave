// civic-identity/api.js
// Minimal HTTP API server. No framework - pure Node.js http module.
// Designed to run on a neighborhood node (WaldoNet Raspberry Pi or similar).
//
// Routes:
//   POST /signup                    - Register anonymous user
//   POST /verify-email              - Submit email for verification
//   POST /confirm-email             - Confirm email token
//   POST /vouch                     - Vouch for another user
//   GET  /users/:handle             - Get public user profile
//   GET  /stats                     - Node stats (user counts by trust level)
//
//   GET  /proposals                 - List open proposals
//   GET  /proposals/:id             - Get proposal detail + current tally
//   POST /proposals                 - Create a proposal
//   POST /proposals/:id/open        - Open a draft for voting
//   POST /proposals/:id/vote        - Cast a vote
//   GET  /proposals/:id/voted       - Has the current session voted?
//   POST /proposals/:id/close       - Close voting
//
//   GET  /federation/peers          - List federation peers
//   POST /federation/peers          - Add a peer request
//   POST /federation/receive        - Receive a data bundle from a peer
//   GET  /federation/bundle/:peer   - Generate outbound bundle for a peer

import http from 'http';
import crypto from 'crypto';
import { openDB, registerAnonymous, addEmail, verifyEmail, vouchFor, getUser,
         getUserByHandle, getTrustHistory, nodeStats, createSession,
         resolveSession, destroySession } from './identity.js';
import { createProposal, openProposal, closeProposal, castVote, tallyVotes,
         listProposals, getProposal, getVoteCount, hasVoted } from './voting.js';
import { addPeer, activatePeer, getActivePeers, buildShareBundle,
         receiveBundle, ensureFederationTable } from './federation.js';

// ----------------------------------------------------------------
// Config (override via environment variables)
// ----------------------------------------------------------------

const PORT = parseInt(process.env.PORT || '4242');
const DB_PATH = process.env.DB_PATH || './civic-identity.db';
const NODE_SLUG = process.env.NODE_SLUG || 'local@waldonet.local';
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || null; // Required for admin routes
const NODE_PRIVKEY = process.env.NODE_PRIVKEY_PATH
  ? readFileSync(process.env.NODE_PRIVKEY_PATH) : null;

// ----------------------------------------------------------------
// Init
// ----------------------------------------------------------------

const db = openDB(DB_PATH);
ensureFederationTable(db);

// ----------------------------------------------------------------
// Routing
// ----------------------------------------------------------------

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;
  const method = req.method;

  // CORS for local UI dev
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  // Auth: resolve session from Authorization header
  const token = (req.headers.authorization || '').replace('Bearer ', '').trim();
  const session = token ? resolveSession(db, token) : null;

  try {
    // ---- Users ----

    if (method === 'POST' && path === '/signup') {
      const body = await readBody(req);
      const user = registerAnonymous(db, body.handle, NODE_SLUG);
      const sessionToken = createSession(db, user.id);
      return respond(res, 201, { user: publicUser(user), token: sessionToken });
    }

    if (method === 'POST' && path === '/verify-email') {
      requireAuth(session);
      const body = await readBody(req);
      const verifyToken = addEmail(db, session.userId, body.email);
      // In production, email this token. Here we return it (dev mode).
      return respond(res, 200, { message: 'Verification token issued', verifyToken });
    }

    if (method === 'POST' && path === '/confirm-email') {
      requireAuth(session);
      const body = await readBody(req);
      const updated = verifyEmail(db, session.userId, body.token);
      return respond(res, 200, { user: publicUser(updated) });
    }

    if (method === 'POST' && path === '/vouch') {
      requireAuth(session);
      const body = await readBody(req);
      const updated = vouchFor(db, session.userId, body.voucheeId, body.note);
      return respond(res, 200, { user: publicUser(updated) });
    }

    if (method === 'GET' && path === '/me') {
      requireAuth(session);
      const user = getUser(db, session.userId);
      const history = getTrustHistory(db, session.userId);
      return respond(res, 200, { user: publicUser(user), trustHistory: history });
    }

    if (method === 'GET' && path.startsWith('/users/')) {
      const handle = path.split('/users/')[1];
      const user = getUserByHandle(db, handle);
      if (!user) return respond(res, 404, { error: 'User not found' });
      return respond(res, 200, { user: publicUser(user) });
    }

    if (method === 'GET' && path === '/stats') {
      return respond(res, 200, nodeStats(db));
    }

    if (method === 'POST' && path === '/logout') {
      if (token) destroySession(db, token);
      return respond(res, 200, { ok: true });
    }

    // ---- Proposals ----

    if (method === 'GET' && path === '/proposals') {
      const status = url.searchParams.get('status') || 'open';
      const category = url.searchParams.get('category') || null;
      const proposals = listProposals(db, { status, category });
      return respond(res, 200, { proposals: proposals.map(p => proposalSummary(p)) });
    }

    if (method === 'GET' && path.match(/^\/proposals\/[^/]+$/)) {
      const id = path.split('/proposals/')[1];
      const proposal = getProposal(db, id);
      if (!proposal) return respond(res, 404, { error: 'Proposal not found' });

      const tally = ['open', 'closed', 'passed', 'failed'].includes(proposal.status)
        ? tallyVotes(db, id) : null;
      const voted = session ? hasVoted(db, session.userId, id) : false;

      return respond(res, 200, {
        proposal: proposalDetail(proposal),
        tally,
        voteCount: getVoteCount(db, id),
        voted
      });
    }

    if (method === 'POST' && path === '/proposals') {
      requireAuth(session);
      const body = await readBody(req);
      const proposal = createProposal(db, {
        ...body,
        authorId: session.userId,
        authorNode: NODE_SLUG
      });
      return respond(res, 201, { proposal: proposalDetail(proposal) });
    }

    if (method === 'POST' && path.match(/^\/proposals\/[^/]+\/open$/)) {
      requireAuth(session);
      const id = path.split('/proposals/')[1].split('/open')[0];
      const proposal = openProposal(db, id, session.userId);
      return respond(res, 200, { proposal: proposalDetail(proposal) });
    }

    if (method === 'POST' && path.match(/^\/proposals\/[^/]+\/vote$/)) {
      requireAuth(session);
      const id = path.split('/proposals/')[1].split('/vote')[0];
      const body = await readBody(req);
      const result = castVote(db, {
        userId: session.userId,
        proposalId: id,
        value: body.value
      });
      return respond(res, 200, { receipt: result.receipt });
    }

    if (method === 'GET' && path.match(/^\/proposals\/[^/]+\/voted$/)) {
      requireAuth(session);
      const id = path.split('/proposals/')[1].split('/voted')[0];
      return respond(res, 200, { voted: hasVoted(db, session.userId, id) });
    }

    if (method === 'POST' && path.match(/^\/proposals\/[^/]+\/close$/)) {
      requireAuth(session);
      const id = path.split('/proposals/')[1].split('/close')[0];
      const result = closeProposal(db, id);
      return respond(res, 200, result);
    }

    // ---- Federation ----

    if (method === 'GET' && path === '/federation/peers') {
      requireAdmin(req);
      return respond(res, 200, { peers: getActivePeers(db) });
    }

    if (method === 'POST' && path === '/federation/peers') {
      requireAdmin(req);
      const body = await readBody(req);
      const peer = addPeer(db, body);
      return respond(res, 201, { peer });
    }

    if (method === 'POST' && path === '/federation/receive') {
      const body = await readBody(req);
      const result = receiveBundle(db, body);
      return respond(res, 200, result);
    }

    if (method === 'GET' && path.startsWith('/federation/bundle/')) {
      requireAdmin(req);
      const peerNode = decodeURIComponent(path.split('/federation/bundle/')[1]);
      if (!NODE_PRIVKEY) return respond(res, 500, { error: 'Node private key not configured' });
      const bundle = buildShareBundle(db, NODE_SLUG, NODE_PRIVKEY, peerNode);
      return respond(res, 200, bundle);
    }

    // ---- Health ----

    if (method === 'GET' && path === '/health') {
      return respond(res, 200, { ok: true, node: NODE_SLUG, time: new Date().toISOString() });
    }

    respond(res, 404, { error: 'Not found' });

  } catch (err) {
    const status = err.message?.includes('required') || err.message?.includes('must') ? 400
                 : err.message?.includes('not found') ? 404
                 : err.message?.includes('trust level') ? 403
                 : err.message?.includes('already') ? 409
                 : 500;
    respond(res, status, { error: err.message });
  }
});

server.listen(PORT, () => {
  console.log(`Civic Identity API running on port ${PORT}`);
  console.log(`Node: ${NODE_SLUG}`);
  console.log(`DB: ${DB_PATH}`);
});

// ----------------------------------------------------------------
// Helpers
// ----------------------------------------------------------------

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => { data += chunk; });
    req.on('end', () => {
      try { resolve(JSON.parse(data || '{}')); }
      catch { reject(new Error('Invalid JSON body')); }
    });
    req.on('error', reject);
  });
}

function respond(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data, null, 2));
}

function requireAuth(session) {
  if (!session) throw Object.assign(new Error('Authentication required'), { statusCode: 401 });
}

function requireAdmin(req) {
  if (!ADMIN_TOKEN) return; // No admin token set = open (dev mode)
  const token = (req.headers.authorization || '').replace('Bearer ', '').trim();
  if (token !== ADMIN_TOKEN) throw Object.assign(new Error('Admin required'), { statusCode: 401 });
}

// Public-safe user fields (never expose email_hash, phone_hash)
function publicUser(user) {
  if (!user) return null;
  return {
    id: user.id,
    handle: user.handle,
    trustLevel: user.trust_level,
    homeNode: user.home_node,
    createdAt: user.created_at,
    lastActive: user.last_active
  };
}

function proposalSummary(p) {
  return {
    id: p.id,
    title: p.title,
    category: p.category,
    voteMethod: p.vote_method,
    minTrust: p.min_trust,
    status: p.status,
    authorHandle: p.author_handle,
    opensAt: p.opens_at,
    closesAt: p.closes_at,
    createdAt: p.created_at
  };
}

function proposalDetail(p) {
  return {
    ...proposalSummary(p),
    body: p.body,
    federationNodes: p.federation_nodes ? JSON.parse(p.federation_nodes) : null,
    quorumRules: p.quorum_rules ? JSON.parse(p.quorum_rules) : null
  };
}
