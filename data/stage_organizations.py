"""Validate evidence-backed discovery/corrections; apply only into a NEW DB copy.

Validation is default and makes no writes. --db opens an existing DB read-only.
--output-db creates a review copy; never mutates source or public exports.
Evidence is attached to changed fields, never converted into `human_verified`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from audit_public_exports import ISO2, coordinate_state, normalized_name, valid_url

FIELDS = {"name", "description", "website", "country_code", "city", "state_province",
          "framework_area", "model_type", "source", "legibility", "lat", "lon"}
AREAS = {"democracy", "healthcare", "education", "food", "housing_land", "housing",
         "ecology", "cooperatives", "recreation_arts", "recreation-arts", "energy_digital",
         "energy-digital", "conflict-resolution", "conflict_resolution", "unknown"}


def validate(proposals, as_of=None, require_accepted=False):
    as_of = as_of or date.today()
    if not isinstance(proposals, list) or not proposals:
        raise ValueError("proposals must be a nonempty array")
    ids = set()
    for p in proposals:
        if not isinstance(p, dict):
            raise ValueError("Every proposal must be an object")
        pid = p.get("proposal_id")
        if not isinstance(pid, str) or not pid.strip() or pid in ids:
            raise ValueError("A unique proposal_id is required")
        ids.add(pid)
        if p.get("operation") not in ("add", "update"):
            raise ValueError(f"{pid}: operation must be add or update")
        changes = p.get("changes")
        if not isinstance(changes, dict) or not changes or set(changes) - FIELDS:
            raise ValueError(f"{pid}: missing changes or unsupported field (scores/status/tier cannot be promoted)")
        if p["operation"] == "add":
            if not {"name", "country_code", "description", "source"} <= changes.keys():
                raise ValueError(f"{pid}: new candidates need name, country_code, description, source")
            if len(str(changes["description"]).strip()) < 40:
                raise ValueError(f"{pid}: write a specific description of at least 40 characters")
        else:
            if not isinstance(p.get("organization_id"), (str, int)) or isinstance(p.get("organization_id"), bool) or not str(p["organization_id"]).strip() or not isinstance(p.get("expected"), dict) or set(p["expected"]) != set(changes):
                raise ValueError(f"{pid}: update requires organization_id and expected old value for every changed field")
        for key, value in changes.items():
            if key in {"lat", "lon"} and value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)):
                raise ValueError(f"{pid}: {key} must be a number or null")
            if key not in {"lat", "lon"} and value is not None and not isinstance(value, str):
                raise ValueError(f"{pid}: {key} must be text or null")
            if key in {"name", "description", "source"} and not str(value or "").strip():
                raise ValueError(f"{pid}: {key} cannot be empty")
        if "website" in changes and changes["website"] and not valid_url(changes["website"]):
            raise ValueError(f"{pid}: website must be a public HTTP(S) URL")
        if "country_code" in changes and changes["country_code"] not in ISO2:
            raise ValueError(f"{pid}: country_code must be ISO alpha-2; store service scope separately")
        if "framework_area" in changes and changes["framework_area"] not in AREAS:
            raise ValueError(f"{pid}: unknown framework_area; do not silently invent taxonomy")
        if "legibility" in changes and changes["legibility"] not in {"formal", "hybrid", "informal", "unknown"}:
            raise ValueError(f"{pid}: invalid legibility")
        safety = p.get("visibility_review", {})
        if not isinstance(safety, dict) or safety.get("decision") not in ("public", "country_only", "withhold") or not isinstance(safety.get("reason"), str) or not safety["reason"].strip():
            raise ValueError(f"{pid}: visibility_review decision and reasoning required")
        if safety["decision"] == "withhold":
            raise ValueError(f"{pid}: withheld organizations must not enter the public pipeline")
        if safety["decision"] == "country_only" and any(changes.get(k) not in (None, "") for k in ("lat", "lon", "city", "state_province")):
            raise ValueError(f"{pid}: country_only disallows detailed location")
        if "lat" in changes or "lon" in changes:
            if not {"lat", "lon"} <= changes.keys():
                raise ValueError(f"{pid}: change latitude and longitude together")
            if coordinate_state(changes["lat"], changes["lon"]) not in {"present", "missing"}:
                raise ValueError(f"{pid}: invalid/ambiguous coordinates")
            if changes["lat"] is not None and p.get("location_precision") not in ("premises", "city", "region"):
                raise ValueError(f"{pid}: source-supported location_precision required")
        reuse = p.get("reuse", {})
        if not isinstance(reuse, dict) or reuse.get("basis") not in ("open_license", "permission", "original_factual_summary") or not valid_url(reuse.get("url")):
            raise ValueError(f"{pid}: explicit reuse basis and URL required; public visibility is not permission to copy a database")
        evidence = p.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"{pid}: evidence required")
        covered = set()
        for e in evidence:
            if not isinstance(e, dict) or not valid_url(e.get("url")) or not isinstance(e.get("excerpt"), str) or not e["excerpt"].strip():
                raise ValueError(f"{pid}: evidence needs a public URL and short supporting excerpt")
            if not isinstance(e.get("fields"), list) or not e["fields"] or any(not isinstance(field, str) for field in e["fields"]) or set(e["fields"]) - set(changes):
                raise ValueError(f"{pid}: evidence.fields must identify changed fields")
            try:
                checked = date.fromisoformat(e.get("checked_at", ""))
            except (ValueError, TypeError):
                raise ValueError(f"{pid}: evidence.checked_at must be YYYY-MM-DD") from None
            if checked > as_of or (as_of - checked).days > 180:
                raise ValueError(f"{pid}: evidence must be checked within 180 days, not in the future")
            covered.update(e["fields"])
        if set(changes) - covered:
            raise ValueError(f"{pid}: every changed field needs supporting evidence")
        review = p.get("review", {})
        if not isinstance(review, dict) or review.get("decision") not in ("pending", "accepted"):
            raise ValueError(f"{pid}: explicit pending or accepted review required")
        if require_accepted and review["decision"] != 'accepted':
            raise ValueError(f"{pid}: accepted review required before writing a database copy")
        if review["decision"] == 'accepted' and (not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip()):
            raise ValueError(f"{pid}: accepted review requires a named reviewer")
    return proposals


def check_against_db(db, proposals):
    db.row_factory = sqlite3.Row
    schema = list(db.execute("PRAGMA table_info(organizations)"))
    columns = {row[1] for row in schema}
    if not {"id", "name", "country_code", "status", "tier"} <= columns:
        raise ValueError("Database lacks supported identity/status/tier schema")
    primary_key = [row for row in schema if row[5]]
    integer_id = (len(primary_key) == 1 and primary_key[0][1] == 'id'
                  and primary_key[0][2].upper() == 'INTEGER')
    seen_targets = set()
    known_names = {(row["country_code"], normalized_name(row["name"])) for row in db.execute("SELECT name, country_code FROM organizations")}
    plans = []
    for p in proposals:
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='organization_evidence'").fetchone():
            if db.execute("SELECT 1 FROM organization_evidence WHERE proposal_id=?", (p['proposal_id'],)).fetchone():
                raise ValueError(f"{p['proposal_id']}: already applied; no duplicate evidence or mutation")
        if set(p["changes"]) - columns:
            raise ValueError(f"{p['proposal_id']}: database lacks fields {sorted(set(p['changes']) - columns)}")
        if p["operation"] == "update":
            oid = str(p["organization_id"])
            if oid in seen_targets:
                raise ValueError("Combine changes to the same organization into one proposal")
            row = db.execute("SELECT * FROM organizations WHERE id = ?", (oid,)).fetchone()
            if row is None or any(row[k] != value for k, value in p["expected"].items()):
                raise ValueError(f"{p['proposal_id']}: record missing or expected values conflict; re-review current record")
            if p["visibility_review"]["decision"] == "country_only":
                final = dict(row) | p["changes"]
                if any(final.get(k) not in (None, "") for k in ("lat", "lon", "city", "state_province")):
                    raise ValueError(f"{p['proposal_id']}: country_only must clear existing detailed location")
        else:
            candidate = p["changes"]
            key = candidate["country_code"], normalized_name(candidate["name"])
            if key in known_names:
                raise ValueError(f"{p['proposal_id']}: same country/name already exists; resolve identity before adding")
            known_names.add(key)
            # The canonical schema uses INTEGER PRIMARY KEY. Let SQLite allocate
            # that ID and retain its proposal mapping in organization_evidence.
            # Text-ID schemas retain the deterministic proposal-qualified ID.
            oid = None if integer_id else "candidate_" + hashlib.sha256(p["proposal_id"].encode()).hexdigest()[:20]
            if oid is not None and db.execute("SELECT 1 FROM organizations WHERE id=?", (oid,)).fetchone():
                raise ValueError(f"{p['proposal_id']}: already present")
        if oid is not None:
            seen_targets.add(oid)
        plans.append((oid, p))
    return plans


def create_review_copy(source, destination, proposals, as_of=None):
    validate(proposals, as_of, require_accepted=True)
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or destination.exists():
        raise ValueError("output-db must be a new file, distinct from the source")
    # mode=ro prevents creation of a typo/empty source database.
    db = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    try:
        plans = check_against_db(db, proposals)
        # Exclusive creation avoids overwriting even if another process won a race.
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb"):
            pass
        target = sqlite3.connect(destination)
        try:
            db.backup(target)
            with target:
                target.execute('BEGIN IMMEDIATE')
                # A source could change between the first validation and backup.
                # Preconditions must hold in the exact snapshot being changed.
                plans = check_against_db(target, proposals)
                target.execute("CREATE TABLE IF NOT EXISTS organization_evidence (proposal_id TEXT PRIMARY KEY, organization_id TEXT NOT NULL, payload_json TEXT NOT NULL, applied_at TEXT NOT NULL)")
                columns = {row[1] for row in target.execute('PRAGMA table_info(organizations)')}
                if 'location_precision' not in columns and any('lat' in p['changes'] for _, p in plans):
                    # Preserve precision for exporters without migrating the source.
                    # This schema change belongs to the same review transaction.
                    target.execute('ALTER TABLE organizations ADD COLUMN location_precision TEXT')
                for oid, proposal in plans:
                    updates = dict(proposal["changes"])
                    if 'lat' in updates:
                        updates['location_precision'] = proposal.get('location_precision') if updates['lat'] is not None else None
                    if proposal["operation"] == "add":
                        record = {**updates, "status": "candidate", "tier": "D"}
                        if oid is not None:
                            record['id'] = oid
                        inserted = target.execute(f"INSERT INTO organizations ({','.join(record)}) VALUES ({','.join('?' for _ in record)})", list(record.values()))
                        if oid is None:
                            oid = inserted.lastrowid
                    else:
                        target.execute(f"UPDATE organizations SET {','.join(k+'=?' for k in updates)} WHERE id=?", [*updates.values(), oid])
                    target.execute("INSERT INTO organization_evidence VALUES (?,?,?,?)", (
                        proposal["proposal_id"], oid, json.dumps(proposal, sort_keys=True, ensure_ascii=False), datetime.now(timezone.utc).isoformat()))
        except Exception:
            target.close()
            destination.unlink()  # Only the new review copy created above.
            raise
        finally:
            target.close()
    finally:
        db.close()
    return len(plans)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proposals", type=Path)
    parser.add_argument("--db", type=Path, help="existing source DB; opened read-only")
    parser.add_argument("--output-db", type=Path, help="new review copy; source is never modified")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        data = json.loads(args.proposals.read_text(encoding="utf-8"))
        proposals = data.get("proposals") if isinstance(data, dict) else data
        validate(proposals, args.as_of)
        if args.output_db:
            if not args.db:
                raise ValueError("--output-db requires --db")
            count = create_review_copy(args.db, args.output_db, proposals, args.as_of)
            print(f"{count} reviewed proposals written to NEW database copy: {args.output_db}")
        else:
            if args.db:
                with sqlite3.connect(args.db.resolve().as_uri() + "?mode=ro", uri=True) as db:
                    check_against_db(db, proposals)
            print(f"{len(proposals)} proposals structurally valid. No writes; evidence requires reviewer judgment.")
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(2, f"Rejected: {error}\n")


if __name__ == "__main__":
    main()
