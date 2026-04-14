import sqlite3
db = sqlite3.connect(r'C:\Users\simon\.openclaw\workspace\ecolibrium\data\ecolibrium_directory.db')
c = db.cursor()
c.execute("SELECT COUNT(*) FROM organizations WHERE status != 'removed'")
print(f"Active orgs: {c.fetchone()[0]:,}")
c.execute("SELECT country_code, COUNT(*) as cnt FROM organizations WHERE status != 'removed' GROUP BY country_code ORDER BY cnt DESC LIMIT 30")
for cc, cnt in c.fetchall():
    print(f"  {cc}: {cnt:,}")
c.execute("SELECT source, COUNT(*) FROM organizations WHERE status != 'removed' GROUP BY source ORDER BY COUNT(*) DESC")
print("\nBy source:")
for src, cnt in c.fetchall():
    print(f"  {src}: {cnt:,}")
db.close()
