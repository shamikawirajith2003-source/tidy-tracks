from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from ..db import messages
from ..schemas import MessageIn
from ..security import add_hit, too_many

router = APIRouter(prefix="/api", tags=["contact"])


@router.post("/messages", status_code=201)
def send_message(body: MessageIn, request: Request):
    key = f"msg:{request.client.host if request.client else 'unknown'}"
    if too_many(key, limit=5, window=3600):
        raise HTTPException(429, "Too many messages. Please try again later.")
    messages.insert_one({
        "name": body.name.strip(), "email": body.email.strip().lower(), "message": body.message.strip(),
        "created_at": datetime.now(timezone.utc),
    })
    add_hit(key)
    return {"ok": True}
