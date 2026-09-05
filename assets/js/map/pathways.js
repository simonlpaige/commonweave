/* Goal pathways are planning hypotheses. Category matches never assert services,
 * capacity, endorsement or a relationship between the named organizations. */
(function (global) {
  'use strict';
  const AREAS = { food: 'Food', housing_land: 'Housing & land', cooperatives: 'Cooperatives', democracy: 'Democracy', healthcare: 'Healthcare', education: 'Education', conflict: 'Conflict resolution', energy_digital: 'Energy & digital', ecology: 'Ecology', recreation_arts: 'Arts & recreation' };
  const GOALS = [
    { id: 'food', label: 'Build a community food project', steps: [
      ['food', 'Find food knowledge', 'Ask about growing, food access and distribution.'],
      ['housing_land', 'Explore land or a shared space', 'Ask whether a site could support the food project.'],
      ['cooperatives', 'Plan shared ownership', 'Ask who can help with member governance and a viable operating model.']
    ] },
    { id: 'housing', label: 'Explore community owned housing', steps: [
      ['housing_land', 'Find housing and land experience', 'Ask about eligibility, location and the ownership model.'],
      ['cooperatives', 'Plan member ownership', 'Ask about cooperative formation and finance referrals.'],
      ['democracy', 'Include residents in decisions', 'Ask about accessible resident participation and accountability.']
    ] },
    { id: 'cooperative', label: 'Start or strengthen a cooperative', steps: [
      ['cooperatives', 'Find cooperative experience', 'Ask about formation, governance and support for your sector.'],
      ['education', 'Build skills together', 'Ask about relevant training and whether it is open to your members.'],
      ['democracy', 'Design member decisions', 'Ask about participation, representation and resolving disagreements.']
    ] },
    { id: 'energy', label: 'Explore community energy', steps: [
      ['energy_digital', 'Find energy experience', 'This category also includes digital projects; confirm energy expertise.'],
      ['cooperatives', 'Explore shared ownership', 'Ask about member investment and an affordable ownership model.'],
      ['ecology', 'Understand local ecological constraints', 'Ask who can advise on site impacts and community consent.']
    ] },
    { id: 'care', label: 'Strengthen community care', steps: [
      ['healthcare', 'Find community care experience', 'Confirm services, access criteria and capacity directly.'],
      ['education', 'Support carers and skills', 'Ask about relevant training and sustainable paid care work.'],
      ['recreation_arts', 'Explore social connection', 'Ask about accessible activities and whether referrals are welcome.']
    ] }
  ];
  function normalize(value) {
    return String(value || '').normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  }
  function phrase(haystack, needle) { return (' ' + normalize(haystack) + ' ').includes(' ' + normalize(needle) + ' '); }
  function safeUrl(value) {
    try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password ? u.href : ''; } catch (_) { return ''; }
  }
  function planText(result, chosen) {
    if (!result || !result.goal) return '';
    const line = value => String(value || '').replace(/[\r\n]+/g, ' ').trim();
    const lines = ['COMMONWEAVE — PROPOSED COMMUNITY PLAN', '', line(result.goal.label),
      'Place: ' + (result.city ? [result.city.city, result.city.region, result.city.country].filter(Boolean).map(line).join(', ') : line(result.country) || 'All countries'), '',
      'These are your research choices. Role sequences do not establish partnerships, availability or suitability.', ''];
    result.steps.forEach((step, i) => {
      const picked = step.candidates.find(c => c.org.id === chosen[step.area]);
      lines.push((i + 1) + '. ' + line(step.label), line(step.question));
      if (picked) {
        const org = picked.org;
        const hash = new URLSearchParams({ view: 'list', selectedId: String(org.id) });
        lines.push('Your choice: ' + line(org.n || org.id), 'Recorded locality: ' + ([org.ci, org.st, org.cc].filter(Boolean).map(line).join(', ') || 'Not recorded'),
          'Review record: https://commonweave.earth/map.html#' + hash.toString());
      } else lines.push('No organization chosen. ' + step.total + ' category candidates in this selection.');
      lines.push('Confirm: service area, eligibility, cost, accessibility, capacity and consent to referrals.', 'Notes: ', '');
    });
    lines.push('Suggested next action: check each chosen record with the organization, then agree who will do what. Do not share personal details without consent.',
      'Public data audit: https://github.com/simonlpaige/commonweave/blob/master/docs/DATA-AUDIT-2026-09-05.md');
    return lines.join('\n');
  }
  function evidence(edge) {
    const links = (Array.isArray(edge.evidence) ? edge.evidence : []).map(e => safeUrl(e.value || e.url)).filter(Boolean);
    const declared = ['verified_relationship', 'federation_membership', 'attestation'].includes(edge.edge_type);
    const documented = declared && edge.derived === false && links.length > 0;
    const explanation = documented ? edge.explanation || 'A relationship source is supplied; review its scope and date.' : edge.edge_type === 'same_section_proximity'
      ? 'Shared category in the export. Coordinates have no recorded precision, so physical proximity and collaboration are unconfirmed.'
      : 'An inferred connection in the export. Category or network similarity does not establish a partnership or ability to help.';
    return { documented, links, explanation, label: documented ? 'Documented relationship' : edge.edge_type === 'same_section_proximity' ? 'Shared category; locality unconfirmed' : 'Suggested connection' };
  }
  function discover(points, options) {
    const opts = Object.assign({ query: '', country: '', city: null, tiers: ['A', 'B'], goal: '' }, options);
    const goal = GOALS.find(g => g.id === opts.goal);
    const query = normalize(opts.query);
    const tokens = query.split(' ').filter(Boolean);
    const categories = Object.entries(global.CommonweaveScoring ? global.CommonweaveScoring.SECTION_KEYWORDS : {}).filter(([, words]) => words.some(w => phrase(query, w))).map(([area]) => area);
    const city = opts.city;
    const scoped = points.filter(p => opts.tiers.includes(p.t) && (!opts.country || p.cc === opts.country) && (!opts.area || p.f === opts.area) && (!opts.filter || opts.filter(p))).filter(p => {
      if (!city) return true;
      // The public export has no location precision. Country centroids must
      // never be used as evidence of physical proximity or service coverage.
      return normalize(p.ci) === normalize(city.city) && p.cc === city.country && (p.st || '') === (city.region || '');
    });
    const ranked = scoped.map(org => {
      const hay = normalize([org.n, org.d, org.ci, org.cc].filter(Boolean).join(' '));
      const textMatch = tokens.length > 0 && tokens.every(t => phrase(hay, t));
      const categoryMatch = categories.includes(org.f);
      return { org, distance: null, rank: textMatch ? 2 : categoryMatch ? 1 : 0, reasons: [AREAS[org.f] ? 'Listed under ' + AREAS[org.f] : 'Category not assigned', org.ci ? 'Recorded locality: ' + org.ci : 'Locality not recorded'] };
    }).filter(r => !query || r.rank > 0).sort((a, b) => b.rank - a.rank || (a.distance ?? Infinity) - (b.distance ?? Infinity) || normalize(a.org.n).localeCompare(normalize(b.org.n)) || String(a.org.id).localeCompare(String(b.org.id)));
    const steps = goal ? goal.steps.map(([area, label, question]) => {
      const candidates = ranked.filter(r => r.org.f === area);
      return { area, label, question, total: candidates.length, candidates };
    }) : [];
    const matches = goal ? steps.flatMap(s => s.candidates) : ranked;
    // Connect roles only. Alphabetical category candidates must never be
    // promoted into a named pathway without the user's assessment and choice.
    const bridges = steps.slice(1).map((step, i) => ({ sourceRole: steps[i].label, targetRole: step.label, basis: 'Proposed role sequence; no organization or partnership selected' }));
    return { goal, steps, matches, bridges, total: goal ? steps.reduce((n, s) => n + s.total, 0) : ranked.length, searched: scoped.length, city, country: opts.country };
  }
  global.CommonweavePathways = { GOALS, AREAS, normalize, phrase, safeUrl, evidence, discover, planText };
  if (typeof module !== 'undefined' && module.exports) module.exports = global.CommonweavePathways;
})(typeof window !== 'undefined' ? window : globalThis);
