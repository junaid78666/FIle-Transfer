"""
app/transfer/routes.py — Transfer Blueprint Routes
====================================================
Handles all file transfer operations.

Endpoints:
  POST /transfer/send                      → Upload and encrypt a file for a recipient
  GET  /transfer/inbox                     → List all transfers received by current user
  GET  /transfer/sent                      → List all transfers sent by current user
  GET  /transfer/history                   → Combined sent + received history
  POST /transfer/download/<transfer_id>    → Decrypt and stream original file
  GET  /transfer/info/<transfer_id>        → Transfer metadata (no file content)
  DELETE /transfer/delete/<transfer_id>    → Sender deletes a pending transfer

Security:
  - All endpoints require authentication (@login_required).
  - Download endpoint validates the current user is the intended receiver.
  - Transfer info validates the current user is sender OR receiver.
"""

import io
import os

from flask import (
    Blueprint, request, jsonify, current_app,
    send_file, abort,
)
from flask_login import login_required, current_user

from app import db
from app.models.transfer import Transfer, TransferStatus
from app.models.user import User
from app.transfer.forms import SendFileForm
from app.transfer.utils import (
    validate_file, encrypt_and_store, decrypt_and_verify,
    delete_stored_file, format_file_size,
    FileValidationError,
)
from app.crypto.ecc import ECCError
from app.crypto.aes import AESDecryptionError
from app.crypto.hashing import IntegrityError

# ── Blueprint definition ──────────────────────────────────────
transfer_bp = Blueprint("transfer", __name__)


# ══════════════════════════════════════════════════════════════
# POST /transfer/send
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/send", methods=["POST"])
@login_required
def send_file_transfer():
    """
    Upload a file, encrypt it, and create a secure transfer for a recipient.

    Request: multipart/form-data
        file        → File upload field
        receiver_id → ID of recipient user

    Response 201:
        { "status": "success", "message": "...", "transfer": {...} }

    Response 400: Validation error
    Response 403: Receiver not found or self-transfer
    Response 500: Encryption or storage error
    """
    form = SendFileForm()

    if not form.validate_on_submit():
        errors = []
        for field_errors in form.errors.values():
            errors.extend(field_errors)
        return jsonify({
            "status": "error",
            "message": "Validation failed.",
            "errors": errors,
        }), 400

    # ── Validate the uploaded file ────────────────────────────
    file = form.file.data
    try:
        original_filename, mime_type, file_size = validate_file(file)
    except FileValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    # ── Verify recipient exists and has an ECC key ────────────
    receiver_id = form.receiver_id.data
    receiver = User.query.filter_by(id=receiver_id, is_active=True).first()
    if not receiver:
        return jsonify({
            "status": "error",
            "message": "Recipient not found.",
        }), 404

    if not receiver.ecc_key:
        return jsonify({
            "status": "error",
            "message": "Recipient does not have an ECC key pair. Cannot encrypt for them.",
        }), 422

    # ── Read file content ─────────────────────────────────────
    file.seek(0)
    plaintext = file.read()

    # ── Encrypt and store ─────────────────────────────────────
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    try:
        crypto_data = encrypt_and_store(
            plaintext=plaintext,
            receiver_public_key_pem=receiver.ecc_key.public_key,
            upload_folder=upload_folder,
        )
    except ECCError as e:
        current_app.logger.error(f"[TRANSFER/SEND] ECC error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Encryption failed due to a cryptographic error. Please try again.",
        }), 500
    except Exception as e:
        current_app.logger.error(f"[TRANSFER/SEND] Unexpected error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred during encryption.",
        }), 500

    # ── Create Transfer DB record ─────────────────────────────
    transfer = Transfer(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        original_filename=original_filename,
        file_size_bytes=file_size,
        file_mime_type=mime_type,
        stored_filename=crypto_data["stored_filename"],
        plaintext_sha256=crypto_data["plaintext_sha256"],
        encrypted_session_key=crypto_data["encrypted_session_key"],
        ephemeral_public_key=crypto_data["ephemeral_public_key"],
        wrap_nonce=crypto_data["wrap_nonce"],
        wrap_auth_tag=crypto_data["wrap_auth_tag"],
        aes_nonce=crypto_data["aes_nonce"],
        aes_auth_tag=crypto_data["aes_auth_tag"],
        status=TransferStatus.PENDING,
    )
    db.session.add(transfer)
    db.session.commit()

    current_app.logger.info(
        f"[TRANSFER/SEND] Transfer created: id={transfer.id} "
        f"sender={current_user.username} → receiver={receiver.username} "
        f"file='{original_filename}' size={format_file_size(file_size)}"
    )

    return jsonify({
        "status": "success",
        "message": (
            f"File '{original_filename}' ({format_file_size(file_size)}) "
            f"encrypted and transferred securely to '{receiver.username}'."
        ),
        "transfer": transfer.to_dict(),
    }), 201


# ══════════════════════════════════════════════════════════════
# POST /transfer/download/<transfer_id>
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/download/<string:transfer_id>", methods=["POST"])
@login_required
def download_file(transfer_id: str):
    """
    Decrypt and stream the original file to the authenticated receiver.

    Request: JSON body
        { "password": "<user's login password>" }
    The password is needed to recover the receiver's ECC private key.

    Response 200: Binary file stream (attachment)
    Response 400: Missing password
    Response 403: Not the intended recipient
    Response 404: Transfer not found
    Response 422: Decryption or integrity failure
    """
    # ── Fetch transfer ────────────────────────────────────────
    transfer = Transfer.query.get(transfer_id)
    if not transfer:
        return jsonify({
            "status": "error",
            "message": "Transfer not found.",
        }), 404

    # ── Authorization: only the intended receiver can download ─
    if transfer.receiver_id != current_user.id:
        current_app.logger.warning(
            f"[TRANSFER/DOWNLOAD] Unauthorized access attempt: "
            f"user_id={current_user.id} tried to access transfer_id={transfer_id} "
            f"belonging to receiver_id={transfer.receiver_id}"
        )
        return jsonify({
            "status": "error",
            "message": "Access denied. You are not the intended recipient of this transfer.",
        }), 403

    # ── Get password from request ─────────────────────────────
    data = request.get_json(silent=True) or {}
    password = data.get("password", "").strip()
    if not password:
        return jsonify({
            "status": "error",
            "message": "Your password is required to decrypt and recover the file.",
        }), 400

    # ── Decrypt and verify ────────────────────────────────────
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    receiver_ecc_key = current_user.ecc_key

    if not receiver_ecc_key:
        return jsonify({
            "status": "error",
            "message": "No ECC key found for your account. Cannot decrypt.",
        }), 422

    try:
        plaintext = decrypt_and_verify(
            transfer=transfer,
            receiver_ecc_key_record=receiver_ecc_key,
            password=password,
            upload_folder=upload_folder,
        )
    except ECCError as e:
        current_app.logger.warning(
            f"[TRANSFER/DOWNLOAD] ECC error (possibly wrong password): "
            f"transfer_id={transfer_id}, user_id={current_user.id} — {e}"
        )
        return jsonify({
            "status": "error",
            "message": "Decryption failed. Your password may be incorrect.",
        }), 422

    except AESDecryptionError as e:
        current_app.logger.error(
            f"[TRANSFER/DOWNLOAD] AES-GCM failure (possible tampering): "
            f"transfer_id={transfer_id} — {e}"
        )
        transfer.mark_failed()
        return jsonify({
            "status": "error",
            "message": "File decryption failed. The file may have been tampered with.",
        }), 422

    except IntegrityError as e:
        current_app.logger.error(
            f"[TRANSFER/DOWNLOAD] SHA-256 mismatch (tampering detected): "
            f"transfer_id={transfer_id} — {e}"
        )
        transfer.mark_failed()
        return jsonify({
            "status": "error",
            "message": "File integrity verification failed. The file has been tampered with.",
        }), 422

    except FileNotFoundError as e:
        current_app.logger.error(
            f"[TRANSFER/DOWNLOAD] Encrypted file missing: transfer_id={transfer_id}"
        )
        return jsonify({
            "status": "error",
            "message": "The encrypted file could not be found on the server.",
        }), 404

    except Exception as e:
        current_app.logger.error(
            f"[TRANSFER/DOWNLOAD] Unexpected error: {e}", exc_info=True
        )
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred during decryption.",
        }), 500

    # ── Mark as downloaded ────────────────────────────────────
    transfer.mark_downloaded()

    # ── Optionally delete server-side file after download ─────
    # Uncomment to auto-delete after first download:
    # delete_stored_file(transfer.stored_filename, upload_folder)

    current_app.logger.info(
        f"[TRANSFER/DOWNLOAD] Successful: transfer_id={transfer_id} "
        f"receiver={current_user.username} file='{transfer.original_filename}'"
    )

    # ── Stream plaintext as file download ─────────────────────
    return send_file(
        io.BytesIO(plaintext),
        as_attachment=True,
        download_name=transfer.original_filename,
        mimetype=transfer.file_mime_type or "application/octet-stream",
    )


# ══════════════════════════════════════════════════════════════
# GET /transfer/inbox
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/inbox", methods=["GET"])
@login_required
def inbox():
    """
    Return all transfers received by the current user.

    Query Parameters:
        page     (int, default=1):    Page number.
        per_page (int, default=10):   Items per page.
        status   (str, optional):     Filter by status (PENDING/DOWNLOADED/FAILED).

    Response 200:
        {
            "status": "success",
            "transfers": [...],
            "total": 5,
            "page": 1,
            "pages": 1,
            "unread_count": 3
        }
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    status_filter = request.args.get("status", "").upper()

    query = Transfer.query.filter_by(receiver_id=current_user.id)

    if status_filter and status_filter in TransferStatus.ALL:
        query = query.filter_by(status=status_filter)

    query = query.order_by(Transfer.sent_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Count unread (PENDING) transfers
    unread_count = Transfer.query.filter_by(
        receiver_id=current_user.id,
        status=TransferStatus.PENDING,
    ).count()

    return jsonify({
        "status": "success",
        "transfers": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "unread_count": unread_count,
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /transfer/sent
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/sent", methods=["GET"])
@login_required
def sent():
    """
    Return all transfers sent by the current user.

    Query Parameters:
        page, per_page, status (same as inbox)

    Response 200:
        { "status": "success", "transfers": [...], "total": N, "page": N, "pages": N }
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    status_filter = request.args.get("status", "").upper()

    query = Transfer.query.filter_by(sender_id=current_user.id)

    if status_filter and status_filter in TransferStatus.ALL:
        query = query.filter_by(status=status_filter)

    query = query.order_by(Transfer.sent_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "status": "success",
        "transfers": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /transfer/history
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/history", methods=["GET"])
@login_required
def history():
    """
    Return combined sent and received transfer history for the current user.

    Query Parameters:
        page       (int):    Page number (default=1).
        per_page   (int):    Items per page (default=10, max=50).
        direction  (str):    "sent" | "received" | "all" (default="all").
        status     (str):    "PENDING" | "DOWNLOADED" | "FAILED" | "" (all).

    Response 200:
        {
            "status": "success",
            "transfers": [...],
            "total": N,
            "page": N,
            "pages": N
        }
    """
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    direction = request.args.get("direction", "all").lower()
    status_filter = request.args.get("status", "").upper()

    from sqlalchemy import or_

    if direction == "sent":
        query = Transfer.query.filter_by(sender_id=current_user.id)
    elif direction == "received":
        query = Transfer.query.filter_by(receiver_id=current_user.id)
    else:  # "all"
        query = Transfer.query.filter(
            or_(
                Transfer.sender_id == current_user.id,
                Transfer.receiver_id == current_user.id,
            )
        )

    if status_filter and status_filter in TransferStatus.ALL:
        query = query.filter_by(status=status_filter)

    query = query.order_by(Transfer.sent_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "status": "success",
        "transfers": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /transfer/info/<transfer_id>
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/info/<string:transfer_id>", methods=["GET"])
@login_required
def transfer_info(transfer_id: str):
    """
    Return metadata for a specific transfer.
    Only the sender or receiver can access this endpoint.

    Response 200:
        { "status": "success", "transfer": {...} }

    Response 403: Not sender or receiver
    Response 404: Not found
    """
    transfer = Transfer.query.get(transfer_id)
    if not transfer:
        return jsonify({"status": "error", "message": "Transfer not found."}), 404

    if transfer.sender_id != current_user.id and transfer.receiver_id != current_user.id:
        return jsonify({
            "status": "error",
            "message": "Access denied. You are not a participant in this transfer.",
        }), 403

    return jsonify({
        "status": "success",
        "transfer": transfer.to_dict(),
    }), 200


# ══════════════════════════════════════════════════════════════
# DELETE /transfer/delete/<transfer_id>
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/delete/<string:transfer_id>", methods=["DELETE"])
@login_required
def delete_transfer(transfer_id: str):
    """
    Allow the SENDER to delete a PENDING transfer (before it is downloaded).
    Removes the DB record and the stored encrypted file.

    Response 200: { "status": "success", "message": "..." }
    Response 403: Not the sender, or transfer already downloaded
    Response 404: Transfer not found
    """
    transfer = Transfer.query.get(transfer_id)
    if not transfer:
        return jsonify({"status": "error", "message": "Transfer not found."}), 404

    # Only sender can delete
    if transfer.sender_id != current_user.id:
        return jsonify({
            "status": "error",
            "message": "Access denied. Only the sender can delete a transfer.",
        }), 403

    # Cannot delete already-downloaded transfers
    if transfer.status == TransferStatus.DOWNLOADED:
        return jsonify({
            "status": "error",
            "message": "Cannot delete a transfer that has already been downloaded.",
        }), 422

    # Delete encrypted file from disk
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    delete_stored_file(transfer.stored_filename, upload_folder)

    # Delete DB record
    filename = transfer.original_filename
    db.session.delete(transfer)
    db.session.commit()

    current_app.logger.info(
        f"[TRANSFER/DELETE] Transfer deleted: id={transfer_id} "
        f"by sender={current_user.username}"
    )

    return jsonify({
        "status": "success",
        "message": f"Transfer for '{filename}' has been deleted.",
    }), 200


# ══════════════════════════════════════════════════════════════
# GET /transfer/stats
# ══════════════════════════════════════════════════════════════

@transfer_bp.route("/stats", methods=["GET"])
@login_required
def stats():
    """
    Return transfer statistics for the current user.

    Response 200:
        {
            "status": "success",
            "stats": {
                "total_sent": N,
                "total_received": N,
                "pending_received": N,
                "downloaded_received": N,
                "failed": N
            }
        }
    """
    total_sent = Transfer.query.filter_by(sender_id=current_user.id).count()
    total_received = Transfer.query.filter_by(receiver_id=current_user.id).count()
    pending_received = Transfer.query.filter_by(
        receiver_id=current_user.id, status=TransferStatus.PENDING
    ).count()
    downloaded_received = Transfer.query.filter_by(
        receiver_id=current_user.id, status=TransferStatus.DOWNLOADED
    ).count()
    failed = Transfer.query.filter_by(
        receiver_id=current_user.id, status=TransferStatus.FAILED
    ).count()

    return jsonify({
        "status": "success",
        "stats": {
            "total_sent": total_sent,
            "total_received": total_received,
            "pending_received": pending_received,
            "downloaded_received": downloaded_received,
            "failed": failed,
        },
    }), 200
