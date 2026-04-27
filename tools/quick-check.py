import sqlite3
db = sqlite3.connect(r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db')
c = db.cursor()

print("=== Apache ===")
c.execute("SELECT name, source, alignment_score, website, framework_area, country_code FROM organizations WHERE lower(name) LIKE '%apache%' AND status='active' ORDER BY alignment_score DESC LIMIT 10")
for r in c.fetchall(): print(r)

print("\n=== Linux Foundation / Mozilla / Wikipedia ===")
for term in ['linux foundation', 'mozilla', 'wikimedia', 'creative commons', 'open source initiative']:
    c.execute("SELECT name, source, alignment_score, country_code FROM organizations WHERE lower(name) LIKE ? AND status='active' LIMIT 3", [f'%{term}%'])
    rows = c.fetchall()
    if rows:
        for r in rows: print(r)
    else:
        print(f'  NOT FOUND: {term}')

print("\n=== Geo coverage ===")
c.execute("SELECT COUNT(id) FROM organizations WHERE status='active'")
print('Total active:', c.fetchone()[0])
c.execute("SELECT COUNT(id) FROM organizations WHERE status='active' AND lat IS NOT NULL")
print('Geocoded (lat):', c.fetchone()[0])
c.execute("SELECT COUNT(id) FROM organizations WHERE status='active' AND state_province IS NOT NULL AND state_province != ''")
print('Has state/province:', c.fetchone()[0])
c.execute("SELECT COUNT(id) FROM organizations WHERE status='active' AND city IS NOT NULL AND city != ''")
print('Has city:', c.fetchone()[0])

print("\n=== Sources with 'open' in name ===")
c.execute("SELECT DISTINCT source FROM organizations WHERE status='active' ORDER BY source")
for r in c.fetchall():
    if 'open' in r[0].lower() or 'collect' in r[0].lower():
        print(r[0])
