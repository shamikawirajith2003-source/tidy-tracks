import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..config import settings
from ..db import pickups, reports, stops
from ..schemas import PickupIn
from ..security import require_roles
from ..serializers import pickup_public, report_public

router = APIRouter(prefix="/api", tags=["resident"])
resident_only = require_roles("resident")

IMAGE_MESSAGE = "Please upload a JPG, PNG, GIF or WebP image under 5 MB."


def detect_image_ext(data: bytes) -> str | None:
    """Identify the image type from its first bytes, so the filename the client sends is never trusted."""
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None


@router.post("/pickups", status_code=201)
def request_pickup(body: PickupIn, user: dict = Depends(resident_only)):
    try:
        wanted = date.fromisoformat(body.date)
    except ValueError:
        raise HTTPException(422, "Pickup date cannot be in the past.")
    if wanted < date.today():
        raise HTTPException(422, "Pickup date cannot be in the past.")
    doc = {"user_id": user["_id"], "material": body.material, "date": body.date,
           "created_at": datetime.now(timezone.utc)}
    doc["_id"] = pickups.insert_one(doc).inserted_id
    # The crew visits this resident's street earlier in today's route.
    stops.update_one({"_id": user["stop"], "done": False}, {"$set": {"pri": True}})
    return pickup_public(doc, user["name"])


@router.get("/me/pickups")
def my_pickups(user: dict = Depends(resident_only)):
    return [pickup_public(p, user["name"]) for p in pickups.find({"user_id": user["_id"]}).sort("created_at", -1)]


@router.post("/reports", status_code=201)
def create_report(
    text: str = Form(..., min_length=1, max_length=1000),
    geo: str = Form("", max_length=100),
    photo: UploadFile | None = File(None),
    user: dict = Depends(resident_only),
):
    filename = None
    if photo is not None and photo.filename:
        data = photo.file.read(settings.max_upload + 1)
        ext = detect_image_ext(data)
        if len(data) > settings.max_upload or ext is None:
            raise HTTPException(422, IMAGE_MESSAGE)
        filename = uuid.uuid4().hex + ext
        (Path(settings.upload_dir) / filename).write_bytes(data)
    doc = {"user_id": user["_id"], "by": "Resident", "reporter_name": user["name"], "text": text.strip(),
           "geo": geo.strip(), "photo": filename, "open": True, "created_at": datetime.now(timezone.utc)}
    doc["_id"] = reports.insert_one(doc).inserted_id
    return report_public(doc)


@router.get("/me/reports")
def my_reports(user: dict = Depends(resident_only)):
    return [report_public(r) for r in reports.find({"user_id": user["_id"], "by": "Resident"}).sort("created_at", -1)]
