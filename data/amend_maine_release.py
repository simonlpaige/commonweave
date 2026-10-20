"""Stage reviewed Maine amendments from pinned public files, without a database.

Produces only the affected release representations and directory shard in a new
output directory. Original files are never written. See docs/RELEASE-AMENDMENTS.md.
"""
import argparse
import copy
import csv
import gzip
import hashlib
import io
import json
from datetime import date
from pathlib import Path
from audit_public_exports import valid_url

FILES = (
    'releases/organizations.json.gz', 'releases/organizations.csv.gz',
    'releases/by-country/US.csv', 'releases/by-source/ic_directory.csv',
    'data/search/US_ME.json', 'releases/MANIFEST.json',
)
KEYS = {'name': 'n', 'website': 'w', 'city': 'c', 'description': 'd'}
LEDGER = 'releases/AMENDMENTS.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def input_sha(name, data):
    return sha(data if name.endswith('.gz') else data.replace(b'\r\n', b'\n'))


def compressed_bytes(value):
    raw = gzip.compress(value, compresslevel=9, mtime=0)
    # Python versions differ in the gzip OS header despite mtime=0.
    return raw[:9] + b'\xff' + raw[10:]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply_rows(rows, proposals):
    result = copy.deepcopy(rows)
    for proposal in proposals:
        matches = [row for row in result if str(row.get('id')) == proposal['organization_id']]
        require(len(matches) == 1, 'Missing or ambiguous release identity')
        row = matches[0]
        require(row.get('country_code') == 'US' and row.get('state_province') == 'Maine', 'Wrong locality')
        for key, value in proposal['identity'].items():
            require(str(row.get(key)) == str(value), 'Source identity changed')
        for key, old in proposal['expected'].items():
            require(row.get(key) == old, 'Expected value mismatch: ' + key)
        row.update(proposal['changes'])
    return result


def csv_amend(data, proposals):
    compressed = data[:2] == b'\x1f\x8b'
    # Git normalizes tracked text, including quoted multiline CSV cells. Read
    # the canonical LF representation rather than Windows checkout conversion.
    if not compressed:
        data = data.replace(b'\r\n', b'\n')
    text = gzip.decompress(data).decode('utf-8-sig') if compressed else data.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text, newline=''))
    fields = reader.fieldnames
    rows = list(reader)
    changed = apply_rows(rows, proposals)
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(changed)
    raw = output.getvalue().encode('utf-8')
    return compressed_bytes(raw) if compressed else raw


def prepare(root, plan, as_of=None):
    root = Path(root)
    as_of = as_of or date.today()
    require(plan.get('schema_version') == 1 and plan.get('amendment_id'), 'Invalid amendment')
    has_ledger = (root / LEDGER).exists()
    required_files = set(FILES) | ({LEDGER} if has_ledger else set())
    require(set(plan.get('base_files', {})) == required_files, 'Exactly the current base files and ledger must be pinned')
    inputs = {name: (root / name).read_bytes() for name in required_files}
    for name, raw in inputs.items():
        require(input_sha(name, raw) == plan['base_files'][name], 'Base hash mismatch: ' + name)
    prior = json.loads(inputs[LEDGER]) if has_ledger else None
    history = []
    receipts = []
    if prior is not None:
        require(prior.get('schema_version') == 1, 'Unsupported prior ledger')
        history = prior.get('amendments', [])
        require(isinstance(history, list) and bool(history), 'Invalid prior amendment history')
        prior_ids = [entry.get('amendment_id') for entry in history]
        require(all(isinstance(value, str) and value for value in prior_ids) and len(set(prior_ids)) == len(prior_ids), 'Invalid prior amendment IDs')
        require(plan['amendment_id'] not in prior_ids, 'Amendment replay')
        require(set(prior.get('output_sha256', {})) == set(FILES), 'Incomplete prior output receipt')
        for name in FILES:
            require(input_sha(name, inputs[name]) == prior['output_sha256'][name], 'Prior published output changed: ' + name)
        receipts = list(prior.get('history_receipts', []))
        receipts.append({'amendment_id': prior_ids[-1], 'ledger_sha256': input_sha(LEDGER, inputs[LEDGER]), 'output_sha256': prior['output_sha256']})
    proposals = plan.get('proposals', [])
    require(bool(proposals), 'No accepted changes')
    ids = set()
    for p in proposals:
        oid = p.get('organization_id')
        require(isinstance(oid, str) and oid not in ids, 'Duplicate/invalid organization ID')
        ids.add(oid)
        changes = p.get('changes', {})
        require(bool(changes) and set(changes) <= set(KEYS) and set(changes) == set(p.get('expected', {})), 'Unsupported field or missing expected value')
        require(all(isinstance(v, str) and bool(v.strip()) for v in changes.values()), 'Invalid replacement')
        if 'website' in changes:
            require(valid_url(changes['website']), 'Invalid website')
        require(p.get('identity', {}).get('source') == 'ic_directory' and p['identity'].get('source_id'), 'Missing source identity')
        require(p.get('visibility_review', {}).get('decision') == 'public', 'Visibility not accepted')
        require(p.get('reuse', {}).get('basis') == 'original_factual_summary', 'Unsupported reuse basis')
        review = p.get('review', {})
        require(review.get('decision') == 'accepted' and review.get('reviewer'), 'Accepted named review required')
        evidence = p.get('evidence', [])
        for field in changes:
            supporting = [e for e in evidence if field in e.get('fields', [])]
            require(bool(supporting), 'Missing field evidence')
            for e in supporting:
                checked = date.fromisoformat(e['checked_at'])
                require(0 <= (as_of - checked).days <= 180, 'Stale or future evidence')
                require(valid_url(e.get('url')) and e.get('summary'), 'Invalid evidence')
    rows = json.loads(gzip.decompress(inputs[FILES[0]]))
    amended = apply_rows(rows, proposals)
    manifest = json.loads(inputs['releases/MANIFEST.json'])
    require(len(rows) == manifest['row_count'], 'Manifest row count mismatch')
    shard = json.loads(inputs['data/search/US_ME.json'])
    require(shard.get('count') == len(shard['orgs']), 'Maine shard count mismatch')
    for p in proposals:
        selector = p.get('search_selector', {})
        require(set(selector) == {'n', 'c', 'w'}, 'Exact name/city/source URL selector required')
        matches = [r for r in shard['orgs'] if all(r.get(k) == v for k, v in selector.items())]
        require(len(matches) == 1, 'Missing or ambiguous directory identity')
        target = matches[0]
        search_expected = p.get('search_expected', p['expected'])
        require(set(search_expected) == set(p['changes']), 'Directory expected fields differ')
        for key, old in search_expected.items():
            if key != 'description':
                require(old == p['expected'][key], 'Directory identity precondition differs')
            require(target.get(KEYS[key]) == old, 'Directory precondition mismatch')
        target.update({KEYS[k]: v for k, v in p['changes'].items()})
    outputs = {
        FILES[0]: compressed_bytes(encoded(amended)),
        'data/search/US_ME.json': (json.dumps(shard, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf-8'),
    }
    for name in FILES[1:4]:
        outputs[name] = csv_amend(inputs[name], proposals)
    field_count = sum(len(p['changes']) for p in proposals)
    prior_manifest = manifest.get('amendments', [])
    require([entry.get('id') for entry in prior_manifest] == [entry['amendment_id'] for entry in history], 'Manifest amendment history differs')
    manifest['amendments'] = prior_manifest + [{'id': plan['amendment_id'], 'ledger': 'AMENDMENTS.json',
                               'scope': f'{field_count} fields across {len(proposals)} Maine records; directory shard reconciled.'}]
    note = 'Reviewed amendments overlay the historical extraction; original generated_at and source provenance are retained. Rebuilds must explicitly reconcile AMENDMENTS.json.'
    if note not in manifest['notes']:
        manifest['notes'].append(note)
    outputs['releases/MANIFEST.json'] = encoded(manifest)
    outputs['releases/AMENDMENTS.json'] = encoded({
        'schema_version': 1, 'amendments': history + [plan],
        'history_receipts': receipts,
        'output_sha256': {name: sha(raw) for name, raw in outputs.items()},
        'verification_scope': 'Field review only; no service, availability, legal form or whole-record verification.',
    })
    return outputs


def stage(root, plan, output, as_of=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    require(not output.exists(), 'Output must be a new directory')
    require(output != root and root not in output.parents and output not in root.parents, 'Output must be outside the source checkout')
    outputs = prepare(root, plan, as_of)
    output.mkdir(parents=True)
    for name, raw in outputs.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return {name: sha(raw) for name, raw in outputs.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8-sig'))
    print(json.dumps(stage(args.root, plan, args.output), indent=2))


if __name__ == '__main__':
    main()
