"""
Experiment 5: i18n dry-run preview (word-boundary version).

Read-only. No writes. Uses phase2_filter.score_org directly so results
reflect the real scoring path, including the word-boundary regex that
replaced naive substring matching (see BOT-CRITIQUE followup 2026-04-17).

Reports:
  - How many active orgs currently score below the alignment threshold
    but would pass it under the multilingual STRONG_POS.
  - Score-distribution before/after the i18n merge.
  - Samples of newly-passing orgs so Simon can eyeball for regressions.
"""

import os
import sys
import sqlite3
import unicodedata

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.dirname(_THIS_DIR)
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

from i18n_terms import (  # noqa: E402
    CONCEPT_TERMS,
    STRONG_POS_MULTI,
    TERMS_MOVED_TO_SEARCH_ONLY,
)
# Reuse scoring to estimate lift under the new multilingual list.
from phase2_filter import score_org  # noqa: E402

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'


def nfc_lower(text):
    return unicodedata.normalize('NFC', text or '').lower()


def non_english_terms_by_concept():
    """For each concept, return {lang: [terms]} for non-English languages only."""
    out = {}
    for concept, by_lang in CONCEPT_TERMS.items():
        non_en = {lang: terms for lang, terms in by_lang.items() if lang != 'en'}
        out[concept] = non_en
    return out


def main():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM organizations WHERE status='active'")
    total_active = c.fetchone()[0]
    print(f'Active orgs in DB: {total_active:,}')
    print(f'STRONG_POS_MULTI terms in scorer: {len(STRONG_POS_MULTI):,}')
    print(f'Short/ambiguous terms excluded from scoring: {len(TERMS_MOVED_TO_SEARCH_ONLY):,}')
    print('  (excluded sample):', ', '.join(sorted(TERMS_MOVED_TO_SEARCH_ONLY)[:15]))
    print()

    # Pass 1: score every active org under the new multilingual scorer.
    # Compare to current alignment_score column (set by previous phase2_filter run).
    print('Scoring active orgs under multilingual word-boundary scorer...')
    c.execute("""
        SELECT id, name, description, alignment_score
        FROM organizations
        WHERE status='active'
    """)

    new_passers = []        # currently < 2, would be >= 2
    new_droppers = []       # currently >= 2, would be < 2 (regressions)
    score_delta_hist = {}

    for org_id, name, desc, current_score in c:
        current_score = current_score if current_score is not None else 0
        new_score = score_org(name, desc)
        delta = new_score - current_score
        score_delta_hist[delta] = score_delta_hist.get(delta, 0) + 1

        if current_score < 2 and new_score >= 2:
            new_passers.append((name, desc, current_score, new_score))
        elif current_score >= 2 and new_score < 2:
            new_droppers.append((name, desc, current_score, new_score))

    print()
    print('=== Score delta distribution (new_score - current_score) ===')
    for delta in sorted(score_delta_hist):
        bar = '#' * min(60, score_delta_hist[delta] // 50)
        print(f'  {delta:+3d}: {score_delta_hist[delta]:>6,}  {bar}')

    print()
    print(f'=== Threshold crossings ===')
    print(f'  Newly passing  (score crossed into >=2): {len(new_passers):,}')
    print(f'  Newly dropping (score fell below 2):     {len(new_droppers):,}')

    print()
    print('=== Sample newly-passing orgs (first 15) ===')
    for name, desc, old, new in new_passers[:15]:
        print(f'  {old:+d} -> {new:+d}   "{(name or "")[:80]}"')

    if new_droppers:
        print()
        print('=== WARNING: sample newly-dropping orgs (regressions, first 15) ===')
        for name, desc, old, new in new_droppers[:15]:
            print(f'  {old:+d} -> {new:+d}   "{(name or "")[:80]}"')
    else:
        print()
        print('=== No regressions detected (no orgs fell below threshold) ===')

    print()
    print('NOTE: This is a read-only preview. No DB mutations occurred.')


if __name__ == '__main__':
    main()
