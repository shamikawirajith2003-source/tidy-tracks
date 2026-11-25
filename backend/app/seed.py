"""First-run data: map stops, collection zones, the admin account and (optionally) demo accounts."""
from datetime import datetime, timedelta, timezone

from .config import settings
from .data import DEMO_PASSWORD, DEMO_USERS, STOPS, ZONES
from .db import fleet, reports, stops, users, zones
from .routing import DEPOT
from .security import hash_password


def reset_fleet() -> None:
    """Start a new collection day: every stop pending, truck back at the depot."""
    now = datetime.now(timezone.utc)
    stops.update_many({}, {"$set": {"done": False, "issue": "", "pri": False}})
    fleet.update_one(
        {"_id": "main"},
        {"$set": {"x": DEPOT["x"], "y": DEPOT["y"], "slow": False, "updated_at": now}, "$inc": {"epoch": 1}},
        upsert=True,
    )


def _add_user(doc: dict, password: str, created_at: datetime) -> None:
    if users.find_one({"email": doc["email"]}):
        return
    users.insert_one({**doc, "password_hash": hash_password(password), "active": True, "created_at": created_at})


def seed() -> None:
    now = datetime.now(timezone.utc)
    if stops.count_documents({}) == 0:
        stops.insert_many([
            {"_id": i + 1, "name": n, "x": x, "y": y, "done": False, "issue": "", "pri": False}
            for i, (x, y, n) in enumerate(STOPS)
        ])
    if fleet.find_one({"_id": "main"}) is None:
        reset_fleet()
    if zones.count_documents({}) == 0:
        zones.insert_many([{"_id": i, "name": n, "day": d} for i, n, d in ZONES])

    _add_user({"name": "Municipal Admin", "email": settings.admin_email, "role": "admin", "phone": "-"},
              settings.admin_password, now)

    if settings.seed_demo:
        for u in DEMO_USERS:
            _add_user(u, DEMO_PASSWORD, now - timedelta(days=30))
        if reports.count_documents({}) == 0:
            reports.insert_one({
                "user_id": None, "by": "Resident", "reporter_name": "Resident",
                "text": "Overflowing bin near Hospital Rd", "geo": "", "photo": None,
                "open": True, "created_at": now,
            })
