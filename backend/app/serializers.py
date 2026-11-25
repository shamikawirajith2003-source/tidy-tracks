"""Turn MongoDB documents into JSON-safe dicts (ObjectId -> str, datetime -> ISO string). Password hashes never leave here."""


def user_public(u: dict) -> dict:
    return {
        "id": str(u["_id"]),
        "name": u["name"],
        "email": u["email"],
        "phone": u.get("phone", ""),
        "role": u["role"],
        "stop": u.get("stop"),
        "vehicle": u.get("vehicle"),
        "active": u.get("active", True),
        "created_at": u["created_at"].isoformat(),
    }


def report_public(r: dict) -> dict:
    return {
        "id": str(r["_id"]),
        "text": r["text"],
        "by": r["by"],
        "reporter": r.get("reporter_name", ""),
        "geo": r.get("geo", ""),
        "photo_url": f"/uploads/{r['photo']}" if r.get("photo") else None,
        "open": r.get("open", True),
        "created_at": r["created_at"].isoformat(),
    }


def pickup_public(p: dict, resident_name: str = "") -> dict:
    return {
        "id": str(p["_id"]),
        "material": p["material"],
        "date": p["date"],
        "resident": resident_name,
        "created_at": p["created_at"].isoformat(),
    }
