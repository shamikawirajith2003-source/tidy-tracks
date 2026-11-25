import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import client, ensure_indexes
from .routers import admin, auth, contact, fleet, resident
from .seed import seed

log = logging.getLogger("tidytrack")
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.jwt_secret.startswith("change-me-in-production"):
        log.warning("JWT_SECRET is the default value. Set a long random secret before deploying.")
    ensure_indexes()
    seed()
    yield


app = FastAPI(title="TidyTrack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


for module in (auth, resident, fleet, admin, contact):
    app.include_router(module.router)

# Photos attached to complaints. File names are random, and the server checks the file really is an image.
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/api/health")
def health():
    client.admin.command("ping")
    return {"status": "ok"}
