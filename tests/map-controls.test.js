const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

async function harness() {
  const elements = new Map();
  class Element {
    constructor(tag) { this.tag = tag; this.value = ''; this.textContent = ''; this.children = []; this.events = {}; this.disabled = false; this.classList = { add() {}, remove() {} }; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    addEventListener(event, fn) { this.events[event] = fn; }
    setAttribute(key, value) { this[key] = value; }
    click() { if (!this.disabled) this.events.click?.(); }
    focus() {}
  }
  const document = { getElementById(id) { if (!elements.has(id)) elements.set(id, new Element('div')); return elements.get(id); }, createElement(tag) { return new Element(tag); } };
  const points = Array.from({ length: 8 }, (_, i) => ({ id: 'us-' + i, n: 'Food ' + i, f: 'food', t: 'B', cc: 'US', ci: 'Springfield', st: 'IL' }));
  points.push({ id: 'ca', n: 'Canadian Food', f: 'food', t: 'B', cc: 'CA', ci: 'Springfield', st: 'ON' });
  let visible = [], resetCount = 0;
  const context = vm.createContext({ document, allPoints: points, Intl, URL, URLSearchParams, console,
    _setDiscoveryResultIds(ids) { visible = Array.from(ids); },
    _resetDiscoveryFilters() { resetCount++; },
    matchMedia() { return { matches: false }; } });
  for (const file of ['pathways.js', 'search.js']) vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/js/map', file), 'utf8'), context);
  await context.CommonweaveSearch.init();
  function descendants(node) { return [node, ...node.children.flatMap(descendants)]; }
  const results = () => descendants(elements.get('discovery-list-results'));
  const buttons = text => results().filter(n => n.tag === 'button' && n.textContent === text);
  const change = (id, value) => { const el = elements.get(id); el.value = value; el.events.change?.(); };
  return { elements, context, results, buttons, change, visible: () => visible, resets: () => resetCount };
}

test('actual controls require an explicit choice and reset removes the plan', async () => {
  const h = await harness(); h.change('need-goal', 'food');
  assert.equal(h.buttons('Download this plan')[0].disabled, true);
  assert.equal(h.results().filter(n => n.textContent === 'No organization chosen').length, 3);
  h.buttons('Use in this plan')[0].click();
  assert.equal(h.buttons('Download this plan')[0].disabled, false);
  assert.equal(h.buttons('Remove choice').length, 1);
  h.elements.get('need-clear').click();
  assert.equal(h.resets(), 1);
  assert.equal(h.buttons('Download this plan').length, 0);
  h.change('need-goal', 'food');
  assert.equal(h.buttons('Download this plan')[0].disabled, true);
});

test('country changes remove a chosen record that no longer matches', async () => {
  const h = await harness(); h.change('need-goal', 'food'); h.change('need-country', 'US');
  h.buttons('Use in this plan')[0].click();
  h.change('need-country', 'CA');
  assert.deepEqual(h.visible(), ['ca']);
  assert.equal(h.buttons('Remove choice').length, 0);
  assert.equal(h.buttons('Download this plan')[0].disabled, true);
});

test('invalid or wrong-country city clears stale map and list results', async () => {
  const h = await harness(); h.change('need-country', 'US');
  h.elements.get('need-city').value = 'Springfield';
  assert.equal(h.context.CommonweaveSearch.run(), false);
  assert.deepEqual(h.visible(), []);
  assert.match(h.elements.get('need-status').textContent, /Choose a listed city/);
  h.elements.get('need-city').value = 'Springfield, ON, CA';
  assert.equal(h.context.CommonweaveSearch.run(), false);
  assert.deepEqual(h.visible(), []);
  h.elements.get('need-city').value = 'Springfield, IL, US';
  assert.equal(h.context.CommonweaveSearch.run(), true);
  assert.equal(h.visible().length, 8);
});

test('candidate paging does not truncate the set shown on the map', async () => {
  const h = await harness(); h.change('need-goal', 'food'); h.change('need-country', 'US');
  assert.equal(h.visible().length, 8);
  assert.equal(h.buttons('Use in this plan').length, 3);
  h.buttons('Next candidates')[0].click();
  assert.ok(h.results().some(n => n.textContent === 'Food 3'));
  assert.ok(!h.results().some(n => n.textContent === 'Food 0'));
  h.buttons('Next candidates')[0].click();
  assert.equal(h.buttons('Use in this plan').length, 2);
  assert.equal(h.buttons('Next candidates')[0].disabled, true);
  assert.equal(h.visible().length, 8);
});
