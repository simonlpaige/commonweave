"""
build_edges.py: produce data/map/edges.json from the directory database plus
two curated files:
  - data/federations.yaml      (federation hub -> member rules)
  - data/relationships.csv     (manual verified pair-wise partnerships)

Edge types emitted:
  - same_section_proximity        (derived, existing rule)
  - cross_section_complementarity (derived, existing rule)
  - federation_membership         (curated, from federations.yaml)
  - verified_relationship         (curated, from relationships.csv)

Score formula (edge weight, 0..1):
    edge_score =
        0.30 * section_similarity
      + 0.25 * geographic_proximity
      + 0.20 * complementary_function
      + 0.15 * data_quality
      + 0.10 * shared_resources_or_keywords

Suppress derived edges below 0.55 unless --weak is passed (for the "show weak
links" toggle on the front end). Curated edges always pass through.

Outputs data/map/edges.json (list, with id/source_id/target_id/edge_type/
weight/confidence/derived/explanation/created_at/source_script/evidence).
"""
import argparse
import csv
import json
import math
import os
import sqlite3
import sys
from collections import defaultdict, Counter
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, 'data', 'commonweave_directory.db')
MAP_DIR = os.path.join(ROOT, 'data', 'map')
FEDERATIONS_YAML = os.path.join(ROOT, 'data', 'federations.yaml')
RELATIONSHIPS_CSV = os.path.join(ROOT, 'data', 'relationships.csv')

SECTIONS = [
    'democracy', 'cooperatives', 'healthcare', 'food', 'education',
    'housing_land', 'conflict', 'energy_digital', 'recreation_arts', 'ecology'
]

COMPLEMENTARY = {
    ('food', 'housing_land'), ('food', 'cooperatives'), ('food', 'ecology'),
    ('housing_land', 'cooperatives'), ('housing_land', 'democracy'),
    ('healthcare', 'education'), ('healthcare', 'conflict'),
    ('energy_digital', 'cooperatives'), ('energy_digital', 'democracy'),
    ('education', 'democracy'), ('ecology', 'food'),
}

MAX_PROX_KM = 50
MAX_EDGES_PER_ORG = 5
WEAK_LINK_FLOOR = 0.62


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def confidence_band(w):
    if w >= 0.66:
        return 'high'
    if w >= 0.33:
        return 'medium'
    return 'low'


def load_orgs(db):
    """Pull every Tier A/B/C geocoded org. Edges only ever live between these.

    Returns a dict: org_id -> { 'id', 'lat', 'lon', 'f' (section), 't' (tier),
    'name', 'cc' }.
    """
    c = db.cursor()
    c.execute("""
        SELECT id, name, lat, lon, framework_area, country_code, quality_tier
        FROM organizations
        WHERE status='active' AND lat IS NOT NULL AND lon IS NOT NULL
          AND quality_tier IN ('tier_a', 'tier_b', 'tier_c')
    """)
    orgs = {}
    for org_id, name, lat, lon, area, cc, tier in c.fetchall():
        orgs[org_id] = {
            'id': f'org_{org_id}',
            '_db_id': org_id,
            'name': name or '',
            'lat': lat,
            'lon': lon,
            'f': area or 'democracy',
            'cc': cc or '',
            't': (tier or 'tier_d').replace('tier_', '').upper(),
        }
    return orgs


def score_derived(p1, p2, dist_km):
    """Compute the brief's weighted score in [0,1].

    Phase 2 uses a simplified shared_resources signal: 1.0 if same country,
    0.4 otherwise. Real keyword/resource overlap is a Phase 3+ refinement.
    """
    same_section = p1['f'] == p2['f']
    complementary = (p1['f'], p2['f']) in COMPLEMENTARY or (p2['f'], p1['f']) in COMPLEMENTARY

    section_similarity = 1.0 if same_section else (0.5 if complementary else 0.0)
    geographic_proximity = max(0.0, 1.0 - (dist_km / MAX_PROX_KM)) if dist_km <= MAX_PROX_KM else 0.0
    complementary_function = 1.0 if complementary else (0.0 if same_section else 0.0)
    # Data quality: A=1.0, B=0.7, C=0.4. Use the lower of the two endpoints so
    # one strong + one weak does not get a free pass.
    quality_map = {'A': 1.0, 'B': 0.7, 'C': 0.4}
    data_quality = min(quality_map.get(p1['t'], 0.4), quality_map.get(p2['t'], 0.4))
    shared_resources_or_keywords = 1.0 if p1['cc'] and p1['cc'] == p2['cc'] else 0.4

    score = (
        0.30 * section_similarity
        + 0.25 * geographic_proximity
        + 0.20 * complementary_function
        + 0.15 * data_quality
        + 0.10 * shared_resources_or_keywords
    )
    return round(min(score, 1.0), 4)


def build_proximity_edges(orgs, weak=False):
    """Same-section + complementary proximity edges with the new score."""
    today_iso = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    points = list(orgs.values())

    CELL = 0.5  # ~50km cells
    grid = defaultdict(list)
    for p in points:
        cell = (int(p['lat'] / CELL), int(p['lon'] / CELL))
        grid[cell].append(p)

    edges = []
    edge_count = defaultdict(int)
    seen = set()

    for cell, cell_points in grid.items():
        neighbours = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbours.extend(grid.get((cell[0] + dx, cell[1] + dy), []))
        for p1 in cell_points:
            if edge_count[p1['_db_id']] >= MAX_EDGES_PER_ORG:
                continue
            cands = []
            for p2 in neighbours:
                if p1['_db_id'] >= p2['_db_id']:
                    continue
                key = (p1['_db_id'], p2['_db_id'])
                if key in seen:
                    continue
                same_section = p1['f'] == p2['f']
                complementary = (p1['f'], p2['f']) in COMPLEMENTARY or (p2['f'], p1['f']) in COMPLEMENTARY
                if not same_section and not complementary:
                    continue
                dist = haversine_km(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
                if dist > MAX_PROX_KM or dist < 0.5:
                    continue
                score = score_derived(p1, p2, dist)
                if not weak and score < WEAK_LINK_FLOOR:
                    continue
                cands.append((dist, score, p2, same_section, key))
            cands.sort(key=lambda x: -x[1])  # highest score first
            for dist, score, p2, same_section, key in cands[:MAX_EDGES_PER_ORG]:
                if edge_count[p1['_db_id']] >= MAX_EDGES_PER_ORG:
                    break
                if edge_count[p2['_db_id']] >= MAX_EDGES_PER_ORG:
                    continue
                edge_type = 'same_section_proximity' if same_section else 'cross_section_complementarity'
                if same_section:
                    explanation = (
                        f"Both work on {p1['f'].replace('_', ' ')} and are within "
                        f"{round(dist, 1)} km of each other."
                    )
                else:
                    explanation = (
                        f"Complementary work ({p1['f'].replace('_', ' ')} + "
                        f"{p2['f'].replace('_', ' ')}) within {round(dist, 1)} km."
                    )
                a, b = sorted([p1['_db_id'], p2['_db_id']])
                edges.append({
                    'id': f'edge_org_{a}_org_{b}',
                    'source_id': p1['id'],
                    'target_id': p2['id'],
                    'edge_type': edge_type,
                    'weight': score,
                    'confidence': confidence_band(score),
                    'derived': True,
                    'explanation': explanation,
                    'created_at': today_iso,
                    'source_script': 'data/build_edges.py',
                    'evidence': [{'type': 'inference', 'value': f'distance={round(dist, 1)}km'}],
                    'f': p1['f'],
                })
                seen.add(key)
                edge_count[p1['_db_id']] += 1
                edge_count[p2['_db_id']] += 1
    return edges


def build_federation_edges(orgs, db):
    """Read federations.yaml and emit federation_membership edges from each
    member org to the hub. Skips federations whose hub is not geocoded.
    """
    if not os.path.exists(FEDERATIONS_YAML):
        print(f"  federations.yaml missing, skipping federation edges")
        return []
    with open(FEDERATIONS_YAML, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    today_iso = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    edges = []
    c = db.cursor()
    for fed in cfg.get('federations', []):
        hub_id = fed.get('hub_id')
        if hub_id not in orgs:
            print(f"  skipping {fed.get('name')}: hub org_{hub_id} not geocoded / not Tier A/B/C")
            continue
        hub = orgs[hub_id]
        members = fed.get('members') or {}
        member_ids = set()
        if 'from_source' in members:
            src = members['from_source']
            c.execute("""SELECT id FROM organizations
                         WHERE source = ? AND status='active'
                           AND lat IS NOT NULL AND lon IS NOT NULL
                           AND quality_tier IN ('tier_a','tier_b','tier_c')""", (src,))
            for (mid,) in c.fetchall():
                if mid != hub_id and mid in orgs:
                    member_ids.add(mid)
        for mid in members.get('member_ids', []) or []:
            if mid != hub_id and mid in orgs:
                member_ids.add(mid)

        for mid in member_ids:
            m = orgs[mid]
            a, b = sorted([hub_id, mid])
            edge_id = f'edge_fed_{a}_{b}'
            explanation = (
                f"{m['name']} is listed as a member of {fed.get('short') or fed.get('name')}."
            )
            edges.append({
                'id': edge_id,
                'source_id': m['id'],
                'target_id': hub['id'],
                'edge_type': 'federation_membership',
                'weight': 0.9,
                'confidence': 'high',
                'derived': False,
                'explanation': explanation,
                'created_at': today_iso,
                'source_script': 'data/build_edges.py (federations.yaml)',
                'evidence': [
                    {'type': 'registry', 'value': fed.get('source_url', fed.get('name', ''))},
                ],
                'f': hub['f'],
                'federation': fed.get('short') or fed.get('name'),
            })
        print(f"  {fed.get('short') or fed.get('name')}: {len(member_ids)} federation_membership edges")
    return edges


def build_verified_edges(orgs):
    """Read relationships.csv and emit verified_relationship edges. Both
    endpoints must be in the orgs dict (geocoded + Tier A/B/C); rows that
    reference an off-map org are skipped with a warning.
    """
    if not os.path.exists(RELATIONSHIPS_CSV):
        print(f"  relationships.csv missing, skipping verified edges")
        return []
    today_iso = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    edges = []
    skipped = 0
    with open(RELATIONSHIPS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sid = int(row['source_id'].replace('org_', ''))
                tid = int(row['target_id'].replace('org_', ''))
            except (ValueError, KeyError):
                skipped += 1
                continue
            if sid not in orgs or tid not in orgs:
                skipped += 1
                continue
            s = orgs[sid]
            t = orgs[tid]
            edges.append({
                'id': row.get('id') or f'edge_rel_{min(sid, tid)}_{max(sid, tid)}',
                'source_id': s['id'],
                'target_id': t['id'],
                'edge_type': 'verified_relationship',
                'weight': 0.95,
                'confidence': 'high',
                'derived': False,
                'explanation': row.get('description') or 'Verified partnership.',
                'created_at': today_iso,
                'source_script': 'data/build_edges.py (relationships.csv)',
                'evidence': [{'type': 'url', 'value': row.get('source_url', '')}],
                'f': s['f'],
                'relationship_type': row.get('relationship_type', ''),
            })
    print(f"  verified_relationship: {len(edges)} edges (skipped {skipped} off-map rows)")
    return edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weak', action='store_true', help='Include derived edges with score < 0.55')
    parser.add_argument('--out', default=os.path.join(MAP_DIR, 'edges.json'))
    parser.add_argument('--legacy-out', default='',
                        help='Optional: also write a legacy compact edges file. Empty disables.')
    args = parser.parse_args()

    os.makedirs(MAP_DIR, exist_ok=True)

    print(f"Loading orgs from {DB_PATH}...")
    db = sqlite3.connect(DB_PATH)
    orgs = load_orgs(db)
    print(f"  {len(orgs):,} geocoded Tier A/B/C orgs")

    print("\nBuilding federation_membership edges...")
    fed_edges = build_federation_edges(orgs, db)

    print("\nBuilding verified_relationship edges...")
    verified_edges = build_verified_edges(orgs)

    print("\nBuilding proximity edges (derived)...")
    prox_edges = build_proximity_edges(orgs, weak=args.weak)
    print(f"  {len(prox_edges):,} proximity edges (after >= {WEAK_LINK_FLOOR} score floor)" if not args.weak else f"  {len(prox_edges):,} proximity edges (no score floor)")

    db.close()

    # Curated first, derived after. Front-end can keep this order or rerank.
    all_edges = verified_edges + fed_edges + prox_edges

    # De-dup by id (curated edges win over derived if both exist for a pair).
    seen_ids = set()
    deduped = []
    for e in all_edges:
        if e['id'] in seen_ids:
            continue
        seen_ids.add(e['id'])
        deduped.append(e)

    counts = Counter(e['edge_type'] for e in deduped)
    print(f"\nTotal: {len(deduped):,} edges")
    for k, v in counts.most_common():
        print(f"  {k}: {v:,}")

    # Strip the internal _db_id from sources before writing
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(deduped, f, separators=(',', ':'))
    print(f"\nWrote {args.out} ({os.path.getsize(args.out) / 1024:.1f} KB)")

    # Legacy alias for the existing renderer in case anything still reads it.
    if args.legacy_out:
        os.makedirs(os.path.dirname(args.legacy_out), exist_ok=True)
        with open(args.legacy_out, 'w', encoding='utf-8') as f:
            json.dump(deduped, f, separators=(',', ':'))
        print(f"Wrote legacy alias {args.legacy_out}")

    # Patch stats.json so the public-facing edges_total reflects this run.
    stats_path = os.path.join(MAP_DIR, 'stats.json')
    if os.path.exists(stats_path):
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        stats['edges_total'] = len(deduped)
        stats['edges_by_type'] = dict(counts)
        stats['edges_built_by'] = 'data/build_edges.py'
        stats['edges_built_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"Patched edge counts into {stats_path}")


if __name__ == '__main__':
    main()
