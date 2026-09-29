"""
app/auth/routes.py — Authentication Blueprint Routes
======================================================
Handles user registration, login, logout, and profile endpoints.

Endpoints:
  POST /auth/register   → Create a new user account
  POST /auth/login      → Authenticate and create session
  POST /auth/logout     → Destroy session
  GET  /auth/me         → Return current user info (JSON)
  GET  /auth/profile    → Return current user + ECC public key (JSON)
  GET  /users/list      → List all users except current user (for recipient selection)
"""

from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user

from app.auth.forms import RegistrationForm, LoginForm
from app.auth.utils import register_user, authenticate_user, collect_form_errors
from app.auth.jwt import generate_tokens, decode_token, jwt_required, get_jwt_user, JWTError
from app.models.user import User

# ── Blueprint definition ──────────────────────────────────────
auth_bp = Blueprint("auth", __name__)


# ══════════════════════════════════════════════════════════════
# GET/POST /auth/register
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Render registration page in browser.
    POST: Register a new user account.

    Request (JSON or form-data):
        username, email, password, confirm_password

    Response 201:
        { "status": "success", "message": "...", "user": {...} }

    Response 400:
        { "status": "error", "errors": [...] }
    """
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("main.dashboard"))
        return render_template("auth/register.html")
    form = RegistrationForm(data=request.get_json(silent=True) or request.form)

    if not form.validate():
        return jsonify({
            "status": "error",
            "message": "Validation failed.",
            "errors": collect_form_errors(form),
        }), 400

    try:
        user = register_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        # Auto-login: Flask-Login session + JWT tokens in one step
        login_user(user, remember=True)
        user.update_last_login()
        tokens = generate_tokens(user)

        # Cache recovered private key in session for seamless ECDSA signing and decryption
        if hasattr(user, "_priv_key_pem") and user._priv_key_pem:
            session["_priv_key_pem"] = user._priv_key_pem

        current_app.logger.info(
            f"[AUTH] Registered + auto-login: user_id={user.id} username='{user.username}'"
        )

        return jsonify({
            "status":  "success",
            "message": f"Welcome, {user.username}! Your ECC key pair has been generated.",
            "user":    user.to_dict(),
            "tokens":  tokens,
            "redirect": "/dashboard",
        }), 201

    except Exception as exc:
        current_app.logger.error(f"[AUTH] Registration error: {exc}", exc_info=True)
        return jsonify({
            "status":  "error",
            "message": "An unexpected error occurred during registration. Please try again.",
        }), 500


# ══════════════════════════════════════════════════════════════
# GET/POST /auth/login
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Render login page in browser.
    POST: Authenticate a registered user and create a session.

    Request (JSON or form-data):
        email, password, remember_me (optional bool)

    Response 200:
        { "status": "success", "message": "...", "user": {...} }

    Response 400 (validation error):
        { "status": "error", "errors": [...] }

    Response 401 (wrong credentials):
        { "status": "error", "message": "..." }
    """
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("main.dashboard"))
        return render_template("auth/login.html")
    form = LoginForm(data=request.get_json(silent=True) or request.form)

    if not form.validate():
        return jsonify({
            "status": "error",
            "message": "Validation failed.",
            "errors": collect_form_errors(form),
        }), 400

    user = authenticate_user(form.email.data, form.password.data)

    if user is None:
        return jsonify({
            "status": "error",
            "message": "Invalid email or password. Please try again.",
        }), 401

    # If already logged in as a different user (or same), log out first
    try:
        if current_user.is_authenticated:
            logout_user()
    except Exception:
        pass

    # Create Flask-Login session (cookie) + JWT tokens
    remember = bool(form.remember_me.data)
    login_user(user, remember=remember)
    user.update_last_login()
    tokens = generate_tokens(user)

    # Cache recovered private key in session for seamless ECDSA signing and decryption
    if user.ecc_key:
        try:
            from app.crypto.ecc import recover_private_key, serialize_private_key
            priv_key = recover_private_key(
                user.ecc_key.private_key_enc,
                user.ecc_key.kdf_salt,
                user.ecc_key.priv_nonce,
                user.ecc_key.priv_auth_tag,
                form.password.data,
            )
            session["_priv_key_pem"] = serialize_private_key(priv_key)
        except Exception as e:
            current_app.logger.warning(f"[AUTH] Could not cache private key in session: {e}")

    current_app.logger.info(
        f"[AUTH] User logged in: user_id={user.id} username='{user.username}'"
    )

    return jsonify({
        "status":  "success",
        "message": f"Welcome back, {user.username}!",
        "user":    user.to_dict(include_timestamps=True),
        "tokens":  tokens,
    }), 200


# ══════════════════════════════════════════════════════════════
# POST /auth/logout
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Destroy the current user's Flask-Login session.
    The client must also delete the JWT from localStorage.

    Response 200:
        { "status": "success", "message": "..." }
    """
    session.pop("_priv_key_pem", None)
    username = getattr(current_user, 'username', 'unknown')
    user_id  = getattr(current_user, 'id', None)

    logout_user()

    if user_id:
        current_app.logger.info(
            f"[AUTH] User logged out: user_id={user_id} username='{username}'"
        )

    return jsonify({
        "status":  "success",
        "message": "You have been logged out successfully.",
    }), 200


# ════════════════════════════════════════════════════════════
# POST /auth/refresh — Exchange refresh token for new access token
# ════════════════════════════════════════════════════════════

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Exchange a valid refresh token for a fresh access token.

    Request JSON:
        { "refresh_token": "<token>" }

    Response 200:
        { "status": "success", "tokens": { access_token, refresh_token, ... } }
    """
    body = request.get_json(silent=True) or {}
    raw_refresh = body.get("refresh_token", "")

    if not raw_refresh:
        return jsonify({"status": "error", "message": "refresh_token is required."}), 400

    try:
        payload = decode_token(raw_refresh, expected_type="refresh")
    except JWTError as e:
        return jsonify({"status": "error", "message": str(e), "code": 401}), 401

    from app import db
    user_id = int(payload["sub"])
    user = db.session.get(User, user_id)

    if user is None or not user.is_active:
        return jsonify({"status": "error", "message": "User not found.", "code": 401}), 401

    tokens = generate_tokens(user)
    return jsonify({"status": "success", "tokens": tokens}), 200


# ════════════════════════════════════════════════════════════
# GET /auth/verify — Check if a token is still valid
# ════════════════════════════════════════════════════════════

@auth_bp.route("/verify", methods=["GET"])
def verify_token():
    """
    Verify an access token sent via Authorization: Bearer header.
    Called by the frontend on page load to check if the stored token is still valid.

    Response 200: { "status": "success", "user": {...} }
    Response 401: { "status": "error", "message": "..." }
    """
    from app.auth.jwt import get_user_from_access_token, _extract_bearer_token
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "message": "No token provided."}), 401

    try:
        user = get_user_from_access_token(token)
    except JWTError as e:
        return jsonify({"status": "error", "message": str(e)}), 401

    return jsonify({
        "status": "success",
        "user":   user.to_dict(include_timestamps=True),
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /auth/me
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """
    Return the currently authenticated user's information.

    Response 200:
        { "status": "success", "user": {...} }
    """
    return jsonify({
        "status": "success",
        "user": current_user.to_dict(include_timestamps=True),
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /auth/profile
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    """
    Return current user info including their ECC public key.
    The private key is NEVER returned.

    Response 200:
        {
            "status": "success",
            "user": { ... },
            "ecc_key": { "public_key": "...", "curve": "P-256", ... }
        }
    """
    ecc_key = current_user.ecc_key
    ecc_data = ecc_key.to_dict(include_public_key=True) if ecc_key else None

    return jsonify({
        "status": "success",
        "user": current_user.to_dict(include_timestamps=True),
        "ecc_key": ecc_data,
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /users/list and /auth/users
# ══════════════════════════════════════════════════════════════

@auth_bp.route("/users/list", methods=["GET"])
@auth_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    """
    Return all active users except the currently logged-in user.
    Used to populate the recipient dropdown on the Send File page.
    """
    search = request.args.get("search", "").strip()

    query = User.query.filter(
        User.id != current_user.id,
        User.is_active == True,
    )

    if search:
        query = query.filter(User.username.ilike(f"{search}%"))

    users = query.order_by(User.username.asc()).all()

    return jsonify({
        "status": "success",
        "users": [{"id": u.id, "user_id": u.id, "username": u.username} for u in users],
        "total": len(users),
    }), 200
