"""SQLite-backed document storage compatible with the PyMongo collection interface.

Allows TidyTrack to run out-of-the-box without Docker or MongoDB installed,
while preserving full persistence, ObjectId semantics, datetime precision,
and unique constraints.
"""

from __future__ import annotations

import os
import pickle
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_PATH = DB_DIR / "tidytrack.db"


class InsertOneResult:
    def __init__(self, inserted_id: Any):
        self.inserted_id = inserted_id


class InsertManyResult:
    def __init__(self, inserted_ids: list[Any]):
        self.inserted_ids = inserted_ids


class UpdateResult:
    def __init__(self, matched_count: int, modified_count: int):
        self.matched_count = matched_count
        self.modified_count = modified_count


class SQLiteCursor:
    def __init__(self, docs: list[dict], projection: dict | None = None):
        self._docs = docs
        self._projection = projection

    def sort(self, key_or_list: Any, direction: int = ASCENDING):
        if isinstance(key_or_list, list):
            for key, d in reversed(key_or_list):
                rev = (d == -1 or d == DESCENDING)
                self._docs.sort(key=lambda x: (x.get(key) is None, x.get(key)), reverse=rev)
        else:
            rev = (direction == -1 or direction == DESCENDING)
            self._docs.sort(key=lambda x: (x.get(key_or_list) is None, x.get(key_or_list)), reverse=rev)
        return self

    def _project(self, doc: dict) -> dict:
        if not self._projection:
            return doc.copy()
        res = {"_id": doc["_id"]} if "_id" in doc else {}
        for k, v in self._projection.items():
            if v and k in doc:
                res[k] = doc[k]
        return res

    def __iter__(self):
        for doc in self._docs:
            yield self._project(doc)

    def __len__(self):
        return len(self._docs)

    def __getitem__(self, index):
        return [self._project(d) for d in self._docs][index]


def _matches(doc: dict, filt: dict | None) -> bool:
    if not filt:
        return True
    for key, val in filt.items():
        doc_val = doc.get(key)
        if isinstance(val, dict):
            if "$in" in val:
                in_list = val["$in"]
                matched = False
                for item in in_list:
                    if doc_val == item or str(doc_val) == str(item):
                        matched = True
                        break
                if not matched:
                    return False
            elif "$eq" in val:
                if doc_val != val["$eq"] and str(doc_val) != str(val["$eq"]):
                    return False
            elif "$ne" in val:
                if doc_val == val["$ne"] or str(doc_val) == str(val["$ne"]):
                    return False
        else:
            if doc_val != val:
                if isinstance(val, (ObjectId, str)) and isinstance(doc_val, (ObjectId, str)):
                    if str(doc_val) != str(val):
                        return False
                else:
                    return False
    return True


def _apply_update(doc: dict, update: dict) -> None:
    if "$set" in update:
        for k, v in update["$set"].items():
            doc[k] = v
    if "$inc" in update:
        for k, v in update["$inc"].items():
            doc[k] = doc.get(k, 0) + v


class SQLiteCollection:
    def __init__(self, db: Any, name: str):
        self.db = db
        self.name = name
        self.unique_keys: list[list[str]] = []

    def create_index(self, keys, unique: bool = False, **kwargs):
        if unique:
            key_names = [k[0] if isinstance(k, (list, tuple)) else k for k in keys]
            if key_names not in self.unique_keys:
                self.unique_keys.append(key_names)
        return "_".join(f"{k}_{d}" for k, d in keys)

    def _check_unique(self, doc: dict, exclude_id: Any = None):
        for keys in self.unique_keys:
            check_filter = {k: doc[k] for k in keys if k in doc}
            if len(check_filter) == len(keys):
                existing = self.find(check_filter)
                for other in existing:
                    if exclude_id is not None and other.get("_id") == exclude_id:
                        continue
                    raise DuplicateKeyError(
                        f"E11000 duplicate key error collection: {self.name} index on {keys} dup key: {check_filter}"
                    )

    def insert_one(self, doc: dict) -> InsertOneResult:
        doc = doc.copy()
        if "_id" not in doc or doc["_id"] is None:
            doc["_id"] = ObjectId()
        self._check_unique(doc)
        self.db._write_doc(self.name, doc["_id"], doc)
        return InsertOneResult(doc["_id"])

    def insert_many(self, docs: list[dict]) -> InsertManyResult:
        ids = []
        for doc in docs:
            res = self.insert_one(doc)
            ids.append(res.inserted_id)
        return InsertManyResult(ids)

    def find_one(self, filter: dict | None = None) -> dict | None:
        all_docs = self.db._load_collection(self.name)
        for doc in all_docs:
            if _matches(doc, filter):
                return doc.copy()
        return None

    def find(self, filter: dict | None = None, projection: dict | None = None) -> SQLiteCursor:
        all_docs = self.db._load_collection(self.name)
        matched = [doc for doc in all_docs if _matches(doc, filter)]
        return SQLiteCursor(matched, projection)

    def count_documents(self, filter: dict | None = None) -> int:
        all_docs = self.db._load_collection(self.name)
        return sum(1 for doc in all_docs if _matches(doc, filter))

    def update_one(self, filter: dict, update: dict, upsert: bool = False) -> UpdateResult:
        all_docs = self.db._load_collection(self.name)
        for doc in all_docs:
            if _matches(doc, filter):
                updated_doc = doc.copy()
                _apply_update(updated_doc, update)
                self._check_unique(updated_doc, exclude_id=doc.get("_id"))
                self.db._write_doc(self.name, doc["_id"], updated_doc)
                return UpdateResult(matched_count=1, modified_count=1)
        if upsert:
            new_doc = {}
            for k, v in filter.items():
                if not isinstance(v, dict):
                    new_doc[k] = v
            if "_id" not in new_doc:
                new_doc["_id"] = ObjectId()
            _apply_update(new_doc, update)
            self._check_unique(new_doc)
            self.db._write_doc(self.name, new_doc["_id"], new_doc)
            return UpdateResult(matched_count=0, modified_count=1)
        return UpdateResult(matched_count=0, modified_count=0)

    def update_many(self, filter: dict, update: dict) -> UpdateResult:
        all_docs = self.db._load_collection(self.name)
        matched = 0
        for doc in all_docs:
            if _matches(doc, filter):
                matched += 1
                updated_doc = doc.copy()
                _apply_update(updated_doc, update)
                self.db._write_doc(self.name, doc["_id"], updated_doc)
        return UpdateResult(matched_count=matched, modified_count=matched)


class SQLiteDatabase:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()
        self._collections: dict[str, SQLiteCollection] = {}

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    collection TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    data BLOB NOT NULL,
                    PRIMARY KEY (collection, doc_id)
                );
                """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_col ON documents(collection);")
            self._conn.commit()

    def _write_doc(self, collection: str, doc_id: Any, doc: dict) -> None:
        blob = pickle.dumps(doc)
        doc_id_str = str(doc_id)
        with self._lock:
            self._conn.execute("""
                INSERT INTO documents (collection, doc_id, data)
                VALUES (?, ?, ?)
                ON CONFLICT(collection, doc_id) DO UPDATE SET data = excluded.data;
                """, (collection, doc_id_str, blob))
            self._conn.commit()

    def _load_collection(self, collection: str) -> list[dict]:
        with self._lock:
            cursor = self._conn.execute("SELECT data FROM documents WHERE collection = ?", (collection,))
            rows = cursor.fetchall()
            return [pickle.loads(r[0]) for r in rows]

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __getitem__(self, name: str) -> SQLiteCollection:
        if name not in self._collections:
            self._collections[name] = SQLiteCollection(self, name)
        return self._collections[name]


class FakeAdmin:
    def command(self, cmd: str) -> dict:
        return {"ok": 1.0}


class SQLiteClient:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db = SQLiteDatabase(db_path)
        self.admin = FakeAdmin()

    def __getitem__(self, name: str) -> SQLiteDatabase:
        return self.db
