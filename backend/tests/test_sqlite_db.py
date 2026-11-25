import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.sqlite_db import SQLiteClient, SQLiteDatabase


class SQLiteDBTests(unittest.TestCase):
    def setUp(self):
        self.test_db_path = Path(__file__).resolve().parent / "test_temp.db"
        if self.test_db_path.exists():
            self.test_db_path.unlink()
        self.db = SQLiteDatabase(self.test_db_path)

    def tearDown(self):
        self.db.close()
        if self.test_db_path.exists():
            self.test_db_path.unlink()

    def test_insert_and_find_one(self):
        users = self.db["users"]
        res = users.insert_one({"name": "Test User", "email": "test@example.com"})
        self.assertIsNotNone(res.inserted_id)
        self.assertIsInstance(res.inserted_id, ObjectId)
        found = users.find_one({"email": "test@example.com"})
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Test User")
        self.assertEqual(found["_id"], res.inserted_id)

    def test_find_by_objectid(self):
        reports = self.db["reports"]
        doc_id = ObjectId()
        now = datetime.now(timezone.utc)
        reports.insert_one({"_id": doc_id, "text": "Broken bin", "created_at": now})
        found = reports.find_one({"_id": doc_id})
        self.assertIsNotNone(found)
        self.assertEqual(found["text"], "Broken bin")
        self.assertEqual(found["created_at"], now)

    def test_unique_index(self):
        users = self.db["users"]
        users.create_index([("email", ASCENDING)], unique=True)
        users.insert_one({"email": "unique@example.com", "name": "One"})
        with self.assertRaises(DuplicateKeyError):
            users.insert_one({"email": "unique@example.com", "name": "Two"})

    def test_sort_and_projection(self):
        items = self.db["items"]
        items.insert_many([
            {"_id": 1, "val": 30, "name": "C"},
            {"_id": 2, "val": 10, "name": "A"},
            {"_id": 3, "val": 20, "name": "B"},
        ])
        sorted_asc = list(items.find().sort("val", ASCENDING))
        self.assertEqual([d["val"] for d in sorted_asc], [10, 20, 30])
        sorted_desc = list(items.find().sort("val", DESCENDING))
        self.assertEqual([d["val"] for d in sorted_desc], [30, 20, 10])

        projected = list(items.find({}, {"name": 1}))
        self.assertIn("name", projected[0])
        self.assertNotIn("val", projected[0])

    def test_update_one_and_upsert(self):
        fleet = self.db["fleet"]
        res = fleet.update_one({"_id": "main"}, {"$set": {"x": 50, "y": 60}}, upsert=True)
        self.assertEqual(res.modified_count, 1)
        doc = fleet.find_one({"_id": "main"})
        self.assertEqual(doc["x"], 50)
        self.assertEqual(doc["y"], 60)

    def test_filter_in(self):
        users = self.db["users"]
        users.insert_many([
            {"role": "resident", "name": "R"},
            {"role": "driver", "name": "D"},
            {"role": "admin", "name": "A"},
        ])
        results = list(users.find({"role": {"$in": ["resident", "driver"]}}))
        self.assertEqual(len(results), 2)

    def test_count_documents(self):
        reports = self.db["reports"]
        reports.insert_many([
            {"open": True},
            {"open": True},
            {"open": False},
        ])
        self.assertEqual(reports.count_documents({}), 3)
        self.assertEqual(reports.count_documents({"open": True}), 2)
        self.assertEqual(reports.count_documents({"open": False}), 1)


if __name__ == "__main__":
    unittest.main()
