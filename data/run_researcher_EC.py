"""
ECO-66: Ecuador (EC) Regional Research
Uses web search (DuckDuckGo) to find Ecuadorian organizations.
Output: data/regional/DIRECTORY_EC.md
"""

import urllib.request
import urllib.parse
import json
import os
import time
import sys
import re
from research_evidence import validate_org_result

DATA_DIR = r"C:\Users\simon\.openclaw\workspace\ecolibrium\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "regional", "DIRECTORY_EC.md")
COUNTRY_CODE = "EC"
SKIP_AUDIT_FILE = os.path.join(DATA_DIR, "audit", f"research_skipped_{COUNTRY_CODE}.csv")

# 15-search protocol for Ecuador
SEARCHES = [
    "Ecuador ONGs directorio organizaciones sociedad civil",
    "Ecuador cooperativas organizaciones trabajadores federacion",
    "Ecuador soberania alimentaria agroecologia organizaciones campesinas",
    "Ecuador salud comunitaria organizaciones pueblos indigenas",
    "Ecuador democracia participacion ciudadana organizaciones",
    "Ecuador vivienda cooperativa tierra comunidad",
    "Ecuador energia renovable cooperativa solar comunidad",
    "Ecuador pueblos indigenas organizaciones Kichwa Shuar derechos",
    "Ecuador mujeres organizaciones cooperativa ahorro",
    "Ecuador economia solidaria mutual aid network",
    "Ecuador justicia restaurativa paz derechos humanos",
    "Ecuador tecnologia civica open source organizaciones",
    "Ecuador registro ONG MIES organizaciones base datos",
    "Ecuador educacion popular escuela comunitaria federacion",
    "Ecuador medio ambiente conservacion ecologia Amazonia Galapagos",
]

FRAMEWORK_KEYWORDS = {
    'democracy': ['civic', 'democracy', 'governance', 'community', 'citizen', 'rights', 'political', 'participation', 'democracia', 'ciudadana'],
    'cooperatives': ['cooperative', 'co-op', 'worker', 'savings', 'credit union', 'thrift', 'mutual', 'cooperativa', 'ahorro', 'credito'],
    'healthcare': ['health', 'medical', 'hospital', 'clinic', 'salud', 'medicina', 'nurse', 'materno', 'maternal'],
    'food': ['food', 'agriculture', 'farming', 'nutrition', 'hunger', 'agroecology', 'smallholder', 'alimentaria', 'campesina', 'agricola'],
    'education': ['school', 'education', 'learn', 'literacy', 'university', 'training', 'youth', 'educacion', 'escuela', 'aprendizaje'],
    'housing_land': ['housing', 'shelter', 'land', 'slum', 'urban', 'home', 'settlement', 'vivienda', 'tierra', 'terreno'],
    'conflict': ['peace', 'conflict', 'justice', 'violence', 'reconciliation', 'refugee', 'displaced', 'paz', 'justicia', 'derechos'],
    'energy_digital': ['energy', 'solar', 'electricity', 'digital', 'tech', 'internet', 'connectivity', 'energia', 'tecnologia'],
    'recreation_arts': ['arts', 'culture', 'music', 'dance', 'heritage', 'sport', 'recreation', 'arte', 'cultura', 'musica'],
    'ecology': ['environment', 'ecology', 'conservation', 'forest', 'water', 'climate', 'nature', 'ambiente', 'ecologia', 'conservacion', 'amazonia'],
}

def guess_framework(name, desc=''):
    text = (name + ' ' + desc).lower()
    best = None
    best_score = 0
    for area, kws in FRAMEWORK_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text)
        if score > best_score:
            best_score = score
            best = area
    return best or 'democracy'

def search_ddg_html(query):
    """Scrape DuckDuckGo HTML results."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html'
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        results = []
        title_pattern = re.compile(r'class="result__a"[^>]*>([^<]+)</a>', re.IGNORECASE)
        snippet_pattern = re.compile(r'class="result__snippet"[^>]*>([^<]+(?:<[^>]*>[^<]*</[^>]*>)*[^<]*)</[^>]+>', re.IGNORECASE)
        url_pattern = re.compile(r'class="result__url"[^>]*>([^<]+)</[^>]+>', re.IGNORECASE)
        
        titles = title_pattern.findall(html)
        snippets = snippet_pattern.findall(html)
        urls_found = url_pattern.findall(html)
        
        for i, title in enumerate(titles[:8]):
            snippet = snippets[i] if i < len(snippets) else ''
            url_found = urls_found[i] if i < len(urls_found) else ''
            snippet = re.sub(r'<[^>]+>', ' ', snippet).strip()
            results.append({'title': title.strip(), 'snippet': snippet, 'url': url_found.strip()})
        
        return results
    except Exception as e:
        print(f"  DDG HTML error: {e}", flush=True)
        return []

def extract_orgs_from_results(results, query):
    """Try to identify organization names from search results."""
    orgs = []
    
    for r in results:
        title = r.get('title', '') or r.get('text', '')
        snippet = r.get('snippet', '') or ''
        url = r.get('url', '')
        
        if not title or len(title) < 3:
            continue
        
        title = re.sub(r'\s+', ' ', title).strip()
        if any(x in title.lower() for x in ['wikipedia', 'facebook.com', 'twitter.com', 'pdf', 'page 1']):
            continue
        
        org_indicators = ['foundation', 'trust', 'association', 'network', 'society', 'union',
                         'institute', 'centre', 'center', 'organization', 'coalition', 'alliance',
                         'initiative', 'project', 'community', 'cooperative', 'forum', 'federation',
                         'council', 'committee', 'group', 'ngo', 'cso',
                         # Spanish terms
                         'fundacion', 'asociacion', 'red ', 'sociedad', 'sindicato', 'instituto',
                         'centro', 'organizacion', 'coalicion', 'alianza', 'iniciativa', 'proyecto',
                         'comunidad', 'cooperativa', 'foro', 'federacion', 'consejo', 'comite',
                         'colectivo', 'movimiento', 'ong ', 'corporacion', 'corporacion',]
        
        title_lower = title.lower()
        is_org = any(ind in title_lower for ind in org_indicators)
        is_ecuador = '.ec' in url.lower() or 'ecuador' in title_lower or 'ecuator' in title_lower

        if is_org or is_ecuador:
            evidence = validate_org_result(title, title, url, snippet, query, SKIP_AUDIT_FILE)
            if not evidence:
                continue
            framework = guess_framework(title, snippet)
            orgs.append({
                'name': title,
                'description': evidence['description'] or (snippet[:200] if snippet else f"Found via: {query[:80]}"),
                'website': evidence['website'],
                'framework_area': framework,
                'source': f"Web search: {query[:60]}",
                'evidence_url': evidence['evidence_url'],
                'evidence_quote': evidence['evidence_quote'],
                'evidence_fetched_at': evidence['evidence_fetched_at'],
            })
    
    return orgs

def main():
    print("ECO-66: Ecuador (EC) Regional Research", flush=True)
    os.makedirs(os.path.join(DATA_DIR, "regional"), exist_ok=True)
    
    all_orgs = []
    seen_names = set()
    
    for i, query in enumerate(SEARCHES):
        print(f"\n[{i+1}/{len(SEARCHES)}] Searching: {query[:60]}...", flush=True)
        
        results = search_ddg_html(query)
        print(f"  Got {len(results)} results", flush=True)
        
        orgs = extract_orgs_from_results(results, query)
        
        new_orgs = []
        for org in orgs:
            name_key = org['name'].lower()[:40]
            if name_key not in seen_names:
                seen_names.add(name_key)
                new_orgs.append(org)
        
        print(f"  Extracted {len(new_orgs)} new orgs", flush=True)
        all_orgs.extend(new_orgs)
        
        time.sleep(1.5)
    
    # Targeted known Ecuador org searches
    print(f"\n[Bonus] Searching known Ecuador organizations...", flush=True)
    known_resources = [
        ("CONAIE Confederacion Nacionalidades Indigenas Ecuador", "democracy"),
        ("FENOCIN Ecuador campesinos indigenas negros", "food"),
        ("Accion Ecologica Ecuador ambiental", "ecology"),
        ("CEDHU Ecuador derechos humanos", "conflict"),
        ("Coordinadora Agraria Nacional Ecuador", "food"),
        ("FLACSO Ecuador sociedad civil investigacion", "democracy"),
        ("CDES Centro Derechos Economicos Sociales Ecuador", "conflict"),
    ]
    
    for query, framework_hint in known_resources:
        results = search_ddg_html(query)
        for r in results[:3]:
            title = r.get('title', '')
            if title and len(title) > 5:
                evidence = validate_org_result(title, title, r.get('url', ''), r.get('snippet', ''), query, SKIP_AUDIT_FILE)
                if not evidence:
                    continue
                name_key = title.lower()[:40]
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    all_orgs.append({
                        'name': title,
                        'description': evidence['description'] or r.get('snippet', '')[:200],
                        'website': evidence['website'],
                        'framework_area': framework_hint,
                        'source': f"Targeted: {query[:60]}",
                        'evidence_url': evidence['evidence_url'],
                        'evidence_quote': evidence['evidence_quote'],
                        'evidence_fetched_at': evidence['evidence_fetched_at'],
                    })
        time.sleep(1)
    
    print(f"\nWriting {len(all_orgs)} organizations to {OUTPUT_FILE}", flush=True)
    
    by_area = {}
    for org in all_orgs:
        area = org['framework_area']
        if area not in by_area:
            by_area[area] = []
        by_area[area].append(org)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Ecuador (EC) -- Regional Directory\n\n")
        f.write(f"**Searches conducted:** {len(SEARCHES) + len(known_resources)}\n")
        f.write(f"**Organizations found:** {len(all_orgs)}\n")
        f.write(f"**Generated:** ECO-66 Researcher run\n\n")
        f.write(f"*Note: These orgs were found via web search and need verification. ")
        f.write(f"Most are NOT in the IRS bulk data (Ecuador is non-US). ")
        f.write(f"Quality varies -- treat as leads for human review.*\n\n")
        f.write(f"---\n\n")
        
        for area, orgs in sorted(by_area.items()):
            f.write(f"## {area.replace('_', ' ').title()} ({len(orgs)} orgs)\n\n")
            f.write(f"| Name | Description | Website | Source |\n")
            f.write(f"|---|---|---|---|\n")
            for org in orgs:
                name = org['name'].replace('|', '-')[:80]
                desc = org['description'].replace('|', '-').replace('\n', ' ')[:120]
                web = org['website'][:60] if org['website'] else ''
                src = org['source'][:40]
                f.write(f"| {name} | {desc} | {web} | {src} |\n")
            f.write(f"\n")
        
        f.write(f"---\n\n")
        f.write(f"## Coverage Assessment\n\n")
        f.write(f"- IRS BMF records for EC: 0 (expected -- US-only database)\n")
        f.write(f"- This research adds: {len(all_orgs)} Ecuadorian organizations\n")
        f.write(f"- Framework coverage: {', '.join(f'{a}({len(o)})' for a,o in by_area.items())}\n")
        f.write(f"- Recommended follow-up: Contact MIES registry, CONAIE for indigenous org directory\n")
    
    print(f"\nECO-66 COMPLETE", flush=True)
    print(f"Total orgs: {len(all_orgs)}", flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)
    
    return len(all_orgs)

if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
