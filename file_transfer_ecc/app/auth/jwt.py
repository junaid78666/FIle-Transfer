"""
app/auth/jwt.py — JWT Token Utilities
======================================
Provides:
  - generate_tokens(user)  → { access_token, refresh_token, expires_in }
  - decode_access_token(token) → user_id (int) or raises JWTError
  - jwt_required decorator  → protects routes via Authorization: Bearer header
                               while remaining backward-compatible with Flask-Login sessions
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, g
from app.models.user import User


class JWTError(Exception):
    pass


# ─────────────────────────────────────────────────────────────
# Token Generation
# ─────────────────────────────────────────────────────────────

def generate_tokens(user):
    """
    Generate a short-lived access token and a longer-lived refresh token.

    Returns:
        dict with keys: access_token, refresh_token, token_type, expires_in (seconds)
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    secret = current_app.config["JWT_SECRET_KEY"]

    access_expires  = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    refresh_expires = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]

    access_payload = {
        "sub":      str(user.id),
        "username": user.username,
        "type":     "access",
        "iat":      now,
        "exp":      now + access_expires,
    }

    refresh_payload = {
        "sub":  str(user.id),
        "type": "refresh",
        "iat":  now,
        "exp":  now + refresh_expires,
    }

    access_token  = jwt.encode(access_payload,  secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "Bearer",
        "expires_in":    int(access_expires.total_seconds()),
    }


# ─────────────────────────────────────────────────────────────
# Token Decoding
# ─────────────────────────────────────────────────────────────

def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: Raw JWT string
        expected_type: 'access' or 'refresh'

    Returns:
        Decoded payload dict

    Raises:
        JWTError with a human-readable message
    """
    secret = current_app.config["JWT_SECRET_KEY"]
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise JWTError("Token has expired. Please log in again.")
    except jwt.InvalidTokenError as e:
        raise JWTError(f"Invalid token: {e}")

    if payload.get("type") != expected_type:
        raise JWTError(f"Expected '{expected_type}' token, got '{payload.get('type')}'.")

    return payload


def get_user_from_access_token(token: str):
    """
    Decode an access token and return the matching User object.

    Returns:
        User instance

    Raises:
        JWTError if token is invalid or user not found / inactive
    """
    payload = decode_token(token, expected_type="access")
    user_id = int(payload["sub"])

    # Import inside function to avoid circular imports
    from app import db
    user = db.session.get(User, user_id)

    if user is None or not user.is_active:
        raise JWTError("User not found or account disabled.")

    return user


# ─────────────────────────────────────────────────────────────
# Extract Token from Request
# ─────────────────────────────────────────────────────────────

def _extract_bearer_token() -> str | None:
    """
    Pull the raw JWT string from the Authorization header.
    Expects:  Authorization: Bearer <token>
    Returns None if header is absent or malformed.
    """
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


# ─────────────────────────────────────────────────────────────
# jwt_required Decorator
# ─────────────────────────────────────────────────────────────

def jwt_required(fn):
    """
    Route decorator that accepts EITHER:
      1. A valid JWT Bearer token in Authorization header   (new JWT flow)
      2. A valid Flask-Login session cookie                 (legacy / browser flow)

    On success: sets g.current_jwt_user to the User object.
    On failure: returns 401 JSON.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # ── Try JWT Bearer token first ──────────────────────
        token = _extract_bearer_token()
        if token:
            try:
                user = get_user_from_access_token(token)
                g.current_jwt_user = user
                return fn(*args, **kwargs)
            except JWTError as e:
                return jsonify({"status": "error", "message": str(e), "code": 401}), 401

        # ── Fall back to Flask-Login session ─────────────────
        from flask_login import current_user
        if current_user.is_authenticated:
            g.current_jwt_user = current_user
            return fn(*args, **kwargs)

        return jsonify({
            "status":  "error",
            "message": "Authentication required. Please log in.",
            "code":    401,
        }), 401

    return wrapper


# ─────────────────────────────────────────────────────────────
# Convenience: get the authenticated user in a jwt_required view
# ─────────────────────────────────────────────────────────────

def get_jwt_user():
    """
    Return the authenticated user set by @jwt_required.
    Call this inside any @jwt_required view instead of current_user.
    """
    return g.get("current_jwt_user")
