"""
Queue-based Commonweave ingest pipeline orchestrator.

Runs the current safe ingest layers for one country:
- GlobalGiving Atlas, with optional v1 projectservice fallback caveat
- OpenCorporates, when OPENCORPORATES_API_KEY/--opencorporates-api-key is available
- Wikidata SPARQL
- ICA Cooperatives Connect directory scraper

Writes source coverage after each layer and only mutates QUEUE status outside
--dry-run.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
QUEUE_FILE = os.path.join(DATA_DIR, 'QUEUE.txt')
LOG_FILE = os.path.join(DATA_DIR, 'coverage_logs', 'pipeline_runs.jsonl')
SOURCES_DIR = os.path.join(DATA_DIR, 'sources')
SCRIPTS = {
    'globalgiving': os.path.join(SOURCES_DIR, 'ingest_globalgiving.py'),
    'opencorporates': os.path.join(SOURCES_DIR, 'ingest_opencorporates.py'),
    'wikidata': os.path.join(SOURCES_DIR, 'wikidata_ingest.py'),
    'ica_coops': os.path.join(SOURCES_DIR, 'ingest_ica_coops.py'),
}

STATUS_VALUES = {'pending', 'running', 'complete', 'error', 'skipped'}
LAYER_ORDER = ['globalgiving', 'opencorporates', 'wikidata', 'ica_coops']

sys.path.insert(0, DATA_DIR)
from write_coverage import append_coverage  # noqa: E402


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_queue_line(line):
    raw = line.rstrip('\n')
    stripped = raw.strip()
    if not stripped or stripped.startswith('#'):
        return {'type': 'comment', 'raw': raw}
    parts = stripped.split(None, 2)
    if len(parts) < 2:
        return {'type': 'comment', 'raw': raw}
    cc = parts[0].upper()
    if len(parts) >= 3 and parts[1].lower() in STATUS_VALUES:
        return {'type': 'row', 'cc': cc, 'status': parts[1].lower(), 'name': parts[2].strip(), 'raw': raw}
    return {'type': 'row', 'cc': cc, 'status': 'pending', 'name': stripped.split(None, 1)[1].strip(), 'raw': raw}


def format_row(row):
    return f"{row['cc']}  {row['status']:<8}  {row['name']}"


def load_queue(path=QUEUE_FILE):
    with open(path, encoding='utf-8-sig') as f:
        return [parse_queue_line(line) for line in f]


def write_queue(rows, path=QUEUE_FILE):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        for row in rows:
            if row['type'] == 'row':
                f.write(format_row(row) + '\n')
            else:
                raw = row.get('raw', '')
                if raw.strip() == '# Format: CC  Country Name':
                    raw = '# Format: CC  status  Country Name'
                f.write(raw + '\n')
    os.replace(tmp, path)


def next_country(rows):
    for row in rows:
        if row['type'] == 'row' and row.get('status') != 'complete':
            return row
    return None


def find_country(rows, cc):
    for row in rows:
        if row['type'] == 'row' and row['cc'] == cc.upper():
            return row
    return None


def set_status(rows, cc, status):
    row = find_country(rows, cc)
    if not row:
        raise KeyError(f'{cc} not found in queue')
    row['status'] = status
    return row


def append_log(record):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + '\n')


def parse_json_tail(stdout):
    text = stdout or ''
    for i in range(len(text)):
        if text[i] in '[{':
            candidate = text[i:].strip()
            try:
                return json.loads(candidate)
            except Exception:
                pass
    return {}


def parse_wikidata_counts(stdout):
    found = changed = 0
    for line in (stdout or '').splitlines():
        line = line.strip()
        if line.startswith('Found ') and ' unique organizations' in line:
            try:
                found = int(line.split()[1].replace(',', ''))
            except Exception:
                pass
        if line.startswith('Done: ') and ' orgs inserted/updated' in line:
            try:
                changed = int(line.split()[1].replace(',', ''))
            except Exception:
                pass
    return {'found': found, 'inserted': changed}


def run_cmd(cmd, dry_run=False):
    print('+ ' + ' '.join(cmd))
    return subprocess.run(cmd, cwd=DATA_DIR, capture_output=True, text=True, encoding='utf-8')


def build_layer_cmd(layer, cc, name, args):
    if layer == 'globalgiving':
        cmd = [sys.executable, SCRIPTS[layer], cc, '--limit', str(args.limit), '--sleep', str(args.sleep)]
        if args.globalgiving_api_key:
            cmd.extend(['--api-key', args.globalgiving_api_key])
        if args.globalgiving_fallback_v1:
            cmd.append('--fallback-v1')
        if args.dry_run:
            cmd.append('--dry-run')
        return cmd
    if layer == 'opencorporates':
        cmd = [sys.executable, SCRIPTS[layer], cc, '--pages', str(args.opencorporates_pages), '--per-page', str(args.opencorporates_per_page), '--sleep', str(args.sleep)]
        key = args.opencorporates_api_key or os.environ.get('OPENCORPORATES_API_KEY') or os.environ.get('OPENCORPORATES_API_TOKEN')
        if key:
            cmd.extend(['--api-key', key])
        if args.dry_run:
            cmd.append('--dry-run')
        return cmd
    if layer == 'wikidata':
        cmd = [sys.executable, SCRIPTS[layer], cc, name, '--delay', str(args.wikidata_delay)]
        if args.wikidata_query_index:
            cmd.extend(['--query-index', str(args.wikidata_query_index)])
        if args.dry_run:
            cmd.append('--dry-run')
        return cmd
    if layer == 'ica_coops':
        cmd = [sys.executable, SCRIPTS[layer], cc]
        if args.dry_run:
            cmd.append('--dry-run')
        return cmd
    raise ValueError(layer)


def counts_for_layer(layer, result):
    if layer == 'wikidata':
        return parse_wikidata_counts(result.stdout)
    data = parse_json_tail(result.stdout)
    return {'found': int(data.get('found') or 0), 'inserted': int((data.get('inserted') or 0) + (data.get('updated') or 0))}


def run_layer(layer, cc, name, args):
    cmd = build_layer_cmd(layer, cc, name, args)
    result = run_cmd(cmd, dry_run=args.dry_run)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    counts = counts_for_layer(layer, result)
    status = 'complete' if result.returncode == 0 else 'error'
    notes = f'{layer} run via run_pipeline.py'
    if layer == 'globalgiving':
        notes += '; Atlas may require paid v2 license; v1 fallback is project-level only when enabled'
    coverage = append_coverage(
        cc, name, layer, status,
        found=counts['found'], inserted=counts['inserted'], notes=notes,
        extra={'returncode': result.returncode, 'dry_run': args.dry_run},
    )
    record = {
        'timestamp': now_iso(), 'country_code': cc, 'country_name': name, 'source': layer,
        'status': status, 'found': counts['found'], 'inserted': counts['inserted'],
        'returncode': result.returncode, 'dry_run': args.dry_run,
    }
    append_log(record)
    return result.returncode, coverage, record


def run_next(args):
    rows = load_queue()
    row = find_country(rows, args.country) if args.country else next_country(rows)
    if not row:
        if args.country:
            print(f'Country {args.country.upper()} not found in QUEUE.txt', file=sys.stderr)
            return 2
        print('QUEUE complete: no pending/error/running countries remain')
        return 0
    cc, name = row['cc'], row['name']
    layers = args.layers or LAYER_ORDER
    print(f'Country: {cc} {name} ({row["status"]}); layers={layers}')
    if not args.dry_run:
        set_status(rows, cc, 'running')
        write_queue(rows)

    failures = []
    records = []
    for layer in layers:
        rc, coverage, record = run_layer(layer, cc, name, args)
        records.append(record)
        if rc != 0:
            failures.append(layer)
            if not args.keep_going:
                break

    final_status = 'error' if failures else 'complete'
    if not args.dry_run:
        rows = load_queue()
        set_status(rows, cc, final_status)
        write_queue(rows)
    print(json.dumps({'country_code': cc, 'country_name': name, 'status': final_status, 'failures': failures, 'runs': records}, indent=2, sort_keys=True))
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='Run Commonweave ingest pipeline layers for the next or selected country.')
    ap.add_argument('--country', help='ISO alpha-2 country code; default first non-complete QUEUE row')
    ap.add_argument('--layers', nargs='+', choices=LAYER_ORDER, help='Subset/order of layers to run')
    ap.add_argument('--dry-run', action='store_true', help='Do not mutate DB or QUEUE status; coverage proof is still written')
    ap.add_argument('--keep-going', action='store_true', help='Continue later layers after a layer fails')
    ap.add_argument('--show-next', action='store_true', help='Print the next queue row and exit')
    ap.add_argument('--limit', type=int, default=100, help='GlobalGiving max rows')
    ap.add_argument('--sleep', type=float, default=1.0, help='Sleep between API pages/terms')
    ap.add_argument('--globalgiving-api-key', default=os.environ.get('GLOBALGIVING_ATLAS_API_KEY') or os.environ.get('GLOBALGIVING_API_KEY'))
    ap.add_argument('--globalgiving-fallback-v1', action='store_true', help='Try GlobalGiving v1 projectservice when Atlas returns the license 401')
    ap.add_argument('--opencorporates-api-key', default=os.environ.get('OPENCORPORATES_API_KEY') or os.environ.get('OPENCORPORATES_API_TOKEN'))
    ap.add_argument('--opencorporates-pages', type=int, default=1)
    ap.add_argument('--opencorporates-per-page', type=int, default=30)
    ap.add_argument('--wikidata-delay', type=float, default=3.0)
    ap.add_argument('--wikidata-query-index', type=int, help='Run only one Wikidata SPARQL query (1-6)')
    args = ap.parse_args(argv)
    if args.show_next:
        row = next_country(load_queue())
        print(json.dumps(row, indent=2, sort_keys=True))
        return 0
    return run_next(args)


if __name__ == '__main__':
    raise SystemExit(main())
