"""
apply-enrichments.py

Reads an accepted enrichment export JSON (downloaded from audit/enrich.html)
and updates the SQLite DB for each accepted proposal.

Rules:
- Only fills in website, email, description if the existing value is null/empty.
- Never overwrites an existing non-null value unless the proposal has force=True.
- Logs every update to data/trim_audit/enrichment-log-YYYY-MM-DD.md.
- Appends one JSONL line per update to data/training-data/enrichment-training.jsonl.

Usage:
    python data/apply-enrichments.py path/to/accepted-proposals.json [--dry-run]

Run from commonweave/ root.
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

# Make sure we can import _common.py from this directory
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from _common import DB_PATH, TRIM_AUDIT_DIR, DATA_DIR

# ── Parse CLI args ────────────────────────────────────────────────────────────

def parse_args():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    paths   = [a for a in args if not a.startswith('--')]
    if not paths:
        print('Usage: python data/apply-enrichments.py <accepted-proposals.json> [--dry-run]')
        sys.exit(1)
    return paths[0], dry_run


# ── Load the export file ──────────────────────────────────────────────────────

def load_proposals(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f'File not found: {abs_path}')
        sys.exit(1)
    with open(abs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Accept a plain list or { proposals: [...] }
    return data if isinstance(data, list) else data.get('proposals', [])


# ── Check that the orgs table has the columns we need ────────────────────────

def ensure_columns(db):
    """Add website/email/description columns if the DB predates them."""
    for col, typedef in [('website', 'TEXT'), ('email', 'TEXT'), ('description', 'TEXT')]:
        try:
            db.execute(f'ALTER TABLE organizations ADD COLUMN {col} {typedef}')
            db.commit()
            print(f'  Migration: added organizations.{col}')
        except Exception:
            pass  # already exists


# ── Apply one proposal ────────────────────────────────────────────────────────

def apply_proposal(db, proposal, dry_run, log_lines, training_rows):
    org_id = proposal.get('id')
    if not org_id:
        print('  Skipping proposal with no id.')
        return 0

    row = db.execute('SELECT * FROM organizations WHERE id = ?', (org_id,)).fetchone()
    if not row:
        print(f'  Org id {org_id} not found in DB, skipping.')
        return 0

    force   = proposal.get('force', False)
    updates = {}

    for field in ('website', 'email', 'description'):
        new_val = (proposal.get(field) or proposal.get(f'proposed_{field}') or '').strip() or None
        if not new_val:
            continue
        existing = row[field] if field in row.keys() else None
        if existing and not force:
            # Do not overwrite an existing value
            continue
        updates[field] = new_val

    if not updates:
        print(f'  {row["name"] if "name" in row.keys() else org_id}: nothing new to apply.')
        return 0

    if not dry_run:
        set_clause = ', '.join(f'{k} = ?' for k in updates)
        values     = list(updates.values()) + [org_id]
        db.execute(f'UPDATE organizations SET {set_clause} WHERE id = ?', values)
        db.commit()

    org_name = row['name'] if 'name' in row.keys() else str(org_id)
    print(f'  Updated {org_name}: {list(updates.keys())}')

    # Build log entry
    fields_summary = ' | '.join(f'{k}: {v}' for k, v in updates.items())
    log_lines.append(f'- **{org_name}** (`{org_id}`) -- {fields_summary}')

    # Build training JSONL row
    training_rows.append({
        'org_id':            str(org_id),
        'org_name':          org_name,
        'country_code':      proposal.get('country_code'),
        'search_query':      proposal.get('search_query'),
        'found_website':     updates.get('website'),
        'found_email':       updates.get('email'),
        'found_description': updates.get('description'),
        'confidence':        proposal.get('confidence'),
        'human_verified':    True,
    })

    return 1


# ── Write logs ────────────────────────────────────────────────────────────────

def write_log(log_lines, dry_run):
    if not log_lines:
        return
    today    = datetime.utcnow().strftime('%Y-%m-%d')
    log_path = os.path.join(TRIM_AUDIT_DIR, f'enrichment-log-{today}.md')
    os.makedirs(TRIM_AUDIT_DIR, exist_ok=True)

    header = f'# Enrichment log {today}\n\nApplied by apply-enrichments.py\n\n'
    body   = '\n'.join(log_lines) + '\n'

    if not dry_run:
        # Append if file already exists (multiple runs same day)
        mode = 'a' if os.path.exists(log_path) else 'w'
        with open(log_path, mode, encoding='utf-8') as f:
            if mode == 'w':
                f.write(header)
            f.write(body)
        print(f'\nLog written to: {log_path}')
    else:
        print(f'\n[dry-run] Would write log to: {log_path}')


def write_training(training_rows, dry_run):
    if not training_rows:
        return
    training_dir  = os.path.join(DATA_DIR, 'training-data')
    training_path = os.path.join(training_dir, 'enrichment-training.jsonl')
    os.makedirs(training_dir, exist_ok=True)

    lines = [json.dumps(r, ensure_ascii=False) for r in training_rows]

    if not dry_run:
        with open(training_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'Training data appended to: {training_path}')
    else:
        print(f'[dry-run] Would append {len(lines)} rows to: {training_path}')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    file_path, dry_run = parse_args()

    proposals = load_proposals(file_path)
    print(f'Loaded {len(proposals)} accepted proposals from {file_path}')
    if dry_run:
        print('[dry-run mode - no DB changes will be made]\n')

    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    ensure_columns(db)

    log_lines    = []
    training_rows = []
    applied      = 0

    for proposal in proposals:
        verdict = proposal.get('verdict', 'accepted')
        if verdict != 'accepted':
            continue  # skip wrong/skipped entries that may have been included
        applied += apply_proposal(db, proposal, dry_run, log_lines, training_rows)

    db.close()

    write_log(log_lines, dry_run)
    write_training(training_rows, dry_run)

    print(f'\nDone. {applied} orgs updated{"" if not dry_run else " (dry-run)"}.')


if __name__ == '__main__':
    main()
