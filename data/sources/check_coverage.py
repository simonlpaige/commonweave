import sqlite3
db = sqlite3.connect(r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db')
c = db.cursor()
c.execute("""
    SELECT country_code, source, COUNT(*) as cnt
    FROM organizations WHERE status != 'removed' AND country_code != 'US'
    GROUP BY country_code, source ORDER BY country_code, source
""")
print("CC   Source               Count")
print("-" * 50)
for cc, src, cnt in c.fetchall():
    print(f"{cc:4s} {src:20s} {cnt}")

print("\n\nCountries with Wikidata vs without:")
c.execute("""
    SELECT country_code, 
           SUM(CASE WHEN source='wikidata' THEN 1 ELSE 0 END) as wiki,
           SUM(CASE WHEN source='web_research' THEN 1 ELSE 0 END) as ddg,
           SUM(CASE WHEN source NOT IN ('wikidata','web_research') THEN 1 ELSE 0 END) as other,
           COUNT(*) as total
    FROM organizations WHERE status != 'removed' AND country_code != 'US'
    GROUP BY country_code ORDER BY total DESC
""")
print(f"{'CC':4s} {'Wiki':>6s} {'DDG':>6s} {'Other':>6s} {'Total':>6s}  Status")
print("-" * 60)
for cc, wiki, ddg, other, total in c.fetchall():
    status = "OK" if wiki > 0 else "NEEDS WIKIDATA"
    print(f"{cc:4s} {wiki:6d} {ddg:6d} {other:6d} {total:6d}  {status}")
db.close()
