# -*- coding: utf-8 -*-
"""
Probe script for NGO Darpan (ngodarpan.gov.in).

Tests whether the CSRF-protected JSON endpoint is accessible without a
browser session. Reports status, response type, and a data sample if successful.

NOT a bulk scraper - this is a feasibility check only.
Respects robots.txt intent: read-only, no account creation, no bypass of auth.
"""

import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar

BASE_URL = "https://ngodarpan.gov.in"
CSRF_URL = f"{BASE_URL}/index.php/ajaxcontroller/get_csrf"
# State 10 = Maharashtra, page 0
SAMPLE_STATE_URL = f"{BASE_URL}/index.php/home/statewise_ngo/10/0"

HEADERS = {
    "User-Agent": "Ecolibrium-Research-Bot/1.0 (nonprofit directory research; contact ecolibrium-research@example.com)",
    "Accept": "application/json, text/html",
    "Accept-Language": "en-US,en;q=0.9",
}


def probe():
    results = {}

    # Set up cookie jar for session handling
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    # Step 1: Get a session cookie + CSRF token
    print("Step 1: Requesting CSRF token...")
    try:
        req = urllib.request.Request(CSRF_URL, headers=HEADERS)
        with opener.open(req, timeout=15) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(2000).decode("utf-8", errors="replace")
            results["csrf_status"] = status
            results["csrf_content_type"] = content_type
            results["csrf_raw_snippet"] = raw[:300]
            print(f"  Status: {status}")
            print(f"  Content-Type: {content_type}")
            print(f"  Response snippet: {raw[:200]!r}")

            # Try to parse as JSON
            csrf_token = None
            try:
                data = json.loads(raw)
                csrf_token = data.get("csrf_token") or data.get("token")
                results["csrf_token_found"] = bool(csrf_token)
                print(f"  CSRF token: {'FOUND' if csrf_token else 'NOT in JSON'}")
            except json.JSONDecodeError:
                results["csrf_token_found"] = False
                print("  Response is not JSON (probably HTML redirect)")
    except urllib.error.HTTPError as exc:
        results["csrf_status"] = exc.code
        results["csrf_error"] = str(exc)
        print(f"  HTTP ERROR: {exc.code} {exc.reason}")
    except Exception as exc:
        results["csrf_error"] = str(exc)
        print(f"  ERROR: {exc}")
        csrf_token = None

    # Step 2: Even without a CSRF token, try the statewise endpoint directly
    time.sleep(2)
    print("\nStep 2: Probing statewise JSON endpoint directly...")
    try:
        req = urllib.request.Request(
            SAMPLE_STATE_URL,
            headers={**HEADERS, "Accept": "application/json"},
        )
        with opener.open(req, timeout=15) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(3000).decode("utf-8", errors="replace")
            results["statewise_status"] = status
            results["statewise_content_type"] = content_type
            print(f"  Status: {status}")
            print(f"  Content-Type: {content_type}")
            print(f"  Response snippet: {raw[:400]!r}")

            try:
                data = json.loads(raw)
                ngo_list = data.get("ngos") or data.get("data") or data.get("result") or []
                results["statewise_is_json"] = True
                results["statewise_ngo_count"] = len(ngo_list)
                if ngo_list:
                    print(f"  JSON parsed! NGOs in response: {len(ngo_list)}")
                    print(f"  Sample keys: {list(ngo_list[0].keys()) if ngo_list else 'n/a'}")
                else:
                    print(f"  JSON parsed but ngo list key not found. Top keys: {list(data.keys())[:10]}")
            except json.JSONDecodeError:
                results["statewise_is_json"] = False
                print("  Response is not JSON")
    except Exception as exc:
        results["statewise_error"] = str(exc)
        print(f"  ERROR: {exc}")

    # Cookies received
    cookies = list(cookie_jar)
    results["cookies_received"] = len(cookies)
    print(f"\nCookies received from site: {len(cookies)}")
    for ck in cookies:
        print(f"  {ck.name} = {ck.value[:30] if ck.value else '(empty)'}")

    return results


if __name__ == "__main__":
    probe()
