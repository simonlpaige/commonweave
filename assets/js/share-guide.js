/* Sharing is an explicit clipboard action. No cookies, tracking or URL state. */
(function () {
  'use strict';
  const button = document.getElementById('copy-guide');
  const status = document.getElementById('copy-status');
  if (!button || !status || !navigator.clipboard || !window.isSecureContext) return;
  button.hidden = false;
  button.addEventListener('click', async function () {
    try {
      await navigator.clipboard.writeText('https://commonweave.earth/find-community-organizations.html');
      status.textContent = 'Guide link copied.';
    } catch (_) {
      status.textContent = 'Copy the guide link shown above.';
    }
  });
}());
