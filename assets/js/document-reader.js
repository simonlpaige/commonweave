(function (global) {
  'use strict';
  function documentPath(value) {
    const name = String(value || 'README');
    if (name.length > 220 || !/^[a-zA-Z0-9_./-]+$/.test(name) || name.startsWith('/') || name.split('/').some(part => !part || part === '.' || part === '..')) throw new Error('Choose a document from the knowledge base.');
    if (/\.[^/]+$/.test(name) && !name.endsWith('.md')) throw new Error('Only Markdown documents can be opened here.');
    return name.endsWith('.md') ? name : name + '.md';
  }
  function headingSlug(text) {
    return String(text).trim().toLowerCase().replace(/[^\p{L}\p{N}\s_-]/gu, '').replace(/\s/g, '-');
  }
  function resourceLink(raw, source, origin) {
    if (!raw || /[\u0000-\u001f\\]/.test(raw)) return null;
    if (raw.startsWith('#')) return raw;
    let url;
    try { url = new URL(raw, new URL(source, origin + '/')); } catch (_) { return null; }
    if (!['http:', 'https:', 'mailto:'].includes(url.protocol) || url.username || url.password) return null;
    if (url.origin === origin && url.pathname.endsWith('.md')) {
      try {
        const file = documentPath(decodeURIComponent(url.pathname.slice(1)));
        return 'doc.html?file=' + encodeURIComponent(file.slice(0, -3)) + url.hash;
      } catch (_) { return null; }
    }
    return url.href;
  }
  async function init() {
    const doc = global.document, $ = id => doc.getElementById(id);
    let file, controller;
    const content = $('content'), status = $('document-status'), heading = $('document-heading');
    function node(tag, text) { const item = doc.createElement(tag); if (text !== undefined) item.textContent = text; return item; }
    function showFailure(message, retry) {
      status.hidden = false; status.replaceChildren(node('h2', 'This reading could not be opened'), node('p', message));
      if (retry) { const button = node('button', 'Try again'); button.type = 'button'; button.addEventListener('click', load); status.append(button); }
      const back = node('a', 'Browse the knowledge base'); back.href = 'knowledge.html'; const p = node('p'); p.append(back); status.append(p);
    }
    try { file = documentPath(new URLSearchParams(global.location.search).get('file')); }
    catch (error) { showFailure(error.message, false); return; }
    const path = file.split('/').map(encodeURIComponent).join('/');
    $('document-source').href = 'https://github.com/simonlpaige/commonweave/blob/master/' + path;
    $('document-download').href = path;
    $('document-download').download = file.split('/').pop();
    $('document-tools').hidden = false;
    async function load() {
      if (controller) controller.abort();
      controller = new AbortController();
      const activeController = controller;
      status.hidden = false; status.replaceChildren(node('p', 'Loading document…'));
      $('document-tools').hidden = false;
      content.replaceChildren(); content.setAttribute('aria-busy', 'true');
      $('document-outline').hidden = true; $('document-notice').hidden = true; $('document-next').hidden = true;
      const timer = setTimeout(() => activeController.abort(), 15000);
      try {
        if (!global.marked || !global.DOMPurify) throw new Error('The reader could not load. You can still view the source on GitHub.');
        const response = await fetch(path, { signal: activeController.signal });
        if (!response.ok) {
          if (response.status === 404) $('document-tools').hidden = true;
          throw new Error(response.status === 404 ? 'This document is not available at that address. Choose a reading from the knowledge base.' : 'The document could not be downloaded. Try again or view the source on GitHub.');
        }
        const markdown = await response.text();
        if (markdown.length > 3000000) throw new Error('This document is too large for the reader. Download the text or view the source on GitHub.');
        if (controller !== activeController) return;
        const clean = global.DOMPurify.sanitize(global.marked.parse(markdown, { gfm: true }), {
          USE_PROFILES: { html: true },
          FORBID_TAGS: ['style', 'form', 'iframe', 'object', 'embed', 'button', 'textarea', 'select', 'base', 'link', 'meta'],
          FORBID_ATTR: ['style', 'id', 'name', 'srcset']
        });
        content.innerHTML = clean;
        content.querySelectorAll('a').forEach(a => {
          const url = resourceLink(a.getAttribute('href'), file, global.location.origin);
          if (url) { a.setAttribute('href', url); a.removeAttribute('target'); a.setAttribute('rel', 'noopener noreferrer'); }
          else a.removeAttribute('href');
        });
        content.querySelectorAll('img').forEach(img => {
          const url = resourceLink(img.getAttribute('src'), file, global.location.origin);
          if (!url || !/^https?:/.test(url)) { img.remove(); return; }
          img.src = url; img.loading = 'lazy'; img.referrerPolicy = 'no-referrer';
        });
        content.querySelectorAll('input').forEach(input => { input.disabled = true; });
        const first = content.querySelector('h1');
        const title = first ? first.textContent : file.split('/').pop().replace('.md', '').replace(/[-_]/g, ' ');
        heading.textContent = title; $('breadcrumb-current').textContent = title; doc.title = title + ' · Commonweave';
        const counts = new Map(), toc = $('toc-list'); toc.replaceChildren();
        content.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => {
          const base = headingSlug(h.textContent) || 'section', count = counts.get(base) || 0;
          counts.set(base, count + 1); h.id = base + (count ? '-' + count : '');
          if (h.tagName === 'H2' || h.tagName === 'H3') {
            const link = node('a', h.textContent); link.href = '#' + h.id; if (h.tagName === 'H3') link.className = 'toc-h3';
            const li = node('li'); li.append(link); toc.append(li);
          }
        });
        // Keep the source's title anchor while displaying the title only once.
        if (first) { const anchor = node('span'); anchor.id = first.id; first.replaceWith(anchor); }
        content.querySelectorAll('table').forEach(table => {
          const wrap = node('div'); wrap.className = 'reader-table'; wrap.tabIndex = 0; wrap.setAttribute('role', 'region'); wrap.setAttribute('aria-label', 'Scrollable comparison table');
          table.before(wrap); wrap.append(table);
        });
        const outline = $('document-outline'); outline.hidden = !toc.children.length; outline.open = global.matchMedia('(min-width: 901px)').matches;
        const legacy = new Set(['RESEARCH.md', 'DEEP-DIVE.md', 'BLUEPRINT.md', 'THEORY-OF-CHANGE.md', 'OPENCOOP-RESEARCH.md', 'WISEREARTH.md']);
        const notice = $('document-notice'); notice.replaceChildren();
        notice.append(node('p', legacy.has(file)
          ? 'Research notes · source review needed. Dates, figures and named examples in this older document have not all been checked. Treat them as claims to investigate, not established evidence or current service guidance.'
          : 'Working knowledge · inspect the sources, assumptions and limits. A proposal or a named example does not by itself establish that an approach works.'));
        notice.hidden = false;
        const next = $('document-next'); next.replaceChildren();
        for (const [url, label] of [['knowledge.html', 'Back to knowledge base'], ['map.html', 'Explore organizations on the map']]) { const a = node('a', label); a.href = url; next.append(a); }
        next.hidden = false; status.hidden = true;
        if (global.location.hash) {
          let id; try { id = decodeURIComponent(global.location.hash.slice(1)); } catch (_) { id = ''; }
          const target = doc.getElementById(id);
          if (target && content.contains(target)) requestAnimationFrame(() => target.scrollIntoView());
        }
      } catch (error) {
        if (controller !== activeController) return;
        showFailure(error.name === 'AbortError' ? 'The document took too long to load. Try again or view the source on GitHub.' : error.message, true);
      } finally { clearTimeout(timer); if (controller === activeController) content.setAttribute('aria-busy', 'false'); }
    }
    await load();
  }
  const api = { documentPath, headingSlug, resourceLink, init };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.CommonweaveReader = api;
  if (global.document) init();
})(typeof window !== 'undefined' ? window : globalThis);
