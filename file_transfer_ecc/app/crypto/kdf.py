"""
app/crypto/kdf.py — Key Derivation Functions
=============================================
Provides two KDF utilities:

1. derive_key_from_password()
   - PBKDF2-HMAC-SHA256 with random salt
   - Used to derive an AES wrapping key from a user's password
   - Purpose: Protect the user's ECC private key at rest

2. derive_key_from_shared_secret()
   - HKDF-SHA256
   - Used to derive an AES wrapping key from an ECDH shared secret
   - Purpose: ECIES session-key encapsulation per transfer
"""

import os
import hashlib
import hmac

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# ── Constants ─────────────────────────────────────────────────
PBKDF2_ITERATIONS = 260_000   # OWASP recommended minimum (2023)
PBKDF2_KEY_LENGTH = 32        # 256-bit AES key
PBKDF2_SALT_LENGTH = 32       # 256-bit random salt
HKDF_KEY_LENGTH = 32          # 256-bit AES key
HKDF_INFO = b"file-transfer-ecc-session-key-wrap"


# ══════════════════════════════════════════════════════════════
# 1. Password-based KDF  (for private key protection at rest)
# ══════════════════════════════════════════════════════════════

def generate_kdf_salt() -> bytes:
    """
    Generate a cryptographically random salt for PBKDF2.

    Returns:
        32-byte random salt.
    """
    return os.urandom(PBKDF2_SALT_LENGTH)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit AES wrapping key from a user password using PBKDF2-HMAC-SHA256.

    This key is used to encrypt/decrypt the user's ECC private key stored in the DB.

    Args:
        password: The user's plaintext password.
        salt:     A random 32-byte salt (stored alongside the encrypted private key).

    Returns:
        32-byte AES key.

    Example:
        salt = generate_kdf_salt()
        key  = derive_key_from_password("MyP@ssw0rd!", salt)
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=PBKDF2_KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(password.encode("utf-8"))


# ══════════════════════════════════════════════════════════════
# 2. ECDH Shared-Secret KDF  (for per-transfer session-key wrapping)
# ══════════════════════════════════════════════════════════════

def derive_key_from_shared_secret(
    shared_secret: bytes,
    salt: bytes = None,
    info: bytes = HKDF_INFO,
) -> bytes:
    """
    Derive a 256-bit AES wrapping key from an ECDH shared secret using HKDF-SHA256.

    This key wraps (encrypts) the AES session key in ECIES.

    Args:
        shared_secret: Raw bytes from ECDH key agreement.
        salt:          Optional random salt. If None, HKDF uses a zero-filled salt.
        info:          Context / application-specific info string.

    Returns:
        32-byte AES key.

    Example:
        shared = private_key.exchange(ec.ECDH(), peer_public_key)
        wrap_key = derive_key_from_shared_secret(shared)
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=HKDF_KEY_LENGTH,
        salt=salt,
        info=info,
        backend=default_backend(),
    )
    return hkdf.derive(shared_secret)
