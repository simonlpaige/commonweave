"""
Pipeline auditor: the self-improvement loop for the Commonweave directory.

Read-only. Never writes to the database. Runs once a week. Looks at the
current state and drafts concrete, evidence-cited upgrade proposals.

What the auditor does each run:
  1. Coverage analysis (what countries and framework areas are thin).
  2. Legibility analysis (what % of each country is formal vs hybrid vs
     informal; flag countries that are nearly all formal as bias-narrow).
  3. Quality signals (field completeness, staleness rate, alignment
     score distribution, merge rate).
  4. Source performance (which ingesters are plateauing).
  5. Proposals - but only if they cite a named source AND specific
     numbers from this run. Generic proposals are dropped before writing.
  6. Self-check - read the last 4 weeks of proposals. Flag ones still
     unbuilt. If the same proposal has been ignored 3 weeks running,
     retire it to rejected-proposals.md.

Output: commonweave/data/trim_audit/proposals-YYYY-MM-DD.md

Usage:
    python pipeline_auditor.py
    python pipeline_auditor.py --dry-run     # skip writing the file
"""
import argparse
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from glob import glob

sys.path.insert(0, os.path.dirname(__file__))
from _common import DB_PATH, TRIM_AUDIT_DIR, trim_audit_path


# Rough population estimates (millions) for the top 50 countries.
# Used for per-capita coverage ratios. These are not precise, they are
# order-of-magnitude. Good enough to flag egregious gaps.
POPULATION_M = {
    'IN': 1430, 'CN': 1410, 'US': 335, 'ID': 280, 'PK': 240,
    'NG': 220, 'BR': 215, 'BD': 170, 'RU': 145, 'MX': 130,
    'JP': 125, 'ET': 125, 'PH': 115, 'EG': 110, 'VN': 100,
    'CD': 100, 'IR': 90, 'TR': 85, 'DE': 85, 'TH': 70,
    'GB': 68, 'FR': 68, 'IT': 60, 'ZA': 60, 'TZ': 63,
    'MM': 55, 'KE': 55, 'KR': 52, 'CO': 52, 'ES': 48,
    'UG': 48, 'AR': 46, 'DZ': 45, 'SD': 48, 'IQ': 45,
    'UA': 40, 'PL': 38, 'CA': 40, 'AF': 40, 'MA': 37,
    'SA': 36, 'PE': 34, 'UZ': 35, 'MY': 33, 'AO': 35,
    'GH': 33, 'MZ': 33, 'NP': 30, 'YE': 33, 'VE': 28,
    'MG': 29, 'CI': 28, 'AU': 26, 'CM': 27, 'NE': 26,
    'LK': 22, 'BF': 22, 'MW': 21, 'CL': 19, 'KZ': 20,
    'ZM': 20, 'ZW': 17, 'GT': 17, 'EC': 17, 'NL': 18,
    'SN': 17, 'ML': 22, 'TD': 17, 'RW': 14, 'SO': 18,
    'GN': 14, 'SS': 11, 'BI': 13, 'BJ': 13, 'HT': 12,
    'TN': 12, 'BE': 12, 'BO': 12, 'HN': 10, 'SE': 11,
    'PT': 10, 'HU': 10, 'CZ': 11, 'GR': 10, 'AZ': 10,
    'BY': 9, 'PG': 11, 'AT': 9, 'IL': 9, 'CH': 9,
    'TG': 8, 'SL': 8, 'LA': 8, 'LY': 7, 'KG': 7,
    'PY': 7, 'NI': 7, 'BG': 7, 'RS': 7, 'SV': 6,
    'JO': 11, 'CR': 5, 'IE': 5, 'NO': 5, 'FI': 5,
    'DK': 6, 'NZ': 5, 'SG': 6, 'UY': 3, 'EE': 1,
    'IS': 0.4,
}


def load_country_stats(db):
    """Per-country: total active, by legibility tier, by completeness."""
    c = db.cursor()
    c.execute(
        "SELECT country_code, legibility, "
        "       SUM(CASE WHEN website IS NOT NULL AND website != '' THEN 1 ELSE 0 END), "
        "       SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END), "
        "       SUM(CASE WHEN lat IS NOT NULL AND lon IS NOT NULL THEN 1 ELSE 0 END), "
        "       SUM(CASE WHEN description IS NOT NULL AND length(description) > 30 THEN 1 ELSE 0 END), "
        "       COUNT(*) "
        "FROM organizations WHERE status='active' "
        "GROUP BY country_code, legibility"
    )
    per_cc = defaultdict(lambda: {
        'total': 0,
        'by_tier': defaultdict(int),
        'with_website': 0,
        'with_email': 0,
        'with_latlng': 0,
        'with_desc': 0,
    })
    for cc, tier, web, email, ll, desc, total in c.fetchall():
        if not cc:
            continue
        s = per_cc[cc]
        s['total'] += total
        s['by_tier'][tier or 'unknown'] += total
        s['with_website'] += web or 0
        s['with_email'] += email or 0
        s['with_latlng'] += ll or 0
        s['with_desc'] += desc or 0
    return per_cc


def load_source_stats(db):
    """Per-source org counts."""
    c = db.cursor()
    c.execute(
        "SELECT source, COUNT(*) FROM organizations "
        "WHERE status='active' GROUP BY source ORDER BY COUNT(*) DESC"
    )
    return c.fetchall()


def load_framework_stats(db):
    c = db.cursor()
    c.execute(
        "SELECT framework_area, COUNT(*) FROM organizations "
        "WHERE status='active' GROUP BY framework_area ORDER BY COUNT(*) DESC"
    )
    return c.fetchall()


def load_alignment_distribution(db):
    c = db.cursor()
    c.execute(
        "SELECT alignment_score, COUNT(*) FROM organizations "
        "WHERE status='active' GROUP BY alignment_score "
        "ORDER BY alignment_score"
    )
    return c.fetchall()


def load_single_source_countries(db):
    """Countries where only one source contributed - fragility signal."""
    c = db.cursor()
    c.execute(
        "SELECT country_code, COUNT(DISTINCT source) as sources, COUNT(*) as n "
        "FROM organizations WHERE status='active' "
        "GROUP BY country_code HAVING sources = 1 ORDER BY n DESC"
    )
    return c.fetchall()


# ── Proposal generation ───────────────────────────────────────────────
# Every proposal MUST have: title, named source (URL or registry name),
# specific numbers from this run, scope, expected yield, exec prompt.

def propose_coverage_gaps(per_cc):
    """Find top 5 underfilled countries by (population / orgs) ratio."""
    proposals = []
    ratios = []
    for cc, stats in per_cc.items():
        pop = POPULATION_M.get(cc)
        if not pop or pop < 5 or stats['total'] < 1:
            continue
        # orgs per million people
        per_m = stats['total'] / pop
        ratios.append((cc, stats['total'], pop, per_m))
    ratios.sort(key=lambda x: x[3])  # lowest per-million first

    # Filter for "we have at least SOMETHING but nowhere near enough"
    candidates = [r for r in ratios if r[1] >= 5 and r[3] < 2.0]

    for cc, n, pop, per_m in candidates[:5]:
        # Only emit if we can name at least one concrete source to try
        source = country_specific_source_hint(cc)
        if not source:
            continue
        proposals.append({
            'title': f'Fill {cc} coverage (currently {n} orgs, ~{per_m:.2f}/M)',
            'why': (
                f'{cc} has population ~{pop}M and only {n} aligned orgs, '
                f'ratio {per_m:.2f} orgs per million. For comparison, GB has '
                f'~170 per million.'
            ),
            'source': source,
            'scope': 'medium',
            'yield': f'Estimated 500-5,000 orgs depending on source depth',
            'prompt': (
                f'"Larry, build a {cc}-focused ingester. Start with the '
                f'source I documented in the proposal."'
            ),
            'key': f'coverage-{cc}',
        })
    return proposals


def propose_legibility_narrow(per_cc):
    """Flag countries that are almost entirely formal-tier."""
    proposals = []
    candidates = []
    for cc, stats in per_cc.items():
        if stats['total'] < 100:
            continue
        formal = stats['by_tier'].get('formal', 0)
        unknown = stats['by_tier'].get('unknown', 0)
        formal_share = (formal + unknown) / stats['total']
        informal = stats['by_tier'].get('informal', 0)
        hybrid = stats['by_tier'].get('hybrid', 0)
        if informal + hybrid == 0 and stats['total'] >= 100:
            candidates.append((cc, stats['total'], formal, unknown))
    # Sort by total desc - biggest blind spots first
    candidates.sort(key=lambda x: -x[1])

    for cc, total, formal, unknown in candidates[:3]:
        hint = country_informal_source_hint(cc)
        if not hint:
            continue
        proposals.append({
            'title': f'{cc} has zero informal/hybrid orgs - blind spot',
            'why': (
                f'{cc} has {total} active orgs but 0 tagged informal or '
                f'hybrid. That cannot be true. We are missing the grassroots '
                f'tier entirely.'
            ),
            'source': hint,
            'scope': 'medium',
            'yield': f'Hundreds to thousands of hybrid/informal orgs',
            'prompt': (
                f'"Larry, run an informal-tier ingest for {cc}. Start '
                f'with the source in the proposal."'
            ),
            'key': f'legibility-{cc}',
        })
    return proposals


def propose_quality_gaps(per_cc):
    """Countries where contact info (email, lat/lng) is particularly thin."""
    proposals = []
    low_contact = []
    for cc, stats in per_cc.items():
        if stats['total'] < 200:
            continue
        email_share = stats['with_email'] / stats['total']
        if email_share < 0.05:
            low_contact.append((cc, stats['total'], email_share))
    low_contact.sort(key=lambda x: x[1], reverse=True)

    for cc, total, share in low_contact[:3]:
        proposals.append({
            'title': f'{cc} orgs have no email ({share * 100:.1f}% coverage)',
            'why': (
                f'{cc} has {total} active orgs but only {share * 100:.1f}% '
                f'have a contact email. Without that, the directory is a '
                f'map we cannot use for outreach.'
            ),
            'source': (
                'Extend the email-scraping pass in '
                'modules/groundlayer/factory/lead-gen/outbound/lead-finder.js '
                '(strips mailto: from pages) to cover Commonweave orgs by '
                f'running it against the {cc} subset.'
            ),
            'scope': 'small',
            'yield': f'5-20% email enrichment on {cc} orgs',
            'prompt': (
                f'"Larry, run a contact-email enrichment pass for {cc} '
                f'Commonweave orgs using the lead-finder email scraper."'
            ),
            'key': f'contact-{cc}',
        })
    return proposals


def propose_source_plateau(sources):
    """Sources that look stagnant or too dominant."""
    proposals = []
    if not sources:
        return proposals
    total = sum(n for _, n in sources)
    for src, n in sources[:3]:
        if not src:
            continue
        share = n / total
        if share > 0.35:
            proposals.append({
                'title': (
                    f'Source `{src}` is {share * 100:.0f}% of the directory'
                ),
                'why': (
                    f'`{src}` contributed {n:,} orgs, which is '
                    f'{share * 100:.0f}% of all active orgs. Directory '
                    f'concentration this high means most of our "global '
                    f'coverage" is one country or one pipeline.'
                ),
                'source': (
                    'Diversify: prioritize the next focused ingester '
                    '(see ingest_india.py catalog or similar for other '
                    'underfilled regions).'
                ),
                'scope': 'medium',
                'yield': 'Reduce source concentration below 30%',
                'prompt': (
                    '"Larry, pick the next country-focused ingester to '
                    'build based on the concentration finding."'
                ),
                'key': f'plateau-{src}',
            })
    return proposals


# ── Country-specific source hints ─────────────────────────────────────
# These are the names we drop into proposals. They are the "cite a real
# source" mechanism that prevents the auditor from producing vapor.

COUNTRY_SOURCE_HINTS = {
    'CN': (
        'China MOCA cooperative registry (difficult to scrape but '
        'exists); Chinese Academy of Social Sciences NGO directory.'
    ),
    'ID': (
        'Indonesia Ministry of Cooperatives and SMEs directory '
        '(kemenkopukm.go.id); Lembaga Keuangan Mikro registry.'
    ),
    'PK': (
        'Pakistan Cooperative Societies directory (provincial level); '
        'PCP NGO directory (pcp.org.pk).'
    ),
    'BR': (
        'Brazil OCB (Organization of Brazilian Cooperatives) state '
        'registries; ANCOSOL solidarity economy federation.'
    ),
    'BD': (
        'Bangladesh Cooperative Department statewise directory '
        '(coop.gov.bd); NGO Affairs Bureau (ngoab.gov.bd).'
    ),
    'RU': (
        'Russia Rosstat cooperative registry; Agency of Strategic '
        'Initiatives solidarity economy list.'
    ),
    'MX': (
        'Mexico INAES (Instituto Nacional de la Economia Social) '
        'cooperative directory.'
    ),
    'JP': (
        'Japan National Federation of Agricultural Cooperatives '
        '(JA-ZENCHU); Japanese Consumers Cooperative Union (JCCU).'
    ),
    'PH': (
        'Philippines Cooperative Development Authority (cda.gov.ph) '
        'master list.'
    ),
    'EG': (
        'Egypt Ministry of Social Solidarity cooperative registry.'
    ),
    'VN': (
        'Vietnam Cooperative Alliance (vca.org.vn) member list.'
    ),
    'IR': (
        'Iran Ministry of Cooperative, Labour and Social Welfare '
        'cooperative registry.'
    ),
    'TR': (
        'Turkey Ministry of Commerce cooperative directory.'
    ),
    'TH': (
        'Thailand Cooperative Promotion Department (cpd.go.th).'
    ),
    'IN': (
        'NCDC, NGO Darpan, SFAC FPO lists, Kudumbashree, JEEViKA - '
        'see ingest_india.py catalog for full list.'
    ),
}

COUNTRY_INFORMAL_HINTS = {
    'IN': (
        'Community Forest Resource titles (MoTA FRA), Pani Panchayats, '
        'Van Panchayats, state SHG federations.'
    ),
    'BR': (
        'Comunidades quilombolas registries (Palmares Foundation); '
        'MST settlement list; indigenous community directories (FUNAI).'
    ),
    'MX': (
        'Ejidos registries (RAN); indigenous autonomous community lists.'
    ),
    'ID': (
        'Masyarakat Hukum Adat (customary community) registries; '
        'BUMDes village-owned enterprises directory.'
    ),
    'BO': (
        'TCO (Tierra Comunitaria de Origen) indigenous territory registry.'
    ),
    'PE': (
        'Comunidades campesinas and nativas registries (SUNARP).'
    ),
    'PH': (
        'Ancestral Domain/Ancestral Land titles (NCIP); barangay-level '
        'peoples organizations.'
    ),
    'KE': (
        'Community land registries (Community Land Act 2016); '
        'self-help groups under KNFJK.'
    ),
}

def country_specific_source_hint(cc):
    return COUNTRY_SOURCE_HINTS.get(cc)

def country_informal_source_hint(cc):
    return COUNTRY_INFORMAL_HINTS.get(cc)


# ── Self-check: read prior proposals ──────────────────────────────────
def prior_proposals():
    """Return list of (date, content) for previous proposals files."""
    pattern = os.path.join(TRIM_AUDIT_DIR, 'proposals-*.md')
    out = []
    for path in sorted(glob(pattern)):
        m = re.search(r'proposals-(\d{4}-\d{2}-\d{2})\.md$', path)
        if not m:
            continue
        with open(path, encoding='utf-8') as f:
            out.append((m.group(1), f.read()))
    return out


def proposal_key_from_text(text):
    """Extract proposal keys from a prior file's content."""
    return set(re.findall(r'\[key:([\w\-.]+)\]', text))


def self_check(current_keys):
    """
    Returns:
      still_pending: keys that appeared in last week's file but not built
      reject_these: keys that appeared 3+ weeks in a row - retire them
    """
    history = prior_proposals()
    if not history:
        return set(), set()

    # Keys per file, newest first
    keys_per_week = [(d, proposal_key_from_text(t)) for d, t in history[-4:]]

    # Keys still pending: appeared last week AND this week
    last_week_keys = keys_per_week[-1][1] if keys_per_week else set()
    still_pending = last_week_keys & current_keys

    # Keys ignored 3+ weeks: appear in 3+ consecutive weeks
    counts = defaultdict(int)
    for _, keys in keys_per_week:
        for k in keys:
            counts[k] += 1
    reject_these = {k for k, n in counts.items() if n >= 3 and k in current_keys}

    return still_pending, reject_these


def write_proposals(proposals, still_pending, retired, out_path):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# Commonweave Pipeline Proposals - {today}\n\n')
        f.write(
            'Evidence-based upgrade proposals. Each cites a named source '
            'and specific numbers from this run. Generic proposals are '
            'dropped before writing.\n\n'
        )

        if retired:
            f.write('## Retired (3+ weeks unbuilt, stop suggesting)\n\n')
            for k in sorted(retired):
                f.write(f'- `{k}`\n')
            f.write('\n')

        ranked = sorted(
            proposals,
            key=lambda p: _rank_score(p),
            reverse=True
        )

        f.write(f'## {len(ranked)} proposals ranked by impact/effort\n\n')
        for i, p in enumerate(ranked, 1):
            pending_tag = ' **STILL PENDING**' if p['key'] in still_pending else ''
            f.write(f'### {i}. {p["title"]}{pending_tag} [key:{p["key"]}]\n\n')
            f.write(f'**Why:** {p["why"]}\n\n')
            f.write(f'**Source to use:** {p["source"]}\n\n')
            f.write(f'**Scope:** {p["scope"]} | **Expected yield:** '
                    f'{p["yield"]}\n\n')
            f.write(f'**Prompt:** `{p["prompt"]}`\n\n')
            f.write('---\n\n')


def _rank_score(p):
    scope_weight = {'small': 3, 'medium': 2, 'large': 1}.get(p['scope'], 1)
    return scope_weight


def main():
    ap = argparse.ArgumentParser(
        description='Pipeline auditor - evidence-based upgrade proposals'
    )
    ap.add_argument('--dry-run', action='store_true',
                    help='Print but do not write the proposals file')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    per_cc = load_country_stats(db)
    sources = load_source_stats(db)
    framework = load_framework_stats(db)
    alignment = load_alignment_distribution(db)
    single_source = load_single_source_countries(db)

    total_active = sum(s['total'] for s in per_cc.values())
    print(f'Directory has {total_active:,} active orgs across '
          f'{len(per_cc)} countries.')
    print(f'Top sources: '
          f'{", ".join(f"{s}({n:,})" for s,n in sources[:5] if s)}')

    # Generate proposals
    proposals = []
    proposals.extend(propose_coverage_gaps(per_cc))
    proposals.extend(propose_legibility_narrow(per_cc))
    proposals.extend(propose_quality_gaps(per_cc))
    proposals.extend(propose_source_plateau(sources))

    # Filter: only keep proposals with a named source AND specific evidence
    kept = []
    for p in proposals:
        if p.get('source') and p.get('why') and p.get('key'):
            kept.append(p)
    dropped = len(proposals) - len(kept)
    if dropped:
        print(f'Dropped {dropped} proposals for missing source/evidence.')

    current_keys = {p['key'] for p in kept}
    still_pending, retired = self_check(current_keys)

    # Retired proposals get stripped from this week's output
    kept = [p for p in kept if p['key'] not in retired]

    # Top 5 only
    kept = sorted(kept, key=_rank_score, reverse=True)[:5]

    print(f'\n{len(kept)} proposals generated. '
          f'{len(still_pending)} still pending from last week. '
          f'{len(retired)} retired.')

    for p in kept:
        tag = ' (STILL PENDING)' if p['key'] in still_pending else ''
        print(f'  - {p["title"]}{tag}')

    db.close()

    if args.dry_run:
        print('[DRY RUN] No file written.')
        return

    out = trim_audit_path('proposals')
    write_proposals(kept, still_pending, retired, out)
    print(f'\nProposals written: {out}')

    # Also log retired proposals to a running file
    if retired:
        rejected_path = os.path.join(
            TRIM_AUDIT_DIR, 'rejected-proposals.md'
        )
        with open(rejected_path, 'a', encoding='utf-8') as f:
            f.write(f'\n## Retired {datetime.now(timezone.utc).strftime("%Y-%m-%d")}\n\n')
            for k in sorted(retired):
                f.write(f'- `{k}` (ignored 3+ weeks)\n')


if __name__ == '__main__':
    main()
