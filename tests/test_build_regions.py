import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'data'))

import build_regions as br


def max_lon_step(ring, ignore_pole=True):
    return max(
        (abs(a[0] - b[0]) for a, b in zip(ring, ring[1:])
         if not (ignore_pole and abs(a[1]) > 89.9 and abs(b[1]) > 89.9)),
        default=0,
    )


class UnwrapAntimeridianTests(unittest.TestCase):
    def test_ordinary_ring_is_untouched(self):
        ring = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
        self.assertEqual(br.unwrap_ring(ring), ring)

    def test_crossing_ring_becomes_continuous(self):
        ring = [[179, 10], [-179, 10], [-179, 12], [179, 12], [179, 10]]
        out = br.unwrap_ring(ring)
        self.assertLess(max_lon_step(out), 180)
        self.assertEqual([c[1] for c in out], [c[1] for c in ring])
        self.assertEqual(out[0], out[-1])

    def test_result_is_stable_when_reapplied(self):
        ring = [[179, 10], [-179, 10], [-179, 12], [179, 12], [179, 10]]
        once = br.unwrap_ring(ring)
        self.assertEqual(br.unwrap_ring(once), once)

    def test_pole_circling_coast_closes_along_the_pole(self):
        coast = [[-180, -80], [-90, -70], [0, -75], [90, -70], [179, -80], [-180, -80]]
        pole = [[-180, -89.999], [0, -89.999], [179, -89.999], [-180, -89.999]]
        rings = br.unwrap_polygon([pole, coast])
        self.assertEqual(len(rings), 1)
        self.assertLess(max_lon_step(rings[0]), 180)
        self.assertEqual(min(c[1] for c in rings[0]), -90.0)
        self.assertEqual(rings[0][0], rings[0][-1])


if __name__ == '__main__':
    unittest.main()
