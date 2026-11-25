import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.routing import DEPOT, baseline_order, eta_minutes, km, nearest_order, route_length  # noqa: E402
from app.data import STOPS  # noqa: E402


def stops(priority_id=None):
    return [{"id": i + 1, "x": x, "y": y, "n": n, "pri": (i + 1) == priority_id} for i, (x, y, n) in enumerate(STOPS)]


class RoutingTests(unittest.TestCase):
    def test_visits_every_stop_once(self):
        order = nearest_order(DEPOT, stops())
        self.assertEqual(sorted(s["id"] for s in order), list(range(1, 13)))

    def test_optimised_route_is_shorter_than_baseline_sheet(self):
        s = stops()
        optimised = route_length(DEPOT, nearest_order(DEPOT, s))
        baseline = route_length(DEPOT, baseline_order(s))
        self.assertLess(optimised, baseline)
        self.assertGreater(1 - optimised / baseline, 0.3)  # more than 30 % shorter on the demo map

    def test_priority_stop_goes_first(self):
        self.assertEqual(nearest_order(DEPOT, stops(priority_id=10))[0]["id"], 10)

    def test_traffic_delay_moves_bus_stand_later(self):
        normal = [s["id"] for s in nearest_order(DEPOT, stops())]
        slow = [s["id"] for s in nearest_order(DEPOT, stops(), slow=True)]
        self.assertGreaterEqual(slow.index(4), normal.index(4))

    def test_eta_grows_along_the_route(self):
        order = nearest_order(DEPOT, stops())
        eta = eta_minutes(DEPOT, order)
        minutes = [eta[s["id"]] for s in order]
        self.assertEqual(minutes, sorted(minutes))
        self.assertTrue(all(m >= 1 for m in minutes))

    def test_empty_route(self):
        self.assertEqual(nearest_order(DEPOT, []), [])
        self.assertEqual(eta_minutes(DEPOT, []), {})
        self.assertTrue(math.isclose(route_length(DEPOT, []), 0.0))

    def test_km_conversion(self):
        self.assertAlmostEqual(km(1000), 11.0)


if __name__ == "__main__":
    unittest.main()
