"""
ECO-65: Bolivia (BO) Regional Research
Uses web search (DuckDuckGo) to find Bolivian organizations.
Output: data/regional/DIRECTORY_BO.md
"""

import urllib.request
import urllib.parse
import json
import os
import time
import sys
import re
from research_evidence import validate_org_result

DATA_DIR = r"C:\Users\simon\.openclaw\workspace\commonweave\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "regional", "DIRECTORY_BO.md")
COUNTRY_CODE = "BO"
SKIP_AUDIT_FILE = os.path.join(DATA_DIR, "audit", f"research_skipped_{COUNTRY_CODE}.csv")

# 15-search protocol for Bolivia
SEARCHES = [
    "Bolivia organizaciones sociedad civil ONG directorio",
    "Bolivia cooperativas federacion nacional trabajadores",
    "Bolivia soberania alimentaria agroecologia organizaciones campesinas",
    "Bolivia salud comunitaria organizaciones salud indigena",
    "Bolivia gobernanza democratica participacion ciudadana organizaciones",
    "Bolivia vivienda cooperativa tierra comunidad",
    "Bolivia energia renovable solar comunidad cooperativa",
    "Bolivia pueblos indigenas organizaciones derechos CIDOB CONAMAQ",
    "Bolivia mujeres organizaciones cooperativa ayuda mutua",
    "Bolivia economia solidaria redes mutualismo",
    "Bolivia justicia restaurativa paz reconciliacion organizaciones",
    "Bolivia tecnologia civica codigo abierto organizaciones",
    "Bolivia registro ONGs SEPREC fundaciones sociedad civil",
    "Bolivia educacion grassroots escuela comunitaria federacion",
    "Bolivia medio ambiente ecologia conservacion organizaciones",
]

FRAMEWORK_KEYWORDS = {
    'democracy': ['civic', 'democracy', 'governance', 'community', 'citizen', 'rights', 'political', 'vote', 'democratica', 'ciudadana'],
    'cooperatives': ['cooperative', 'co-op', 'worker', 'savings', 'credit union', 'thrift', 'mutual', 'cooperativa', 'federacion'],
    'healthcare': ['health', 'medical', 'hospital', 'clinic', 'salud', 'maternal', 'nurse', 'medicina'],
    'food': ['food', 'agriculture', 'farming', 'nutrition', 'hunger', 'agroecology', 'smallholder', 'alimentaria', 'campesina', 'agraria'],
    'education': ['school', 'education', 'learn', 'literacy', 'university', 'training', 'youth', 'educacion', 'escuela'],
    'housing_land': ['housing', 'shelter', 'land', 'slum', 'urban', 'home', 'settlement', 'vivienda', 'tierra'],
    'conflict': ['peace', 'conflict', 'justice', 'violence', 'reconciliation', 'refugee', 'displaced', 'paz', 'justicia'],
    'energy_digital': ['energy', 'solar', 'electricity', 'digital', 'tech', 'internet', 'connectivity', 'energia', 'tecnologia'],
    'recreation_arts': ['arts', 'culture', 'music', 'dance', 'heritage', 'sport', 'recreation', 'cultura', 'arte'],
    'ecology': ['environment', 'ecology', 'conservation', 'forest', 'water', 'climate', 'nature', 'medio ambiente', 'ecologia', 'conservacion'],
    'indigenous': ['indigenous', 'indigena', 'native', 'originario', 'originaria', 'pueblo', 'CIDOB', 'CONAMAQ'],
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

def search_ddg_api(query):
    """Use DuckDuckGo instant answers API as fallback."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&skip_disambig=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            if data.get('Abstract'):
                results.append({'title': data.get('Heading', query), 'snippet': data['Abstract'], 'url': data.get('AbstractURL', '')})
            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({'title': topic['Text'][:80], 'snippet': topic['Text'], 'url': topic.get('FirstURL', '')})
            return results
    except Exception as e:
        print(f"  DDG API error: {e}", flush=True)
        return []

def extract_orgs_from_results(results, query):
    """Try to identify organization names from search results."""
    orgs = []
    seen_local = set()
    
    for r in results:
        title = r.get('title', '') or ''
        snippet = r.get('snippet', '') or ''
        url = r.get('url', '')
        
        if not title or len(title) < 3:
            continue
        
        title = re.sub(r'\s+', ' ', title).strip()
        if any(x in title.lower() for x in ['wikipedia', 'facebook.com', 'twitter.com', 'pdf', 'page 1', 'youtube']):
            continue
        
        org_indicators = ['foundation', 'trust', 'association', 'network', 'society', 'union',
                         'institute', 'centre', 'center', 'organization', 'coalition', 'alliance',
                         'initiative', 'project', 'community', 'cooperative', 'cooperative',
                         'forum', 'federation', 'council', 'committee', 'group', 'ngo', 'cso',
                         # Spanish indicators
                         'fundacion', 'asociacion', 'red ', 'sociedad', 'union', 'instituto',
                         'centro', 'organizacion', 'coalicion', 'alianza', 'iniciativa',
                         'proyecto', 'comunidad', 'cooperativa', 'foro', 'federacion',
                         'consejo', 'comite', 'grupo', 'movimiento', 'coordinadora']
        
        title_lower = title.lower()
        is_org = any(ind in title_lower for ind in org_indicators)
        is_bolivia = '.bo' in url.lower() or 'bolivia' in title_lower or 'bolivian' in title_lower or 'boliviano' in title_lower
        
        name_key = title.lower()[:40]
        if (is_org or is_bolivia) and name_key not in seen_local:
            evidence = validate_org_result(title, title, url, snippet, query, SKIP_AUDIT_FILE)
            if not evidence:
                continue
            seen_local.add(name_key)
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
    print("ECO-65: Bolivia (BO) Regional Research", flush=True)
    os.makedirs(os.path.join(DATA_DIR, "regional"), exist_ok=True)
    
    all_orgs = []
    seen_names = set()
    
    for i, query in enumerate(SEARCHES):
        print(f"\n[{i+1}/{len(SEARCHES)}] Searching: {query[:70]}...", flush=True)
        
        results = search_ddg_html(query)
        print(f"  Got {len(results)} results", flush=True)
        
        if not results:
            results = search_ddg_api(query)
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
    
    # Targeted searches for known Bolivian orgs/networks
    print(f"\n[Bonus] Targeted searches...", flush=True)
    targeted = [
        ("CIDOB Bolivia Confederacion indigenas orientales", "indigenous"),
        ("CONAMAQ Bolivia Consejo Nacional Ayllus Markas Qullasuyu", "indigenous"),
        ("CSUTCB Bolivia Confederacion Sindical Unica Trabajadores Campesinos", "food"),
        ("CNMCIOB Bartolina Sisa Bolivia mujeres campesinas", "food"),
        ("CONAMAQ CIDOB Pacto Unidad Bolivia organizaciones indigenas", "indigenous"),
        ("Bolivia redes economia solidaria mercados comunitarios", "cooperatives"),
        ("Fundacion Tierra Bolivia derechos tierra campesinos", "housing_land"),
        ("CEDIB Bolivia informacion documentacion organizaciones", "democracy"),
    ]
    
    for query, framework_hint in targeted:
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
        f.write(f"# Bolivia (BO) -- Regional Directory\n\n")
        f.write(f"**Searches conducted:** {len(SEARCHES) + len(targeted)}\n")
        f.write(f"**Organizations found:** {len(all_orgs)}\n")
        f.write(f"**Generated:** ECO-65 Researcher run\n\n")
        f.write(f"*Note: These orgs were found via web search and need verification. ")
        f.write(f"Bolivia has rich indigenous and campesino organizational traditions ")
        f.write(f"that are underrepresented in English-language databases. ")
        f.write(f"Treat as leads for human review.*\n\n")
        f.write(f"---\n\n")
        
        for area, orgs in sorted(by_area.items()):
            f.write(f"## {area.replace('_', ' ').title()} ({len(orgs)} orgs)\n\n")
            f.write(f"| Name | Location | Framework Area | Description | Website | Source |\n")
            f.write(f"|---|---|---|---|---|---|\n")
            for org in orgs:
                name = org['name'].replace('|', '-')[:80]
                desc = org['description'].replace('|', '-').replace('\n', ' ')[:120]
                web = org['website'][:60] if org['website'] else ''
                src = org['source'][:40]
                f.write(f"| {name} | Bolivia | {area} | {desc} | {web} | {src} |\n")
            f.write(f"\n")
        
        f.write(f"---\n\n")
        f.write(f"## Coverage Assessment\n\n")
        f.write(f"- IRS BMF records for BO: 0 (US-only database)\n")
        f.write(f"- This research adds: {len(all_orgs)} Bolivian organizations\n")
        f.write(f"- Framework coverage: {', '.join(f'{a}({len(o)})' for a,o in sorted(by_area.items()))}\n")
        f.write(f"- Key gaps: Informal mutual aid networks, rural community organizations, sub-national grassroots\n")
        f.write(f"- Recommended follow-up: Contact SEPREC registry, CEDIB documentation center\n")
    
    print(f"\nECO-65 COMPLETE", flush=True)
    print(f"Total orgs: {len(all_orgs)}", flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)
    
    return len(all_orgs)

if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
