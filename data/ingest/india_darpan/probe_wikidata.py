# -*- coding: utf-8 -*-
"""
Feasibility probe: Wikidata SPARQL for Indian nonprofit organizations.

Tests whether Wikidata returns useful Indian nonprofit data tonight.
If yes, we can run a full pull in Task 4 follow-up.
"""

import json
import urllib.request
import urllib.parse

ENDPOINT = "https://query.wikidata.org/sparql"

# Query: non-profit organizations (Q163740) located in India (Q668)
# Limited to 20 for probe; full query would drop LIMIT.
QUERY = """
SELECT ?org ?orgLabel ?orgDescription ?website ?stateLabel WHERE {
  ?org wdt:P31/wdt:P279* wd:Q163740 .   # nonprofit organization (or subclass)
  ?org wdt:P17 wd:Q668 .                # country = India
  OPTIONAL { ?org wdt:P856 ?website }
  OPTIONAL { ?org wdt:P131 ?state }
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "en,hi,ta,bn,te,ml,mr,pa"
  }
}
LIMIT 20
"""


def probe():
    params = urllib.parse.urlencode({"query": QUERY, "format": "json"})
    url = f"{ENDPOINT}?{params}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Commonweave-Research-Bot/1.0 (nonprofit directory research)",
        "Accept": "application/sparql-results+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return

    bindings = data.get("results", {}).get("bindings", [])
    print(f"SPARQL returned {len(bindings)} results")
    for i, b in enumerate(bindings[:10]):
        name = b.get("orgLabel", {}).get("value", "?")
        desc = b.get("orgDescription", {}).get("value", "")
        state = b.get("stateLabel", {}).get("value", "")
        site = b.get("website", {}).get("value", "")
        print(f"  [{i+1}] {name}  |  state={state}  |  {desc[:60]}")
        if site:
            print(f"       website: {site}")

    # Count how many have non-ASCII in name (proxy for native-script labels)
    non_ascii = sum(
        1 for b in bindings
        if any(ord(c) > 127 for c in b.get("orgLabel", {}).get("value", ""))
    )
    print(f"\nResults with non-ASCII names (Hindi/Tamil/Bengali): {non_ascii}/{len(bindings)}")
    print(f"Results with websites: {sum(1 for b in bindings if b.get('website'))}")


if __name__ == "__main__":
    probe()
