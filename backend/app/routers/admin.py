from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from ..db import messages, pickups, reports, users, zones
from ..schemas import ActiveIn, ZoneIn
from ..security import require_roles
from ..serializers import pickup_public, report_public, user_public

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_roles("admin"))])


def oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(404, "Not found")


@router.get("/overview")
def overview():
    return {
        "residents": users.count_documents({"role": "resident"}),
        "drivers": users.count_documents({"role": "driver"}),
        "pickups": pickups.count_documents({}),
        "reports": reports.count_documents({}),
        "open_reports": reports.count_documents({"open": True}),
        "messages": messages.count_documents({}),
    }


@router.get("/users")
def list_users():
    found = users.find({"role": {"$in": ["resident", "driver"]}}).sort("created_at", -1)
    return [user_public(u) for u in found]


@router.patch("/users/{user_id}")
def set_active(user_id: str, body: ActiveIn):
    user = users.find_one({"_id": oid(user_id)})
    if user is None:
        raise HTTPException(404, "Not found")
    if user["role"] == "admin":
        raise HTTPException(400, "Admin accounts cannot be disabled here.")
    users.update_one({"_id": user["_id"]}, {"$set": {"active": body.active}})
    user["active"] = body.active
    return user_public(user)


@router.get("/pickups")
def list_pickups():
    names = {u["_id"]: u["name"] for u in users.find({}, {"name": 1})}
    return [pickup_public(p, names.get(p["user_id"], "Unknown")) for p in pickups.find().sort("created_at", -1)]


@router.get("/reports")
def list_reports():
    return [report_public(r) for r in reports.find().sort("created_at", -1)]


@router.patch("/reports/{report_id}/resolve")
def resolve_report(report_id: str):
    if reports.update_one({"_id": oid(report_id)}, {"$set": {"open": False}}).matched_count == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}


@router.get("/messages")
def list_messages():
    return [
        {"id": str(m["_id"]), "name": m["name"], "email": m["email"], "message": m["message"],
         "created_at": m["created_at"].isoformat()}
        for m in messages.find().sort("created_at", -1)
    ]


@router.get("/zones")
def list_zones():
    return [{"id": z["_id"], "name": z["name"], "day": z["day"]} for z in zones.find().sort("_id", 1)]


@router.put("/zones/{zone_id}")
def set_zone_day(zone_id: int, body: ZoneIn):
    if zones.update_one({"_id": zone_id}, {"$set": {"day": body.day}}).matched_count == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}
