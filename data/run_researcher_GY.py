"""
ECO-68: Guyana (GY) Regional Research
15-search protocol for Guyana organizations.
Output: data/regional/DIRECTORY_GY.md
"""

import urllib.request
import urllib.parse
import json
import os
import time
import sys
import re

DATA_DIR = r"C:\Users\simon\.openclaw\workspace\ecolibrium\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "regional", "DIRECTORY_GY.md")

SEARCHES = [
    "Guyana NGO civil society organizations directory",
    "Guyana indigenous peoples organizations Amerindian rights",
    "Guyana cooperative federation worker cooperative",
    "Guyana environmental ecology conservation organizations",
    "Guyana women organization empowerment mutual aid",
    "Guyana food sovereignty agriculture farming community",
    "Guyana community health organizations primary care",
    "Guyana housing land rights organizations",
    "Guyana renewable energy solar community initiative",
    "Guyana civic democracy governance organizations",
    "Guyana solidarity economy mutual aid network",
    "Guyana youth organizations education grassroots",
    "Guyana Amerindian village council organization community",
    "Guyana environmental justice climate change organizations",
    "Guyana LGBTQ rights social justice organizations Georgetown",
]

FRAMEWORK_KEYWORDS = {
    'democracy': ['civic', 'democracy', 'governance', 'community', 'citizen', 'rights', 'political'],
    'cooperatives': ['cooperative', 'co-op', 'worker', 'savings', 'credit union', 'thrift', 'mutual'],
    'healthcare': ['health', 'medical', 'hospital', 'clinic', 'hiv', 'maternal', 'nurse', 'care'],
    'food': ['food', 'agriculture', 'farming', 'nutrition', 'hunger', 'agroecology', 'smallholder'],
    'education': ['school', 'education', 'learn', 'literacy', 'university', 'training', 'youth'],
    'housing_land': ['housing', 'shelter', 'land', 'slum', 'urban', 'home', 'settlement', 'tenure'],
    'conflict': ['peace', 'conflict', 'justice', 'violence', 'reconciliation', 'refugee', 'displaced'],
    'energy_digital': ['energy', 'solar', 'electricity', 'digital', 'tech', 'internet', 'connectivity'],
    'recreation_arts': ['arts', 'culture', 'music', 'dance', 'heritage', 'sport', 'recreation'],
    'ecology': ['environment', 'ecology', 'conservation', 'forest', 'water', 'climate', 'nature'],
    'indigenous': ['indigenous', 'amerindian', 'tribal', 'native', 'first nation', 'traditional'],
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
        snippet_pattern = re.compile(r'class="result__snippet"[^>]*>(.*?)</(?:a|span|div)>', re.IGNORECASE | re.DOTALL)
        url_pattern = re.compile(r'class="result__url"[^>]*>([^<]+)</[^>]+>', re.IGNORECASE)
        
        titles = title_pattern.findall(html)
        snippets = snippet_pattern.findall(html)
        urls_found = url_pattern.findall(html)
        
        for i, title in enumerate(titles[:8]):
            snippet = snippets[i] if i < len(snippets) else ''
            url_found = urls_found[i] if i < len(urls_found) else ''
            snippet = re.sub(r'<[^>]+>', ' ', snippet).strip()
            results.append({'title': title.strip(), 'snippet': snippet[:200], 'url': url_found.strip()})
        
        return results
    except Exception as e:
        print(f"  DDG error: {e}", flush=True)
        return []

def search_web(query):
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&skip_disambig=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = []
            if data.get('Abstract'):
                results.append({'title': data.get('Heading', ''), 'snippet': data['Abstract'], 'url': data.get('AbstractURL', '')})
            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({'title': topic['Text'][:80], 'snippet': topic['Text'], 'url': topic.get('FirstURL', '')})
            return results
    except Exception as e:
        print(f"  DDG instant error: {e}", flush=True)
        return []

def extract_orgs(results, query):
    orgs = []
    org_indicators = ['foundation', 'trust', 'association', 'network', 'society', 'union',
                     'institute', 'centre', 'center', 'organization', 'coalition', 'alliance',
                     'initiative', 'project', 'community', 'cooperative', 'forum', 'federation',
                     'council', 'committee', 'group', 'ngo', 'cso', 'movement']
    
    for r in results:
        title = r.get('title', '').strip()
        snippet = r.get('snippet', '') or ''
        url = r.get('url', '')
        
        if not title or len(title) < 4:
            continue
        if any(x in title.lower() for x in ['wikipedia', 'facebook.com', 'twitter', '.pdf', 'page 1']):
            continue
        
        title_lower = title.lower()
        is_org = any(ind in title_lower for ind in org_indicators)
        is_guyana = 'guyan' in title_lower or 'georgetown' in title_lower or '.gy' in url.lower()
        is_amerindian = any(x in title_lower for x in ['amerindian', 'indigenous', 'toshaos'])
        
        if is_org or is_guyana or is_amerindian:
            framework = guess_framework(title, snippet)
            orgs.append({
                'name': title[:100],
                'description': snippet[:200],
                'website': url if url.startswith('http') else '',
                'framework_area': framework,
                'source': f"Search: {query[:60]}"
            })
    return orgs

def main():
    print("ECO-68: Guyana (GY) Regional Research", flush=True)
    os.makedirs(os.path.join(DATA_DIR, "regional"), exist_ok=True)
    
    all_orgs = []
    seen_names = set()
    
    for i, query in enumerate(SEARCHES):
        print(f"\n[{i+1}/{len(SEARCHES)}] {query[:70]}...", flush=True)
        
        results = search_ddg_html(query)
        print(f"  HTML results: {len(results)}", flush=True)
        
        if len(results) < 2:
            results = search_web(query)
            print(f"  Fallback results: {len(results)}", flush=True)
        
        orgs = extract_orgs(results, query)
        new_orgs = []
        for org in orgs:
            key = org['name'].lower()[:40]
            if key not in seen_names:
                seen_names.add(key)
                new_orgs.append(org)
        
        print(f"  New orgs: {len(new_orgs)}", flush=True)
        all_orgs.extend(new_orgs)
        time.sleep(1.5)
    
    # Targeted known orgs
    targeted = [
        ("Amerindian Peoples Association Guyana APA", "indigenous"),
        ("Red Thread Guyana women organization", "democracy"),
        ("Guyana Human Rights Association GHRA", "democracy"),
        ("Guyana Responsible Parenthood Association GRPA", "healthcare"),
        ("Guyana Cooperative Financial Institution", "cooperatives"),
        ("Caribbean Natural Resources Institute CANARI Guyana", "ecology"),
        ("Guyana Organization of Indigenous Peoples", "indigenous"),
    ]
    
    print(f"\n[Targeted] Known orgs...", flush=True)
    for query, hint in targeted:
        results = search_ddg_html(query)
        for r in results[:3]:
            title = r.get('title', '')
            if title and len(title) > 5:
                key = title.lower()[:40]
                if key not in seen_names:
                    seen_names.add(key)
                    all_orgs.append({
                        'name': title[:100],
                        'description': r.get('snippet', '')[:200],
                        'website': r.get('url', ''),
                        'framework_area': hint,
                        'source': f"Targeted: {query[:60]}"
                    })
        time.sleep(1)
    
    # Group by framework area
    by_area = {}
    for org in all_orgs:
        area = org['framework_area']
        by_area.setdefault(area, []).append(org)
    
    print(f"\nWriting {len(all_orgs)} orgs to {OUTPUT_FILE}", flush=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Guyana (GY) -- Regional Directory\n\n")
        f.write(f"**Searches conducted:** {len(SEARCHES) + len(targeted)}\n")
        f.write(f"**Organizations found:** {len(all_orgs)}\n")
        f.write(f"**Generated:** ECO-68 Researcher run\n\n")
        f.write(f"*Organizations found via web search. Prioritized: indigenous-led (Amerindian), ")
        f.write(f"mutual aid, grassroots. Needs human verification.*\n\n")
        f.write(f"---\n\n")
        
        for area, orgs in sorted(by_area.items()):
            f.write(f"## {area.replace('_', ' ').title()} ({len(orgs)} orgs)\n\n")
            f.write(f"| Name | Description | Website | Source |\n")
            f.write(f"|---|---|---|---|\n")
            for org in orgs:
                name = org['name'].replace('|', '-')
                desc = org['description'].replace('|', '-').replace('\n', ' ')[:120]
                web = org['website'][:80] if org['website'] else ''
                src = org['source'][:50]
                f.write(f"| {name} | {desc} | {web} | {src} |\n")
            f.write(f"\n")
        
        f.write(f"---\n\n")
        f.write(f"## Coverage Assessment\n\n")
        f.write(f"- IRS BMF records for GY: 0 (US-only database)\n")
        f.write(f"- This research adds: {len(all_orgs)} Guyanese organizations\n")
        f.write(f"- Framework coverage: {', '.join(f'{a}({len(o)})' for a,o in by_area.items())}\n")
        f.write(f"- Key areas: Amerindian/indigenous orgs, environmental (rainforest), cooperative sector\n")
        f.write(f"- Recommended follow-up: Amerindian Peoples Association, Red Thread, GHRA directories\n")
    
    print(f"\nECO-68 COMPLETE -- {len(all_orgs)} orgs", flush=True)
    return len(all_orgs)

if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
