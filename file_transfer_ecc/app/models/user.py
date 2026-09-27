"""
app/models/user.py — User Model
=================================
Represents a registered user of the system.

Relationships:
  - One-to-One  →  ECCKey   (each user has exactly one ECC key pair)
  - One-to-Many →  Transfer (as sender: files sent by this user)
  - One-to-Many →  Transfer (as receiver: files received by this user)
"""

from datetime import datetime, timezone
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    Stores account credentials and metadata for each registered user.

    Flask-Login integration via UserMixin provides:
        is_authenticated, is_active, is_anonymous, get_id()
    """

    __tablename__ = "users"

    # ── Primary Key ───────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Identity Fields ───────────────────────────────────────
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique display name for the user",
    )
    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True,
        comment="Login email address",
    )

    # ── Security Fields ───────────────────────────────────────
    password_hash = db.Column(
        db.String(255),
        nullable=False,
        comment="bcrypt hash of user password",
    )

    # ── Account Status ────────────────────────────────────────
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment="False = account disabled",
    )

    # ── Timestamps ────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Account creation timestamp (UTC)",
    )
    last_login_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
        comment="Most recent successful login timestamp (UTC)",
    )

    # ── Relationships ─────────────────────────────────────────
    # One-to-one: user ↔ ECC key pair
    ecc_key = db.relationship(
        "ECCKey",
        back_populates="user",
        uselist=False,          # One-to-one
        cascade="all, delete-orphan",
        lazy="select",
    )

    # One-to-many: user → transfers sent
    sent_transfers = db.relationship(
        "Transfer",
        foreign_keys="Transfer.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
        lazy="dynamic",         # Dynamic for paginated queries
    )

    # One-to-many: user → transfers received
    received_transfers = db.relationship(
        "Transfer",
        foreign_keys="Transfer.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # ── Representation ────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' email='{self.email}'>"

    # ── Helper Methods ────────────────────────────────────────
    def update_last_login(self) -> None:
        """Update last_login_at to current UTC time and flush/commit."""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.add(self)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def to_dict(self, include_timestamps: bool = False) -> dict:
        """
        Serialize user to a safe dictionary (no sensitive fields).

        Args:
            include_timestamps: Include created_at and last_login_at.

        Returns:
            Dictionary representation of the user.
        """
        data = {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
        }
        if include_timestamps:
            data["created_at"] = (
                self.created_at.isoformat() if self.created_at else None
            )
            data["last_login_at"] = (
                self.last_login_at.isoformat() if self.last_login_at else None
            )
        return data
