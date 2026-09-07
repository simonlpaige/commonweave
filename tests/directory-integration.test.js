const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const api = require('../assets/js/directory-data.js');
const html = fs.readFileSync(path.join(__dirname, '../directory.html'), 'utf8');
const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
const tick = () => new Promise(resolve => setImmediate(resolve));

async function harness() {
  const elements = new Map();
  function element(id = '') {
    return {id, value:'', textContent:'', innerHTML:'', style:{}, children:[],
      appendChild(child) {this.children.push(child);}, querySelector() {return null;},
      addEventListener(event, fn) {this[event] = fn;}, scrollIntoView() {},
      classList:{add() {}, remove() {}}};
  }
  const document = {getElementById(id) {if (!elements.has(id)) elements.set(id, element(id)); return elements.get(id);},
    createElement() {return element();}, querySelectorAll() {return [];}};
  const waiting = new Map();
  const index = {total_orgs:2,total_countries:3,ntee_categories:{},countries:{ZA:{name:'South Africa',count:1},FR:{name:'France',count:1},US:{name:'United States',count:0}}};
  const context = vm.createContext({document, CommonweaveDirectory:api, URLSearchParams,
    location:{search:''}, setTimeout, clearTimeout, console,
    fetch(url) {
      if (url.includes('/index.json')) return Promise.resolve({ok:true,json:async()=>index});
      return new Promise(resolve => waiting.set(url.split('?')[0], resolve));
    }});
  vm.runInContext(script, context);
  await tick();
  return {context,elements,waiting};
}

test('the actual directory ignores an old country response after selection changes', async () => {
  const {context,elements,waiting} = await harness();
  const first = vm.runInContext('selectCountry("ZA")', context);
  const second = vm.runInContext('selectCountry("FR")', context);
  waiting.get('data/search/FR.json')({ok:true,json:async()=>({orgs:[{n:'French cooperative'}]})});
  await second;
  waiting.get('data/search/ZA.json')({ok:true,json:async()=>({orgs:[{n:'Old South African result'}]})});
  await first;
  assert.match(elements.get('content').innerHTML, /French cooperative/);
  assert.doesNotMatch(elements.get('content').innerHTML, /Old South African result/);
  assert.equal(elements.get('country-select').value, 'FR');
});

test('failed state metadata leaves a recoverable state and no stale country results', async () => {
  const {context,elements,waiting} = await harness();
  const request = vm.runInContext('selectCountry("US")', context);
  waiting.get('data/search/US_meta.json')({ok:false,json:async()=>({})});
  await request;
  assert.match(elements.get('content').innerHTML, /try this place again/);
  assert.equal(elements.get('stat-loaded').textContent, '0');
  assert.equal(vm.runInContext('countryData', context), null);
});

test('rendered organization links reject attribute injection and preserve safe query strings', async () => {
  const {context,elements,waiting} = await harness();
  const request = vm.runInContext('selectCountry("FR")', context);
  waiting.get('data/search/FR.json')({ok:true,json:async()=>({organizations:[
    {n:'Unsafe',w:'https://example.org/" onclick="alert(1)'},
    {n:'Safe & sound',w:'https://example.org/?a=1&b=2',id:'known-id'}
  ]})});
  await request;
  const content = elements.get('content').innerHTML;
  assert.doesNotMatch(content, /onclick="alert/);
  assert.match(content, /href="https:\/\/example.org\/\?a=1&amp;b=2"/);
  assert.match(content, /participate.html\?org=Safe\+%26\+sound&amp;id=known-id&amp;country=FR/);
});

test('reset country invalidates inflight requests and resets the visible count', async () => {
  const {context,elements,waiting} = await harness();
  const request = vm.runInContext('selectCountry("FR")', context);
  elements.get('country-select').change({target:{value:''}});
  waiting.get('data/search/FR.json')({ok:true,json:async()=>({orgs:[{n:'Stale response'}]})});
  await request;
  assert.doesNotMatch(elements.get('content').innerHTML, /Stale response/);
  assert.equal(elements.get('stat-loaded').textContent, '0');
});
