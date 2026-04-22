"""
Shared utilities for Commonweave pipeline scripts.
Import this instead of copying boilerplate across scripts.
"""
import os
import re
import sqlite3
import unicodedata
from datetime import datetime

DB_PATH = r'C:\Users\simon\.openclaw\workspace\commonweave\data\commonweave_directory.db'
TRIM_AUDIT_DIR = r'C:\Users\simon\.openclaw\workspace\commonweave\data\trim_audit'
WORKSPACE_DIR = r'C:\Users\simon\.openclaw\workspace'
DATA_DIR = r'C:\Users\simon\.openclaw\workspace\commonweave\data'


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def ensure_column(db, table, col, typedef):
    """Idempotent ALTER TABLE ADD COLUMN. Silent if already exists."""
    try:
        db.execute(f'ALTER TABLE {table} ADD COLUMN {col} {typedef}')
        db.commit()
        print(f'  Migration: added {table}.{col} ({typedef})')
    except Exception:
        pass  # Column already exists - that's fine


def trim_audit_path(prefix):
    """Return a dated log path like trim_audit/dedup-2026-04-22.md"""
    os.makedirs(TRIM_AUDIT_DIR, exist_ok=True)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return os.path.join(TRIM_AUDIT_DIR, f'{prefix}-{today}.md')


# Legal-form suffixes to strip when normalizing names for dedup
STRIP_SUFFIXES = [
    r'\binc\.?$', r'\bltd\.?$', r'\bltda\.?$', r'\bgmbh\.?$',
    r'\be\.v\.?$', r'\bev$', r'\bpvt\.?\s*ltd\.?$', r'\bsa$',
    r'\bsarl$', r'\bsrl$', r'\bsociete\s+cooperative$',
    r'\bcooperative$', r'\bcoop$', r'\bcoop\.$',
    r'\bassociation$', r'\bassoc\.?$', r'\bfoundation$',
    r'\btrust$', r'\bcharity$', r'\bngo$', r'\bnpo$',
    r'\bllc$', r'\bplc$', r'\bag$', r'\bbv$', r'\bnv$',
]

def normalize_name(name):
    """Lowercase, strip punctuation and common legal suffixes for dedup grouping."""
    if not name:
        return ''
    # Normalize unicode to ASCII-like
    n = unicodedata.normalize('NFD', name.lower())
    n = ''.join(c for c in n if unicodedata.category(c) != 'Mn')
    # Remove punctuation except spaces
    n = re.sub(r"[^\w\s]", ' ', n)
    # Strip each suffix
    for pat in STRIP_SUFFIXES:
        n = re.sub(pat, '', n, flags=re.IGNORECASE)
    # Collapse whitespace
    n = re.sub(r'\s+', ' ', n).strip()
    return n


# ── Alignment scoring (same as ingest_gov_registry.py) ────────────────────
# Import from the registry module when possible; replicate here as fallback.
def _load_align():
    try:
        import sys
        sys.path.insert(0, DATA_DIR)
        from ingest_gov_registry import ALIGNMENT_KEYWORDS, FRAMEWORK_KEYWORDS_ML
        from ingest_gov_registry import classify_org_ml
        return ALIGNMENT_KEYWORDS, FRAMEWORK_KEYWORDS_ML, classify_org_ml
    except ImportError:
        return None, None, None

ALIGNMENT_KEYWORDS, FRAMEWORK_KEYWORDS_ML, classify_org_ml = _load_align()

NONPROFIT_ENTITY_TYPES = {
    'cooperative', 'co-op', 'coop', 'mutual', 'foundation', 'trust',
    'charity', 'ngo', 'npo', 'credit union', 'microfinance',
    'genossenschaft', 'cooperativa', 'coopérative', 'mutuelle',
    'stiftung', 'stichting', 'forening', 'vereniging',
}

def is_nonprofit_entity_type(name):
    """True if the name contains a recognized nonprofit entity-type indicator."""
    low = name.lower()
    return any(t in low for t in NONPROFIT_ENTITY_TYPES)
