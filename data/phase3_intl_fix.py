"""
Phase 3: Fix international orgs + clean up P2 placeholder rows.
1. Export P2 rows to an audit CSV, then mark them removed
2. For all active web_research orgs where framework_area IS NULL:
   Assign framework_area from description+name keywords
"""
import csv
import os
import sqlite3
from datetime import datetime

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
AUDIT_DIR = r'C:\Users\simon\.openclaw\workspace\commonweave\data\audit'

FRAMEWORK_KEYWORDS = {
    'healthcare': ['health','clinic','hospital','medical','medicine','nurse','doctor','hiv','aids','malaria','maternal'],
    'food': ['food','farm','agri','seed','nutrition','hunger','crop','livestock','agroecol','permaculture','harvest'],
    'education': ['education','school','learn','literacy','teach','curriculum','library','university','college','training'],
    'ecology': ['environment','ecology','conservation','climate','biodiversity','forest','ocean','watershed','rewild','wildlife','restoration'],
    'housing_land': ['housing','shelter','land trust','tenure','homeless','eviction','affordable housing','community land'],
    'democracy': ['democracy','civic','governance','participat','voting','election','transparency','accountability','human rights','civil liberties'],
    'cooperatives': ['cooperative','co-op','worker-owned','mutual','solidarity economy','credit union','social enterprise'],
    'energy_digital': ['energy','solar','wind','renewable','digital','open source','internet','data','technology'],
    'conflict': ['justice','conflict','mediation','reconciliation','peace','restorative','prison','abolition','transitional'],
    'recreation_arts': ['arts','culture','recreation','sport','music','theater','museum','heritage','creative'],
}


def assign_framework_area(name, desc):
    combined = ((name or '') + ' ' + (desc or '')).lower()
    best_area = None
    best_score = 0
    for area, keywords in FRAMEWORK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > best_score:
            best_score = score
            best_area = area
    return best_area


def export_rows_to_csv(cursor, rows, out_path):
    cursor.execute("PRAGMA table_info(organizations)")
    columns = [row[1] for row in cursor.fetchall()]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def run():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    
    # 1. Delete P2 orgs
    c.execute("SELECT * FROM organizations WHERE country_code='P2' ORDER BY id")
    p2_rows = c.fetchall()
    p2_count = len(p2_rows)
    if p2_rows:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        audit_path = os.path.join(AUDIT_DIR, f'p2_cleanup_{timestamp}.csv')
        export_rows_to_csv(c, p2_rows, audit_path)
        c.execute("""
            UPDATE organizations
            SET status='removed',
                description=TRIM(COALESCE(description, '') || ' [P2 cleanup placeholder row]')
            WHERE country_code='P2'
        """)
        db.commit()
        print(f'Exported P2 audit CSV: {audit_path}')
    print(f'Cleaned up {p2_count} P2 orgs')
    
    # 2. Assign framework_area for active web_research orgs where it's NULL
    c.execute("""
        SELECT COUNT(*) FROM organizations 
        WHERE status='active' AND source='web_research' AND framework_area IS NULL
    """)
    null_count = c.fetchone()[0]
    print(f'Active web_research orgs with NULL framework_area: {null_count}')
    
    # Process in batches
    batch_size = 5000
    last_id = 0
    total_assigned = 0
    area_counts = {}

    while True:
        c.execute("""
            SELECT id, name, description
            FROM organizations
            WHERE status='active' AND source='web_research' AND framework_area IS NULL AND id > ?
            ORDER BY id
            LIMIT ?
        """, (last_id, batch_size))
        rows = c.fetchall()
        if not rows:
            break

        updates = []
        for row in rows:
            org_id, name, desc = row
            area = assign_framework_area(name, desc)
            last_id = org_id
            if area is None:
                continue
            updates.append((area, org_id))
            area_counts[area] = area_counts.get(area, 0) + 1

        if updates:
            c.executemany("UPDATE organizations SET framework_area=? WHERE id=?", updates)
            db.commit()
            total_assigned += len(updates)
            print(f'  Assigned framework_area to {total_assigned} orgs so far...')
    
    print(f'\n=== Phase 3 Complete ===')
    print(f'P2 orgs cleaned: {p2_count}')
    print(f'framework_area assigned: {total_assigned}')
    print('\nFramework area distribution for assigned:')
    for area, cnt in sorted(area_counts.items(), key=lambda x: -x[1]):
        print(f'  {area}: {cnt}')
    
    # Final stats
    c.execute("SELECT COUNT(*) FROM organizations WHERE status='active'")
    active = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM organizations")
    total = c.fetchone()[0]
    print(f'\nDB totals: active={active:,}, total={total:,}')
    
    db.close()


if __name__ == '__main__':
    run()
