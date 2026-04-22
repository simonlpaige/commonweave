# Federation Vote Aggregation

How we combine a federation proposal's per-node tallies into one result.

The short answer: three modes, picked per-proposal. Default is
`one_person_one_vote`. The other two exist because the fair answer depends
on what you are voting on.

---

## Why this document exists

Before this doc, the codebase had a half-built federation-proposal path:
the schema supported `federation_nodes`, each node ran the vote locally,
and there was an endpoint that reported a per-node summary. Nothing said
how to combine those summaries. If a 500-resident node and a 50-resident
node voted on the same thing and we just added the yes/no counts, the
50-resident node's voice was mathematically invisible.

That is a governance bug, not a code bug. Picking an aggregation rule is
a design decision that affects power. It deserves explicit wording.

---

## The three modes

### `one_person_one_vote` (default)

Sum yes, no, and abstain across every reporting node. Majority of
yes-over-no wins.

**When to use:** the decision affects every resident equally, regardless
of which node they live in. Example: "Should the federation of
neighborhoods jointly request the city install speed humps on all of
Wornall Road?" A resident in West Waldo and a resident in Brookside are
both affected.

**Trade-off:** a large node dominates a small one in direct proportion
to population. That is usually right for things that affect individuals.

### `one_node_one_vote`

Each node's local tally collapses to a single boolean (did yes beat no
locally?). The federation result is yes if a majority of nodes voted yes.

**When to use:** the decision affects structure, not individuals. Example:
"Should we add Waldo East to the federation as a full peer?" A node's
answer is the neighborhood's answer; a 500-resident node and a 50-resident
node each have one vote because each is one neighborhood.

**Trade-off:** a tiny node can veto a measure a large neighborhood strongly
supports. That is usually right for federation membership, treaties, and
shared resource allocation rules.

### `weighted_capped`

Scale each node's counts by `min(1, cap / nodeEligiblePopulation)`, then
sum. The cap is the per-node maximum weight; residents beyond the cap do
not add to the federation total.

**When to use:** when you want population to matter but not to swamp
smaller participants. Example: a funding proposal where each neighborhood
should feel heard, but a neighborhood five times larger should not be
one-fifth of the decision.

**Trade-off:** harder to explain at the meeting. Pick a cap that matches
the smallest neighborhood you expect to participate meaningfully and
commit to it in the proposal text.

---

## Completeness rule

The aggregator refuses to report a result unless every node listed in
`federation_nodes` has either reported OR been marked as timed out. This
is deliberate. A federation vote is not "best of whoever answered"; it is
"the federation spoke." If a peer is silent, that silence should be
resolved (timed_out, revoked, or awaited) before the result stands.

The default timeout window is **7 days from the close of local voting**.
If a peer has not reported in that window, a coordinator calls
`markPeerTimedOut(proposalId, peerNode)` and logs a line in the audit
trail explaining why. The federation result then ignores that node.

Timed-out nodes are not counted toward caucus mode totals. In
`one_node_one_vote`, three reporting nodes plus one timed-out node means
a majority is 2 of 3.

---

## How a proposal declares its mode

Store the mode in `proposals.quorum_rules` JSON:

```json
{
  "federation_mode": "one_node_one_vote",
  "federation_cap": 100
}
```

`modeForProposal(db, proposalId)` returns the mode for a given proposal,
falling back to `one_person_one_vote` when unset. `federation_cap` is only
meaningful for `weighted_capped`.

---

## What aggregation never does

- It never mixes raw votes from different nodes. Each node does its own
  tally first; aggregation works on tallies.
- It never imports voter_blind_id values across nodes. Blind ids are
  per-proposal and per-salt; they are not globally unique.
- It never retroactively changes a result. If a node re-reports after a
  result has been posted, that re-report is logged but does not rewrite
  the historical record. If the new report differs materially, an issue
  is filed and a coordinator decides how to handle it.

This lines up with the federation honesty note from the deep-dive review:
federated results are the sum of what peers claim, and the integrity of
the sum depends on the integrity of the peers you added. Pick peers
carefully.

---

_Last revised 2026-04-22 in response to the 2026-04-21 deep-dive review._
