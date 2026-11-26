const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
require('./scoring.js');
const P = require('./pathways.js');

const points = [
  { id: 'food-a', n: 'Harvest food collective', f: 'food', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL', la: 40, lo: -90 },
  { id: 'land', n: 'Community land trust', f: 'housing_land', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL', la: 40, lo: -90 },
  { id: 'coop', n: 'Member cooperative', f: 'cooperatives', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL', la: 40, lo: -90 },
  { id: 'other-city', n: 'Another food collective', f: 'food', t: 'B', cc: 'US', ci: 'Springfield', st: 'MO', la: 40, lo: -90 },
  { id: 'other-country', n: 'Another cooperative', f: 'cooperatives', t: 'B', cc: 'CA', ci: 'Springfield', st: 'IL', la: 40, lo: -90 },
  { id: 'inferred', n: 'An inferred food project', f: 'food', t: 'C', cc: 'US', ci: 'Springfield', st: 'IL', la: null, lo: null },
];

test('goal composes distinct roles without automatically pairing named organizations', () => {
  const r = P.discover(points, { goal: 'food', country: 'US', city: { city: 'Springfield', region: 'IL', country: 'US' } });
  assert.deepEqual(r.steps.map(s => s.candidates.map(c => c.org.id)), [['food-a'], ['land'], ['coop']]);
  assert.equal(r.bridges.length, 2);
  assert.ok(r.bridges.every(b => b.basis.includes('no organization or partnership selected')));
  assert.deepEqual(Object.keys(r.bridges[0]).sort(), ['basis', 'sourceRole', 'targetRole']);
  assert.equal(r.bridges[0].sourceRole, r.steps[0].label);
  assert.equal(r.bridges[0].targetRole, r.steps[1].label);
});
test('identical country centroid coordinates never establish locality or distance', () => {
  const r = P.discover(points, { city: { city: 'Springfield', region: 'IL', country: 'US' } });
  assert.deepEqual(r.matches.map(m => m.org.id).sort(), ['coop', 'food-a', 'land']);
  assert.ok(r.matches.every(m => m.distance === null));
});
test('unrecognized query returns zero; no fabricated global recommendations', () => {
  assert.equal(P.discover(points, { query: 'zzqxnotaword' }).total, 0);
});
test('word boundaries prevent art from matching earth; accents and punctuation normalize', () => {
  assert.equal(P.phrase('earth', 'art'), false);
  assert.equal(P.phrase('São Paulo community-owned', 'Sao Paulo'), true);
  assert.equal(P.discover(points, { query: 'Harvest food' }).matches[0].org.id, 'food-a');
});
test('tier selection and empty tier filters are respected in all goal steps', () => {
  assert.equal(P.discover(points, { goal: 'food', tiers: [] }).total, 0);
  assert.equal(P.discover(points, { tiers: ['C'] }).matches[0].org.id, 'inferred');
});
test('missing pieces stay explicit and never fabricate organizations', () => {
  const r = P.discover(points.slice(0, 1), { goal: 'food' });
  assert.equal(r.steps.length, 3);
  assert.equal(r.steps[1].total, 0);
  assert.equal(r.steps[2].total, 0);
  assert.equal(r.bridges.length, 2);
  assert.ok(r.steps.slice(1).every(s => s.candidates.length === 0));
  assert.ok(r.bridges.every(b => !('source' in b) && !('target' in b)));
});
test('results are deterministic after source reordering and deduplicate nothing speculatively', () => {
  assert.deepEqual(P.discover(points, {}).matches.map(m => m.org.id), P.discover([...points].reverse(), {}).matches.map(m => m.org.id));
});
test('documented relationship requires declared non-derived evidence and a safe URL', () => {
  const edge = { edge_type: 'verified_relationship', derived: false, evidence: [{ value: 'https://example.org/evidence' }] };
  assert.equal(P.evidence(edge).documented, true);
  assert.equal(P.evidence({ ...edge, derived: true }).documented, false);
  assert.equal(P.evidence({ ...edge, evidence: [{ value: 'javascript:alert(1)' }] }).documented, false);
  assert.equal(P.evidence({ ...edge, edge_type: 'same_section_proximity' }).documented, false);
  assert.equal(P.safeUrl('data:text/html,malicious'), '');
  assert.equal(P.safeUrl('https://person:secret@example.org'), '');
});
test('download contains only eligible explicit choices and keeps missing roles visible', () => {
  const r = P.discover(points, { goal: 'food', country: 'US', city: { city: 'Springfield', region: 'IL', country: 'US' } });
  const empty = P.planText(r, {});
  assert.equal((empty.match(/No organization chosen/g) || []).length, 3);
  assert.ok(!empty.includes('Harvest food collective'));
  const text = P.planText(r, { food: 'food-a', housing_land: 'other-country' });
  assert.ok(text.includes('Your choice: Harvest food collective'));
  assert.ok(text.includes('selectedId=food-a'));
  assert.ok(!text.includes('Another cooperative'));
  assert.equal((text.match(/No organization chosen/g) || []).length, 2);
  assert.ok(text.includes('do not establish partnerships'));
  assert.equal(P.planText(P.discover(points, {}), {}), '');
});
test('all goal candidates remain reachable after the first three records', () => {
  const many = Array.from({ length: 11 }, (_, i) => ({ ...points[0], id: 'food-' + i, n: 'Food ' + i }));
  const r = P.discover(many, { goal: 'food' });
  assert.equal(r.steps[0].candidates.length, 11);
  assert.equal(r.matches.length, 11);
});
test('current exported data yields only existing IDs and finite results without enriched fields', () => {
  const file = path.resolve(__dirname, '../../../data/map/orgs.geojson');
  const records = JSON.parse(fs.readFileSync(file, 'utf8')).features.map(f => ({ ...f.properties, lo: f.geometry.coordinates[0], la: f.geometry.coordinates[1] }));
  const ids = new Set(records.map(p => p.id));
  for (const goal of P.GOALS) {
    const r = P.discover(records, { goal: goal.id, country: 'US' });
    assert.equal(r.steps.length, goal.steps.length);
    assert.ok(r.matches.every(m => ids.has(m.org.id) && m.org.cc === 'US' && m.org.t === 'B'));
    assert.equal(new Set(r.matches.map(m => m.org.id)).size, r.matches.length);
    assert.equal(r.total, r.matches.length);
    assert.ok(r.matches.every(m => m.distance === null));
  }
});

const circuitGoals = P.GOALS.filter(g => g.circuit);
const mapRecords = () => JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../../data/map/orgs.geojson'), 'utf8')).features.map(f => f.properties);
test('circuit goals are generated from data/circuits.yaml with unique step keys and graded evidence', () => {
  assert.ok(circuitGoals.length >= 20);
  assert.equal(new Set(P.GOALS.map(g => g.id)).size, P.GOALS.length);
  assert.equal(new Set(P.GOALS.map(g => g.label)).size, P.GOALS.length);
  for (const goal of circuitGoals) {
    assert.ok(goal.steps.length >= 2);
    assert.equal(new Set(goal.steps.map(s => s[0])).size, goal.steps.length);
    assert.ok(['combination_documented', 'components_documented', 'hypothesis'].includes(goal.circuit.evidence));
    assert.ok(goal.steps.every(s => s[3] && Array.isArray(s[3].any_of) && Array.isArray(s[3].none_of)));
  }
});
test('role rules match on name, model and source with whole words and exclusions', () => {
  const union = circuitGoals.find(g => g.id === 'circuit-labor_for_housing').steps.find(s => s[0] === 'labor_union')[3];
  assert.equal(P.matchRule(union, { n: 'Anytown Union Chapel Choir', m: 'nonprofit', src: 'x', f: 'democracy' }), false);
  assert.equal(P.matchRule(union, { n: 'Sindicato dos Metalúrgicos', m: 'nonprofit', src: 'x', f: 'democracy' }), true);
  assert.equal(P.matchRule(union, { n: 'Anything', m: 'labor_union', src: 'x', f: 'democracy' }), true);
  assert.equal(P.matchRule(union, { n: 'Anytown Credit Union', m: 'labor_union', src: 'x', f: 'democracy' }), false);
  assert.equal(P.matchRule(union, { n: 'Reunion Trade Unionists Club', m: 'nonprofit', src: 'x', f: 'democracy' }), false);
});
test('a circuit goal lists candidates per role, pairs nobody, and keeps empty roles visible', () => {
  const pts = [
    { id: 'u', n: 'Metal Workers Trade Union', f: 'democracy', m: 'labor_union', src: 's', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL' },
    { id: 'c', n: 'Springfield Community Land Trust', f: 'housing_land', m: 'nonprofit', src: 's', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL' },
    { id: 'x', n: 'Unrelated Choir', f: 'recreation_arts', m: 'nonprofit', src: 's', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL' },
  ];
  const r = P.discover(pts, { goal: 'circuit-labor_for_housing', country: 'US' });
  const byKey = Object.fromEntries(r.steps.map(s => [s.area, s.candidates.map(c => c.org.id)]));
  assert.deepEqual(byKey.labor_union, ['u']);
  assert.deepEqual(byKey.community_land_trust, ['c']);
  assert.deepEqual(byKey.cooperative_finance, []);
  assert.ok(!r.matches.some(m => m.org.id === 'x'));
  assert.ok(r.bridges.every(b => b.basis.includes('no organization or partnership selected') && !('source' in b)));
  const text = P.planText(r, { labor_union: 'u' });
  assert.ok(text.includes('Your choice: Metal Workers Trade Union'));
  assert.ok(!text.includes('Springfield Community Land Trust'));
  assert.ok(text.includes('Evidence for this combination: Combination documented.'));
  assert.ok(text.includes('doc.html?file=SOLUTION-CIRCUITS#labor-for-housing-pipeline'));
  assert.ok(text.includes('Also needed, and not in this directory:'));
  assert.equal((text.match(/No organization chosen/g) || []).length, r.steps.length - 1);
});
test('JavaScript role matching agrees with the Python coverage build on every published map point', () => {
  const coverage = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../../data/map/circuit-coverage.json'), 'utf8'));
  const records = mapRecords().filter(p => ['A', 'B', 'C'].includes(p.t));
  assert.equal(records.length, coverage.inputs.map_points_with_valid_tier);
  const rules = {};
  circuitGoals.forEach(g => g.steps.forEach(s => { rules[s[0]] = s[3]; }));
  assert.deepEqual(Object.keys(rules).sort(), Object.keys(coverage.roles).sort());
  for (const [key, rule] of Object.entries(rules)) {
    assert.equal(records.filter(p => P.matchRule(rule, p)).length, coverage.roles[key].map_points, key);
  }
});
