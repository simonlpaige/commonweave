"""Checks for the solution-circuit definitions, matcher and published coverage."""
import copy
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'data'))

import build_circuits as bc  # noqa: E402
from circuit_match import Record, normalize, role_matches  # noqa: E402


class MatcherTests(unittest.TestCase):
    def test_normalize_strips_accents_and_punctuation(self):
        self.assertEqual(normalize('São  Paulo — Co-operative!'), 'sao paulo co operative')
        self.assertEqual(normalize(None), '')

    def test_phrases_match_whole_words_only(self):
        role = {'any_of': [{'name': ['land trust']}]}
        self.assertTrue(role_matches(role, Record(1, 'Riverside Land Trust')))
        self.assertFalse(role_matches(role, Record(2, 'Riverside Landtrusts United')))
        self.assertFalse(role_matches(role, Record(3, 'Island Trustees')))

    def test_fields_inside_a_clause_are_all_required(self):
        role = {'any_of': [{'name': ['land trust'], 'area': ['housing_land']}]}
        self.assertTrue(role_matches(role, Record(1, 'X Land Trust', area='housing_land')))
        self.assertFalse(role_matches(role, Record(2, 'X Land Trust', area='ecology')))

    def test_exclusions_override_a_positive_match(self):
        role = {'any_of': [{'model': ['labor_union']}], 'none_of': [{'name': ['credit union']}]}
        self.assertTrue(role_matches(role, Record(1, 'Metal Workers', model='labor_union')))
        self.assertFalse(role_matches(role, Record(2, 'Metal Workers Credit Union', model='labor_union')))

    def test_ntee_prefix_tag_and_description(self):
        self.assertTrue(role_matches({'any_of': [{'ntee': ['J40']}]}, Record(1, 'a', ntee='j402')))
        self.assertFalse(role_matches({'any_of': [{'ntee': ['J40']}]}, Record(1, 'a', ntee='')))
        self.assertTrue(role_matches({'any_of': [{'tag': ['sweat_equity']}]}, Record(1, 'a', tags=['x', 'sweat_equity'])))
        self.assertTrue(role_matches({'any_of': [{'text': ['chitalishte']}]}, Record(1, 'a', description='chitalishte in Elhovo')))
        self.assertFalse(role_matches({'any_of': [{'name': ['chitalishte']}]}, Record(1, 'a', description='chitalishte in Elhovo')))

    def test_unknown_rule_field_is_an_error_not_a_silent_miss(self):
        with self.assertRaises(ValueError):
            role_matches({'any_of': [{'colour': ['red']}]}, Record(1, 'a'))


class SpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = bc.load_spec()

    def test_committed_spec_is_valid(self):
        self.assertEqual(bc.validate_spec(self.spec), [])

    def test_every_documented_circuit_has_a_checked_source_and_a_limit(self):
        for c in self.spec['circuits']:
            if c['evidence'] == 'hypothesis':
                self.assertEqual(c.get('precedents') or [], [], c['id'])
                continue
            self.assertTrue(c['precedents'], c['id'])
            self.assertTrue(c.get('limits'), f"{c['id']} lists no failure or limit")
            for p in c['precedents']:
                self.assertRegex(str(p['checked']), r'^\d{4}-\d{2}-\d{2}$')
                self.assertTrue(p['source'].startswith('https://'))

    def test_validator_rejects_unsourced_and_inconsistent_circuits(self):
        bad = copy.deepcopy(self.spec)
        bad['circuits'][0]['precedents'][0]['source'] = 'I remember reading this'
        self.assertTrue(any('https URL' in p for p in bc.validate_spec(bad)))
        bad = copy.deepcopy(self.spec)
        bad['circuits'][0]['precedents'] = []
        self.assertTrue(any('needs at least one precedent' in p for p in bc.validate_spec(bad)))
        bad = copy.deepcopy(self.spec)
        bad['circuits'][0]['roles'][0]['role'] = 'no_such_role'
        self.assertTrue(any('unknown role' in p for p in bc.validate_spec(bad)))
        bad = copy.deepcopy(self.spec)
        del bad['circuits'][0]['falsifier']
        self.assertTrue(any('missing falsifier' in p for p in bc.validate_spec(bad)))

    def test_map_rules_keep_only_clauses_a_map_point_can_answer(self):
        rule = bc.map_rule({'any_of': [{'ntee': ['J40']}, {'model': ['labor_union']}, {'name': ['Trade Union'], 'tag': ['x']}],
                            'none_of': [{'name': ['Crédit Union']}, {'registration_type': ['x']}]})
        self.assertEqual(rule['any_of'], [{'model': ['labor_union']}])
        self.assertEqual(rule['none_of'], [{'name': ['credit union']}])


class LocalityTests(unittest.TestCase):
    def test_city_with_region_suffix_and_region_names_are_normalized(self):
        lookup = bc.load_region_lookup()
        a = bc.locality_of(Record(1, 'a', country='US', city='Saint Paul, MN'), lookup)
        b = bc.locality_of(Record(2, 'b', country='US', region='Minnesota', city='SAINT PAUL'), lookup)
        self.assertEqual(a, b)
        self.assertIsNone(bc.locality_of(Record(3, 'c', country='US', city=''), lookup))
        self.assertIsNone(bc.locality_of(Record(4, 'd', country='', city='Paris'), lookup))


class PublishedCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(bc.COVERAGE_OUT, encoding='utf-8') as f:
            cls.coverage = json.load(f)
        cls.spec = bc.load_spec()

    def test_coverage_holds_counts_and_places_but_no_organization_fields(self):
        allowed = {'country', 'region', 'city', 'candidates_per_role'}
        for c in self.coverage['circuits']:
            for loc in c['localities']:
                self.assertEqual(set(loc), allowed)
                self.assertTrue(all(isinstance(n, int) and n >= 1 for n in loc['candidates_per_role'].values()))
        text = json.dumps(self.coverage)
        for forbidden in ('rec_', 'org_', 'http://', 'https://', '@'):
            self.assertNotIn(forbidden, text, forbidden)
        circuit_names = {c['name'] for c in self.spec['circuits']}
        self.assertEqual({c['name'] for c in self.coverage['circuits']}, circuit_names)

    def test_sensitive_circuits_publish_no_city_level_coverage(self):
        sensitive = {c['id'] for c in self.spec['circuits'] if c.get('sensitive')}
        self.assertTrue(sensitive)
        for c in self.coverage['circuits']:
            if c['id'] in sensitive:
                self.assertEqual(c['localities'], [])
                self.assertIn('localities_withheld', c)

    def test_coverage_matches_the_committed_spec(self):
        self.assertEqual([c['id'] for c in self.coverage['circuits']], [c['id'] for c in self.spec['circuits']])
        self.assertEqual(sorted(self.coverage['roles']), sorted(self.spec['roles']))
        self.assertEqual(self.coverage['inputs']['release_sha256'], bc.sha256_of(bc.RELEASE_PATH))


if __name__ == '__main__':
    unittest.main()
