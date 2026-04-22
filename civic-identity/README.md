# Civic Identity System

> Sign up as a neighbor. Earn trust. Vote on things that matter. Federate with other neighborhoods.

Part of NeighborhoodOS / Commonweave. Runs on neighborhood-owned hardware.

---

## What It Is

Three things in one system that grow together:

1. **Signup** - Get a handle. Start at zero trust. No data required.
2. **Trust Verification** - Earn higher trust levels by verifying your email, getting vouched by a neighbor, or having a coordinator verify your address.
3. **Federated Voting** - Propose things. Vote on them. Share results (not raw votes) with other neighborhoods.

---

## Trust Levels

| Level | Name | How to Get It | What It Unlocks |
|-------|------|---------------|-----------------|
| 0 | Anonymous | Just sign up with a handle | Read, comment on discussion |
| 1 | Self-identified | Provided email (not yet verified) | Nothing extra yet |
| 2 | Email-verified | Clicked the link | Surveys, advisory votes |
| 3 | Neighbor-vouched | A verified resident vouched for you | Full neighborhood votes |
| 4 | Address-verified | Coordinator checked a bill or lease | Can vouch for others |
| 5 | Full resident | Level 4 + 1 year of participation | Constitutional proposals |

**The floor for meaningful civic votes is level 3.** That means either:
- A neighbor at level 4+ vouches "I know this person lives here," or
- A coordinator checks your address.

Surveys and lightweight feedback work at level 2 (email verified).

---

## Voting Methods

| Method | Use Case | How It Works |
|--------|----------|--------------|
| `binary` | Yes/no decisions | Yes, no, or abstain. Simple majority. |
| `approval` | Pick your favorites | Select any options you support. Highest count wins. |
| `ranked` | Elections, priority lists | Rank options 1, 2, 3. Instant runoff. |
| `score` | Rate proposals 1-5 | Average score per option. Useful for budgets. |
| `liquid` | Delegation democracy | Vote yourself or delegate to a trusted neighbor. |

---

## Privacy Model

**The vote is yours. Who you voted for is not stored.**

- Your voter ID is **blinded** per-proposal using HMAC. Nobody can trace a vote back to you, even with DB access.
- You get a **receipt** after voting. You can verify your vote was counted.
- **Aggregate tallies** are public. Individual vote-to-voter mapping is not.
- Your email is stored as a **bcrypt hash**, not plaintext.
- Nothing is sold. Nothing feeds advertising. No engagement loops.

---

## Federation Model

Each neighborhood runs its own node. Federation is opt-in and bilateral.

**What gets shared (default):**
- User counts by trust level (how many verified residents)
- Aggregated vote tallies on closed proposals (yes: 34, no: 12 - not who voted what)

**What stays local forever:**
- Individual votes
- Email hashes
- Session tokens
- Raw user records

**What can be shared with explicit consent:**
- Full proposal text (so other neighborhoods can see what you decided)
- Detailed vote breakdowns

Federation lets neighborhoods ask: "Is the city doing this to us specifically, or to everyone?" and coordinate responses across district lines without surrendering autonomy.

---

## File Structure

```
civic-identity/
  schema.sql              - Base SQLite schema
  migrations.js           - Versioned migrations runner
  migrations/             - Numbered SQL migrations applied in order
  config.js               - Per-node config loader (node.config.json)
  identity.js             - Registration, trust, sessions, Ed25519 keypair at signup
  voting.js               - Proposals, voting, tallying (binary, approval, ranked IRV, score, liquid)
  two-op-verify.js        - Two-coordinator address verification flow
  federation.js           - Peer management, envelope-signed bundles, replay+staleness guards
  federation-aggregate.js - Combine per-node tallies for federation votes
  audit.js                - Durable audit log for privileged actions
  admin-tokens.js         - Per-admin tokens, hashed at rest, rotatable
  admin-cli.js            - CLI for provisioning/rotating admin tokens
  rate-limit.js           - In-process sliding-window rate limiter
  issues.js               - Resident issue lifecycle
  commitments.js          - Commitment tracker + follow-through scores
  retention.js            - Prune job for expired sessions, old social posts
  ballot-pdf.js           - Paper-ballot generator (letter-size PDF with QR)
  digest.js               - Weekly markdown email digest (nodemailer/SMTP)
  api.js                  - HTTP API server (pure Node, no framework)
  smoke-test.js           - End-to-end sanity tests for the main flows
  federation-smoke.js     - Federation handshake + replay + tamper tests
  FEDERATION-AGGREGATE.md - Governance doc for federation aggregation modes
  README.md               - This file
```

---

## Quick Start

```bash
# Install deps
npm install better-sqlite3 bcrypt

# Start the API
NODE_SLUG="westwaldo@waldonet.local" \
PORT=4242 \
DB_PATH=./civic-identity.db \
node api.js
```

**Register a user:**
```bash
curl -X POST http://localhost:4242/signup \
  -H "Content-Type: application/json" \
  -d '{"handle":"neighbor42"}'
# Returns: {"user": {...}, "token": "..."}
```

**Create a proposal:**
```bash
curl -X POST http://localhost:4242/proposals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Install traffic calming on 75th Street",
    "body": "Proposal to request the city install speed humps on 75th between Wornall and Holmes...",
    "category": "policy",
    "voteMethod": "binary",
    "minTrust": 3
  }'
```

**Vote:**
```bash
curl -X POST http://localhost:4242/proposals/<id>/vote \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"value": "yes"}'
# Returns a receipt with your blinded voter ID
```

---

## Running the Smoke Tests

```bash
# Install deps first (in neighborhood-os/, which hosts node_modules)
cd ../neighborhood-os && npm install && cd ../civic-identity

node smoke-test.js            # end-to-end identity + voting + audit + retention
node federation-smoke.js      # federation bundle build/receive/replay/tamper
```

Both tests use temp SQLite files and clean up after themselves.

## Hardening Features (post 2026-04-21 deep dive)

- **Fail-closed admin.** Admin routes require either a per-admin token or the legacy shared `ADMIN_TOKEN`; `ALLOW_OPEN_ADMIN=1` opens them for local dev only.
- **Per-admin tokens.** Provision, rotate, and revoke per-operator bearer tokens via `admin-cli.js`. Tokens are bcrypt-hashed at rest, labeled (`simon@waldonet`), and prefix-indexed for fast verify. Rotation does not require a server restart.
- **Two-operator address verification.** Promoting a user to trust-4 now requires two distinct trust-4+ coordinators: one requests, another approves. Both signatures land in `trust_events`.
- **Ed25519 keypair at signup.** Private key is returned once at signup and never stored. Public key lives on the user row; vote signatures are verified on cast.
- **Separated voting salt.** `body_hash` stays a pure hash; the per-proposal salt lives in `voting_salt`. `GET /proposals/:id/verify-body` surfaces tampering.
- **Liquid delegation in blind-space.** Delegation chains resolve across multiple hops and never leak raw user ids.
- **Deterministic IRV tiebreak.** When two candidates tie for elimination, the one with the smaller sha256 of its option id is eliminated. Reproducible by any observer, not gameable.
- **Federation replay + tamper guard.** Envelope-signed bundles, 24h staleness window, and signature-seen check.
- **Federation aggregation modes.** `one_person_one_vote` (default), `one_node_one_vote`, and `weighted_capped`. Refuses to report unless every listed peer has responded or timed out. See `FEDERATION-AGGREGATE.md`.
- **Rate limiter.** Sliding-window limits on signup, vote, email, federation receive, and a generic per-IP cap.
- **Audit log.** Every admin and trust-changing action is recorded; IPs are HMAC-hashed with a node-local salt.
- **Issues + commitments API.** Residents can file issues; coordinators (trust 4+) close them out. Commitments link back to originating issues.
- **Paper ballot PDF.** `GET /proposals/:id/ballot.pdf` renders a letter-size ballot with the proposal text, vote options, and a QR code encoding the proposal id and body-hash prefix so the coordinator can scan-verify.
- **Meeting packet PDF.** `GET /meetings/:eventId/packet.pdf` assembles the Legistar agenda and minutes into one printable file.
- **Weekly email digest.** `node digest.js --send` renders a markdown summary of overdue commitments, recent issues, open proposals, and legislative matters, then mails it via SMTP (`SMTP_*` env vars).
- **Connector health probe.** `ingest/sync.js` probes each dataset before pulling; status is in `connector_status`.
- **Network retry + backoff.** Every outbound HTTP call in the connectors goes through `_fetch.js` with three attempts and full-jitter exponential backoff on 429/5xx.
- **PID lockfile on sync.** `ingest/sync.js` writes a pid lock next to the DB so two concurrent syncs cannot contend. `--force` overrides a stale lock.
- **Per-node config.** `node.config.json` (see `node.config.example.json`) holds slug, bounds, topic keywords, social handles, retention windows. No more forking code to stand up node two.
- **Versioned migrations.** Schema evolves via numbered `migrations/*.sql` files, tracked in `schema_version`.

## Roadmap

- [ ] **Email sending** - currently returns the token directly (dev mode). Wire up Resend.
- [ ] **Address verification UI** - admin screen for coordinators to review and approve
- [ ] **Liquid democracy UI** - show delegation chain, let users see who they delegated to
- [ ] **Federation sync cron** - periodic bundle exchange with active peers
- [ ] **Whisper integration** - auto-extract commitments from meeting transcripts
- [ ] **Election-grade audit** - generate Belenios-compatible audit log for high-stakes votes
- [ ] **Mobile-friendly web UI** - static HTML, works offline, designed for neighborhood meetings

---

## Connection to Commonweave

This is Commonweave's "Democratic Infrastructure" layer made concrete.

From `BLUEPRINT.md`:
> "Verifiable, tamper-resistant voting at local scale" ✓ (this)
> "Liquid democracy options" ✓ (this)
> "Mandatory inclusion for marginalized voices" → vouching system + low barrier entry
> "Recall and accountability mechanisms" → recall category in proposals

And from NeighborhoodOS:
> The Layer 4 (Resident Voice) + Layer 5 (Federation) infrastructure is this system.

---

*Larry (AlphaWorm AI) + Simon L. Paige, April 2026*
