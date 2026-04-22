"""
India-focused ingest for Commonweave.

India's solidarity economy is huge and largely invisible to Western-style
registries. Registered cooperatives alone number ~854,000, but the real
field also includes:

  formal tier   - registered legal entities (cooperatives, NGOs, FPOs
                  with CIN, PACS). Found via NCDC, NGO Darpan, NABARD.
  hybrid tier   - registered but primarily operating informally. FPOs
                  under SFAC/NABARD, SHG federations under NABARD-SBLP,
                  state SHG networks like Kudumbashree (Kerala) and
                  JEEViKA (Bihar).
  informal tier - unregistered groups, Community Forest Resource holders
                  under FRA, Pani Panchayats, Van Panchayats, caste-based
                  mutual aid networks (Marwari funds, Chettiar associations,
                  etc.). Most are NOT auto-scrapable. Some are only in
                  offline ledgers.

This script is the dispatcher. Right now it:
  1. Runs a targeted Wikidata-India pull (formal tier).
  2. Logs the count delta by legibility to trim_audit/india-YYYY-MM-DD.md.
  3. Documents every source we SHOULD be scraping and what it would take.

A pipeline-auditor run will see the gap and keep nagging us to build the
other tiers. That is the intended behavior - we want the bias visible.

Usage:
    python ingest_india.py --dry-run
    python ingest_india.py --source wikidata
    python ingest_india.py --source all
"""
import argparse
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from _common import DB_PATH, trim_audit_path


# ── Source catalog ────────────────────────────────────────────────────
# Every known India source, its legibility tier, current status, and the
# next concrete build step. Pipeline auditor reads this and reports gaps.

INDIA_SOURCES = [
    # (key, name, tier, url, status, next_step)
    (
        'wikidata',
        'Wikidata SPARQL (cooperative classes, country IN)',
        'formal',
        'https://query.wikidata.org/sparql',
        'IMPLEMENTED',
        'Runs via ingest_wikidata_bulk.py --country IN',
    ),
    (
        'ncdc',
        'National Cooperative Development Corporation directory',
        'formal',
        'https://www.ncdc.in/',
        'TODO',
        'NCDC has no public API. Search UI only. Requires a dedicated '
        'scraper per category (dairy, agriculture, credit, consumer, '
        'housing, womens coops). Estimate: 1 day.',
    ),
    (
        'ngo_darpan',
        'NITI Aayog NGO Darpan (all registered NGOs)',
        'formal',
        'https://ngodarpan.gov.in/',
        'TODO',
        'JavaScript-rendered SPA. Has internal JSON endpoints '
        '(statewise_ngo, etc.) that return org lists. Requires '
        'reverse-engineering the XHR calls. Estimate: 1 day. Will '
        'yield 100K+ registered NGOs, needs alignment filter pass.',
    ),
    (
        'sewa',
        'SEWA affiliated organizations list',
        'formal',
        'https://www.sewa.org/',
        'TODO',
        'Simple HTML, directly scrapable. Small list (~50-100 direct '
        'affiliates). Estimate: 2 hours.',
    ),
    (
        'amul',
        'Amul/GCMMF member unions',
        'formal',
        'https://amul.com/m/member-unions',
        'TODO',
        'Structured HTML table, directly scrapable. ~18 district '
        'unions, each federating thousands of village societies. '
        'Estimate: 2 hours for unions list, 2 days for village-level '
        'rollout.',
    ),
    (
        'sfac_fpos',
        'Small Farmers Agri-Business Consortium - FPO registry',
        'hybrid',
        'https://sfacindia.com/',
        'TODO',
        'SFAC publishes state-wise FPO lists as PDF or Excel. Requires '
        'PDF/xlsx parsing. Several thousand FPOs across India. '
        'Estimate: 1-2 days.',
    ),
    (
        'nabard_fpos',
        'NABARD FPO portal (promoted under POPI scheme)',
        'hybrid',
        'https://www.nabard.org/content.aspx?id=585',
        'TODO',
        'NABARD publishes state-wise FPO directories. Mix of PDF and '
        'JSON API endpoints. Estimate: 2 days including state rollout.',
    ),
    (
        'nabard_pacs',
        'NABARD Primary Agricultural Credit Societies',
        'hybrid',
        'https://www.nabard.org/auth/writereaddata/tender/1312162622PACS%20Status%20Report-2022-23.pdf',
        'TODO',
        'State-level PDFs. ~95,000 PACS nationwide. Start with 3 '
        'biggest states (Maharashtra, UP, Tamil Nadu). pypdf/pdfplumber. '
        'Estimate: 3 days for top-3 states, several weeks for all 28.',
    ),
    (
        'kudumbashree',
        'Kudumbashree (Kerala) CDS network',
        'informal',
        'https://www.kudumbashree.org/',
        'TODO',
        'Kerala state rural livelihood mission. ~4.4M women members in '
        '~300K Neighborhood Groups organized into Community Development '
        'Societies. Directory exists at CDS level per district. '
        'Estimate: 2-3 days.',
    ),
    (
        'jeevika',
        'JEEViKA (Bihar Rural Livelihoods)',
        'informal',
        'https://brlps.in/',
        'TODO',
        'Bihar state rural livelihood mission. ~1M SHGs. Similar '
        'structure to Kudumbashree. Estimate: 2-3 days.',
    ),
    (
        'mota_cfr',
        'Ministry of Tribal Affairs - Community Forest Resource titles',
        'informal',
        'https://tribal.nic.in/FRA.aspx',
        'TODO',
        'Village-level forest commons under the Forest Rights Act. '
        'Published by state CFR cells. Patchy data, some states '
        'publish lists, others do not. Estimate: 1 week for what is '
        'available; some states need right-to-information requests.',
    ),
    (
        'pani_panchayats',
        'Pani Panchayats / Water Users Associations',
        'informal',
        None,
        'PARTIAL',
        'Documented by Forum for Policy Dialogue on Water Conflicts in '
        'India (FPDWCI). No single directory. Maharashtra state has a '
        'partial list. Mostly requires human fieldwork.',
    ),
    (
        'caste_networks',
        'Caste/community mutual aid (Marwari, Chettiar, Khatik funds)',
        'informal',
        None,
        'OUT_OF_SCOPE',
        'Not auto-scrapable. These networks operate through temple '
        'trusts, community halls, and WhatsApp groups. Inclusion '
        'requires ethnographic engagement and community consent, not a '
        'web scraper. Document in OUTCOMES.md as a known gap.',
    ),
]


def run_wikidata_india(dry_run):
    """Shell out to ingest_wikidata_bulk.py for India."""
    script = os.path.join(os.path.dirname(__file__), 'ingest_wikidata_bulk.py')
    args = [sys.executable, script, '--country', 'IN']
    if dry_run:
        args.append('--dry-run')
    print(f'\n>> Running: {" ".join(args)}')
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=1800)
        print(r.stdout[-2000:] if r.stdout else '(no stdout)')
        if r.returncode != 0:
            print(f'  exit {r.returncode}: {r.stderr[-500:]}')
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        print('  TIMEOUT after 30 minutes')
        return False


def count_india_by_legibility(db):
    c = db.cursor()
    c.execute(
        "SELECT legibility, COUNT(*) FROM organizations "
        "WHERE country_code='IN' AND status='active' "
        "GROUP BY legibility"
    )
    return dict(c.fetchall())


def write_audit(before, after, sources_run, log_path):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f'# India Ingest - {today}\n\n')
        f.write('## Active orgs by legibility tier\n\n')
        f.write('| Tier | Before | After | Delta |\n|---|---|---|---|\n')
        all_tiers = set(before) | set(after)
        total_before = sum(before.values())
        total_after = sum(after.values())
        for tier in sorted(all_tiers, key=lambda x: x or 'zz'):
            b = before.get(tier, 0)
            a = after.get(tier, 0)
            f.write(f'| {tier or "(null)"} | {b:,} | {a:,} | '
                    f'{a - b:+,} |\n')
        f.write(f'| **TOTAL** | **{total_before:,}** | '
                f'**{total_after:,}** | **{total_after - total_before:+,}** |\n\n')

        f.write('## Sources run this pass\n\n')
        for key in sources_run:
            f.write(f'- `{key}`\n')

        f.write('\n## Source catalog (all known India sources)\n\n')
        f.write('| Key | Tier | Status | Source |\n|---|---|---|---|\n')
        for key, name, tier, url, status, _ in INDIA_SOURCES:
            url_cell = f'<{url}>' if url else '(offline only)'
            f.write(f'| {key} | {tier} | {status} | {name} {url_cell} |\n')

        f.write('\n## Next steps (pending sources)\n\n')
        for key, name, tier, url, status, step in INDIA_SOURCES:
            if status in ('TODO', 'PARTIAL'):
                f.write(f'### {key} ({tier})\n\n')
                f.write(f'**Source:** {name}\n\n')
                if url:
                    f.write(f'**URL:** <{url}>\n\n')
                f.write(f'**Status:** {status}\n\n')
                f.write(f'**Next step:** {step}\n\n')

        f.write('\n## Out-of-scope\n\n')
        for key, name, tier, url, status, step in INDIA_SOURCES:
            if status == 'OUT_OF_SCOPE':
                f.write(f'- **{name}**: {step}\n')

        f.write('\n\n## Honest note\n\n')
        f.write(
            'India legibility was almost entirely `unknown` before '
            'this pass. The Wikidata pull adds formal-tier coverage '
            'but Wikidata is biased toward notable/Western-documented '
            'entities. The big yield for India will come from NCDC, '
            'NGO Darpan, SFAC FPOs, and the state rural livelihood '
            'missions. Each of those is a focused multi-day build. '
            'Building one per week is a realistic cadence.\n'
        )


def main():
    ap = argparse.ArgumentParser(description='India-focused ingest dispatcher')
    ap.add_argument('--source', default='wikidata',
                    choices=['wikidata', 'all'],
                    help='Which source(s) to run. Today only wikidata is '
                         'implemented; others are documented TODOs.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Report counts without writing')
    args = ap.parse_args()

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    before = count_india_by_legibility(db)
    print('India orgs before:')
    for tier, n in sorted(before.items(), key=lambda x: x[0] or 'zz'):
        print(f'  {tier or "(null)":10s} {n:,}')

    sources_run = []
    if args.source in ('wikidata', 'all'):
        if run_wikidata_india(args.dry_run):
            sources_run.append('wikidata')

    # Re-open to see post-run counts
    db.close()
    db = sqlite3.connect(DB_PATH)
    after = count_india_by_legibility(db)
    print('\nIndia orgs after:')
    for tier, n in sorted(after.items(), key=lambda x: x[0] or 'zz'):
        print(f'  {tier or "(null)":10s} {n:,}')
    db.close()

    log_path = trim_audit_path('india')
    write_audit(before, after, sources_run, log_path)
    print(f'\nLog written: {log_path}')

    # Print TODO summary so it is visible on every run
    todo_count = sum(
        1 for _, _, _, _, s, _ in INDIA_SOURCES if s == 'TODO'
    )
    print(f'\n{todo_count} India sources still TODO. See log for details.')


if __name__ == '__main__':
    main()
