const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const R = require('../assets/js/document-reader.js');
test('reader accepts repository Markdown documents and rejects URL/path escapes', () => {
  assert.equal(R.documentPath(null), 'README.md');
  assert.equal(R.documentPath('docs/DATA-AUDIT-2026-09-05'), 'docs/DATA-AUDIT-2026-09-05.md');
  assert.equal(R.documentPath('README.md'), 'README.md');
  for (const file of ['../README', '/README', 'https://evil.org/x.md', 'data\\x', 'data//x', 'data/./x', '%2e%2e/x', 'file.html', 'a.md?x=1', 'a.md#heading']) assert.throws(() => R.documentPath(file), file);
});
test('nested Markdown links stay in the reader and unsafe schemes stay inert', () => {
  const origin = 'https://commonweave.earth';
  assert.equal(R.resourceLink('../README.md#the-idea', 'docs/REVIEW.md', origin), 'doc.html?file=README#the-idea');
  assert.equal(R.resourceLink('next.md', 'docs/REVIEW.md', origin), 'doc.html?file=docs%2Fnext');
  assert.equal(R.resourceLink('../assets/example.svg', 'docs/REVIEW.md', origin), origin + '/assets/example.svg');
  assert.equal(R.resourceLink('#food', 'README.md', origin), '#food');
  for (const url of ['javascript:alert(1)', 'data:text/html,attack', 'file:///x', 'https://user:pass@example.org', 'https://example.org\\@evil.org']) assert.equal(R.resourceLink(url, 'README.md', origin), null);
});
test('heading IDs preserve GitHub double-hyphen anchors and Unicode', () => {
  assert.equal(R.headingSlug('Cooperatives & Solidarity'), 'cooperatives--solidarity');
  assert.equal(R.headingSlug('Food — shared needs'), 'food--shared-needs');
  assert.equal(R.headingSlug('São Paulo'), 'são-paulo');
});
test('every homepage topic and knowledge reading resolves to a real local destination', () => {
  const base = path.resolve(__dirname, '..');
  const hub = fs.readFileSync(path.join(base, 'knowledge.html'), 'utf8');
  const home = fs.readFileSync(path.join(base, 'index.html'), 'utf8');
  for (const [, id] of home.matchAll(/href="knowledge\.html#([^"]+)"/g)) assert.ok(hub.includes('id="' + id + '"'), id);
  for (const [, file] of hub.matchAll(/href="doc\.html\?file=([^"#]+)/g)) assert.ok(fs.existsSync(path.join(base, R.documentPath(file))), file);
});
