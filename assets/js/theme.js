/* Theme toggle: light <-> dark, persisted in localStorage.
   The toggle button must have id="theme-toggle". The button's icons
   (sun/moon) are styled in commonweave.css and swap based on
   body.dark. We apply the saved theme as early as possible to avoid
   a flash. */
(function () {
  var KEY = 'commonweave.theme';
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (_) { /* ignore */ }
  if (saved === 'dark') document.body.classList.add('dark');

  function syncAria(btn) {
    if (!btn) return;
    var isDark = document.body.classList.contains('dark');
    btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
    btn.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
  }

  function init() {
    var btn = document.getElementById('theme-toggle');
    syncAria(btn);
    if (!btn) return;
    btn.addEventListener('click', function () {
      var nowDark = !document.body.classList.contains('dark');
      document.body.classList.toggle('dark', nowDark);
      try { localStorage.setItem(KEY, nowDark ? 'dark' : 'light'); } catch (_) { /* ignore */ }
      syncAria(btn);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
