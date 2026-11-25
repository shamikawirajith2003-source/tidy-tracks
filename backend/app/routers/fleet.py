from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from ..db import fleet, reports, stops
from ..routing import DEPOT, baseline_order, eta_minutes, km, nearest_order, route_length
from ..schemas import IssueIn, TrafficIn, TruckIn
from ..security import require_roles
from ..seed import reset_fleet

router = APIRouter(prefix="/api/fleet", tags=["fleet"])
crew = require_roles("driver", "admin")


def snapshot() -> dict:
    """Everything the map needs: stops, truck position, the optimised order and ETAs."""
    f = fleet.find_one({"_id": "main"})
    items = [
        {"id": s["_id"], "n": s["name"], "x": s["x"], "y": s["y"],
         "done": s["done"], "issue": s.get("issue", ""), "pri": s.get("pri", False)}
        for s in stops.find().sort("_id", 1)
    ]
    pending = [s for s in items if not s["done"]]
    truck = {"x": f["x"], "y": f["y"]}
    order = nearest_order(truck, pending, f["slow"])
    return {
        "stops": items,
        "truck": truck,
        "slow": f["slow"],
        "epoch": f.get("epoch", 0),
        "updated_at": f["updated_at"].isoformat(),
        "order": [s["id"] for s in order],
        "eta": eta_minutes(truck, order),
        "metrics": {
            "remaining_opt_km": km(route_length(truck, order)),
            "remaining_base_km": km(route_length(truck, baseline_order(pending))),
            "total_opt_km": km(route_length(DEPOT, nearest_order(DEPOT, items))),
            "total_base_km": km(route_length(DEPOT, baseline_order(items))),
        },
    }


@router.get("")
def get_fleet():
    # Public: it holds no personal data, so visitors can see the live map on the home page.
    return snapshot()


@router.post("/truck")
def update_truck(body: TruckIn, user: dict = Depends(require_roles("driver"))):
    """The driver's device reports its position (in a real system: GPS)."""
    fleet.update_one({"_id": "main"}, {"$set": {"x": body.x, "y": body.y, "updated_at": datetime.now(timezone.utc)}})
    return {"ok": True}


@router.post("/stops/{stop_id}/collect")
def collect(stop_id: int, user: dict = Depends(crew)):
    if stops.update_one({"_id": stop_id}, {"$set": {"done": True}}).matched_count == 0:
        raise HTTPException(404, "Stop not found")
    return snapshot()


@router.post("/stops/{stop_id}/issue")
def report_issue(stop_id: int, body: IssueIn, user: dict = Depends(require_roles("driver"))):
    stop = stops.find_one({"_id": stop_id})
    if stop is None:
        raise HTTPException(404, "Stop not found")
    stops.update_one({"_id": stop_id}, {"$set": {"done": True, "issue": body.kind}})
    reports.insert_one({
        "user_id": user["_id"], "by": f"Driver: {user['name']}", "reporter_name": user["name"],
        "text": f"{body.kind} at {stop['name']}", "geo": "", "photo": None,
        "open": True, "created_at": datetime.now(timezone.utc),
    })
    return snapshot()


@router.post("/traffic")
def set_traffic(body: TrafficIn, user: dict = Depends(crew)):
    fleet.update_one({"_id": "main"}, {"$set": {"slow": body.slow}})
    return snapshot()


@router.post("/reset")
def reset(user: dict = Depends(require_roles("admin"))):
    reset_fleet()
    return snapshot()
