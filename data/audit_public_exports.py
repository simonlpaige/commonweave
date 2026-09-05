"""Audit every shipped directory row offline. No network, database writes or endorsement.

python data/audit_public_exports.py --as-of 2026-09-05 --output reports/data-audit-2026-09-05
Outputs a reproducible summary and a complete, gzip-compressed review queue. Queue
locators point back to the existing export; they do not republish contact details.
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import hashlib
import io
import ipaddress
import json
import math
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

ISO2 = set("AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split())
FRESH_DAYS = 180
INVITE_HOSTS = {"chat.whatsapp.com", "discord.gg", "t.me"}


def valid_url(value):
    """Syntactic public HTTP(S) URL check, never a claim that a site exists."""
    if not isinstance(value, str) or re.search(r"[\s\x00-\x1f\\]", value):
        return False
    try:
        url = urlsplit(value)
        host = (url.hostname or "").rstrip('.').encode('idna').decode('ascii').lower()
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            if host in {"localhost"} or host.endswith((".localhost", ".local", ".internal")):
                return False
            # Browsers accept abbreviated/octal/hex IP forms which ipaddress
            # intentionally rejects. Do not mistake those for public DNS names.
            if re.fullmatch(r'(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*', host):
                return False
            if len(host) > 253 or '.' not in host or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in host.split('.')):
                return False
        return (url.scheme in {"http", "https"} and bool(url.hostname)
                and not url.username and not url.password
                and url.port != 0)
    except (ValueError, UnicodeError):
        return False


def normalized_name(name):
    # Do not strip legal suffixes: co-located chapters can be distinct entities.
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", str(name or "")).casefold()))


def coordinate_state(lat, lon):
    if lat in (None, "") and lon in (None, ""):
        return "missing"
    if lat in (None, "") or lon in (None, ""):
        return "incomplete"
    try:
        if isinstance(lat, bool) or isinstance(lon, bool):
            return "invalid"
        a, b = float(lat), float(lon)
        if not math.isfinite(a) or not math.isfinite(b) or not (-90 <= a <= 90 and -180 <= b <= 180):
            return "invalid"
        return "zero_zero" if (a, b) == (0, 0) else "present"
    except (TypeError, ValueError):
        return "invalid"


def row_issues(row, as_of):
    issues = []
    if 'tier' in row and row['tier'] not in {'A', 'B', 'C', 'D'}:
        issues.append('invalid_record_tier')
    if not str(row.get("name") or "").strip():
        issues.append("missing_name")
    country = row.get("country_code") or ""
    if country not in ISO2:
        issues.append("non_iso_country" if country else "missing_country")
    for key in ("website", "evidence_url"):
        value = row.get(key)
        if not value:
            issues.append("missing_" + key)
        elif not valid_url(value):
            issues.append("invalid_" + key)
    if not row.get("source"):
        issues.append("missing_source")
    if not row.get("description") or len(str(row["description"]).strip()) < 40:
        issues.append("thin_description")
    if not row.get("framework_area") or row.get("framework_area") == "unknown":
        issues.append("missing_framework_area")
    if not row.get("evidence_quote"):
        issues.append("missing_evidence_excerpt")
    verified = row.get("last_verified_at")
    if not verified:
        issues.append("verification_date_unknown")
    else:
        try:
            age = (as_of - datetime.fromisoformat(str(verified).replace("Z", "+00:00")).date()).days
            if age < 0:
                issues.append("verification_date_future")
            elif age > FRESH_DAYS:
                issues.append("verification_date_older_than_180_days")
        except (TypeError, ValueError):
            issues.append("verification_date_invalid")
    coords = coordinate_state(row.get("lat"), row.get("lon"))
    if coords != "present":
        issues.append("coordinates_" + coords)
    elif not row.get("location_precision"):
        issues.append("coordinate_precision_unknown")
    if valid_url(row.get("website")) and urlsplit(row["website"]).hostname in INVITE_HOSTS:
        issues.append("invite_link_visibility_review")
    return issues


def compact_stats(rows, as_of, dataset, queue):
    counts, countries, sources, areas = (collections.Counter() for _ in range(4))
    names = collections.defaultdict(list)
    identifiers = collections.defaultdict(list)
    for index, row in enumerate(rows):
        issues = row_issues(row, as_of)
        countries[row.get("country_code") or "(missing)"] += 1
        sources[row.get("source") or "(missing)"] += 1
        areas[row.get("framework_area") or "(missing)"] += 1
        locator = row.get("_locator", str(index))
        if issues:
            counts.update(issues)
            queue.append((dataset, locator, row.get("id", ""), "|".join(issues)))
        name = normalized_name(row.get("name"))
        if name:
            names[(row.get("country_code") or "", name)].append(locator)
        if row.get("id") is not None:
            identifiers[str(row["id"])].append(locator)
    duplicates = [v for v in names.values() if len(v) > 1]
    for group in duplicates:
        for locator in group:
            queue.append((dataset, locator, "", "same_country_normalized_name_review"))
    id_duplicates = [v for v in identifiers.values() if len(v) > 1]
    return {"rows": len(rows), "country_codes": len(countries),
            "iso_country_codes": len(set(countries) & ISO2),
            "countries": dict(countries.most_common()), "sources": dict(sources.most_common()),
            "framework_areas": dict(areas.most_common()), "issues": dict(sorted(counts.items())),
            "same_name_country_groups": len(duplicates),
            "same_name_country_rows": sum(map(len, duplicates)),
            "duplicate_id_groups": len(id_duplicates),
            "rows_in_top_two_countries": sum(n for _, n in countries.most_common(2)),
            "countries_with_fewer_than_50_rows": sum(n < 50 for c, n in countries.items() if c in ISO2)}


def content_hash(row):
    # Normalize CSV nulls and numeric scalars for equivalent JSON/CSV comparison.
    text = json.dumps({k: "" if v is None else str(v).replace("\r\n", "\n") for k, v in row.items()}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()


def audit(repo, as_of):
    queue = []
    with gzip.open(repo / "releases/organizations.json.gz", "rt", encoding="utf-8") as f:
        release = json.load(f)
    summary = {"schema_version": 1, "as_of": as_of.isoformat(),
               "method": "Complete offline structural audit; no organization existence, services, alignment, location or relationships verified.",
               "release": compact_stats(release, as_of, "release", queue)}
    manifest = json.loads((repo / "releases/MANIFEST.json").read_text(encoding="utf-8"))
    summary["release"]["manifest_generated_at"] = manifest.get("generated_at")
    summary["release"]["manifest_row_count"] = manifest.get("row_count")
    json_hashes = collections.Counter(content_hash(r) for r in release)
    with gzip.open(repo / "releases/organizations.csv.gz", "rt", encoding="utf-8", newline="") as f:
        csv_hashes = collections.Counter(content_hash(r) for r in csv.DictReader(f))
    summary["release"]["csv_json_content_equal"] = csv_hashes == json_hashes
    summary["release"]["split_integrity"] = {}
    for directory in ("by-country", "by-source"):
        hashes, file_count = collections.Counter(), 0
        for path in sorted((repo / "releases" / directory).glob("*.csv")):
            file_count += 1
            with path.open(encoding="utf-8", newline="") as f:
                hashes.update(content_hash(row) for row in csv.DictReader(f))
        summary["release"]["split_integrity"][directory] = {
            "files": file_count, "rows": sum(hashes.values()), "same_content_as_full_release": hashes == json_hashes,
            "extra_or_changed_rows": sum((hashes - json_hashes).values()),
            "missing_or_changed_rows": sum((json_hashes - hashes).values())}

    index = json.loads((repo / "data/search/index.json").read_text(encoding="utf-8"))
    search, files, mismatches = [], [], []
    for path in sorted((repo / "data/search").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        orgs = payload.get("orgs", payload.get("organizations")) if isinstance(payload, dict) else None
        if orgs is None:
            continue
        country = payload.get("country_code") or ("US" if path.stem.startswith("US_") else path.stem)
        files.append({"path": path.relative_to(repo).as_posix(), "rows": len(orgs), "country": country})
        if payload.get("count", len(orgs)) != len(orgs):
            mismatches.append({"path": path.name, "declared": payload["count"], "actual": len(orgs)})
        for i, row in enumerate(orgs):
            search.append({"_locator": f"{path.name}#orgs/{i}",
                           "id": row.get("id"),
                           "name": row.get("n", row.get("name")), "country_code": country,
                           "description": row.get("d", row.get("description")),
                           "website": row.get("w", row.get("website")),
                           "source": row.get("src", row.get("source")),
                           "evidence_url": row.get("evidence_url", row.get("source_url")),
                           "evidence_quote": row.get("evidence_quote"),
                           "last_verified_at": row.get("last_verified_at"),
                           "framework_area": row.get("f", row.get("framework_area"))})
    summary["search"] = compact_stats(search, as_of, "search", queue)
    actual_counts = collections.Counter(r["country_code"] for r in search)
    summary["search"].update({"index_generated_at": index.get("generated"), "index_total": index.get("total_orgs"),
                              "files": files, "file_count_mismatches": mismatches,
                              "index_country_mismatches": [{"country": cc, "index": info["count"], "actual": actual_counts[cc]}
                                  for cc, info in index["countries"].items() if info["count"] != actual_counts[cc]],
                              "unindexed_country_files": sorted(set(actual_counts) - set(index["countries"]))})
    summary["search"]["indexed_countries_without_shards"] = sorted(set(index["countries"]) - set(actual_counts))

    geo = json.loads((repo / "data/map/orgs.geojson").read_text(encoding="utf-8"))
    points, positions = [], collections.defaultdict(list)
    for i, feature in enumerate(geo["features"]):
        prop = feature.get("properties", {})
        coordinates = (feature.get("geometry") or {}).get("coordinates", [])
        lon, lat = coordinates[:2] if len(coordinates) >= 2 else (None, None)
        row = {"_locator": str(i), "id": feature.get("id", prop.get("id")), "name": prop.get("n"),
               "country_code": prop.get("cc"), "source": prop.get("src"), "framework_area": prop.get("f"),
               "website": prop.get("w"), "description": prop.get("d"), "lat": lat, "lon": lon, "tier": prop.get("t"),
               "evidence_url": prop.get("evidence_url", prop.get("source_url")),
               "last_verified_at": prop.get("last_verified_at"), "location_precision": prop.get("location_precision")}
        points.append(row)
        if coordinate_state(lat, lon) == "present":
            positions[(round(float(lat), 4), round(float(lon), 4))].append(row)
    summary["map"] = compact_stats(points, as_of, "map", queue)
    hotspots = sorted(positions.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    summary["map"]["coordinate_groups_with_at_least_10_rows"] = sum(len(v) >= 10 for v in positions.values())
    summary["map"]["rows_at_shared_coordinates_10_plus"] = sum(len(v) for v in positions.values() if len(v) >= 10)
    summary["map"]["largest_coordinate_groups"] = [
        {"lat": p[0], "lon": p[1], "rows": len(rows), "countries": dict(collections.Counter(r["country_code"] for r in rows))}
        for p, rows in hotspots[:20]]
    summary["map"]["cross_country_coordinate_groups"] = sum(len({r["country_code"] for r in v}) > 1 for v in positions.values())
    for position, members in positions.items():
        if len(members) >= 10 or len({r["country_code"] for r in members}) > 1:
            for row in members:
                queue.append(("map", row["_locator"], row["id"], "shared_coordinate_precision_review"))
    edges = json.loads((repo / "data/map/edges.json").read_text(encoding="utf-8"))
    ids = {str(row["id"]) for row in points}
    dangling, edge_types, missing_evidence = 0, collections.Counter(), 0
    for edge in edges:
        edge_types[edge.get("edge_type", edge.get("type", "unknown"))] += 1
        ends = (edge.get("source_id", edge.get("source", edge.get("a"))),
                edge.get("target_id", edge.get("target", edge.get("b"))))
        if any(str(x) not in ids for x in ends):
            dangling += 1
        evidence = edge.get("evidence") or []
        has_evidence = any(isinstance(item, dict) and item.get("type") == "url" and valid_url(item.get("value")) for item in evidence)
        if not valid_url(edge.get("evidence_url")) and not valid_url(edge.get("source_url")) and not has_evidence:
            missing_evidence += 1
    summary["map"]["edges"] = {"rows": len(edges), "types": dict(edge_types), "dangling_endpoints": dangling,
                                    "without_evidence_url": missing_evidence}
    summary["map"]["metadata"] = {filename: json.loads((repo / "data/map" / filename).read_text(encoding="utf-8"))
                                      for filename in ("stats.json", "stats.v3.json")}
    summary["review_queue_entries"] = len(queue)
    summary["input_sha256"] = {path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [repo / "releases/organizations.json.gz", repo / "releases/organizations.csv.gz",
                     repo / "data/search/index.json", repo / "data/map/orgs.geojson", repo / "data/map/edges.json"]}
    return summary, queue


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary, queue = audit(args.repo.resolve(), args.as_of)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # mtime=0 makes identical audits byte-identical; no live contact fields in queue.
    with (args.output / "review-queue.csv.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as text:
                writer = csv.writer(text)
                writer.writerow(["dataset", "locator", "id", "review_reasons"])
                writer.writerows(queue)
    print(json.dumps({key: summary[key]["rows"] for key in ("release", "search", "map")}))
    print(f"Wrote summary and {len(queue):,} review queue entries to {args.output}")


if __name__ == "__main__":
    main()
