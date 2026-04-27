"""
gen-audit-data.py -- Generate a clean audit JSON for the web portal.
Usage: python tools/gen-audit-data.py --region usa --n 50 --out audit/usa.json
       python tools/gen-audit-data.py --region india --n 50
       python tools/gen-audit-data.py --region latam --n 60 --stratified
"""
import sqlite3, json, os, sys, argparse, random

DB   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'commonweave_directory.db')
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'audit')

SPANISH = ['MX','CO','AR','CL','PE','VE','EC','BO','PY','UY','DO','GT','HN','SV','NI','CR','PA','CU','ES','PR']

SOURCE_LABELS = {
    'mapa_oscs_brazil': 'Mapa das OSCs (Brazil)',
    'acnc_charity_register': 'ACNC (Australia)',
    'uk_charity_commission': 'UK Charity Commission',
    'IRS_EO_BMF': 'IRS EO BMF (USA)',
    'mutual_aid_wiki': 'Mutual Aid Wiki',
    'wikidata': 'Wikidata',
    'wikidata_bg_npo': 'Wikidata (Bulgaria)',
    'ic_directory': 'Intentional Communities Directory',
    'transition_network': 'Transition Network',
    'mutual_aid_hub': 'Mutual Aid Hub',
    'susy_map': 'SUSY Map',
    'ProPublica': 'ProPublica',
    'wikidata_subregion': 'Wikidata (subregion)',
    'wikidata_land_trusts': 'Wikidata (land trusts)',
    'clt_world_map': 'CLT World Map',
    'wikidata_unions': 'Wikidata (labor unions)',
    'ica_directory': 'ICA Member Directory',
    'ituc_affiliates': 'ITUC Affiliates',
    'nec_members': 'New Economy Coalition',
    'construction_coops': 'Construction Cooperatives',
    'ripess_family': 'RIPESS Network',
    'habitat_affiliates': 'Habitat for Humanity',
    'web_research': 'Web Research',
    'grounded_solutions': 'Grounded Solutions',
    'manual_curation': 'Manual Curation',
}

SECTION_LABELS = {
    'healthcare': 'Healthcare',
    'education': 'Education',
    'food': 'Food Sovereignty',
    'democracy': 'Democratic Infrastructure',
    'housing_land': 'Land & Housing',
    'ecology': 'Ecological Restoration',
    'conflict': 'Conflict Resolution',
    'cooperatives': 'Cooperatives & Solidarity',
    'recreation_arts': 'Recreation & Arts',
    'energy_digital': 'Energy & Digital Commons',
}

ALL_SECTIONS = list(SECTION_LABELS.keys())

parser = argparse.ArgumentParser()
parser.add_argument('--region', default='usa', choices=['usa','india','latam'])
parser.add_argument('--n', type=int, default=50)
parser.add_argument('--stratified', action='store_true')
parser.add_argument('--out', default=None)
args = parser.parse_args()

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

if args.region == 'usa':
    cc_list = ['US']
    label = 'USA'
elif args.region == 'india':
    cc_list = ['IN']
    label = 'India'
else:
    cc_list = SPANISH
    label = 'Spanish-Speaking Countries'

ph = ','.join(['?'] * len(cc_list))

if args.stratified and len(cc_list) > 1:
    orgs = []
    per_country = max(2, args.n // len(cc_list))
    for cc in cc_list:
        c.execute(f"""SELECT id, name, country_code, state_province, city, source,
                             framework_area, alignment_score, description, website,
                             registration_id, legibility, model_type, tags, email, phone
                      FROM organizations WHERE status='active' AND country_code=?
                      ORDER BY RANDOM() LIMIT ?""", [cc, per_country])
        orgs.extend([dict(r) for r in c.fetchall()])
    random.shuffle(orgs)
    orgs = orgs[:args.n]
else:
    c.execute(f"""SELECT id, name, country_code, state_province, city, source,
                         framework_area, alignment_score, description, website,
                         registration_id, legibility, model_type, tags, email, phone
                  FROM organizations WHERE status='active' AND country_code IN ({ph})
                  ORDER BY RANDOM() LIMIT ?""", cc_list + [args.n])
    orgs = [dict(r) for r in c.fetchall()]

conn.close()

# Enrich for portal display
for o in orgs:
    o['source_label'] = SOURCE_LABELS.get(o.get('source') or '', o.get('source') or '')
    o['section_label'] = SECTION_LABELS.get(o.get('framework_area') or '', o.get('framework_area') or '')
    o['tags_list'] = [t.strip() for t in (o.get('tags') or '').split(',') if t.strip()]

out_path = args.out or os.path.join(OUT_DIR, f'{args.region}.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)

payload = {
    'region': args.region,
    'label': label,
    'generated': '2026-04-27',
    'total': len(orgs),
    'sections': SECTION_LABELS,
    'orgs': orgs,
}

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)

print(f'Written {len(orgs)} orgs to {out_path}')
