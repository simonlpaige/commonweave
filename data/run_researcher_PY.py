"""
ECO-67: Paraguay (PY) Regional Research
Uses DuckDuckGo to find Paraguayan organizations.
Output: data/regional/DIRECTORY_PY.md
"""

import urllib.request
import urllib.parse
import json
import os
import time
import sys
import re

DATA_DIR = r"C:\Users\simon\.openclaw\workspace\ecolibrium\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "regional", "DIRECTORY_PY.md")

# 15-search protocol for Paraguay
SEARCHES = [
    "Paraguay organizaciones sociedad civil directorio ONG",
    "Paraguay cooperativas federacion nacional trabajadores",
    "Paraguay soberania alimentaria agroecologia organizaciones campesinas",
    "Paraguay salud comunitaria organizaciones atencion primaria",
    "Paraguay democracia participacion ciudadana organizaciones",
    "Paraguay vivienda cooperativa tierra comunidad",
    "Paraguay energia renovable solar comunitaria cooperativa",
    "Paraguay pueblos indigenas organizaciones derechos Guarani",
    "Paraguay organizaciones mujeres cooperativa ahorro grupo",
    "Paraguay ayuda mutua red economia solidaria",
    "Paraguay justicia restaurativa construccion paz organizaciones",
    "Paraguay tecnologia civica software libre organizaciones",
    "Paraguay registro ONGs directorio organizaciones sin fines de lucro",
    "Paraguay educacion comunitaria escuela federacion",
    "Paraguay medio ambiente ecologia conservacion organizaciones",
]

FRAMEWORK_KEYWORDS = {
    'democracy': ['civic', 'democracy', 'democracia', 'governance', 'community', 'citizen', 'rights', 'political', 'ciudadana', 'participacion'],
    'cooperatives': ['cooperative', 'cooperativa', 'co-op', 'worker', 'savings', 'credit union', 'credito', 'ahorro', 'mutual'],
    'healthcare': ['health', 'salud', 'medical', 'hospital', 'clinic', 'maternal', 'nurse', 'enfermera'],
    'food': ['food', 'alimento', 'agricultura', 'farming', 'campesina', 'nutrition', 'hunger', 'agroecology', 'agroecologia', 'smallholder'],
    'education': ['school', 'escuela', 'education', 'educacion', 'learn', 'literacy', 'university', 'universidad', 'training', 'youth', 'juventud'],
    'housing_land': ['housing', 'vivienda', 'shelter', 'land', 'tierra', 'slum', 'urban', 'home', 'settlement'],
    'conflict': ['peace', 'paz', 'conflict', 'justicia', 'justice', 'violence', 'reconciliation', 'refugee', 'displaced'],
    'energy_digital': ['energy', 'energia', 'solar', 'electricity', 'electricidad', 'digital', 'tech', 'internet', 'connectivity'],
    'recreation_arts': ['arts', 'cultura', 'culture', 'music', 'musica', 'dance', 'heritage', 'sport', 'deporte', 'recreation'],
    'ecology': ['environment', 'ambiente', 'ecology', 'ecologia', 'conservation', 'conservacion', 'forest', 'bosque', 'water', 'agua', 'climate', 'naturaleza'],
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

def search_web_api(query):
    """DuckDuckGo instant answers API fallback."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&skip_disambig=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            if data.get('Abstract'):
                results.append({'title': data.get('Heading', 'Result'), 'snippet': data['Abstract'], 'url': data.get('AbstractURL', '')})
            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({'title': topic.get('Text', '')[:60], 'snippet': topic['Text'], 'url': topic.get('FirstURL', '')})
            return results
    except Exception as e:
        print(f"  API error: {e}", flush=True)
        return []

def extract_orgs_from_results(results, query):
    orgs = []
    
    for r in results:
        title = r.get('title', '') or ''
        snippet = r.get('snippet', '') or ''
        url = r.get('url', '')
        
        if not title or len(title) < 3:
            continue
        
        title = re.sub(r'\s+', ' ', title).strip()
        if any(x in title.lower() for x in ['wikipedia', 'facebook.com', 'twitter.com', 'pdf', 'page 1', 'youtube']):
            continue
        
        org_indicators = ['fundacion', 'fundación', 'asociacion', 'asociación', 'foundation', 'trust',
                         'association', 'network', 'red', 'society', 'union', 'sindicato',
                         'institute', 'instituto', 'centre', 'center', 'centro', 'organization',
                         'organizacion', 'organización', 'coalition', 'alliance', 'alianza',
                         'initiative', 'iniciativa', 'project', 'proyecto', 'community', 'comunidad',
                         'cooperative', 'cooperativa', 'forum', 'foro', 'federation', 'federacion',
                         'federación', 'council', 'consejo', 'committee', 'comite', 'comité',
                         'group', 'grupo', 'ngo', 'ong', 'cso', 'movimiento', 'movement']
        
        title_lower = title.lower()
        is_org = any(ind in title_lower for ind in org_indicators)
        is_py = '.py' in url.lower() or 'paraguay' in title_lower or 'paraguayo' in title_lower or 'paraguaya' in title_lower
        
        if is_org or is_py:
            framework = guess_framework(title, snippet)
            orgs.append({
                'name': title,
                'description': snippet[:200] if snippet else f"Found via: {query[:80]}",
                'website': url if url.startswith('http') else '',
                'framework_area': framework,
                'source': f"Web search: {query[:60]}"
            })
    
    return orgs

def main():
    print("ECO-67: Paraguay (PY) Regional Research", flush=True)
    os.makedirs(os.path.join(DATA_DIR, "regional"), exist_ok=True)
    
    all_orgs = []
    seen_names = set()
    
    for i, query in enumerate(SEARCHES):
        print(f"\n[{i+1}/{len(SEARCHES)}] Searching: {query[:60]}...", flush=True)
        
        results = search_ddg_html(query)
        print(f"  Got {len(results)} results", flush=True)
        
        if not results:
            results = search_web_api(query)
            print(f"  Fallback: {len(results)} results", flush=True)
        
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
    
    # Targeted searches for known Paraguayan organizations
    print(f"\n[Bonus] Targeted Paraguay org searches...", flush=True)
    targeted = [
        ("Decidamos Paraguay democracia ciudadana", "democracy"),
        ("CODEHUPY derechos humanos Paraguay", "democracy"),
        ("Coordinadora de Mujeres del Paraguay CMP", "democracy"),
        ("SEDUPO educacion popular Paraguay", "education"),
        ("BASE Investigaciones Sociales Paraguay", "democracy"),
        ("Federacion Nacional de Cooperativas Paraguay FENACOOP", "cooperatives"),
        ("Alter Vida Paraguay agroecologia ecologia", "ecology"),
        ("Tekojoja Paraguay movimiento campesino", "food"),
    ]
    
    for query, framework_hint in targeted:
        results = search_ddg_html(query)
        for r in results[:3]:
            title = r.get('title', '')
            if title and len(title) > 5:
                name_key = title.lower()[:40]
                if name_key not in seen_names:
                    seen_names.add(name_key)
                    all_orgs.append({
                        'name': title,
                        'description': r.get('snippet', '')[:200],
                        'website': r.get('url', ''),
                        'framework_area': framework_hint,
                        'source': f"Targeted: {query[:60]}"
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
        f.write(f"# Paraguay (PY) -- Regional Directory\n\n")
        f.write(f"**Searches conducted:** {len(SEARCHES) + len(targeted)}\n")
        f.write(f"**Organizations found:** {len(all_orgs)}\n")
        f.write(f"**Generated:** ECO-67 Researcher run\n\n")
        f.write(f"*Note: These orgs were found via web search and need verification. ")
        f.write(f"Most are NOT in the IRS bulk data (Paraguay is non-US). ")
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
        f.write(f"- IRS BMF records for PY: 0 (expected -- US-only database)\n")
        f.write(f"- This research adds: {len(all_orgs)} Paraguayan organizations\n")
        f.write(f"- Framework coverage: {', '.join(f'{a}({len(o)})' for a,o in sorted(by_area.items()))}\n")
        f.write(f"- Recommended follow-up: Contact Decidamos, CODEHUPY, FENACOOP for formal registries\n")
    
    print(f"\nECO-67 COMPLETE", flush=True)
    print(f"Total orgs: {len(all_orgs)}", flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)
    
    return len(all_orgs)

if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
