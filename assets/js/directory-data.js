(function (root) {
  'use strict';
  function safeWebsite(value) {
    const input = String(value || '').trim();
    if (!input || /[\s<>"'`\\]/.test(input)) return '';
    if (/^[a-z][a-z\d+.-]*:/i.test(input) && !/^https?:\/\//i.test(input)) return '';
    try {
      const url = new URL(/^https?:\/\//i.test(input) ? input : `https://${input}`);
      return ['https:', 'http:'].includes(url.protocol) && !url.username && !url.password && url.hostname.includes('.') ? url.href : '';
    } catch (_) { return ''; }
  }
  function organizations(data) {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.orgs)) return data.orgs;
    if (Array.isArray(data?.organizations)) return data.organizations;
    throw new Error('The directory file has an unsupported format.');
  }
  function latestRequest() {
    let generation = 0;
    return {next: () => ++generation, isCurrent: token => token === generation};
  }
  const api = {safeWebsite, organizations, latestRequest};
  root.CommonweaveDirectory = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window === 'undefined' ? globalThis : window);
