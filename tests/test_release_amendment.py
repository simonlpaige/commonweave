import copy
import csv
import gzip
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data'))
SPEC = importlib.util.spec_from_file_location('amend', Path(__file__).resolve().parents[1] / 'data/amend_maine_release.py')
amend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(amend)


class ReleaseAmendmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        self.rows = [dict(id=1, name='Test &amp; Community', city='Blue  Hill', website='https://example.org/profile',
                          country_code='US', state_province='Maine', source='ic_directory', source_id='source-1', last_verified_at=None),
                     dict(id=2, name='Untouched', city='Elsewhere', website='https://example.org/other',
                          country_code='US', state_province='Maine', source='ic_directory', source_id='source-2', last_verified_at=None)]
        text = io.StringIO(newline='')
        writer = csv.DictWriter(text, fieldnames=list(self.rows[0]))
        writer.writeheader()
        writer.writerows(self.rows)
        raw_csv = text.getvalue().encode()
        payloads = {
            amend.FILES[0]: gzip.compress(amend.encoded(self.rows), mtime=0),
            amend.FILES[1]: gzip.compress(raw_csv, mtime=0),
            amend.FILES[2]: raw_csv, amend.FILES[3]: raw_csv,
            amend.FILES[4]: amend.encoded({'count': 2, 'orgs': [dict(n=r['name'], c=r['city'], w=r['website']) for r in self.rows]}),
            amend.FILES[5]: amend.encoded({'row_count': 2, 'generated_at': 'historical', 'notes': []}),
        }
        for name, raw in payloads.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        self.plan = {'schema_version': 1, 'amendment_id': 'test-amendment',
                     'base_files': {n: amend.input_sha(n, b) for n, b in payloads.items()},
                     'proposals': [{'organization_id': '1', 'identity': {'source': 'ic_directory', 'source_id': 'source-1'},
                                    'expected': {'city': 'Blue  Hill'}, 'changes': {'city': 'Blue Hill'},
                                    'search_selector': {'n': self.rows[0]['name'], 'c': self.rows[0]['city'], 'w': self.rows[0]['website']},
                                    'review': {'decision': 'accepted', 'reviewer': 'Test reviewer'},
                                    'visibility_review': {'decision': 'public'}, 'reuse': {'basis': 'original_factual_summary'},
                                    'evidence': [{'fields': ['city'], 'url': 'https://example.org/', 'checked_at': '2026-10-19', 'summary': 'Whitespace normalization.'}]}]}

    def run_prepare(self):
        return amend.prepare(self.root, self.plan, date(2026, 10, 19))

    def test_coherent_outputs_and_determinism(self):
        out = self.run_prepare()
        self.assertEqual(out, self.run_prepare())
        rows = json.loads(gzip.decompress(out[amend.FILES[0]]))
        expected = copy.deepcopy(self.rows)
        expected[0]['city'] = 'Blue Hill'
        self.assertEqual(rows, expected)
        for path in amend.FILES[1:4]:
            raw = gzip.decompress(out[path]) if path.endswith('.gz') else out[path]
            result = list(csv.DictReader(io.StringIO(raw.decode())))
            self.assertEqual(result[0]['city'], 'Blue Hill')
            self.assertEqual(result[1]['name'], 'Untouched')
        self.assertEqual(json.loads(out[amend.FILES[4]])['orgs'][0]['c'], 'Blue Hill')
        self.assertEqual(json.loads(out[amend.FILES[5]])['generated_at'], 'historical')
        ledger = json.loads(out['releases/AMENDMENTS.json'])
        self.assertTrue(all(amend.sha(out[n]) == value for n, value in ledger['output_sha256'].items()))

    def test_source_unchanged_and_new_output_required(self):
        before = {n: (self.root / n).read_bytes() for n in amend.FILES}
        out = Path(self.temp.name) / 'staged'
        amend.stage(self.root, self.plan, out, date(2026, 10, 19))
        self.assertEqual(before, {n: (self.root / n).read_bytes() for n in amend.FILES})
        with self.assertRaises(ValueError):
            amend.stage(self.root, self.plan, out)
        with self.assertRaises(ValueError):
            amend.stage(self.root, self.plan, self.root / 'nested')

    def test_changed_base_rejected_before_output(self):
        (self.root / amend.FILES[2]).write_bytes(b'changed')
        out = Path(self.temp.name) / 'staged'
        with self.assertRaisesRegex(ValueError, 'Base hash'):
            amend.stage(self.root, self.plan, out)
        self.assertFalse(out.exists())

    def test_text_checkout_line_endings_do_not_change_output_hashes(self):
        for name in amend.FILES[2:4]:
            path = self.root / name
            path.write_bytes(path.read_bytes().replace(b'Untouched', b'"Untouched\r\nline"'))
            self.plan['base_files'][name] = amend.input_sha(name, path.read_bytes())
        first = self.run_prepare()
        for name in amend.FILES:
            if not name.endswith('.gz'):
                path = self.root / name
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        self.assertEqual(first, self.run_prepare())

    def test_expected_value_and_source_identity_holds(self):
        self.plan['proposals'][0]['expected']['city'] = 'Different'
        with self.assertRaisesRegex(ValueError, 'Expected value'):
            self.run_prepare()
        self.plan['proposals'][0]['expected']['city'] = 'Blue  Hill'
        self.plan['proposals'][0]['identity']['source_id'] = 'other'
        with self.assertRaisesRegex(ValueError, 'Source identity'):
            self.run_prepare()

    def test_ambiguous_directory_match_rejected(self):
        self.plan['proposals'][0]['search_selector']['n'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'directory identity'):
            self.run_prepare()

    def test_pending_review_and_unsupported_promotions_rejected(self):
        self.plan['proposals'][0]['review']['decision'] = 'pending'
        with self.assertRaisesRegex(ValueError, 'Accepted named review'):
            self.run_prepare()
        self.plan['proposals'][0]['review']['decision'] = 'accepted'
        self.plan['proposals'][0]['changes']['tier'] = 'A'
        with self.assertRaisesRegex(ValueError, 'Unsupported field'):
            self.run_prepare()

    def test_future_evidence_and_duplicate_batch_rejected(self):
        self.plan['proposals'][0]['evidence'][0]['checked_at'] = '2026-10-20'
        with self.assertRaisesRegex(ValueError, 'future evidence'):
            self.run_prepare()
        self.plan['proposals'][0]['evidence'][0]['checked_at'] = '2026-10-19'
        self.plan['proposals'].append(copy.deepcopy(self.plan['proposals'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.run_prepare()

    def test_private_website_and_evidence_urls_refused(self):
        p = self.plan['proposals'][0]
        p['expected'] = {'website': self.rows[0]['website']}
        p['changes'] = {'website': 'http://127.0.0.1/'}
        p['evidence'][0]['fields'] = ['website']
        with self.assertRaisesRegex(ValueError, 'Invalid website'):
            self.run_prepare()
        p['changes']['website'] = 'https://example.org/'
        p['evidence'][0]['url'] = 'http://localhost/'
        with self.assertRaisesRegex(ValueError, 'Invalid evidence'):
            self.run_prepare()

    def test_ledger_replay_and_export_overwrite_refused(self):
        ledger = self.root / 'releases/AMENDMENTS.json'
        ledger.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Existing amendment ledger'):
            self.run_prepare()
        db = Path(self.temp.name) / 'missing.db'
        exporter = Path(__file__).resolve().parents[1] / 'data/export_to_releases.py'
        result = subprocess.run([sys.executable, '-B', str(exporter), '--db', str(db), '--output', str(ledger.parent)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('reviewed amendments', result.stderr)
        self.assertFalse(db.exists())
        self.assertEqual(ledger.read_text(), '{}')


if __name__ == '__main__':
    unittest.main()
