"""
app/main/routes.py — Main Blueprint
=====================================
Serves the root/dashboard routes.

Endpoints:
  GET  /        → API health check / landing
  GET  /dashboard → Current user dashboard data (stats + recent transfers)
"""

from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from app.models.transfer import Transfer, TransferStatus

main_bp = Blueprint("main", __name__)


def wants_html():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return False
    if "application/json" in request.headers.get("Accept", ""):
        return False
    return request.accept_mimetypes.accept_html and not request.is_json


@main_bp.route("/", methods=["GET"])
def index():
    """
    Root endpoint — Landing page in browser, API info in JSON.
    """
    if wants_html():
        return render_template("index.html")

    return jsonify({
        "status": "ok",
        "app": "File Transfer System Using ECC",
        "version": "1.0",
        "description": (
            "Secure file transfer using AES-256-GCM encryption "
            "and ECC (ECIES/ECDH) key management."
        ),
        "endpoints": {
            "register": "POST /auth/register",
            "login":    "POST /auth/login",
            "logout":   "POST /auth/logout",
            "send":     "POST /transfer/send",
            "inbox":    "GET  /transfer/inbox",
            "download": "POST /transfer/download/<id>",
            "history":  "GET  /transfer/history",
        },
    }), 200


@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Return dashboard page in browser, or JSON data for API clients.
    """
    if wants_html():
        return render_template("dashboard/index.html")

    # Transfer stats
    stats = {
        "total_sent": Transfer.query.filter_by(sender_id=current_user.id).count(),
        "total_received": Transfer.query.filter_by(receiver_id=current_user.id).count(),
        "pending_received": Transfer.query.filter_by(
            receiver_id=current_user.id, status=TransferStatus.PENDING
        ).count(),
        "downloaded_received": Transfer.query.filter_by(
            receiver_id=current_user.id, status=TransferStatus.DOWNLOADED
        ).count(),
    }

    # Recent transfers
    recent_received = (
        Transfer.query
        .filter_by(receiver_id=current_user.id)
        .order_by(Transfer.sent_at.desc())
        .limit(5)
        .all()
    )
    recent_sent = (
        Transfer.query
        .filter_by(sender_id=current_user.id)
        .order_by(Transfer.sent_at.desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "status": "success",
        "user": current_user.to_dict(include_timestamps=True),
        "stats": stats,
        "recent_received": [t.to_dict() for t in recent_received],
        "recent_sent": [t.to_dict() for t in recent_sent],
    }), 200


@main_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    """Render the user's cryptographic profile and public key inspector."""
    return render_template("profile/index.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """
    Simple health check endpoint for monitoring.

    Response 200: { "status": "healthy" }
    """
    from app import db
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    return jsonify({
        "status": "healthy",
        "database": db_status,
    }), 200
