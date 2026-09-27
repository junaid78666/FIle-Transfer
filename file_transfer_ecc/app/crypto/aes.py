"""
app/crypto/aes.py — AES-256-GCM Symmetric Encryption
======================================================
Provides AES-256-GCM encrypt/decrypt for file data and key wrapping.

AES-256-GCM provides:
  - Confidentiality  (256-bit key)
  - Integrity        (GCM authentication tag — 16 bytes)
  - Authenticity     (tag verification on decryption)

Output format for encrypt_bytes():
  Returns (ciphertext_only, nonce, auth_tag) as separate values.
  The GCM auth tag is split from the ciphertext for explicit storage.

Usage:
  # Encrypt
  session_key = generate_aes_key()
  ciphertext, nonce, auth_tag = encrypt_bytes(plaintext, session_key)

  # Decrypt
  plaintext = decrypt_bytes(ciphertext, session_key, nonce, auth_tag)
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

# ── Constants ─────────────────────────────────────────────────
AES_KEY_SIZE = 32          # 256 bits
AES_GCM_NONCE_SIZE = 12    # 96 bits  (NIST recommended for GCM)
AES_GCM_TAG_SIZE = 16      # 128 bits


class AESDecryptionError(Exception):
    """Raised when AES-GCM decryption fails (wrong key or tampered data)."""
    pass


def generate_aes_key() -> bytes:
    """
    Generate a cryptographically random 256-bit AES session key.

    Returns:
        32 random bytes.
    """
    return os.urandom(AES_KEY_SIZE)


def generate_nonce() -> bytes:
    """
    Generate a cryptographically random 96-bit GCM nonce.

    Each nonce MUST be unique per (key, plaintext) pair.
    A new nonce is generated for every encryption operation.

    Returns:
        12 random bytes.
    """
    return os.urandom(AES_GCM_NONCE_SIZE)


def encrypt_bytes(plaintext: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt plaintext bytes using AES-256-GCM.

    The GCM tag is appended by `cryptography` to the ciphertext.
    We split it out for explicit, separate storage.

    Args:
        plaintext: Raw bytes to encrypt.
        key:       32-byte AES key.

    Returns:
        Tuple of (ciphertext_without_tag, nonce, auth_tag).
        - ciphertext_without_tag: len(plaintext) bytes
        - nonce:    12 bytes
        - auth_tag: 16 bytes

    Raises:
        ValueError: If key length is not 32 bytes.

    Example:
        key = generate_aes_key()
        ct, nonce, tag = encrypt_bytes(b"secret data", key)
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes, got {len(key)}")

    nonce = generate_nonce()
    aesgcm = AESGCM(key)

    # cryptography appends the 16-byte tag to the end of ciphertext
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)

    # Split ciphertext and tag
    auth_tag = ciphertext_with_tag[-AES_GCM_TAG_SIZE:]
    ciphertext = ciphertext_with_tag[:-AES_GCM_TAG_SIZE]

    return ciphertext, nonce, auth_tag


def decrypt_bytes(
    ciphertext: bytes,
    key: bytes,
    nonce: bytes,
    auth_tag: bytes,
) -> bytes:
    """
    Decrypt AES-256-GCM ciphertext.

    Recombines ciphertext + auth_tag, then decrypts and verifies integrity.
    If the key is wrong or ciphertext was tampered with, raises AESDecryptionError.

    Args:
        ciphertext: Encrypted bytes (without auth tag).
        key:        32-byte AES key.
        nonce:      12-byte GCM nonce used during encryption.
        auth_tag:   16-byte GCM authentication tag.

    Returns:
        Original plaintext bytes.

    Raises:
        AESDecryptionError: If decryption or authentication fails.

    Example:
        plaintext = decrypt_bytes(ct, key, nonce, tag)
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"AES key must be {AES_KEY_SIZE} bytes, got {len(key)}")
    if len(nonce) != AES_GCM_NONCE_SIZE:
        raise ValueError(f"Nonce must be {AES_GCM_NONCE_SIZE} bytes, got {len(nonce)}")
    if len(auth_tag) != AES_GCM_TAG_SIZE:
        raise ValueError(f"Auth tag must be {AES_GCM_TAG_SIZE} bytes, got {len(auth_tag)}")

    try:
        aesgcm = AESGCM(key)
        # Reconstruct ciphertext+tag as expected by cryptography
        ciphertext_with_tag = ciphertext + auth_tag
        return aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except InvalidTag:
        raise AESDecryptionError(
            "AES-GCM decryption failed: invalid authentication tag. "
            "The key is incorrect or the ciphertext has been tampered with."
        )
    except Exception as exc:
        raise AESDecryptionError(f"Decryption error: {exc}") from exc


# ── Hex-encoding helpers ──────────────────────────────────────

def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to lowercase hex string."""
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes."""
    return bytes.fromhex(hex_str)
