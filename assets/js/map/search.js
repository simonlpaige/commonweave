/* Shared discovery controls and results for desktop, mobile and list view. */
(function (global) {
  'use strict';
  let cities = [], lastResult = null, page = 0, ready = false;
  let chosen = {}, stepPages = {}, previousGoal = '';
  const $ = id => document.getElementById(id);
  const P = () => global.CommonweavePathways;
  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function option(value, label) { const n = el('option', '', label); n.value = value; return n; }
  function closeSheet() {
    $('mobile-sheet').classList.remove('open');
    $('mobile-fab').classList.remove('open');
    $('mobile-fab').setAttribute('aria-expanded', 'false');
  }
  function row(candidate) {
    const org = candidate.org, button = el('button', 'nr-row');
    button.type = 'button';
    button.append(el('span', 'nr-name', org.n || org.id));
    button.append(el('span', 'nr-meta', [org.ci, org.st, org.cc].filter(Boolean).join(', ') || 'Locality not recorded'));
    button.append(el('span', 'nr-meta', candidate.reasons[0]));
    button.append(el('span', 'nr-meta', org.t === 'A' ? 'Tier A · reviewed record' : org.t === 'B' ? 'Tier B · source backed; service availability unconfirmed' : 'Tier C · inferred candidate'));
    button.addEventListener('click', () => { closeSheet(); if (global._selectOrgById) global._selectOrgById(org.id); });
    return button;
  }
  function planDiagram(r) {
    const box = el('div', 'pathway-plan');
    box.append(el('p', 'pathway-caution', 'Your proposed plan · choose records below after checking their fit. Arrows connect roles to investigate; they do not confirm partnerships.'));
    const roles = el('ol', 'pathway-role-sequence');
    r.steps.forEach((step, i) => {
      const item = el('li', 'pathway-role');
      item.append(el('strong', '', step.label));
      const picked = step.candidates.find(c => c.org.id === chosen[step.area]);
      item.append(el('span', 'nr-meta', picked ? picked.org.n : 'No organization chosen'));
      if (picked) {
        const remove = el('button', 'need-clear', 'Remove choice'); remove.type = 'button';
        remove.addEventListener('click', () => { delete chosen[step.area]; renderResults(); });
        item.append(remove);
      }
      if (i < r.steps.length - 1) item.append(el('span', 'pathway-thread', '⇢'));
      roles.append(item);
    });
    box.append(roles);
    const download = el('button', 'need-btn', 'Download this plan');
    download.type = 'button';
    download.disabled = !r.steps.some(step => step.candidates.some(c => c.org.id === chosen[step.area]));
    download.addEventListener('click', () => {
      const url = URL.createObjectURL(new Blob([P().planText(r, chosen)], { type: 'text/plain;charset=utf-8' }));
      const link = el('a'); link.href = url; link.download = 'commonweave-' + r.goal.id + '-plan.txt';
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    box.append(download);
    return box;
  }
  function renderResults() {
    resultInto($('need-result'), false);
    resultInto($('discovery-list-results'), true);
  }
  function resultInto(container, full) {
    container.replaceChildren();
    if (!lastResult) return;
    const r = lastResult;
    const place = r.city ? 'with recorded locality ' + cityLabel(r.city) : r.country ? 'in ' + r.country : 'across all countries';
    container.append(el('p', 'nr-summary', r.total.toLocaleString() + ' candidate records ' + place + '. ' + r.searched.toLocaleString() + ' records searched with the current filters.'));
    if (!full) {
      if (r.goal) {
        container.append(el('p', 'pathway-caution', 'A proposed sequence of roles to explore:'));
        r.steps.forEach((step, i) => {
          const picked = step.candidates.find(c => c.org.id === chosen[step.area]);
          container.append(el('p', 'nr-meta', (i + 1) + '. ' + step.label + ' · ' + step.total.toLocaleString() + ' records' + (picked ? ' · chosen: ' + picked.org.n : '')));
        });
      }
      const open = el('button', 'need-btn', r.goal ? 'Review candidates and build a plan' : 'Browse matching records');
      open.type = 'button'; open.addEventListener('click', () => { global._showDiscoveryList(); closeSheet(); });
      container.append(open);
      if (!r.total) container.append(el('p', 'pathway-gap', 'No matching records. Try another place or topic, or reset the filters.'));
      return;
    }
    if (r.goal) {
      container.append(planDiagram(r));
      container.append(el('p', 'pathway-caution', 'Category matches are research leads, shown alphabetically when no topic is entered. For example, a cooperative may operate a service without advising new cooperatives. Open a record to check its work before choosing it.'));
      const steps = el('ol', 'pathway-steps');
      r.steps.forEach(step => {
        const item = el('li', 'pathway-step');
        item.append(el('h3', '', step.label));
        item.append(el('p', '', step.question));
        if (step.total) {
          const stepPage = stepPages[step.area] || 0;
          const start = stepPage * 3;
          item.append(el('p', 'nr-meta', 'Showing ' + (start + 1) + '–' + Math.min(start + 3, step.total) + ' of ' + step.total.toLocaleString() + ' category candidates'));
          step.candidates.slice(start, start + 3).forEach(c => {
            const candidate = el('div', 'pathway-candidate'); candidate.append(row(c));
            const selected = chosen[step.area] === c.org.id;
            const pick = el('button', 'need-clear', selected ? 'Chosen for this role' : 'Use in this plan');
            pick.type = 'button'; pick.setAttribute('aria-pressed', String(selected));
            pick.addEventListener('click', () => { chosen[step.area] = c.org.id; renderResults(); });
            candidate.append(pick); item.append(candidate);
          });
          if (step.total > 3) {
            const nav = el('div', 'need-row');
            const prev = el('button', 'need-clear', 'Previous'), next = el('button', 'need-clear', 'Next candidates');
            prev.type = next.type = 'button'; prev.disabled = !stepPage; next.disabled = start + 3 >= step.total;
            prev.addEventListener('click', () => { stepPages[step.area] = stepPage - 1; resultInto(container, true); });
            next.addEventListener('click', () => { stepPages[step.area] = stepPage + 1; resultInto(container, true); });
            nav.append(prev, next); item.append(nav);
          }
        } else item.append(el('p', 'pathway-gap', 'No matching record in this selection. This is a directory coverage gap, not evidence that local support is absent.'));
        steps.append(item);
      });
      container.append(steps);
      container.append(el('p', 'pathway-caution', 'Before relying on a pathway: confirm service area, eligibility, costs, accessibility, capacity and consent to referrals directly with each organization.'));
    } else {
      if (!r.total) container.append(el('p', 'pathway-gap', 'No matching records. Clear the name or city, choose another country, or include inferred candidates. Unrecognized words do not return unrelated global matches.'));
      const size = 30;
      const start = full ? page * size : 0;
      r.matches.slice(start, start + size).forEach(c => container.append(row(c)));
      if (full && r.total > size) {
        const controls = el('div', 'need-row');
        const prev = el('button', 'need-clear', 'Previous'), next = el('button', 'need-btn', 'Next');
        prev.disabled = page === 0; next.disabled = start + size >= r.total;
        prev.addEventListener('click', () => { page--; resultInto(container, true); container.parentElement.scrollTop = 0; });
        next.addEventListener('click', () => { page++; resultInto(container, true); container.parentElement.scrollTop = 0; });
        controls.append(prev, el('span', 'nr-meta', (start + 1) + '–' + Math.min(start + size, r.total) + ' of ' + r.total), next);
        container.append(controls);
      }
    }
    const link = el('a', 'discovery-link', 'Search the full directory, including unmapped records');
    link.href = 'directory.html'; container.append(link);
  }
  function selectedCity() {
    const val = $('need-city').value.trim();
    return val ? cities.find(c => cityLabel(c) === val) || null : null;
  }
  function cityLabel(c) { return [c.city, c.region, c.country].filter(Boolean).join(', '); }
  function refreshCities() {
    const country = $('need-country').value;
    const list = $('need-cities'); list.replaceChildren();
    cities.filter(c => !country || c.country === country).forEach(c => list.append(option(cityLabel(c), cityLabel(c))));
  }
  function run() {
    if (!ready) return;
    const city = selectedCity();
    if ($('need-city').value.trim() && !city) {
      $('need-status').textContent = 'Choose a listed city including its region and country, or clear the city to search more broadly.';
      invalidateResults(); return false;
    }
    if (city && $('need-country').value && city.country !== $('need-country').value) {
      $('need-status').textContent = 'The chosen city is outside the country filter. Clear the city or choose a matching one.';
      invalidateResults(); return false;
    }
    const filters = global._discoveryFilters ? global._discoveryFilters() : {};
    lastResult = P().discover(global.allPoints || [], Object.assign({}, filters, {
      query: $('need-input').value, goal: $('need-goal').value,
      country: $('need-country').value, city
    }));
    page = 0;
    stepPages = {};
    if (previousGoal !== $('need-goal').value) chosen = {};
    previousGoal = $('need-goal').value;
    for (const area of Object.keys(chosen)) {
      if (!lastResult.steps.some(s => s.area === area && s.candidates.some(c => c.org.id === chosen[area]))) delete chosen[area];
    }
    if (global._setDiscoveryResultIds) global._setDiscoveryResultIds(lastResult.matches.map(m => m.org.id));
    $('need-result').hidden = false;
    renderResults();
    $('need-status').textContent = lastResult.total.toLocaleString() + ' candidates. ' + (lastResult.goal ? 'Explore the steps below.' : 'Open List view for all results.');
    if (global._setNeedHighlight) global._setNeedHighlight(null);
    if (global._writeDiscoveryUrl) global._writeDiscoveryUrl();
    return true;
  }
  function invalidateResults() {
    lastResult = null; chosen = {}; stepPages = {};
    $('need-result').replaceChildren();
    $('discovery-list-results').replaceChildren(el('p', 'pathway-gap', $('need-status').textContent));
    if (global._setDiscoveryResultIds) global._setDiscoveryResultIds([]);
  }
  function clear() {
    chosen = {}; stepPages = {};
    ['need-input', 'need-goal', 'need-country', 'need-city'].forEach(id => { $(id).value = ''; });
    if (global._resetDiscoveryFilters) global._resetDiscoveryFilters();
    refreshCities(); run();
    if (global._setNeedHighlight) global._setNeedHighlight(null);
  }
  function refresh() { if (ready) run(); }
  async function init() {
    P().GOALS.forEach(g => $('need-goal').append(option(g.id, g.label)));
    const countries = [...new Set((global.allPoints || []).map(p => p.cc).filter(Boolean))].sort();
    let names; try { names = new Intl.DisplayNames(['en'], { type: 'region' }); } catch (_) { /* ISO codes remain usable. */ }
    countries.forEach(cc => { let name = cc; try { name = names ? names.of(cc) : cc; } catch (_) {} $('need-country').append(option(cc, name + ' (' + cc + ')')); });
    $('need-go').addEventListener('click', run);
    $('need-clear').addEventListener('click', clear);
    $('need-goal').addEventListener('change', run);
    $('need-country').addEventListener('change', () => { $('need-city').value = ''; refreshCities(); run(); });
    $('need-input').addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); run(); } });
    $('need-list').addEventListener('click', () => { if (run()) { global._showDiscoveryList(); closeSheet(); } });
    $('list-edit').addEventListener('click', () => {
      if (matchMedia('(max-width: 600px)').matches) $('mobile-fab').click();
      $('need-goal').focus();
    });
    const localities = new Map();
    (global.allPoints || []).filter(p => p.ci && p.cc).forEach(p => {
      const c = { city: p.ci, region: p.st || '', country: p.cc };
      localities.set(cityLabel(c), c);
    });
    cities = [...localities.values()].sort((a, b) => cityLabel(a).localeCompare(cityLabel(b)));
    refreshCities();
    if (global._restoreDiscoveryUrl) global._restoreDiscoveryUrl();
    ready = true; run();
  }
  global.CommonweaveSearch = { init, run, clear, refresh, lastResult: () => lastResult };
})(typeof window !== 'undefined' ? window : globalThis);
