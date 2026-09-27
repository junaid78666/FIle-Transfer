"""
app/models/ecc_key.py — ECC Key Pair Model
============================================
Stores the ECC public/private key pair for each user.

Security design:
  - public_key  → stored in plaintext PEM format (safe to expose)
  - private_key → stored AES-256-GCM encrypted, using a key derived
                  from the user's password via PBKDF2-SHA256.
                  The private key is NEVER exposed in the API or UI.

Each user has exactly one ECCKey record (one-to-one with User).
"""

from datetime import datetime, timezone
from app import db


class ECCKey(db.Model):
    """
    Stores the ECC cryptographic key pair associated with a user.

    Fields:
        public_key      - PEM-encoded ECC public key (shareable)
        private_key_enc - AES-256-GCM encrypted PEM private key (secret)
        kdf_salt        - Random salt used for PBKDF2 key derivation
        iv_nonce        - GCM nonce used when encrypting the private key
        auth_tag        - GCM auth tag for private key encryption
        curve           - ECC curve name (e.g., "P-256")
    """

    __tablename__ = "ecc_keys"

    # ── Primary Key ───────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Foreign Key ───────────────────────────────────────────
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,   # One-to-one enforced at DB level
        nullable=False,
        index=True,
        comment="Owning user ID",
    )

    # ── Public Key ────────────────────────────────────────────
    public_key = db.Column(
        db.Text,
        nullable=False,
        comment="PEM-encoded ECC public key",
    )

    # ── Encrypted Private Key ─────────────────────────────────
    private_key_enc = db.Column(
        db.Text,
        nullable=False,
        comment="AES-256-GCM encrypted PEM private key (hex-encoded)",
    )
    kdf_salt = db.Column(
        db.String(64),
        nullable=False,
        comment="PBKDF2 salt used to derive the private-key wrapping key (hex)",
    )
    priv_nonce = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM nonce used to encrypt the private key (hex, 12 bytes)",
    )
    priv_auth_tag = db.Column(
        db.String(32),
        nullable=False,
        comment="GCM authentication tag for private key encryption (hex, 16 bytes)",
    )

    # ── Curve Metadata ────────────────────────────────────────
    curve = db.Column(
        db.String(20),
        nullable=False,
        default="P-256",
        comment="ECC curve name",
    )

    # ── Timestamps ────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Key generation timestamp (UTC)",
    )

    # ── Relationship ──────────────────────────────────────────
    user = db.relationship(
        "User",
        back_populates="ecc_key",
    )

    # ── Representation ────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<ECCKey id={self.id} user_id={self.user_id} curve='{self.curve}'>"

    @property
    def public_key_pem(self) -> str:
        """Alias for public_key."""
        return self.public_key

    @property
    def fingerprint(self) -> str:
        """SHA-256 fingerprint of the public key."""
        from app.crypto.hashing import compute_sha256
        return compute_sha256(self.public_key.encode("utf-8"))[:32]

    def to_dict(self, include_public_key: bool = True) -> dict:
        """
        Serialize ECC key info (public key only; never private key).

        Args:
            include_public_key: Include the PEM public key string.

        Returns:
            Safe dictionary with key metadata.
        """
        data = {
            "key_id": self.id,
            "user_id": self.user_id,
            "curve": self.curve,
            "fingerprint": self.fingerprint,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_public_key:
            data["public_key"] = self.public_key
        return data
