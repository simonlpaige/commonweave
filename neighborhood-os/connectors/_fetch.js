// connectors/_fetch.js
// Single wrapper over the global fetch() with exponential backoff for
// transient network errors and 5xx/429 responses. Three attempts by
// default, 400ms base, jittered. Caller can override via options.
//
// Why this exists: the review flagged "no retries on transient network
// errors" across every connector. One flaky minute on Socrata used to
// kill the nightly sync. This wraps every remote call so the sync rides
// through brief blips.

export async function fetchJson(url, {
  headers = {},
  attempts = 3,
  baseDelayMs = 400,
  timeoutMs = 20_000,
  accept429 = false   // Set true to NOT retry 429 (legistar likes to 429 on paging)
} = {}) {
  let lastError = null;
  for (let attempt = 1; attempt <= attempts; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, {
        headers: { 'Accept': 'application/json', ...headers },
        signal: controller.signal
      });
      clearTimeout(timer);

      if (res.ok) return await res.json();

      // Retry only on 429 or 5xx. Everything else is the caller's bug.
      const retryable = res.status === 429 || (res.status >= 500 && res.status < 600);
      if (!retryable || (res.status === 429 && accept429)) {
        throw new Error(`HTTP ${res.status} at ${url}`);
      }
      lastError = new Error(`HTTP ${res.status} at ${url}`);
    } catch (err) {
      clearTimeout(timer);
      // AbortError or network error - both retryable.
      lastError = err;
    }
    if (attempt < attempts) await sleep(backoffMs(baseDelayMs, attempt));
  }
  throw lastError;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function backoffMs(base, attempt) {
  // Exponential with full jitter. Attempt 1 -> up to base, 2 -> up to 2*base, etc.
  const ceil = base * Math.pow(2, attempt - 1);
  return Math.floor(Math.random() * ceil);
}
