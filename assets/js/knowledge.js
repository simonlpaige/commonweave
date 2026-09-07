(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CommonweaveKnowledge = api;
  if (typeof document !== 'undefined') api.init(document);
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function normalize(value) {
    return String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  }

  function matches(resource, query, topic) {
    if (topic && topic !== 'all' && resource.topic !== topic) return false;
    const terms = normalize(query).split(/\s+/).filter(Boolean);
    const content = normalize(resource.text + ' ' + (resource.keywords || ''));
    return terms.every(term => content.includes(term));
  }

  function init(doc) {
    const form = doc.getElementById('knowledge-search-form');
    if (!form) return;
    const query = doc.getElementById('knowledge-query');
    const topic = doc.getElementById('knowledge-topic');
    const clear = doc.getElementById('knowledge-clear');
    const status = doc.getElementById('knowledge-status');
    const empty = doc.getElementById('knowledge-empty');
    const resources = Array.from(doc.querySelectorAll('[data-knowledge-resource]')).map(element => ({
      element, topic: element.dataset.topic, text: element.textContent,
      keywords: element.dataset.keywords || ''
    }));
    const groups = Array.from(doc.querySelectorAll('[data-knowledge-group]'));

    function render() {
      let visible = 0;
      resources.forEach(resource => {
        resource.element.hidden = !matches(resource, query.value, topic.value);
        if (!resource.element.hidden) visible += 1;
      });
      groups.forEach(group => {
        group.hidden = !resources.some(resource => resource.topic === group.dataset.knowledgeGroup && !resource.element.hidden);
      });
      const filtering = query.value.trim().length > 0 || topic.value !== 'all';
      clear.hidden = !filtering;
      empty.hidden = visible !== 0;
      status.textContent = filtering
        ? `${visible} matching reading${visible === 1 ? '' : 's'} out of ${resources.length}.`
        : `${resources.length} curated readings. Select a topic or search to narrow the list.`;
    }

    function reset() {
      query.value = '';
      topic.value = 'all';
      render();
      query.focus();
    }

    query.addEventListener('input', render);
    topic.addEventListener('change', render);
    clear.addEventListener('click', reset);
    doc.getElementById('knowledge-empty-clear').addEventListener('click', reset);
    form.addEventListener('submit', event => { event.preventDefault(); render(); });
    form.hidden = false;
    status.hidden = false;
    render();
  }

  return { normalize, matches, init };
});
