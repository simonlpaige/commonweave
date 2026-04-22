// civic-identity/federation-aggregate.js
// Combine per-node tallies into a federation-wide result.
//
// Context: a federation proposal runs independently on each participating
// node. Each node reports its own tally back. There are two defensible
// ways to combine them, and picking one by accident is a governance bug,
// not a bug-bug. This module makes the choice explicit.
//
// Modes:
//   one_person_one_vote (default)
//     Simple sum across all participating nodes. A 500-resident node
//     outweighs a 50-resident node by exactly 10x. Fairest when all
//     participating nodes vote on things that affect them equally.
//
//   one_node_one_vote
//     Each node gets equal weight. Each node's outcome is reduced to a
//     single boolean (did yes > no locally?) and the federation result
//     is yes if a majority of nodes voted yes. Use for federation
//     decisions that affect structure, not individuals.
//
//   weighted_capped
//     Each node's yes and no counts are scaled by min(1, cap / nodePop)
//     where nodePop is the node's trust-3+ eligible population. Keeps a
//     very large node from swamping smaller ones while still letting
//     population matter.
//
// The function refuses to report a result unless every declared
// federation_nodes participant has reported OR been marked as timed out.

import { getProposal } from './voting.js';

export const FEDERATION_MODES = ['one_person_one_vote', 'one_node_one_vote', 'weighted_capped'];

// reports: array of { nodeSlug, tally, eligible, reportedAt, status }
// Tally shape matches tallyBinary output: { counts: { yes, no, abstain }, total }
// For non-binary methods, only tally.total is meaningful at federation scope.
export function combineFederationResults(reports, {
  mode = 'one_person_one_vote',
  cap = 100
} = {}) {
  if (!FEDERATION_MODES.includes(mode)) {
    throw new Error(`Unknown federation mode: ${mode}`);
  }

  const received = reports.filter(r => r.status === 'received');
  const missing  = reports.filter(r => r.status !== 'received');

  if (missing.length && !reports.every(r => r.status === 'received' || r.status === 'timed_out')) {
    return {
      mode,
      complete: false,
      reason: 'some participants have not reported and have not timed out',
      received: received.length,
      missing: missing.length
    };
  }

  switch (mode) {
    case 'one_person_one_vote': return combineSum(received);
    case 'one_node_one_vote':   return combineCaucus(received);
    case 'weighted_capped':     return combineWeighted(received, cap);
  }
}

function combineSum(reports) {
  const totals = { yes: 0, no: 0, abstain: 0 };
  for (const r of reports) {
    const c = r.tally?.counts || {};
    totals.yes     += c.yes     || 0;
    totals.no      += c.no      || 0;
    totals.abstain += c.abstain || 0;
  }
  const decided = totals.yes + totals.no;
  return {
    mode: 'one_person_one_vote',
    complete: true,
    counts: totals,
    passed: totals.yes > totals.no,
    margin: decided > 0 ? ((totals.yes - totals.no) / decided).toFixed(3) : '0'
  };
}

function combineCaucus(reports) {
  const perNode = reports.map(r => {
    const c = r.tally?.counts || {};
    return {
      nodeSlug: r.nodeSlug,
      localPassed: (c.yes || 0) > (c.no || 0),
      counts: { yes: c.yes || 0, no: c.no || 0, abstain: c.abstain || 0 }
    };
  });
  const yesNodes = perNode.filter(p => p.localPassed).length;
  const noNodes  = perNode.length - yesNodes;
  return {
    mode: 'one_node_one_vote',
    complete: true,
    nodes: perNode,
    yesNodes, noNodes,
    passed: yesNodes > noNodes
  };
}

function combineWeighted(reports, cap) {
  const nodes = [];
  let wYes = 0, wNo = 0, wAbs = 0;
  for (const r of reports) {
    const c = r.tally?.counts || {};
    const eligible = Math.max(1, r.eligible || 1);
    const scale = Math.min(1, cap / eligible);
    const y = (c.yes || 0) * scale;
    const n = (c.no  || 0) * scale;
    const a = (c.abstain || 0) * scale;
    nodes.push({ nodeSlug: r.nodeSlug, eligible, scale: Number(scale.toFixed(3)),
                 weighted: { yes: Number(y.toFixed(2)), no: Number(n.toFixed(2)), abstain: Number(a.toFixed(2)) } });
    wYes += y; wNo += n; wAbs += a;
  }
  return {
    mode: 'weighted_capped',
    complete: true,
    cap,
    nodes,
    weighted: {
      yes: Number(wYes.toFixed(2)),
      no:  Number(wNo.toFixed(2)),
      abstain: Number(wAbs.toFixed(2))
    },
    passed: wYes > wNo
  };
}

// Convenience: pull the proposal's mode from stored quorum_rules JSON.
export function modeForProposal(db, proposalId) {
  const p = getProposal(db, proposalId);
  if (!p) throw new Error('Proposal not found');
  if (!p.quorum_rules) return 'one_person_one_vote';
  try {
    const rules = JSON.parse(p.quorum_rules);
    return FEDERATION_MODES.includes(rules.federation_mode)
      ? rules.federation_mode : 'one_person_one_vote';
  } catch {
    return 'one_person_one_vote';
  }
}
