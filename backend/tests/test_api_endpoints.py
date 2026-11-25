import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.db import ensure_indexes, fleet, stops, users, zones
from app.routers.admin import (list_messages, list_pickups, list_reports, list_users, list_zones,
                               overview)
from app.routers.auth import login, me, register
from app.routers.contact import send_message
from app.routers.fleet import collect, get_fleet, report_issue, reset, set_traffic, update_truck
from app.routers.resident import my_pickups, my_reports, request_pickup
from app.schemas import IssueIn, LoginIn, MessageIn, PickupIn, RegisterIn, TrafficIn, TruckIn
from app.seed import seed


class DummyClient:
    host = "127.0.0.1"


class DummyRequest:
    client = DummyClient()


class ApiEndpointsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_indexes()
        seed()

    def test_01_fleet_snapshot(self):
        data = get_fleet()
        self.assertIn("stops", data)
        self.assertIn("truck", data)
        self.assertIn("order", data)
        self.assertEqual(len(data["stops"]), 12)

    def test_02_admin_login(self):
        res = login(LoginIn(email="admin@tidytrack.lk", password="admin123", admin=True))
        self.assertIn("token", res)
        self.assertIn("user", res)
        self.assertEqual(res["user"]["role"], "admin")

    def test_03_resident_login(self):
        res = login(LoginIn(email="a.perera@example.lk", password="demo123", admin=False))
        self.assertIn("token", res)
        self.assertIn("user", res)
        self.assertEqual(res["user"]["role"], "resident")

    def test_04_driver_login(self):
        res = login(LoginIn(email="k.silva@example.lk", password="demo123", admin=False))
        self.assertIn("token", res)
        self.assertIn("user", res)
        self.assertEqual(res["user"]["role"], "driver")

    def test_05_admin_overview(self):
        data = overview()
        self.assertGreaterEqual(data["residents"], 1)
        self.assertGreaterEqual(data["drivers"], 1)

    def test_06_driver_update_truck(self):
        driver = users.find_one({"email": "k.silva@example.lk"})
        res = update_truck(TruckIn(x=100.0, y=200.0), user=driver)
        self.assertTrue(res.get("ok"))
        f = get_fleet()
        self.assertEqual(f["truck"]["x"], 100.0)

    def test_07_traffic_and_reset(self):
        driver = users.find_one({"email": "k.silva@example.lk"})
        res = set_traffic(TrafficIn(slow=True), user=driver)
        self.assertTrue(res["slow"])
        admin_user = users.find_one({"email": "admin@tidytrack.lk"})
        f = reset(user=admin_user)
        self.assertFalse(f["slow"])

    def test_08_resident_pickup(self):
        resident = users.find_one({"email": "a.perera@example.lk"})
        p = request_pickup(PickupIn(material="Plastics", date="2027-01-01"), user=resident)
        self.assertEqual(p["material"], "Plastics")
        self.assertEqual(p["date"], "2027-01-01")
        pickups_list = my_pickups(user=resident)
        self.assertGreaterEqual(len(pickups_list), 1)

    def test_09_contact_message(self):
        res = send_message(MessageIn(name="Jane", email="jane@example.com", message="Hello"), request=DummyRequest())
        self.assertTrue(res.get("ok"))


if __name__ == "__main__":
    unittest.main()
