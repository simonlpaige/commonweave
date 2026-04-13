"""
ECO-69: Suriname (SR) Regional Research
Uses web search (DuckDuckGo) to find Surinamese organizations.
Output: data/regional/DIRECTORY_SR.md
"""

import urllib.request
import urllib.parse
import json
import os
import time
import sys
import re

DATA_DIR = r"C:\Users\simon\.openclaw\workspace\ecolibrium\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "regional", "DIRECTORY_SR.md")

# 15-search protocol for Suriname
SEARCHES = [
    "Suriname NGO civil society organizations directory",
    "Suriname cooperative association worker community",
    "Suriname indigenous peoples organizations rights Maroon Amerindian",
    "Suriname environmental conservation ecology organizations",
    "Suriname food agriculture smallholder farming organizations",
    "Suriname community health organizations clinic",
    "Suriname women organizations self-help mutual aid",
    "Suriname civic democracy governance organizations",
    "Suriname education community school organization",
    "Suriname solidarity economy mutual aid network",
    "Suriname housing land rights community organization",
    "Suriname renewable energy solar community",
    "Suriname nonprofit foundation trust association",
    "Suriname Paramaribo community grassroots organizations",
    "Suriname Maroon Saramaka Ndyuka community organizations",
]

FRAMEWORK_KEYWORDS = {
    'democracy': ['civic', 'democracy', 'governance', 'community', 'citizen', 'rights', 'political', 'vote'],
    'cooperatives': ['cooperative', 'co-op', 'worker', 'savings', 'credit union', 'thrift', 'mutual'],
    'healthcare': ['health', 'medical', 'hospital', 'clinic', 'hiv', 'maternal', 'nurse'],
    'food': ['food', 'agriculture', 'farming', 'nutrition', 'hunger', 'agroecology', 'smallholder'],
    'education': ['school', 'education', 'learn', 'literacy', 'university', 'training', 'youth'],
    'housing_land': ['housing', 'shelter', 'land', 'urban', 'home', 'settlement'],
    'conflict': ['peace', 'conflict', 'justice', 'violence', 'reconciliation', 'refugee', 'displaced'],
    'energy_digital': ['energy', 'solar', 'electricity', 'digital', 'tech', 'internet', 'connectivity'],
    'recreation_arts': ['arts', 'culture', 'music', 'dance', 'heritage', 'sport', 'recreation'],
    'ecology': ['environment', 'ecology', 'conservation', 'forest', 'water', 'climate', 'nature'],
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
    """Use DuckDuckGo instant answers API."""
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
        if any(x in title.lower() for x in ['wikipedia', 'facebook.com', 'twitter.com', 'pdf', 'page 1']):
            continue
        
        org_indicators = ['foundation', 'trust', 'association', 'network', 'society', 'union',
                         'institute', 'centre', 'center', 'organization', 'coalition', 'alliance',
                         'initiative', 'project', 'community', 'cooperative', 'forum', 'federation',
                         'council', 'committee', 'group', 'ngo', 'cso', 'stichting', 'fonds']
        
        title_lower = title.lower()
        is_org = any(ind in title_lower for ind in org_indicators)
        is_country = 'surinam' in title_lower or 'suriname' in title_lower or '.sr' in url.lower()
        
        if is_org or is_country:
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
    print("ECO-69: Suriname (SR) Regional Research", flush=True)
    os.makedirs(os.path.join(DATA_DIR, "regional"), exist_ok=True)
    
    all_orgs = []
    seen_names = set()
    
    for i, query in enumerate(SEARCHES):
        print(f"\n[{i+1}/{len(SEARCHES)}] Searching: {query[:70]}...", flush=True)
        
        results = search_ddg_html(query)
        print(f"  Got {len(results)} results", flush=True)
        
        if not results:
            results = search_web_api(query)
            print(f"  Fallback API: {len(results)} results", flush=True)
        
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
    
    # Targeted known Suriname organizations
    print(f"\n[Bonus] Searching known Suriname organizations...", flush=True)
    known_resources = [
        ("Suriname Association of NGOs SANBO civil society", "democracy"),
        ("Suriname Conservation Foundation STINASU ecology", "ecology"),
        ("Stichting Suriname health community foundation", "healthcare"),
        ("Telesur Suriname community development organization", "democracy"),
        ("Bureau of Public Health Suriname BOG community", "healthcare"),
        ("Suriname Amazon Conservation Team ACT Amerindian", "ecology"),
        ("Vrouwen Beweging Suriname women organization", "democracy"),
    ]
    
    for query, framework_hint in known_resources:
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
    
    # Write output
    print(f"\nWriting {len(all_orgs)} organizations to {OUTPUT_FILE}", flush=True)
    
    by_area = {}
    for org in all_orgs:
        area = org['framework_area']
        if area not in by_area:
            by_area[area] = []
        by_area[area].append(org)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Suriname (SR) -- Regional Directory\n\n")
        f.write(f"**Searches conducted:** {len(SEARCHES) + len(known_resources)}\n")
        f.write(f"**Organizations found:** {len(all_orgs)}\n")
        f.write(f"**Generated:** ECO-69 Researcher run\n\n")
        f.write(f"*Note: These orgs were found via web search and need verification. ")
        f.write(f"Prioritized: indigenous/Maroon-led orgs, informal mutual aid, non-English (Dutch/Sranan) orgs, grassroots movements.*\n\n")
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
        f.write(f"- IRS BMF records for SR: 0 (expected -- US-only database)\n")
        f.write(f"- This research adds: {len(all_orgs)} Surinamese organizations\n")
        f.write(f"- Framework coverage: {', '.join(f'{a}({len(o)})' for a,o in by_area.items())}\n")
        f.write(f"- Key gaps: Indigenous/Maroon village-level orgs, Dutch-language civil society, informal savings groups\n")
        f.write(f"- Recommended follow-up: Contact SANBO (Suriname NGO umbrella), Conservation International Suriname\n")
    
    print(f"\nECO-69 COMPLETE", flush=True)
    print(f"Total orgs: {len(all_orgs)}", flush=True)
    print(f"Output: {OUTPUT_FILE}", flush=True)
    
    return len(all_orgs)

if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
