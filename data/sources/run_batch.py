"""Run wikidata ingest for multiple countries, one at a time, in-process."""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from wikidata_ingest import fetch_country, ingest_to_db, COUNTRY_QID

BATCH = [
    ('VE', 'Venezuela'), ('HN', 'Honduras'), ('GT', 'Guatemala'),
    ('NI', 'Nicaragua'), ('EC', 'Ecuador'), ('GY', 'Guyana'),
    ('PY', 'Paraguay'), ('SR', 'Suriname'),
    ('GB', 'United Kingdom'), ('FR', 'France'), ('DE', 'Germany'),
    ('BR', 'Brazil'), ('IN', 'India'), ('MX', 'Mexico'),
    ('CO', 'Colombia'), ('CA', 'Canada'), ('AU', 'Australia'),
    ('NZ', 'New Zealand'), ('JP', 'Japan'), ('IT', 'Italy'),
    ('ES', 'Spain'), ('NL', 'Netherlands'), ('SE', 'Sweden'),
]

total_added = 0
for i, (cc, name) in enumerate(BATCH):
    if cc not in COUNTRY_QID:
        print(f'[{i+1}/{len(BATCH)}] {name} ({cc}) - no QID, skip')
        continue
    print(f'\n[{i+1}/{len(BATCH)}] {name} ({cc})')
    try:
        orgs = fetch_country(cc, name)
        inserted = ingest_to_db(orgs, cc, name)
        total_added += inserted
        print(f'  => {len(orgs)} found, {inserted} new')
    except Exception as e:
        print(f'  ERROR: {e}')
    time.sleep(2)

print(f'\n=== Batch complete: +{total_added} total new orgs ===')
