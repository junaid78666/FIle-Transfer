"""
app/main/routes.py — Main Blueprint
=====================================
Serves the root/dashboard routes.

Endpoints:
  GET  /        → API health check / landing
  GET  /dashboard → Current user dashboard data (stats + recent transfers)
"""

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.transfer import Transfer, TransferStatus

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    """
    Root endpoint — health check / API info.

    Response 200:
        { "status": "ok", "app": "File Transfer ECC", "version": "1.0" }
    """
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
    Return dashboard data for the current user:
      - User info
      - Transfer statistics
      - 5 most recent received transfers
      - 5 most recent sent transfers

    Response 200:
        {
            "status": "success",
            "user": {...},
            "stats": {...},
            "recent_received": [...],
            "recent_sent": [...]
        }
    """
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
