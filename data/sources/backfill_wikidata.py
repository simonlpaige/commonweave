"""
Backfill Wikidata for all countries already in the Commonweave DB.
Runs wikidata_ingest.py for each unique country_code.
"""
import sqlite3
import subprocess
import sys
import time
import os

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
SCRIPT = os.path.join(os.path.dirname(__file__), 'wikidata_ingest.py')

def get_existing_countries():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("""SELECT DISTINCT country_code, country_name
                 FROM organizations
                 WHERE country_code IS NOT NULL AND country_code != ''
                 AND status != 'removed'
                 GROUP BY country_code
                 ORDER BY country_code""")
    rows = c.fetchall()
    db.close()
    return rows

def get_total():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'removed'")
    n = c.fetchone()[0]
    db.close()
    return n

def main():
    # Allow starting from a specific country
    start_from = sys.argv[1].upper() if len(sys.argv) > 1 else None

    countries = get_existing_countries()
    skip = {'US'}  # Already have 660K+ from IRS
    countries = [(cc, name) for cc, name in countries if cc not in skip]

    if start_from:
        idx = next((i for i, (cc, _) in enumerate(countries) if cc == start_from), 0)
        countries = countries[idx:]

    print(f'Will backfill {len(countries)} countries (skipping US)')
    total_before = get_total()

    for i, (cc, name) in enumerate(countries):
        print(f'\n[{i+1}/{len(countries)}] {name} ({cc})')
        try:
            result = subprocess.run(
                ['python', SCRIPT, cc, name],
                capture_output=True, text=True, timeout=180,
                encoding='utf-8', errors='replace'
            )
            for line in result.stdout.split('\n'):
                if 'Found' in line or 'DB:' in line or 'Done:' in line:
                    print(f'  {line.strip()}')
            if result.returncode != 0:
                errs = [l for l in result.stderr.split('\n') if 'Error' in l]
                for e in errs[:2]:
                    print(f'  ERR: {e.strip()}')
        except subprocess.TimeoutExpired:
            print(f'  TIMEOUT')
        except Exception as e:
            print(f'  ERROR: {e}')

        time.sleep(2)

    total_after = get_total()
    print(f'\n=== Backfill complete ===')
    print(f'Before: {total_before:,}')
    print(f'After:  {total_after:,}')
    print(f'Added:  {total_after - total_before:,}')


if __name__ == '__main__':
    main()
