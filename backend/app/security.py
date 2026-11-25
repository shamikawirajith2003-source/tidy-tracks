import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .db import users

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    # bcrypt only uses the first 72 bytes
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


# Checked when the email is unknown so that a missing account takes as long as a wrong password.
DUMMY_HASH = hash_password("not-a-real-password")


def make_token(user: dict) -> str:
    payload = {
        "sub": str(user["_id"]),
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.jwt_hours),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if creds is None:
        raise HTTPException(401, "Not authenticated")
    try:
        data = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=["HS256"])
        user = users.find_one({"_id": ObjectId(data["sub"])})
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    if not user or not user.get("active", True):
        raise HTTPException(401, "Account unavailable")
    return user


def require_roles(*roles: str):
    """Role-based access control: use as Depends(require_roles("admin"))."""
    def dependency(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, "Not allowed for your role")
        return user
    return dependency


# Very small in-memory rate limiter (one process only; use Redis or a proxy for several workers).
_hits: dict[str, list[float]] = {}


def _recent(key: str, window: int) -> list[float]:
    now = time.time()
    recent = [t for t in _hits.get(key, []) if now - t < window]
    _hits[key] = recent
    return recent


def too_many(key: str, limit: int, window: int) -> bool:
    return len(_recent(key, window)) >= limit


def add_hit(key: str) -> None:
    _hits.setdefault(key, []).append(time.time())


def clear_hits(key: str) -> None:
    _hits.pop(key, None)
