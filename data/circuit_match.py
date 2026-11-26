"""
circuit_match.py: one small, dependency-free rule matcher shared by the
solution-circuit tooling.

A *role* (for example "community land trust" or "labor union") is recognised
from published record fields only. Rules never read coordinates and never
assert that a record performs the role; a match is a research lead.

Rule shape (see data/circuits.yaml):

    any_of:                      # record matches if ANY clause matches
      - {model: [labor_union]}   # inside one clause every listed field must match
      - {ntee: [J40]}
      - {name: ["trade union", "sindicato"], area: [democracy]}
    none_of:                     # ...and NO exclusion clause matches
      - {name: ["credit union"]}

Clause fields and how they compare:

    model, source, area, registration_type   exact, case-sensitive value
    tag                                      exact member of the comma list
    ntee                                     code starts with the given prefix
    name                                     whole-word phrase in the name
    text                                     whole-word phrase in name or description

The same semantics are implemented in assets/js/map/pathways.js for the map.
tests/test_circuits.py and assets/js/map/pathways.test.cjs check that the two
implementations agree on every published map point.
"""
import unicodedata
from functools import lru_cache

EXACT_FIELDS = ('model', 'source', 'area', 'registration_type')
CLAUSE_FIELDS = EXACT_FIELDS + ('tag', 'ntee', 'name', 'text')


def normalize(value):
    """Lowercase, strip accents, and collapse anything that is not a letter or
    digit into single spaces. Mirrors normalize() in pathways.js."""
    if value is None:
        return ''
    decomposed = unicodedata.normalize('NFKD', str(value))
    unmarked = ''.join(ch for ch in decomposed if not unicodedata.category(ch).startswith('M'))
    spaced = ''.join(ch if unicodedata.category(ch)[0] in ('L', 'N') else ' ' for ch in unmarked.lower())
    return ' '.join(spaced.split())


@lru_cache(maxsize=None)
def _needle(phrase):
    normalized = normalize(phrase)
    return (' ' + normalized + ' ') if normalized else ''


def has_phrase(normalized_haystack, phrase):
    needle = _needle(phrase)
    return bool(needle) and needle in (' ' + normalized_haystack + ' ')


class Record:
    """Uniform read-only view over a release row or a map point."""

    __slots__ = ('id', 'name', 'model', 'source', 'area', 'registration_type',
                 'tags', 'ntee', 'country', 'region', 'city', '_name_n', '_text_n')

    def __init__(self, id, name, model='', source='', area='', registration_type='',
                 tags=(), ntee='', description='', country='', region='', city=''):
        self.id = id
        self.name = name or ''
        self.model = model or ''
        self.source = source or ''
        self.area = area or ''
        self.registration_type = registration_type or ''
        self.tags = frozenset(tags)
        self.ntee = (ntee or '').strip().upper()
        self.country = country or ''
        self.region = region or ''
        self.city = city or ''
        self._name_n = normalize(self.name)
        self._text_n = normalize(self.name + ' ' + (description or ''))

    @classmethod
    def from_release(cls, row):
        tags = [t.strip() for t in (row.get('tags') or '').split(',') if t.strip()]
        return cls(
            id=row.get('id'), name=row.get('name'), model=row.get('model_type'),
            source=row.get('source'), area=row.get('framework_area'),
            registration_type=row.get('registration_type'), tags=tags,
            ntee=row.get('ntee_code'), description=row.get('description'),
            country=row.get('country_code'), region=row.get('state_province'),
            city=row.get('city'))

    @classmethod
    def from_map_point(cls, props):
        """Map points carry only name, category, model, source and locality."""
        return cls(
            id=props.get('id'), name=props.get('n'), model=props.get('m'),
            source=props.get('src'), area=props.get('f'),
            country=props.get('cc'), region=props.get('st'), city=props.get('ci'))


def clause_matches(clause, rec):
    for field, wanted in clause.items():
        if field in EXACT_FIELDS:
            if getattr(rec, field) not in wanted:
                return False
        elif field == 'tag':
            if not any(w in rec.tags for w in wanted):
                return False
        elif field == 'ntee':
            if not rec.ntee or not any(rec.ntee.startswith(str(w).upper()) for w in wanted):
                return False
        elif field == 'name':
            if not any(has_phrase(rec._name_n, w) for w in wanted):
                return False
        elif field == 'text':
            if not any(has_phrase(rec._text_n, w) for w in wanted):
                return False
        else:
            raise ValueError(f'Unknown rule field: {field!r}')
    return True


def role_matches(role, rec):
    if not any(clause_matches(c, rec) for c in role.get('any_of') or []):
        return False
    return not any(clause_matches(c, rec) for c in role.get('none_of') or [])


def validate_role(key, role):
    """Return a list of human-readable problems with one role definition."""
    problems = []
    if not role.get('any_of'):
        problems.append(f'role {key}: any_of must list at least one clause')
    for part in ('any_of', 'none_of'):
        for i, clause in enumerate(role.get(part) or []):
            if not isinstance(clause, dict) or not clause:
                problems.append(f'role {key}: {part}[{i}] must be a non-empty mapping')
                continue
            for field, wanted in clause.items():
                if field not in CLAUSE_FIELDS:
                    problems.append(f'role {key}: {part}[{i}] uses unknown field {field!r}')
                elif not isinstance(wanted, list) or not wanted or not all(isinstance(w, str) and w.strip() for w in wanted):
                    problems.append(f'role {key}: {part}[{i}].{field} must be a non-empty list of strings')
    return problems
