const test = require('node:test');
const assert = require('node:assert/strict');
const {buildDraft, publicUrl} = require('../assets/js/participation.js');
const {safeWebsite, organizations, latestRequest} = require('../assets/js/directory-data.js');

test('public links reject scripts, injected attributes, credentials and malformed hosts', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,bad', 'https://a.example/" onclick="alert(1)', 'https://user:pass@example.org']) {
    assert.equal(publicUrl(url), '');
    assert.equal(safeWebsite(url), '');
  }
  assert.equal(safeWebsite('example.org/path?x=1&y=2'), 'https://example.org/path?x=1&y=2');
  assert.equal(safeWebsite('mailto:person@example.org'), '');
  assert.equal(safeWebsite('https://'), '');
});

test('draft retains Unicode and evidence exactly in the GitHub query', () => {
  const draft = buildDraft({type:'connection', org:'Réseau & Food', details:'A may supply food; B may distribute. This is a proposal.', source:'https://example.org/?a=1&b=2'});
  const params = new URL(draft.url).searchParams;
  assert.equal(params.get('title'), draft.title);
  assert.equal(params.get('body'), draft.body);
  assert.match(draft.body, /Proposed only/);
  assert.match(draft.body, /Réseau & Food/);
});

test('new listings require evidence but protective requests do not', () => {
  assert.throws(() => buildDraft({type:'add',org:'Org',details:'Please add'}), /public source/);
  assert.throws(() => buildDraft({type:'verify',org:'Org',details:'This is us'}), /public source/);
  assert.throws(() => buildDraft({type:'add',org:'Org',details:'Please add',source:'javascript:alert(1)'}), /public http/);
  assert.match(buildDraft({type:'remove',org:'Listing 123',details:'Please remove'}).body, /Request removal/);
  assert.match(buildDraft({type:'obscure',org:'Listing 123',details:'Country only, please'}).body, /Reduce location detail/);
});

test('long international drafts offer download without dropping evidence', () => {
  const draft = buildDraft({type:'correct',org:'Организация',details:'資'.repeat(2000)});
  assert.equal(draft.url, null);
  assert.ok(draft.text.includes('資'.repeat(2000)));
});

test('switching place invalidates an old request even if it finishes last', () => {
  const gate = latestRequest();
  const old = gate.next();
  const current = gate.next();
  assert.equal(gate.isCurrent(old), false);
  assert.equal(gate.isCurrent(current), true);
  gate.next(); // clearing the selected country must also invalidate pending loads
  assert.equal(gate.isCurrent(current), false);
});

test('directory accepts documented export shapes and rejects malformed data', () => {
  const rows = [{name:'Organization'}];
  assert.equal(organizations({orgs:rows}), rows);
  assert.equal(organizations({organizations:rows}), rows);
  assert.equal(organizations(rows), rows);
  assert.throws(() => organizations({error:'not found'}), /unsupported format/);
});
