import logging
from pathlib import Path
from pymongo import ASCENDING, DESCENDING

from .config import settings

log = logging.getLogger("tidytrack")


def _init_db():
    backend_choice = settings.db_backend
    if backend_choice == "sqlite":
        from .sqlite_db import SQLiteClient

        db_path = settings.sqlite_path or (Path(__file__).resolve().parent.parent / "data" / "tidytrack.db")
        log.info("Using embedded SQLite database at %s", db_path)
        client = SQLiteClient(db_path)
        db = client[settings.mongo_db]
        return client, db
    elif backend_choice in ("auto", "mongodb"):
        try:
            from pymongo import MongoClient

            client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=800, tz_aware=True)
            client.admin.command("ping")
            log.info("Connected to MongoDB at %s", settings.mongo_uri)
            db = client[settings.mongo_db]
            return client, db
        except Exception as err:
            if backend_choice == "mongodb":
                log.error("Failed to connect to required MongoDB at %s: %s", settings.mongo_uri, err)
                raise
            from .sqlite_db import SQLiteClient

            db_path = settings.sqlite_path or (Path(__file__).resolve().parent.parent / "data" / "tidytrack.db")
            log.info("MongoDB not available at %s. Using embedded SQLite database at %s", settings.mongo_uri, db_path)
            client = SQLiteClient(db_path)
            db = client[settings.mongo_db]
            return client, db
    else:
        raise ValueError(f"Unknown DB_BACKEND: {backend_choice}")


client, db = _init_db()

users = db["users"]
stops = db["stops"]
pickups = db["pickups"]
reports = db["reports"]
messages = db["messages"]
zones = db["zones"]
fleet = db["fleet"]


def ensure_indexes() -> None:
    users.create_index([("email", ASCENDING)], unique=True)
    pickups.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    reports.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    reports.create_index([("open", ASCENDING)])
