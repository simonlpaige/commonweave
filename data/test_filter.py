import sys
sys.path.insert(0, r'C:\Users\simon\.openclaw\workspace\ecolibrium\data')
from run_audit import is_in_scope

tests = [
    ('First Baptist Church', 'X20', ''),
    ('Mondragon Cooperative', 'Y', 'worker owned'),
    ('Habitat for Humanity', 'L', 'housing'),
    ('VFW Post 1234', 'W', ''),
    ('Community Solar Cooperative', 'C', 'renewable energy'),
    ('St. Mary Parish', 'X', ''),
    ('St. Mary Free Clinic', 'E', 'healthcare for uninsured'),
    ('Homeowners Association Oak Hills', 'S', ''),
    ('NAACP Chapter', 'R', 'civil rights'),
    ('GolfClub of Denver', 'N', ''),
    ('Community Land Trust', 'L', 'affordable housing'),
    ('Mutual Aid Network', 'P', 'solidarity economy'),
    ('Springfield Booster Club', 'N', ''),
    ('Church of Latter Day Saints', 'X', ''),
    ('LDS Family Services', 'X', 'social services housing immigrant'),
]
for name, ntee, desc in tests:
    result = is_in_scope(name, ntee, desc)
    flag = 'IN ' if result else 'OUT'
    print(f'{flag}  {name} [{ntee}]')
