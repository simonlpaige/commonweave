import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'data')))
from phase2_filter import score_org, is_known_aligned, KNOWN_ALIGNED_NAMES, OPEN_SOURCE_GOVERNANCE
print('known set size:', len(KNOWN_ALIGNED_NAMES))
print('OSG terms:', len(OPEN_SOURCE_GOVERNANCE))
# Known aligned -> 7
print('Apache Software Foundation ->', score_org('Apache Software Foundation', ''))
print('apache software foundation, Inc. ->', score_org('apache software foundation, Inc.', ''))
print('Mozilla Foundation ->', score_org('Mozilla Foundation', ''))
print('NumFOCUS ->', score_org('NumFOCUS', ''))
print('is_known_aligned EFF:', is_known_aligned('EFF'))
# OSG keyword bump
print('Random Open Source Co (no key) ->', score_org('OSS Maintainers', 'fiscal sponsor for open source maintainers, copyleft advocates'))
# Negative test
print('First Baptist Church ->', score_org('First Baptist Church', 'Sunday services'))
