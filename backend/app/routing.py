"""Route optimisation. Pure Python, no database access, so it is easy to test.

Stops are dicts with id, x, y and pri (priority). Coordinates are map units; one unit is U metres.
"""
import math

U = 11  # metres per map unit
DEPOT = {"x": 60.0, "y": 360.0}
SLOW_STOP_ID = 4  # the stop a traffic delay applies to in this demo
TRAFFIC_PENALTY = 150
TRUCK_UNITS_PER_MIN = 333 / U  # about 20 km/h
MIN_PER_STOP = 1.5


def dist(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def km(units):
    return units * U / 1000


def nearest_order(start, stops, slow=False):
    """Visit priority stops first, then always the nearest remaining stop."""
    order, rest, cur = [], list(stops), start
    while rest:
        def score(s):
            v = dist(cur, s)
            if s.get("pri"):
                v -= 1e4
            if slow and s["id"] == SLOW_STOP_ID:
                v += TRAFFIC_PENALTY
            return v
        best = min(rest, key=score)
        rest.remove(best)
        order.append(best)
        cur = best
    return order


def baseline_order(stops):
    """The unoptimised "route sheet" used for comparison: streets in alphabetical order."""
    return sorted(stops, key=lambda s: s["n"])


def route_length(start, order):
    """Length of a route that visits `order` and then returns to the depot."""
    total, cur = 0.0, start
    for s in order:
        total += dist(cur, s)
        cur = s
    return total + dist(cur, DEPOT)


def eta_minutes(start, order):
    """{stop_id: minutes until the truck arrives} for every stop in `order`."""
    out, total, cur = {}, 0.0, start
    for i, s in enumerate(order):
        total += dist(cur, s)
        cur = s
        minutes = total * U / 333 + i * MIN_PER_STOP
        out[s["id"]] = max(1, int(minutes + 0.5))
    return out
