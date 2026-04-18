import sqlite3
db = sqlite3.connect('ecolibrium_directory.db')
c = db.cursor()
c.execute("SELECT COUNT(*) FROM organizations WHERE status='active'")
print('Active:', c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM organizations")
print('Total:', c.fetchone()[0])
c.execute("SELECT alignment_score, COUNT(*) FROM organizations WHERE status='active' GROUP BY alignment_score ORDER BY alignment_score DESC LIMIT 15")
print('Score distribution (top 15 by score):')
for row in c.fetchall():
    print(f'  score {row[0]}: {row[1]}')
# Check if new columns already exist
c.execute("PRAGMA table_info(organizations)")
cols = [row[1] for row in c.fetchall()]
print('Existing columns relevant:', [c2 for c2 in cols if 'alignment' in c2 or 'legacy' in c2 or 'v2' in c2])
db.close()
