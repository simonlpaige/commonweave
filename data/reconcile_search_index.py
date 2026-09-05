"""Reconcile public search metadata against actual shipped shards, without a DB.

No organization records are changed. Run after a search export, or with --check
in CI. Country names are reused from existing metadata; counts come from arrays.
"""
import argparse
import json
from pathlib import Path
from audit_public_exports import ISO2


def inventory(directory):
    directory = Path(directory)
    old = json.loads((directory / "index.json").read_text(encoding="utf-8"))
    countries, states = {}, {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("orgs"), list):
            continue
        if not payload["orgs"]:
            continue
        state = payload.get("state") if path.stem.startswith("US_") else None
        code = "US" if state else payload.get("country_code", path.stem)
        if code not in ISO2:
            continue
        if code == "US" and not state:
            raise ValueError("Both whole-US and state export forms would double-count records; resolve shards first")
        country = countries.setdefault(code, {"name": old.get("countries", {}).get(code, {}).get("name")
            or payload.get("country_name") or code, "count": 0, "source": "public_export", "has_data": True})
        country["count"] += len(payload["orgs"])
        if state:
            states[state] = {"name": payload.get("name", state), "count": len(payload["orgs"])}
    result = dict(old)
    result.update({"total_orgs": sum(c["count"] for c in countries.values()), "total_countries": len(countries),
                   "countries": dict(sorted(countries.items(), key=lambda item: (-item[1]["count"], item[0]))),
                   "count_basis": "Actual orgs arrays in shipped country/state JSON files; candidate rows, not verified organizations.",
                   "inventory_script": "data/reconcile_search_index.py",
                   "provenance_note": "generated identifies the export build time; metadata reconciliation does not reverify organizations."})
    us = json.loads((directory / "US_meta.json").read_text(encoding="utf-8"))
    us["states"] = states
    us["total"] = countries.get("US", {}).get("count", 0)
    return result, us


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parent / "search")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    index, us = inventory(args.directory)
    expected = {"index.json": index, "US_meta.json": us}
    drift = [name for name, content in expected.items()
             if json.loads((args.directory / name).read_text(encoding="utf-8")) != content]
    if args.check:
        if drift:
            parser.exit(1, "Search metadata differs from shipped records: " + ", ".join(drift) + "\n")
        print(f"Search metadata matches {index['total_orgs']:,} candidate rows in {index['total_countries']} countries/territories")
        return
    for name, content in expected.items():
        path = args.directory / name
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(content, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        temp.replace(path)
    print(f"Reconciled {index['total_orgs']:,} rows in {index['total_countries']} countries/territories; no organization records changed")


if __name__ == "__main__":
    main()
