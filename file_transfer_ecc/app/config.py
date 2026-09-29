"""
app/config.py — Configuration Classes
=======================================
Three environments:
  - DevelopmentConfig  (default)
  - TestingConfig      (for pytest)
  - ProductionConfig   (for deployment)

Usage:
    app = Flask(__name__)
    app.config.from_object(config["development"])
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Shared configuration for all environments."""

    # ── Flask Core ────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "dev-secret-key-replace-in-production-!!!"
    )
    DEBUG: bool = False
    TESTING: bool = False

    # ── SQLAlchemy ────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///file_transfer.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False  # Set True to see SQL queries in dev

    # ── File Uploads ──────────────────────────────────────────
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads"
    )
    MAX_CONTENT_LENGTH: int = int(
        os.environ.get("MAX_CONTENT_LENGTH_MB", 100)
    ) * 1024 * 1024  # Convert MB → bytes

    # Allowed file extensions (whitelist)
    ALLOWED_EXTENSIONS: set = {
        "pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt",
        "txt", "csv", "json", "xml",
        "png", "jpg", "jpeg", "gif", "bmp", "webp", "svg",
        "zip", "tar", "gz", "7z", "rar",
        "mp4", "avi", "mkv", "mov",
        "mp3", "wav", "ogg",
        "py", "js", "html", "css", "md",
    }

    # ── Session ───────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_SECURE: bool = False  # Override to True in production
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(
        minutes=int(os.environ.get("PERMANENT_SESSION_LIFETIME_MINUTES", 30))
    )

    # ── WTF CSRF ──────────────────────────────────────────────
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour

    # ── ECC Curve ─────────────────────────────────────────────
    ECC_CURVE: str = "P-256"  # NIST P-256 / secp256r1

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production-!!!"
    )
    # Access token: 7 days; refresh token: 30 days
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        days=int(os.environ.get("JWT_ACCESS_TOKEN_DAYS", 7))
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", 30))
    )


class DevelopmentConfig(BaseConfig):
    """Development environment — verbose logging, SQLite."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # Toggle True if you want SQL output


class TestingConfig(BaseConfig):
    """Testing environment — in-memory DB, CSRF disabled."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False  # Disable CSRF for tests
    UPLOAD_FOLDER: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "tests", "test_uploads"
    )


class ProductionConfig(BaseConfig):
    """Production environment — enforce HTTPS, strict cookies."""

    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: str = "Strict"
    # Requires DATABASE_URL env var set to MySQL/PostgreSQL URI
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///file_transfer_prod.db"
    )


# ── Config selector ───────────────────────────────────────────
config_map: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
