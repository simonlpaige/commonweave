(function (root) {
  'use strict';
  const types = {
    correct: ['Correct a listing', 'Tell us what is wrong and what the evidence supports.'],
    add: ['Suggest an organization', 'A public source is required. New suggestions enter a review queue.'],
    verify: ["Review my organization's listing", 'Include a public organization page. A maintainer must confirm your authority separately.'],
    connection: ['Review a connection', 'Name the organizations, what each contributes, and whether this is documented or only proposed.'],
    help: ['Offer a contribution', 'Choose one small task, the place or network you know, and the time you can offer.'],
    obscure: ['Reduce location detail', 'A listing name or ID and a short request are enough. No address or personal explanation is needed.'],
    remove: ['Request removal', 'A listing name or ID and “please remove” are enough. No proof of ownership is required.']
  };
  function publicUrl(value) {
    const text = String(value || '').trim();
    if (!text || /[\s<>"'`]/.test(text)) return '';
    try {
      const u = new URL(text);
      return ['http:', 'https:'].includes(u.protocol) && !u.username && !u.password ? u.href : '';
    } catch (_) { return ''; }
  }
  function buildDraft(values) {
    const type = Object.hasOwn(types, values.type) ? values.type : 'correct';
    const clean = (key, length) => String(values[key] || '').trim().slice(0, length);
    const org = clean('org', 180);
    const details = clean('details', 3000);
    if (!org || !details) throw new Error('Add an organization or topic and a short explanation.');
    const source = clean('source', 1000);
    if (source && !publicUrl(source)) throw new Error('Use a complete public http:// or https:// source URL.');
    if (['add', 'verify'].includes(type) && !source) throw new Error('Add a public source supporting this organization.');
    const title = `[Commonweave] ${types[type][0]}: ${org}`.replace(/[\r\n]+/g, ' ');
    const body = [
      `## ${types[type][0]}`, `Organization or topic: ${org}`,
      `Listing ID: ${clean('id', 100) || 'Not provided'}`,
      `Country or region: ${clean('country', 80) || 'Not provided'}`,
      `Contributor relationship (self-reported): ${clean('relationship', 100) || 'Not provided'}`,
      '', '## Requested change or contribution', details, '',
      '## Public evidence', source ? publicUrl(source) : 'Not supplied; needs review.', '',
      '## Review status', 'Proposed only. No listing, authority, partnership, or service availability has been verified by this submission.'
    ].join('\n');
    const params = new URLSearchParams({title, body});
    const url = `https://github.com/simonlpaige/commonweave/issues/new?${params}`;
    // Very long UTF-8 URLs can fail in browsers/proxies. Never silently truncate evidence.
    return {title, body, text: `${title}\n\n${body}\n`, url: url.length <= 7000 ? url : null};
  }
  const api = {types, publicUrl, buildDraft};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CommonweaveParticipation = api;
  if (typeof document === 'undefined') return;
  const form = document.getElementById('contribution-form');
  if (!form) return;
  const $ = id => document.getElementById(id);
  const query = new URLSearchParams(location.search);
  ['org', 'id', 'country'].forEach(key => { form.elements[key].value = (query.get(key) || '').slice(0, form.elements[key].maxLength); });
  if (Object.hasOwn(types, query.get('type'))) form.elements.type.value = query.get('type');
  let draft = null;
  function typeHelp() {
    const type = form.elements.type.value;
    $('type-help').textContent = types[type][1];
    const required = ['add', 'verify'].includes(type);
    $('source').required = required;
    $('source-required').textContent = required ? '(required)' : '(optional)';
  }
  form.addEventListener('input', () => {
    draft = null;
    $('draft-section').hidden = true;
    $('draft-status').textContent = '';
    $('source').setCustomValidity('');
    typeHelp();
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    try {
      draft = buildDraft(Object.fromEntries(new FormData(form)));
      $('draft-preview').textContent = draft.text;
      $('draft-section').hidden = false;
      $('github-draft').hidden = !draft.url;
      if (draft.url) $('github-draft').href = draft.url;
      else $('github-draft').removeAttribute('href');
      $('draft-status').textContent = draft.url ? 'Draft ready. Review it below; nothing has been sent.' : 'Draft ready. Download it and paste it into a GitHub issue; it is too long for a reliable prefilled link.';
      $('draft-heading').focus();
    } catch (error) {
      $('draft-status').textContent = error.message;
      $('draft-section').hidden = true;
    }
  });
  $('download-draft').addEventListener('click', () => {
    if (!draft) return;
    const url = URL.createObjectURL(new Blob([draft.text], {type: 'text/markdown;charset=utf-8'}));
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'commonweave-contribution.md';
    document.body.appendChild(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('draft-status').textContent = 'Draft download started. Share it when you are ready; it has not been submitted.';
  });
  typeHelp();
})(typeof window === 'undefined' ? globalThis : window);
