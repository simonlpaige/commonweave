# Civic Identity System

> Sign up as a neighbor. Earn trust. Vote on things that matter. Federate with other neighborhoods.

Part of NeighborhoodOS / Ecolibrium. Runs on neighborhood-owned hardware.

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
  schema.sql     - SQLite schema (users, votes, proposals, federation peers)
  identity.js    - User registration, trust levels, vouching, sessions
  voting.js      - Proposals, vote casting, tallying (all 5 methods)
  federation.js  - Peer management, bundle signing/verification, cross-node votes
  api.js         - HTTP API server (pure Node, no framework)
  README.md      - This file
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

## Roadmap

- [ ] **Email sending** - currently returns the token directly (dev mode). Wire up Resend.
- [ ] **Address verification UI** - admin screen for coordinators to review and approve
- [ ] **Liquid democracy UI** - show delegation chain, let users see who they delegated to
- [ ] **Federation sync cron** - periodic bundle exchange with active peers
- [ ] **Whisper integration** - auto-extract commitments from meeting transcripts, propose them as trackable items
- [ ] **Election-grade audit** - generate Belenios-compatible audit log for high-stakes votes
- [ ] **Mobile-friendly web UI** - static HTML, works offline, designed for neighborhood meetings

---

## Connection to Ecolibrium

This is Ecolibrium's "Democratic Infrastructure" layer made concrete.

From `BLUEPRINT.md`:
> "Verifiable, tamper-resistant voting at local scale" ✓ (this)
> "Liquid democracy options" ✓ (this)
> "Mandatory inclusion for marginalized voices" → vouching system + low barrier entry
> "Recall and accountability mechanisms" → recall category in proposals

And from NeighborhoodOS:
> The Layer 4 (Resident Voice) + Layer 5 (Federation) infrastructure is this system.

---

*Larry (AlphaWorm AI) + Simon L. Paige, April 2026*
