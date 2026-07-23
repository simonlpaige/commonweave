# Attraction Plan: how organizations find Commonweave and want to stay

*2026-07-03, written as part of the red-team rebuild. Companion to OUTREACH.md
(which governs how we contact people). This document is about the opposite
direction: making the directory useful enough that orgs, networks, and
organizers come to it, claim their place in it, and tell others.*

The May 2026 automated outreach experiment taught the lesson the hard way:
push doesn't work for a project whose entire value is trust. A cold email
from an unknown directory is spam; the same directory handing you something
you actually need is infrastructure. Everything below is a variation on one
move: **give a specific, verifiable, locally-relevant gift, and make the
next step obvious and voluntary.**

The asset that makes this possible now exists: `data/map/circuits.json`
identifies groups of nearby organizations that jointly fill the roles of a
documented solution circuit (land + build labor + finance = housing pipeline;
grower + distributor + food access = local food loop; and eight more). That
is information almost no local org has about itself.

---

## Mechanism 1: Circuit introduction briefs (the gift that's also the thesis)

**What.** A one-page brief per circuit candidate: "Within 12 km of each
other: {Land steward} + {Build labor} + {Community finance}. Together these
three could run a labor-for-housing pipeline. Here's the documented pattern
(LABOR-FOR-HOUSING-GUIDE.md), here's what each role contributes, here's what
usually goes wrong." Rendered from circuits.json with a stable URL per
circuit group (map deep-link + printable page).

**Why it attracts.** It's the only artifact in this space that tells three
specific orgs something actionable about *each other*. Nobody has to join
anything: the brief is complete without us. If it's wrong, the correction
flow teaches us; if it's right, we're the project that introduced them.

**How it ships with zero budget.**
- Generator: `tools/build-circuit-briefs.py` renders a static `briefs/` index,
  printable page per group, machine-readable manifest, and sitemap entries.
  As of 2026-07-22, the source declares 76 candidates but contains 13 groups;
  the manifest records that mismatch, and public copy must not claim 76 until
  the export is repaired.
- Distribution is NOT bulk email. Route each brief through the most
  credible LOCAL channel: the city's co-op development center, a CLT
  network's newsletter, one warm human. One brief, hand-delivered, per week
  beats 500 sends.
- Every brief ends with: "Are we wrong about one of these three orgs?
  Correct us" → prefilled GitHub issue (already wired in map.html).

**Success metric.** Replies/corrections per brief delivered (target: any
response on 1 in 4); one documented introduction that led to a real meeting
within 90 days.

## Mechanism 2: Serve federations, not individual orgs

**What.** Every federation/network in the directory (ICA, RIPESS, Grounded
Solutions, Transition Network, mutual aid hubs...) maintains a member
directory, and every one of those directories is partly stale. We generate
**member-directory health reports**: dead websites, moved orgs, missing
geocodes, members that appear in other networks, members that show up in
circuit candidates. CC0, no strings.

**Why it attracts.** One conversation with a network reaches hundreds of
orgs with borrowed trust. Networks have a real, unglamorous maintenance
problem we can partially automate. The report is useful even if they ignore
us forever — which is exactly why it works.

**How it ships.** `tools/federation-health-report.py` reading the DB +
link-checker (a weekend). Deliver v1 to the two networks already curated in
`data/federations.yaml` (ICA, and pick one of RIPESS/Grounded Solutions).
Ask nothing except "is this useful? what did we get wrong?"

**Success metric.** 1 network integrates or replies substantively per
quarter; their members start appearing in the corrections queue (that means
they're looking).

## Mechanism 3: Claim your listing (make the directory self-improving)

**What.** A visible, low-friction path for an org to verify and own its
entry: "This is us" → confirm/fix details → entry gets the reviewed marker
(Tier A path) and a `claimed` badge on the map + a small embeddable badge
("On the Commonweave map — 29,378 organizations weaving healthier
communities") for their site, which links back to their map deep-link.

**Why it attracts.** The badge is a tiny status good and a backlink engine;
each claimed listing is a unit of Tier A data we didn't have to research;
each embed is organic distribution to exactly the right audience.

**How it ships.** Phase 1 needs no backend: "Claim this listing" button in
the map detail panel → prefilled GitHub issue with a `claim` label + an
email fallback (hello@commonweave.earth). A maintainer verifies (reply from
an org-domain address or the org's listed site referencing the claim),
flips `review_status`, done. Badge = one static SVG endpoint per org id.

**Success metric.** Claims per month (target: 5/mo by day 90); % of claims
that arrive via another org's badge or brief (the compounding signal).

---

## Grassroots sequencing (30 / 60 / 90)

**Days 1–30 — prove the gift works.** Ship brief generator; hand-deliver 4
circuit briefs (one per week) through one warm channel each, chosen from the
strongest US candidates in circuits.json (Hartford, Syracuse, Tulsa, Durham
are already promising). Add the claim button. Effort: ~2 evenings/week.
Gate: if 0 of 4 briefs get any response, the brief format is wrong — revise
before scaling, don't send more.

**Days 31–60 — borrow a network's trust.** Federation health report v1 to
ICA + one other. Post ONE show-don't-tell artifact where practitioners
already talk (co-op listservs, a CLT network call, r/cooperatives): the
city-level circuit map for one metro, framed as a question — "we think
these three orgs could build housing together; what are we missing?" —
not an announcement.

**Days 61–90 — make it a habit.** Monthly "weave report": what got added,
what got corrected, which circuits got stronger, one introduction that
happened. Same post, three places (site, one listserv, one fediverse
account). Invite one guest correction-sprint with a partner network's
members.

**What we deliberately do NOT do:** bulk email campaigns, GitHub issue
outreach, engagement-bait threads, press releases, "launch" theater. The
directory is infrastructure; infrastructure earns trust by being repeatedly
useful in small ways.

---

## Honesty rails (applies to every mechanism)

- Every number quoted anywhere comes from `data/map/stats.v3.json` with its
  build date. No exceptions (OUTREACH.md rule 6).
- Circuit briefs say "derived, unverified — treat as an introduction worth
  making, not an existing partnership" in the body, not a footnote.
- Every artifact carries its correction path. The gift includes the ability
  to tell us we're wrong; that's what makes it credible.
