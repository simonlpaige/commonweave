const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {normalize, matches, init} = require('../assets/js/knowledge.js');
const base = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(base, 'knowledge.html'), 'utf8');

test('knowledge search combines terms and topic without losing accented text', () => {
  const reading = {text: 'Coopératives and solidarity', keywords: 'worker ownership', topic: 'areas'};
  assert.equal(normalize('Coopératives & solidarity'), 'cooperatives solidarity');
  assert.equal(matches(reading, 'COOPERATIVES worker', 'areas'), true);
  assert.equal(matches(reading, 'worker housing', 'areas'), false);
  assert.equal(matches(reading, '', 'evidence'), false);
  assert.equal(matches(reading, '!!!', 'all'), true);
});

test('curated reader links refer to actual files and actual Markdown headings', () => {
  const links = [...html.matchAll(/href="doc\.html\?file=([^"#]+)(?:#([^"]+))?"/g)];
  assert.ok(links.length >= 29);
  for (const [, file, anchor] of links) {
    const source = fs.readFileSync(path.join(base, file + '.md'), 'utf8');
    if (anchor) {
      const headings = [...source.matchAll(/^#{1,6}\s+(.+)$/gm)].map(match => match[1]
        .trim().toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, '').replace(/\s/g, '-'));
      assert.ok(headings.includes(anchor), `Missing ${anchor} in ${file}.md`);
    }
  }
});

test('all ten homepage topic targets are available without JavaScript', () => {
  for (const id of ['healthcare', 'education', 'food', 'democracy', 'housing-land', 'ecology', 'conflict', 'cooperatives', 'recreation-arts', 'energy-digital']) {
    assert.match(html, new RegExp(`id="${id}" data-knowledge-resource`));
  }
  assert.match(html, /id="knowledge-search-form"[^>]+hidden/);
});

test('actual search controls hide empty groups, announce results and restore the catalogue', () => {
  function element(properties = {}) {
    return {value: '', hidden: true, handlers: {}, dataset: {}, textContent: '', focused: false,
      addEventListener(type, callback) { this.handlers[type] = callback; },
      focus() { this.focused = true; }, ...properties};
  }
  const controls = Object.fromEntries(['knowledge-search-form', 'knowledge-query', 'knowledge-topic', 'knowledge-clear', 'knowledge-status', 'knowledge-empty', 'knowledge-empty-clear'].map(id => [id, element()]));
  controls['knowledge-topic'].value = 'all';
  const resources = [
    element({dataset: {topic: 'areas', keywords: 'land'}, textContent: 'Housing', hidden: false}),
    element({dataset: {topic: 'evidence', keywords: 'sources'}, textContent: 'Public-data audit', hidden: false})
  ];
  const groups = [element({dataset: {knowledgeGroup: 'areas'}}), element({dataset: {knowledgeGroup: 'evidence'}})];
  const doc = {getElementById: id => controls[id], querySelectorAll: selector => selector === '[data-knowledge-resource]' ? resources : groups};
  init(doc);
  assert.equal(controls['knowledge-search-form'].hidden, false);
  assert.deepEqual(groups.map(group => group.hidden), [false, false]);
  controls['knowledge-query'].value = 'land';
  controls['knowledge-query'].handlers.input();
  assert.deepEqual(resources.map(resource => resource.hidden), [false, true]);
  assert.deepEqual(groups.map(group => group.hidden), [false, true]);
  assert.equal(controls['knowledge-status'].textContent, '1 matching reading out of 2.');
  controls['knowledge-topic'].value = 'evidence';
  controls['knowledge-topic'].handlers.change();
  assert.equal(controls['knowledge-empty'].hidden, false);
  assert.deepEqual(groups.map(group => group.hidden), [true, true]);
  controls['knowledge-empty-clear'].handlers.click();
  assert.deepEqual(resources.map(resource => resource.hidden), [false, false]);
  assert.equal(controls['knowledge-query'].focused, true);
  assert.equal(controls['knowledge-topic'].value, 'all');
  assert.equal(controls['knowledge-clear'].hidden, true);
  assert.equal(controls['knowledge-empty'].hidden, true);
});
