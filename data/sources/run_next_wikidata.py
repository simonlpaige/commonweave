"""
Run Wikidata ingest for the next un-processed country.
Tracks progress in wikidata_done.txt.
Designed to be called by cron/scheduler - runs ONE country per invocation.
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from wikidata_ingest import fetch_country, ingest_to_db, COUNTRY_QID

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
DONE_FILE = os.path.join(os.path.dirname(__file__), 'wikidata_done.txt')

# Priority order: countries with most civil society activity first
PRIORITY_COUNTRIES = [
    ('GB', 'United Kingdom'), ('FR', 'France'), ('DE', 'Germany'),
    ('BR', 'Brazil'), ('IN', 'India'), ('MX', 'Mexico'),
    ('CO', 'Colombia'), ('CA', 'Canada'), ('AU', 'Australia'),
    ('NZ', 'New Zealand'), ('JP', 'Japan'), ('IT', 'Italy'),
    ('ES', 'Spain'), ('NL', 'Netherlands'), ('SE', 'Sweden'),
    ('VE', 'Venezuela'), ('HN', 'Honduras'), ('GT', 'Guatemala'),
    ('NI', 'Nicaragua'), ('EC', 'Ecuador'), ('GY', 'Guyana'),
    ('PY', 'Paraguay'), ('SR', 'Suriname'),
    ('PE', 'Peru'), ('CL', 'Chile'), ('AR', 'Argentina'),
    ('PH', 'Philippines'), ('ID', 'Indonesia'), ('TH', 'Thailand'),
    ('EG', 'Egypt'), ('GH', 'Ghana'), ('ET', 'Ethiopia'),
    ('TZ', 'Tanzania'), ('UG', 'Uganda'), ('RW', 'Rwanda'),
    ('SN', 'Senegal'), ('PL', 'Poland'), ('UA', 'Ukraine'),
    ('TR', 'Turkey'), ('BD', 'Bangladesh'), ('PK', 'Pakistan'),
    ('NP', 'Nepal'), ('LK', 'Sri Lanka'),
    # Countries with only 1 org (from OFN manual curation)
    ('BE', 'Belgium'), ('CH', 'Switzerland'), ('ES', 'Spain'),
    ('HU', 'Hungary'), ('IE', 'Ireland'), ('NO', 'Norway'),
    ('RU', 'Russia'), ('PT', 'Portugal'), ('DK', 'Denmark'),
    ('FI', 'Finland'), ('AT', 'Austria'), ('GR', 'Greece'),
    ('RO', 'Romania'), ('RS', 'Serbia'), ('BG', 'Bulgaria'),
    ('GE', 'Georgia'), ('AM', 'Armenia'), ('KZ', 'Kazakhstan'),
    ('UZ', 'Uzbekistan'),
    # Additional high-value countries
    ('MY', 'Malaysia'), ('VN', 'Vietnam'), ('KH', 'Cambodia'),
    ('MM', 'Myanmar'), ('KR', 'South Korea'), ('TW', 'Taiwan'),
    ('MA', 'Morocco'), ('TN', 'Tunisia'), ('JO', 'Jordan'),
    ('LB', 'Lebanon'), ('CI', 'Cote d Ivoire'), ('CM', 'Cameroon'),
    ('MG', 'Madagascar'), ('MZ', 'Mozambique'), ('ZM', 'Zambia'),
]

def get_done():
    if os.path.exists(DONE_FILE):
        with open(DONE_FILE) as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def mark_done(cc):
    with open(DONE_FILE, 'a') as f:
        f.write(cc + '\n')

def main():
    done = get_done()
    # Find next country not yet processed
    for cc, name in PRIORITY_COUNTRIES:
        if cc in done:
            continue
        if cc not in COUNTRY_QID:
            print(f'No QID for {cc}, skipping')
            mark_done(cc)
            continue

        print(f'Processing: {name} ({cc})')
        try:
            orgs = fetch_country(cc, name)
            inserted = ingest_to_db(orgs, cc, name)
            mark_done(cc)
            print(f'DONE: {name} ({cc}) - {len(orgs)} found, {inserted} new')

            # Get total
            db = sqlite3.connect(DB_PATH)
            c = db.cursor()
            c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'removed'")
            total = c.fetchone()[0]
            remaining = len([c for c, _ in PRIORITY_COUNTRIES if c not in done and c != cc])
            db.close()
            print(f'DB total: {total:,} | Remaining: {remaining} countries')
        except Exception as e:
            print(f'ERROR: {e}')
            # Still mark done to avoid infinite retries
            mark_done(cc)
        return

    print('All priority countries processed!')

if __name__ == '__main__':
    main()
