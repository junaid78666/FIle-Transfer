"""
app/models/transfer.py — Transfer Model
=========================================
Represents a single secure file transfer from one user to another.

Cryptographic fields stored per transfer:
  - plaintext_sha256      → SHA-256 hash of plaintext for integrity check
  - encrypted_session_key → AES session key encrypted via ECIES
  - ephemeral_public_key  → Sender's ephemeral ECC public key (for ECDH)
  - wrap_nonce            → GCM nonce used when wrapping the session key
  - wrap_auth_tag         → GCM auth tag for session key encryption
  - aes_nonce             → GCM nonce used when encrypting the file
  - aes_auth_tag          → GCM auth tag for file encryption

These fields are all that is needed to decrypt the file:
  Receiver uses: ephemeral_public_key + their private key → shared secret
               → HKDF → wrapping key → decrypt session key
               → AES-GCM decrypt file → verify SHA-256
"""

import uuid
from datetime import datetime, timezone
from app import db


class TransferStatus:
    """Enum-like class for transfer status values."""
    PENDING = "PENDING"
    DOWNLOADED = "DOWNLOADED"
    FAILED = "FAILED"

    ALL = {PENDING, DOWNLOADED, FAILED}


class Transfer(db.Model):
    """
    Represents one encrypted file transfer between two users.
    Stores all cryptographic material needed for decryption by the receiver.
    """

    __tablename__ = "transfers"

    # ── Primary Key ───────────────────────────────────────────
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="UUID transfer identifier",
    )

    # ── Participants ──────────────────────────────────────────
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID of the sender",
    )
    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID of the intended recipient",
    )

    # ── File Metadata ─────────────────────────────────────────
    original_filename = db.Column(
        db.String(255),
        nullable=False,
        comment="Original filename before encryption",
    )
    file_size_bytes = db.Column(
        db.BigInteger,
        nullable=False,
        comment="File size in bytes (plaintext)",
    )
    file_mime_type = db.Column(
        db.String(100),
        nullable=True,
        comment="MIME type of the original file",
    )
    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        comment="UUID-based filename on disk (e.g., abc123.enc)",
    )

    # ── Integrity ─────────────────────────────────────────────
    plaintext_sha256 = db.Column(
        db.String(64),
        nullable=False,
        comment="SHA-256 hex digest of plaintext file for integrity check",
    )

    # ── ECIES Key Encapsulation ───────────────────────────────
    ephemeral_public_key = db.Column(
        db.Text,
        nullable=False,
        comment="PEM-encoded ephemeral ECC public key used in ECDH",
    )
    encrypted_session_key = db.Column(
        db.Text,
        nullable=False,
        comment="AES session key wrapped via ECIES (hex-encoded)",
    )
    wrap_nonce = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM nonce used when encrypting the session key (hex, 12 bytes)",
    )
    wrap_auth_tag = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM auth tag for session key encryption (hex, 16 bytes)",
    )

    # ── File Encryption (AES-256-GCM) ────────────────────────
    aes_nonce = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM nonce used when encrypting the file (hex, 12 bytes)",
    )
    aes_auth_tag = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM auth tag for file encryption (hex, 16 bytes)",
    )

    # ── Status ────────────────────────────────────────────────
    status = db.Column(
        db.String(20),
        nullable=False,
        default=TransferStatus.PENDING,
        index=True,
        comment="PENDING | DOWNLOADED | FAILED",
    )

    # ── Timestamps ────────────────────────────────────────────
    sent_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="Transfer creation timestamp (UTC)",
    )
    downloaded_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        comment="When receiver successfully downloaded the file (UTC)",
    )

    # ── Relationships ─────────────────────────────────────────
    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_transfers",
    )
    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_transfers",
    )

    # ── Representation ────────────────────────────────────────
    def __repr__(self) -> str:
        return (
            f"<Transfer id={self.id!r} "
            f"sender={self.sender_id} → receiver={self.receiver_id} "
            f"file='{self.original_filename}' status='{self.status}'>"
        )

    # ── Business Logic ────────────────────────────────────────
    def mark_downloaded(self) -> None:
        """Mark this transfer as DOWNLOADED and record timestamp."""
        self.status = TransferStatus.DOWNLOADED
        self.downloaded_at = datetime.now(timezone.utc)
        db.session.commit()

    def mark_failed(self) -> None:
        """Mark this transfer as FAILED."""
        self.status = TransferStatus.FAILED
        db.session.commit()

    @property
    def is_pending(self) -> bool:
        return self.status == TransferStatus.PENDING

    @property
    def is_downloaded(self) -> bool:
        return self.status == TransferStatus.DOWNLOADED

    def to_dict(self, include_crypto: bool = False) -> dict:
        """
        Serialize transfer to a safe dictionary.

        Args:
            include_crypto: Include cryptographic fields (for decryption use).

        Returns:
            Dictionary representation.
        """
        data = {
            "transfer_id": self.id,
            "sender_id": self.sender_id,
            "sender_username": self.sender.username if self.sender else None,
            "receiver_id": self.receiver_id,
            "receiver_username": self.receiver.username if self.receiver else None,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "file_mime_type": self.file_mime_type,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "downloaded_at": (
                self.downloaded_at.isoformat() if self.downloaded_at else None
            ),
        }
        if include_crypto:
            data.update({
                "plaintext_sha256": self.plaintext_sha256,
                "ephemeral_public_key": self.ephemeral_public_key,
                "encrypted_session_key": self.encrypted_session_key,
                "wrap_nonce": self.wrap_nonce,
                "wrap_auth_tag": self.wrap_auth_tag,
                "aes_nonce": self.aes_nonce,
                "aes_auth_tag": self.aes_auth_tag,
                "stored_filename": self.stored_filename,
            })
        return data
