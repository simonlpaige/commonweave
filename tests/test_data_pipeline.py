"""Regression tests for publication drift and evidence-free database mutations."""
import copy
import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import date
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'data'))
from audit_public_exports import coordinate_state, content_hash, row_issues, valid_url
from build_search_index import build
from export_to_releases import fetch_rows
from reconcile_search_index import inventory
from stage_organizations import create_review_copy, validate
import stage_organizations

TODAY = date(2026, 9, 5)


@contextmanager
def connect(path):
    db = sqlite3.connect(path)
    try:
        with db:
            yield db
    finally:
        db.close()


def proposal():
    return {'proposal_id': 'review-001', 'operation': 'update', 'organization_id': 'one',
            'changes': {'website': 'https://example.org'}, 'expected': {'website': ''},
            'visibility_review': {'decision': 'public', 'reason': 'Organization publishes its service homepage.'},
            'reuse': {'basis': 'original_factual_summary', 'url': 'https://example.org/about'},
            'review': {'decision': 'accepted', 'reviewer': 'test-reviewer'},
            'evidence': [{'fields': ['website'], 'url': 'https://example.org/about',
                          'excerpt': 'Official organization homepage.', 'checked_at': '2026-09-05'}]}


class DataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.db'
        with connect(self.source) as db:
            db.execute('CREATE TABLE organizations (id TEXT PRIMARY KEY, name TEXT, country_code TEXT, status TEXT, tier TEXT, website TEXT, description TEXT, source TEXT, city TEXT, state_province TEXT, framework_area TEXT, lat REAL, lon REAL, legibility TEXT, alignment_score INTEGER, merged_into TEXT)')
            db.executemany('INSERT INTO organizations (id,name,country_code,status,tier,website,source,alignment_score,merged_into) VALUES (?,?,?,?,?,?,?,?,?)', [
                ('one', 'Community Test', 'US', 'active', 'B', '', 'test_source', 6, None),
                ('removed', 'Removed', 'US', 'removed', 'B', '', 'test_source', 8, None),
                ('merged', 'Merged', 'US', 'active', 'B', '', 'test_source', 8, 'one'),
                ('country-error', 'Needs country', 'GLOBAL', 'active', 'D', '', 'test_source', 3, None),
            ])

    def tearDown(self):
        self.temp.cleanup()

    def test_public_urls_reject_unsafe_schemes_and_private_addresses(self):
        for url in ['javascript:alert(1)', 'file:///tmp/a', 'https://user:pass@example.org',
                    'https://127.0.0.1', 'https://192.168.1.1', 'https://foo.local', 'https://example.org\\@evil.com',
                    'https://example.org\nattacker', 'https://example.org:bad']:
            self.assertFalse(valid_url(url), url)
        self.assertTrue(valid_url('https://example.org/about?lang=es'))

    def test_public_urls_reject_browser_numeric_aliases_and_malformed_dns(self):
        for url in ['https://127.1', 'https://0177.0.0.1', 'https://0x7f.0.0.1',
                    'https://2130706433', 'https://%31%32%37.0.0.1', 'https://localhost.',
                    'https://a..com', 'https://-a.com', 'https://example.com:99999']:
            self.assertFalse(valid_url(url), url)
        self.assertTrue(valid_url('https://example.org.'))

    def test_coordinate_validation_includes_nonfinite_zero_and_one_missing(self):
        self.assertEqual(coordinate_state(float('nan'), 20), 'invalid')
        self.assertEqual(coordinate_state(91, 0), 'invalid')
        self.assertEqual(coordinate_state(0, 0), 'zero_zero')
        self.assertEqual(coordinate_state(20, None), 'incomplete')
        self.assertEqual(coordinate_state(None, None), 'missing')
        self.assertEqual(coordinate_state(0, 30), 'present')

    def test_verification_date_does_not_treat_export_date_as_evidence(self):
        issues = row_issues({'last_verified_at': '2027-01-01'}, TODAY)
        self.assertIn('verification_date_future', issues)
        self.assertIn('verification_date_unknown', row_issues({'generated': '2026-09-05'}, TODAY))

    def test_present_invalid_tier_is_flagged_without_inventing_a_replacement(self):
        for tier in ('K31', 'candidate', 'tier_a', '', None):
            row = {'tier': tier}
            self.assertIn('invalid_record_tier', row_issues(row, TODAY))
            self.assertEqual(row['tier'], tier)
        for tier in ('A', 'B', 'C', 'D'):
            self.assertNotIn('invalid_record_tier', row_issues({'tier': tier}, TODAY))
        self.assertNotIn('invalid_record_tier', row_issues({}, TODAY))

    def test_csv_line_endings_are_not_false_content_drift(self):
        self.assertEqual(content_hash({'id': 1, 'description': 'a\nb', 'missing': None}),
                         content_hash({'id': '1', 'description': 'a\r\nb', 'missing': ''}))

    def test_evidence_free_legacy_enrichment_is_rejected(self):
        with self.assertRaises(ValueError):
            validate([{'id': 'one', 'website': 'https://example.org'}], TODAY)

    def test_each_changed_field_requires_evidence(self):
        p = proposal(); p['changes']['description'] = 'Unsupported new description'; p['expected']['description'] = None
        with self.assertRaisesRegex(ValueError, 'every changed field'):
            validate([p], TODAY)

    def test_default_accepted_or_fake_human_verification_not_inferred(self):
        p = proposal(); del p['review']
        with self.assertRaisesRegex(ValueError, 'accepted review'):
            validate([p], TODAY)

    def test_pending_research_validates_but_cannot_be_applied(self):
        p = proposal(); p['review'] = {'decision': 'pending'}
        self.assertEqual(validate([p], TODAY), [p])
        with self.assertRaisesRegex(ValueError, 'accepted review required'):
            create_review_copy(self.source, self.root/'pending.db', [p], TODAY)
        self.assertFalse((self.root/'pending.db').exists())

    def test_malformed_nested_payloads_are_rejected_cleanly(self):
        for key in ['review', 'visibility_review', 'reuse', 'expected']:
            for value in [None, [], 'bad']:
                p = proposal(); p[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    validate([p], TODAY)
        p = proposal(); p['evidence'][0]['fields'] = [['website']]
        with self.assertRaises(ValueError):
            validate([p], TODAY)

    def test_withheld_and_numeric_coordinate_strings_are_rejected(self):
        p = proposal(); p['visibility_review']['decision'] = 'withhold'
        with self.assertRaises(ValueError):
            validate([p], TODAY)
        p = proposal(); p['changes'] = {'lat': '20', 'lon': '30'}
        p['expected'] = {'lat': None, 'lon': None}; p['evidence'][0]['fields'] = ['lat', 'lon']
        p['location_precision'] = 'city'
        with self.assertRaisesRegex(ValueError, 'number or null'):
            validate([p], TODAY)

    def test_stale_or_future_evidence_rejected(self):
        for checked in ['2027-01-01', '2025-01-01']:
            p = proposal(); p['evidence'][0]['checked_at'] = checked
            with self.assertRaisesRegex(ValueError, 'within 180 days'):
                validate([p], TODAY)

    def test_visibility_and_reuse_are_required(self):
        for key in ['visibility_review', 'reuse']:
            p = proposal(); del p[key]
            with self.assertRaises(ValueError):
                validate([p], TODAY)

    def test_country_only_must_clear_existing_location(self):
        with connect(self.source) as db:
            db.execute("UPDATE organizations SET city='Small Town' WHERE id='one'")
        p = proposal(); p['visibility_review']['decision'] = 'country_only'
        with self.assertRaisesRegex(ValueError, 'clear existing detailed location'):
            create_review_copy(self.source, self.root/'copy.db', [p], TODAY)
        self.assertFalse((self.root/'copy.db').exists())

    def test_corrections_only_change_new_copy_and_preserve_evidence(self):
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        out = self.root/'review.db'
        create_review_copy(self.source, out, [proposal()], TODAY)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), before)
        with connect(out) as db:
            self.assertEqual(db.execute("SELECT website FROM organizations WHERE id='one'").fetchone()[0], 'https://example.org')
            evidence = json.loads(db.execute('SELECT payload_json FROM organization_evidence').fetchone()[0])
            self.assertEqual(evidence['evidence'][0]['checked_at'], '2026-09-05')
            self.assertNotIn('human_verified', evidence)

    def test_coordinate_precision_is_migrated_only_in_copy_and_cleared_with_coordinates(self):
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        with connect(self.source) as db:
            source_schema = db.execute('PRAGMA table_info(organizations)').fetchall()
        self.assertNotIn('location_precision', {row[1] for row in source_schema})
        p = proposal()
        p['changes'] = {'lat': 35.5, 'lon': -81.5}
        p['expected'] = {'lat': None, 'lon': None}
        p['evidence'][0]['fields'] = ['lat', 'lon']
        with self.assertRaisesRegex(ValueError, 'location_precision required'):
            create_review_copy(self.source, self.root/'no-precision.db', [p], TODAY)
        self.assertFalse((self.root/'no-precision.db').exists())
        p['location_precision'] = 'city'
        out = self.root/'located-review.db'
        create_review_copy(self.source, out, [p], TODAY)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), before)
        with connect(self.source) as db:
            self.assertEqual(db.execute('PRAGMA table_info(organizations)').fetchall(), source_schema)
        with connect(out) as db:
            self.assertEqual(db.execute("SELECT lat,lon,location_precision FROM organizations WHERE id='one'").fetchone(),
                             (35.5, -81.5, 'city'))
        exported = list(fetch_rows(out, None))
        self.assertEqual(next(r for r in exported if r['id'] == 'one')['location_precision'], 'city')
        clearing = copy.deepcopy(p)
        clearing['proposal_id'] = 'clear-reviewed-location'
        clearing['changes'] = {'lat': None, 'lon': None}
        clearing['expected'] = {'lat': 35.5, 'lon': -81.5}
        del clearing['location_precision']
        cleared = self.root/'cleared-review.db'
        reviewed_hash = hashlib.sha256(out.read_bytes()).hexdigest()
        create_review_copy(out, cleared, [clearing], TODAY)
        self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), reviewed_hash)
        with connect(cleared) as db:
            self.assertEqual(db.execute("SELECT lat,lon,location_precision FROM organizations WHERE id='one'").fetchone(),
                             (None, None, None))

    def test_existing_or_same_output_is_never_overwritten(self):
        with self.assertRaises(ValueError):
            create_review_copy(self.source, self.source, [proposal()], TODAY)
        out = self.root/'exists.db'; out.write_bytes(b'keep this file')
        with self.assertRaises(ValueError):
            create_review_copy(self.source, out, [proposal()], TODAY)
        self.assertEqual(out.read_bytes(), b'keep this file')

    def test_replaying_a_proposal_does_not_duplicate_evidence(self):
        out = self.root/'review.db'; create_review_copy(self.source, out, [proposal()], TODAY)
        before = hashlib.sha256(out.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'already applied'):
            create_review_copy(out, self.root/'retry.db', [proposal()], TODAY)
        self.assertFalse((self.root/'retry.db').exists())
        self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), before)

    def test_preconditions_are_rechecked_on_the_actual_backup_snapshot(self):
        original = stage_organizations.check_against_db
        checks = []
        def change_source_after_precheck(db, proposals):
            result = original(db, proposals)
            checks.append(True)
            if len(checks) == 1:
                with connect(self.source) as writer:
                    writer.execute("UPDATE organizations SET website='https://changed.org' WHERE id='one'")
            return result
        with patch.object(stage_organizations, 'check_against_db', side_effect=change_source_after_precheck):
            with self.assertRaisesRegex(ValueError, 'conflict'):
                create_review_copy(self.source, self.root/'raced.db', [proposal()], TODAY)
        self.assertFalse((self.root/'raced.db').exists())

    def test_database_failure_rolls_back_and_removes_only_new_copy(self):
        with connect(self.source) as db:
            db.execute("CREATE TRIGGER forbid_changes BEFORE UPDATE ON organizations BEGIN SELECT RAISE(ABORT, 'fixture failure'); END")
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        with self.assertRaises(sqlite3.IntegrityError):
            create_review_copy(self.source, self.root/'failed.db', [proposal()], TODAY)
        self.assertFalse((self.root/'failed.db').exists())
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), before)

    def test_conflicting_correction_fails_before_copy_created(self):
        p = proposal(); p['expected']['website'] = 'https://stale.example.org'
        with self.assertRaisesRegex(ValueError, 'conflict'):
            create_review_copy(self.source, self.root/'review.db', [p], TODAY)
        self.assertFalse((self.root/'review.db').exists())

    def test_batch_is_all_or_nothing_on_missing_record(self):
        second = proposal(); second['proposal_id'] = 'second'; second['organization_id'] = 'missing'
        with self.assertRaises(ValueError):
            create_review_copy(self.source, self.root/'review.db', [proposal(), second], TODAY)
        self.assertFalse((self.root/'review.db').exists())

    def test_new_discovery_remains_unpublished_candidate(self):
        p = proposal(); p['operation'] = 'add'
        p['changes'] = {'name': 'A different organization', 'country_code': 'GB', 'source': 'manual_research',
                        'description': 'Provides a community service with a documented public program.'}
        p['evidence'][0]['fields'] = list(p['changes'])
        out = self.root/'review.db'
        create_review_copy(self.source, out, [p], TODAY)
        with connect(out) as db:
            self.assertEqual(db.execute("SELECT status,tier FROM organizations WHERE name=?", (p['changes']['name'],)).fetchone(), ('candidate', 'D'))
        self.assertFalse(any(row['name'] == p['changes']['name'] for row in fetch_rows(out, None)))

    def test_integer_primary_key_discoveries_record_actual_ids_and_reject_replay(self):
        source = self.root/'integer-source.db'
        with connect(source) as db:
            db.execute('CREATE TABLE organizations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, country_code TEXT, status TEXT, tier TEXT, website TEXT, description TEXT, source TEXT)')
            db.execute("INSERT INTO organizations (id,name,country_code,status,tier,website) VALUES (7,'Existing organization','GB','active','B','')")
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        proposals = []
        for number in (1, 2):
            p = proposal()
            p.update({'proposal_id': f'new-integer-{number}', 'operation': 'add'})
            p['changes'] = {'name': f'New community organization {number}', 'country_code': 'GB',
                            'source': 'manual_research',
                            'description': 'Provides a community service with a documented public program.'}
            p['evidence'][0]['fields'] = list(p['changes'])
            proposals.append(p)
        out = self.root/'integer-review.db'
        self.assertEqual(create_review_copy(source, out, proposals, TODAY), 2)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        with connect(out) as db:
            self.assertEqual(db.execute("SELECT id,typeof(id),status,tier FROM organizations WHERE id > 7 ORDER BY id").fetchall(),
                             [(8, 'integer', 'candidate', 'D'), (9, 'integer', 'candidate', 'D')])
            self.assertEqual(db.execute('SELECT proposal_id,organization_id FROM organization_evidence ORDER BY proposal_id').fetchall(),
                             [('new-integer-1', '8'), ('new-integer-2', '9')])
        self.assertEqual([r['id'] for r in fetch_rows(out, None)], [7])
        reviewed_hash = hashlib.sha256(out.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'already applied'):
            create_review_copy(out, self.root/'integer-retry.db', proposals, TODAY)
        self.assertFalse((self.root/'integer-retry.db').exists())
        self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), reviewed_hash)

    def test_integer_primary_key_correction_preserves_identity_and_source(self):
        source = self.root/'integer-source.db'
        with connect(source) as db:
            db.execute('CREATE TABLE organizations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, country_code TEXT, status TEXT, tier TEXT, website TEXT)')
            db.execute("INSERT INTO organizations VALUES (7,'Existing organization','GB','active','B','')")
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        p = proposal(); p['organization_id'] = 7
        out = self.root/'integer-review.db'
        create_review_copy(source, out, [p], TODAY)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        with connect(out) as db:
            self.assertEqual(db.execute('SELECT id,website FROM organizations').fetchall(), [(7, 'https://example.org')])
            self.assertEqual(db.execute('SELECT organization_id FROM organization_evidence').fetchone()[0], '7')

    def test_release_does_not_resurrect_removed_or_merged_rows(self):
        self.assertEqual({r['id'] for r in fetch_rows(self.source, 2)}, {'one', 'country-error'})

    def test_unsupported_score_schema_fails_honestly(self):
        with connect(self.source) as db:
            db.execute('ALTER TABLE organizations DROP COLUMN alignment_score')
        with self.assertRaisesRegex(ValueError, 'no alignment_score'):
            list(fetch_rows(self.source, 2))
        self.assertEqual(len(list(fetch_rows(self.source, None))), 2)

    def test_search_keeps_unlocated_us_rows_and_identity_provenance(self):
        out = self.root/'search'
        counts = build(self.source, out)
        self.assertEqual(counts, {'published': 1, 'countries': 1, 'omitted_for_review': 1})
        row = json.loads((out/'US_UNK.json').read_text())['orgs'][0]
        self.assertEqual(row['id'], 'one'); self.assertEqual(row['src'], 'test_source')
        self.assertEqual(json.loads((out/'US_meta.json').read_text())['total'], 1)

    def test_search_normalizes_full_states_and_removes_inactive_shards(self):
        out = self.root/'search'; build(self.source, out)
        with connect(self.source) as db:
            db.execute("UPDATE organizations SET state_province='California' WHERE id='one'")
        build(self.source, out)
        self.assertTrue((out/'US_CA.json').exists())
        self.assertFalse((out/'US_UNK.json').exists())
        with connect(self.source) as db:
            db.execute("UPDATE organizations SET status='inactive' WHERE id='one'")
        build(self.source, out)
        self.assertFalse((out/'US_CA.json').exists())
        self.assertEqual(json.loads((out/'index.json').read_text())['total_orgs'], 0)

    def test_search_sanitizes_legacy_unsafe_urls_without_changing_database(self):
        with connect(self.source) as db:
            db.execute("UPDATE organizations SET website='javascript:alert(1)' WHERE id='one'")
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        out = self.root/'search'; build(self.source, out)
        self.assertEqual(json.loads((out/'US_UNK.json').read_text())['orgs'][0]['w'], '')
        self.assertEqual(len(json.loads((out/'build-review.json').read_text())['sanitized_fields']), 1)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), before)

    def test_fresh_search_build_passes_metadata_reconciliation(self):
        out = self.root/'search'; build(self.source, out)
        index, us = inventory(out)
        self.assertEqual(index['ntee_categories']['A'], 'Arts & Culture')
        self.assertEqual(set(index['ntee_categories']), set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
        self.assertEqual(index, json.loads((out/'index.json').read_text()))
        self.assertEqual(us, json.loads((out/'US_meta.json').read_text()))

    def test_reconciliation_uses_arrays_removes_nonexistent_countries(self):
        out = self.root/'search'; build(self.source, out)
        index = json.loads((out/'index.json').read_text())
        index['countries']['SG'] = {'name': 'Singapore', 'count': 3}
        index['total_orgs'] = 900
        (out/'index.json').write_text(json.dumps(index))
        corrected, us = inventory(out)
        self.assertNotIn('SG', corrected['countries'])
        self.assertEqual(corrected['total_orgs'], 1)
        self.assertEqual(us['states']['UNK']['count'], 1)


if __name__ == '__main__':
    unittest.main()
