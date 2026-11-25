import os


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes")


class Settings:
    db_backend = os.getenv("DB_BACKEND", "auto").strip().lower()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "tidytrack")
    sqlite_path = os.getenv("SQLITE_PATH", "").strip()
    jwt_secret = os.getenv("JWT_SECRET", "change-me-in-production-minimum-32-bytes-long-key")
    jwt_hours = int(os.getenv("JWT_HOURS", "12"))
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    admin_email = os.getenv("ADMIN_EMAIL", "admin@tidytrack.lk").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    seed_demo = _flag("SEED_DEMO", "true")
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    max_upload = 5 * 1024 * 1024  # bytes


settings = Settings()
