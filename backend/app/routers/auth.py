from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from ..db import stops, users
from ..schemas import LoginIn, RegisterIn
from ..security import (DUMMY_HASH, add_hit, clear_hits, current_user, hash_password, make_token, too_many,
                        verify_password)
from ..serializers import user_public

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(body: RegisterIn):
    email = body.email.strip().lower()
    doc = {
        "name": body.name.strip(),
        "email": email,
        "phone": body.phone.strip(),
        "role": body.role,
        "password_hash": hash_password(body.password),
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    if body.role == "resident":
        if body.stop is None or stops.find_one({"_id": body.stop}) is None:
            raise HTTPException(422, "Choose your street.")
        doc["stop"] = body.stop
    else:
        doc["vehicle"] = (body.vehicle or "").strip() or "Not set"
    try:
        doc["_id"] = users.insert_one(doc).inserted_id
    except DuplicateKeyError:
        raise HTTPException(409, "An account with this email already exists.")
    return {"token": make_token(doc), "user": user_public(doc)}


@router.post("/login")
def login(body: LoginIn):
    email = body.email.strip().lower()
    key = f"login:{email}"
    if too_many(key, limit=5, window=300):
        raise HTTPException(429, "Too many failed attempts. Try again in a few minutes.")
    user = users.find_one({"email": email})
    if not verify_password(body.password, user["password_hash"] if user else DUMMY_HASH) or user is None:
        add_hit(key)
        raise HTTPException(401, "Email or password is not correct.")
    # The admin login page and the normal login page accept different kinds of account.
    if body.admin != (user["role"] == "admin"):
        raise HTTPException(403, "This is not an admin account." if body.admin
                            else "Admins log in from the Admin login page.")
    if not user.get("active", True):
        raise HTTPException(403, "This account is disabled. Contact the municipal office.")
    clear_hits(key)
    return {"token": make_token(user), "user": user_public(user)}


@router.get("/me")
def me(user: dict = Depends(current_user)):
    return user_public(user)
