"""Minimal: run wikidata for ONE country, print result, exit fast."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from wikidata_ingest import fetch_country, ingest_to_db
cc, name = sys.argv[1], sys.argv[2]
orgs = fetch_country(cc, name)
n = ingest_to_db(orgs, cc, name)
print(f'RESULT: {cc} {len(orgs)} found {n} new')
