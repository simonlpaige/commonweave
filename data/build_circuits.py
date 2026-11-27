"""
build_circuits.py: validate data/circuits.yaml and regenerate everything that
is derived from it.

    python data/build_circuits.py           # write outputs
    python data/build_circuits.py --check   # fail if any output is stale
    python data/build_circuits.py --sample 10 > sample.tsv   # rows for a precision review

Inputs (all committed, none modified):
    data/circuits.yaml                      role rules and circuit definitions
    releases/organizations.json.gz          the published release
    releases/MANIFEST.json                  release date, for provenance
    data/map/orgs.geojson                   published map points
    data/state_province_map.json            region name variants
    data/audit/circuit-role-precision.json  optional reviewed samples

Outputs:
    data/map/circuit-coverage.json   counts only; no organization names
    assets/js/map/circuits-data.js   goals and role rules for the map
    SOLUTION-CIRCUITS.md             the readable catalogue

Outputs are deterministic. They carry the release date, not the build time, so
`--check` can compare bytes.

What coverage means here: a locality "has" a role when at least one published
record with that recorded city matches the role rule. Recorded cities can be
wrong, a rule match is not a confirmed activity, and nothing here says that the
organizations know each other. Coverage is a list of places worth a closer
look, and a list of roles the directory cannot currently find.
"""
import argparse
import gzip
import hashlib
import json
import os
import random
import sys
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:  # pragma: no cover
    print('PyYAML required: pip install pyyaml', file=sys.stderr)
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from circuit_match import Record, normalize, role_matches, validate_role  # noqa: E402

SPEC_PATH = os.path.join(ROOT, 'data', 'circuits.yaml')
RELEASE_PATH = os.path.join(ROOT, 'releases', 'organizations.json.gz')
MANIFEST_PATH = os.path.join(ROOT, 'releases', 'MANIFEST.json')
MAP_POINTS_PATH = os.path.join(ROOT, 'data', 'map', 'orgs.geojson')
REGIONS_PATH = os.path.join(ROOT, 'data', 'state_province_map.json')
PRECISION_PATH = os.path.join(ROOT, 'data', 'audit', 'circuit-role-precision.json')

COVERAGE_OUT = os.path.join(ROOT, 'data', 'map', 'circuit-coverage.json')
JS_OUT = os.path.join(ROOT, 'assets', 'js', 'map', 'circuits-data.js')
MD_OUT = os.path.join(ROOT, 'SOLUTION-CIRCUITS.md')

EVIDENCE_LEVELS = {
    'combination_documented': 'Combination documented',
    'components_documented': 'Parts documented separately',
    'hypothesis': 'Hypothesis, no checked precedent',
}
VALID_MAP_TIERS = ('A', 'B', 'C')
TOP_LOCALITIES = 12
# A locality needs at least this many distinct candidates in every role before
# it is named in the public coverage file. One candidate per role is too easy
# to reach through a single mislabelled record.
MIN_PER_ROLE_TO_NAME = 1


def load_spec(path=SPEC_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_spec(spec):
    """Return a list of problems. An empty list means the file is usable."""
    problems = []
    roles = spec.get('roles') or {}
    circuits = spec.get('circuits') or []
    if spec.get('schema_version') != 1:
        problems.append('schema_version must be 1')
    for key, role in roles.items():
        if not role.get('label'):
            problems.append(f'role {key}: missing label')
        problems.extend(validate_role(key, role))
    seen = set()
    used_roles = set()
    for c in circuits:
        cid = c.get('id', '?')
        if cid in seen:
            problems.append(f'circuit {cid}: duplicate id')
        seen.add(cid)
        for field in ('id', 'name', 'goal', 'problem', 'evidence', 'falsifier'):
            if not c.get(field):
                problems.append(f'circuit {cid}: missing {field}')
        if c.get('evidence') not in EVIDENCE_LEVELS:
            problems.append(f'circuit {cid}: evidence must be one of {sorted(EVIDENCE_LEVELS)}')
        steps = c.get('roles') or []
        if len(steps) < 2:
            problems.append(f'circuit {cid}: needs at least two roles')
        step_roles = [s.get('role') for s in steps]
        if len(set(step_roles)) != len(step_roles):
            problems.append(f'circuit {cid}: a role is listed twice')
        for s in steps:
            if s.get('role') not in roles:
                problems.append(f'circuit {cid}: unknown role {s.get("role")!r}')
            used_roles.add(s.get('role'))
            for field in ('label', 'question'):
                if not s.get(field):
                    problems.append(f'circuit {cid}: role {s.get("role")} missing {field}')
        precedents = c.get('precedents') or []
        if c.get('evidence') != 'hypothesis' and not precedents:
            problems.append(f'circuit {cid}: evidence level {c.get("evidence")} needs at least one precedent')
        if c.get('evidence') == 'hypothesis' and precedents:
            problems.append(f'circuit {cid}: has precedents, so evidence should not be "hypothesis"')
        for p in precedents:
            for field in ('name', 'place', 'finding', 'source', 'checked'):
                if not p.get(field):
                    problems.append(f'circuit {cid}: precedent {p.get("name", "?")} missing {field}')
            if not str(p.get('source', '')).startswith('https://'):
                problems.append(f'circuit {cid}: precedent {p.get("name", "?")} source must be an https URL')
        for lim in c.get('limits') or []:
            if not lim.get('finding') or not str(lim.get('source', '')).startswith('https://'):
                problems.append(f'circuit {cid}: every limit needs a finding and an https source')
    for key in roles:
        if key not in used_roles:
            problems.append(f'role {key}: not used by any circuit')
    return problems


# --------------------------------------------------------------------------
# Loading published data
# --------------------------------------------------------------------------

def load_release():
    with gzip.open(RELEASE_PATH, 'rt', encoding='utf-8') as f:
        rows = json.load(f)
    return [Record.from_release(r) for r in rows]


def load_map_points():
    with open(MAP_POINTS_PATH, 'r', encoding='utf-8') as f:
        features = json.load(f)['features']
    return [Record.from_map_point(ft['properties']) for ft in features
            if ft['properties'].get('t') in VALID_MAP_TIERS]


def load_region_lookup():
    """(country, normalized variant) -> subdivision code, e.g. ('US','vermont') -> 'VT'."""
    with open(REGIONS_PATH, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    lookup = {}
    for code, variants in raw.items():
        if code.startswith('_') or '-' not in code:
            continue
        country, sub = code.split('-', 1)
        lookup[(country, normalize(sub))] = sub
        for v in variants:
            lookup[(country, normalize(v))] = sub
    return lookup


def locality_of(rec, region_lookup):
    """Return (country, region, city) or None when no usable city is recorded.

    'Saint Paul, MN' style values are split when the tail is a known region.
    """
    country = (rec.country or '').strip().upper()
    city = (rec.city or '').strip()
    region = (rec.region or '').strip()
    if not country or len(country) != 2 or not city or city.lower() == 'none':
        return None
    if ',' in city:
        head, tail = city.rsplit(',', 1)
        sub = region_lookup.get((country, normalize(tail)))
        if sub and head.strip():
            city, region = head.strip(), region or sub
    region = region_lookup.get((country, normalize(region)), region if region.lower() != 'none' else '')
    city_n = normalize(city)
    if not city_n:
        return None
    return (country, region, city_n)


def display_city(city_n):
    return ' '.join(w.capitalize() for w in city_n.split())


# --------------------------------------------------------------------------
# Coverage
# --------------------------------------------------------------------------

def match_roles(records, roles):
    """role key -> list of matching records."""
    return {key: [r for r in records if role_matches(role, r)] for key, role in roles.items()}


def build_coverage(spec, release, map_points, manifest):
    roles = spec['roles']
    region_lookup = load_region_lookup()
    by_role = match_roles(release, roles)
    map_by_role = match_roles(map_points, roles)

    role_summary = {}
    # role -> locality -> set of distinct normalized names
    role_localities = {}
    role_countries = {}
    for key in roles:
        recs = by_role[key]
        locs = defaultdict(set)
        countries = defaultdict(set)
        for r in recs:
            name_n = normalize(r.name)
            cc = (r.country or '').strip().upper()
            if len(cc) == 2:
                countries[cc].add(name_n)
            loc = locality_of(r, region_lookup)
            if loc:
                locs[loc].add(name_n)
        role_localities[key] = locs
        role_countries[key] = countries
        role_summary[key] = {
            'label': roles[key]['label'],
            'release_records': len(recs),
            'release_distinct_names': len({(r.country, normalize(r.name)) for r in recs}),
            'release_with_locality': sum(1 for r in recs if locality_of(r, region_lookup)),
            'countries': len(countries),
            'top_countries': [[cc, len(names)] for cc, names in
                              sorted(countries.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:5]],
            'map_points': len(map_by_role[key]),
        }

    circuits_out = []
    for c in spec['circuits']:
        keys = [s['role'] for s in c['roles']]
        all_localities = set()
        for k in keys:
            all_localities.update(role_localities[k])
        complete, one_short = [], Counter()
        for loc in all_localities:
            counts = [len(role_localities[k].get(loc, ())) for k in keys]
            missing = [k for k, n in zip(keys, counts) if n == 0]
            if not missing:
                complete.append((loc, counts))
            elif len(missing) == 1:
                one_short[missing[0]] += 1
        complete.sort(key=lambda lc: (-min(lc[1]), -sum(lc[1]), lc[0]))
        countries_complete = sorted(
            cc for cc in set().union(*[set(role_countries[k]) for k in keys])
            if all(cc in role_countries[k] for k in keys))
        entry = {
            'id': c['id'],
            'name': c['name'],
            'evidence': c['evidence'],
            'roles': keys,
            'countries_with_every_role': countries_complete,
            'localities_with_any_role': len(all_localities),
            'localities_with_every_role': len(complete),
            'localities_missing_exactly_one_role': {k: one_short.get(k, 0) for k in keys},
            'role_most_often_missing': (max(keys, key=lambda k: (one_short.get(k, 0), -keys.index(k)))
                                         if one_short else None),
        }
        if c.get('sensitive'):
            entry['localities'] = []
            entry['localities_withheld'] = 'Circuit is marked sensitive; only country-level coverage is published.'
        else:
            entry['localities'] = [
                {'country': loc[0], 'region': loc[1], 'city': display_city(loc[2]),
                 'candidates_per_role': dict(zip(keys, counts))}
                for loc, counts in complete[:TOP_LOCALITIES]
                if min(counts) >= MIN_PER_ROLE_TO_NAME]
        circuits_out.append(entry)

    return {
        'schema_version': 1,
        'source_script': 'data/build_circuits.py',
        'inputs': {
            'circuits': 'data/circuits.yaml',
            'release': 'releases/organizations.json.gz',
            'release_generated_at': manifest.get('generated_at'),
            'release_rows': len(release),
            'release_sha256': sha256_of(RELEASE_PATH),
            'map_points': 'data/map/orgs.geojson',
            'map_points_with_valid_tier': len(map_points),
        },
        'note': (
            'Counts of published records that match role rules, grouped by recorded city. '
            'A match is a research lead, not a confirmed activity; recorded cities can be wrong; '
            'no relationship between organizations is implied. No organization is named here.'
        ),
        'roles': role_summary,
        'circuits': circuits_out,
    }


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------

MAP_FIELDS = ('model', 'source', 'area', 'name', 'text')


def map_rule(role):
    """Reduce a role rule to the clauses the map can evaluate.

    Map points carry name, model, source and category only. A clause that
    needs a field the map does not have (NTEE code, registration type, tag)
    can never match there, so it is dropped from any_of. Exclusions are kept
    only when fully evaluable; `text` falls back to the name.
    """
    def usable(clause):
        return all(f in MAP_FIELDS for f in clause)

    def convert(clause):
        out = {}
        for f, wanted in clause.items():
            out['name' if f == 'text' else f] = [normalize(w) if f in ('name', 'text') else w for w in wanted]
        return out

    return {
        'any_of': [convert(c) for c in role.get('any_of') or [] if usable(c)],
        'none_of': [convert(c) for c in role.get('none_of') or [] if usable(c)],
    }


def render_js(spec):
    roles = spec['roles']
    circuits = []
    for c in spec['circuits']:
        circuits.append({
            'id': c['id'],
            'label': c['goal'],
            'name': c['name'],
            'anchor': heading_anchor(c['name']),
            'evidence': c['evidence'],
            'evidenceLabel': EVIDENCE_LEVELS[c['evidence']],
            'sensitive': c.get('sensitive') or '',
            'outside': c.get('outside_directory') or [],
            'steps': [{
                'key': s['role'],
                'label': s['label'],
                'question': s['question'],
                'roleLabel': roles[s['role']]['label'],
                'rule': map_rule(roles[s['role']]),
            } for s in c['roles']],
        })
    body = '{"schemaVersion":1,"circuits":[\n' + ',\n'.join(
        json.dumps(c, ensure_ascii=False, separators=(',', ':'), sort_keys=True) for c in circuits) + '\n]}'
    return (
        '/* GENERATED by data/build_circuits.py from data/circuits.yaml. Do not edit.\n'
        ' * Role rules are research leads: a match never asserts a service, capacity,\n'
        ' * endorsement or a relationship between organizations. */\n'
        '(function (global) {\n'
        "  'use strict';\n"
        '  const data = ' + body + ';\n'
        '  global.CommonweaveCircuits = data;\n'
        "  if (typeof module !== 'undefined' && module.exports) module.exports = data;\n"
        "})(typeof window !== 'undefined' ? window : globalThis);\n"
    )


def load_precision():
    if not os.path.exists(PRECISION_PATH):
        return {}
    with open(PRECISION_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def heading_anchor(text):
    """Anchor the document reader and GitHub derive from a heading."""
    kept = ''.join(ch for ch in str(text).strip().lower() if ch.isalnum() or ch in ' _-')
    return kept.replace(' ', '-')


def md_escape(text):
    return str(text).replace('|', '\\|').replace('\n', ' ')


def render_md(spec, coverage, precision):
    roles = spec['roles']
    cov = {c['id']: c for c in coverage['circuits']}
    rs = coverage['roles']
    inp = coverage['inputs']
    reviewed = (precision or {}).get('roles', {})
    L = []
    w = L.append
    w('# Solution circuits')
    w('')
    w('<!-- GENERATED by data/build_circuits.py from data/circuits.yaml. Edit the YAML, then rebuild. -->')
    w('')
    w('A solution circuit is a set of different kinds of organization that have been used together on one problem. '
      'Community land trusts hold land, unions organize labor, credit unions lend. The question this page tries to answer is which combinations have a track record, '
      'what went wrong when they were tried, and where the directory can find the pieces.')
    w('')
    w('Read this before using it:')
    w('')
    w('- **A circuit is a pattern, not a partnership.** Nothing here says that any two listed organizations know each other or want to work together.')
    w('- **Evidence is graded.** "Combination documented" means the sources show these kinds of organization working together. '
      '"Parts documented separately" means each part has evidence but the combination does not. "Hypothesis" means no precedent has been checked.')
    w('- **Every circuit lists what went wrong.** The limits are part of the evidence. Several of the best-known examples have closed, converted or lost funding.')
    w('- **Sources were opened by an automated research pass on the date shown, and have not been re-checked by a person.** If a link no longer says what is quoted, please correct `data/circuits.yaml`.')
    w('- **Coverage is counts of rule matches.** It comes from the public release dated '
      f'{str(inp["release_generated_at"])[:10]} ({inp["release_rows"]:,} rows). A match is a research lead; see [Role rules](#role-rules) for how accurate each rule looked in a sample.')
    w('')
    w('To try one, open the [map](https://commonweave.earth/map.html#view=list), pick the goal, choose a country and city, and select candidates for each role yourself. '
      'The method and its limits are in the [operating model](FRAMEWORK-OPERATING-MODEL.md).')
    w('')
    w('## Summary')
    w('')
    w('| Circuit | Evidence | Roles | Countries with every role | Cities with every role | Role most often missing |')
    w('|---|---|---:|---:|---:|---|')
    for c in spec['circuits']:
        k = cov[c['id']]
        missing = roles[k['role_most_often_missing']]['label'] if k['role_most_often_missing'] else 'n/a'
        w(f'| [{md_escape(c["name"])}](#{heading_anchor(c["name"])}) | {EVIDENCE_LEVELS[c["evidence"]]} | {len(c["roles"])} | '
          f'{len(k["countries_with_every_role"])} | {k["localities_with_every_role"]:,} | {md_escape(missing)} |')
    w('')
    w('"Cities with every role" counts recorded cities where at least one release record matches each role rule. '
      '"Role most often missing" is the role absent from the largest number of cities that have all the others. '
      'It points at a gap in the directory at least as often as a gap in the place.')
    w('')
    for c in spec['circuits']:
        k = cov[c['id']]
        w(f'## {c["name"]}')
        w('')
        w(f'**Goal on the map:** {c["goal"]}  ')
        w(f'**Evidence:** {EVIDENCE_LEVELS[c["evidence"]]}' + (f'. {c["evidence_note"]}' if c.get('evidence_note') else ''))
        w('')
        w(c['problem'])
        w('')
        if c.get('sensitive'):
            w(f'> **Care needed.** {c["sensitive"]}')
            w('')
        w('| Role | What to ask | Release records | Map points |')
        w('|---|---|---:|---:|')
        for s in c['roles']:
            r = rs[s['role']]
            w(f'| {md_escape(s["label"])} ({md_escape(r["label"].lower())}) | {md_escape(s["question"])} | {r["release_records"]:,} | {r["map_points"]:,} |')
        w('')
        if c.get('precedents'):
            w('**Where it has been done**')
            w('')
            for p in c['precedents']:
                w(f'- **{p["name"]}** ({p["place"]}). {p["finding"]} [Source]({p["source"]}), checked {p["checked"]}.')
            w('')
        if c.get('limits'):
            w('**What went wrong or remains unproven**')
            w('')
            for lim in c['limits']:
                w(f'- {lim["finding"]} [Source]({lim["source"]}).')
            w('')
        if c.get('outside_directory'):
            w('**Needed, but not something the directory can find**')
            w('')
            for o in c['outside_directory']:
                w(f'- {o}')
            w('')
        w(f'**What would count against it:** {c["falsifier"]}')
        w('')
        cw = k['countries_with_every_role']
        line = (f'**Directory coverage:** {k["localities_with_every_role"]:,} recorded cities have a match for every role, '
                f'out of {k["localities_with_any_role"]:,} with a match for at least one. ')
        line += (f'Countries with every role: {", ".join(cw)}.' if cw else 'No country has a match for every role.')
        w(line)
        if k.get('localities'):
            places = '; '.join(f'{loc["city"]}{", " + loc["region"] if loc["region"] else ""} ({loc["country"]})' for loc in k['localities'])
            w('')
            w(f'Cities with the most candidates per role, as leads for a closer look: {places}.')
        elif k.get('localities_withheld'):
            w('')
            w('City-level coverage is not published for this circuit because the work involves people at risk.')
        w('')
        if c.get('open_problems'):
            links = ', '.join(f'[{op}](OPEN-PROBLEMS.md#{op})' for op in c['open_problems'])
            w(f'**Related open problems:** {links}')
            w('')
    w('## Role rules')
    w('')
    w('Each role is recognised from published fields only: organization model, source list, registration type, tags, United States NTEE activity code, and whole-word phrases in the name. '
      'The rules are in [`data/circuits.yaml`](data/circuits.yaml) and the matcher is [`data/circuit_match.py`](data/circuit_match.py). '
      'The map has fewer fields than the release, so it finds fewer candidates.')
    w('')
    if reviewed:
        meta = precision.get('method', {})
        w(f'Sample check: {meta.get("summary", "")}')
        w('')
    w('| Role | Release records | Distinct names | Countries | Largest sources of matches (country, distinct names) | Map points | Sample judged plausible |')
    w('|---|---:|---:|---:|---|---:|---|')
    for key, role in roles.items():
        r = rs[key]
        top = ', '.join(f'{cc} {n:,}' for cc, n in r['top_countries'])
        pr = reviewed.get(key)
        prs = f'{pr["plausible"]}/{pr["sampled"]}' if pr else 'not reviewed'
        w(f'| {md_escape(role["label"])} | {r["release_records"]:,} | {r["release_distinct_names"]:,} | {r["countries"]} | {top} | {r["map_points"]:,} | {prs} |')
    w('')
    if reviewed:
        notes = [(key, v['note']) for key, v in reviewed.items() if v.get('note')]
        if notes:
            w('Notes from the sample check:')
            w('')
            for key, note in notes:
                w(f'- **{roles[key]["label"]}:** {note}')
            w('')
    w('## Adding or changing a circuit')
    w('')
    w('1. Edit `data/circuits.yaml`. A precedent needs a public source you opened yourself and the date you opened it.')
    w('2. Add at least one limit: a failure, a null result, or a condition the precedent depended on.')
    w('3. Write a falsifier that names something a third party could observe.')
    w('4. Run `python data/build_circuits.py`, then `python data/build_circuits.py --check` and the test suites.')
    w('5. If a rule looks wrong, sample it with `python data/build_circuits.py --sample 10` and record what you find in `data/audit/circuit-role-precision.json`.')
    w('')
    return '\n'.join(L)


def render_all(spec):
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    coverage = build_coverage(spec, load_release(), load_map_points(), manifest)
    return {
        COVERAGE_OUT: json.dumps(coverage, ensure_ascii=False, indent=1) + '\n',
        JS_OUT: render_js(spec),
        MD_OUT: render_md(spec, coverage, load_precision()),
    }


def sample_rows(spec, n, seed=20261126):
    """Deterministic review sample: up to n matches per role, spread over sources."""
    release = load_release()
    rows = []
    for key, role in spec['roles'].items():
        matches = sorted((r for r in release if role_matches(role, r)), key=lambda r: str(r.id))
        rng = random.Random(f'{seed}:{key}')
        by_source = defaultdict(list)
        for r in matches:
            by_source[r.source].append(r)
        picked = []
        sources = sorted(by_source, key=lambda s: (-len(by_source[s]), s))
        while len(picked) < min(n, len(matches)):
            for s in sources:
                pool = by_source[s]
                if pool and len(picked) < n:
                    picked.append(pool.pop(rng.randrange(len(pool))))
            if not any(by_source.values()):
                break
        for r in picked:
            rows.append((key, str(r.id), r.source, r.country, r.name, r.ntee))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--check', action='store_true', help='fail if any generated file is stale')
    parser.add_argument('--sample', type=int, metavar='N', help='print N matches per role for review and exit')
    args = parser.parse_args(argv)

    spec = load_spec()
    problems = validate_spec(spec)
    if problems:
        print('data/circuits.yaml is not valid:', file=sys.stderr)
        for p in problems:
            print('  - ' + p, file=sys.stderr)
        return 1
    if args.sample:
        print('role\tid\tsource\tcountry\tname\tntee')
        for row in sample_rows(spec, args.sample):
            print('\t'.join(row))
        return 0

    files = render_all(spec)
    if args.check:
        stale = []
        for path, text in files.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    current = f.read()
            except FileNotFoundError:
                current = None
            if current != text:
                stale.append(os.path.relpath(path, ROOT))
        if stale:
            print('Generated circuit files are not current: ' + ', '.join(stale), file=sys.stderr)
            print('Run: python data/build_circuits.py', file=sys.stderr)
            return 1
        print(f'Circuit files are current ({len(spec["circuits"])} circuits, {len(spec["roles"])} roles).')
        return 0
    for path, text in files.items():
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        print('Wrote ' + os.path.relpath(path, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
