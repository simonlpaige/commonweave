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
    assert.equal(r.steps.length, 3);
    assert.ok(r.matches.every(m => ids.has(m.org.id) && m.org.cc === 'US' && m.org.t === 'B'));
    assert.ok(r.matches.every(m => m.distance === null));
  }
});
