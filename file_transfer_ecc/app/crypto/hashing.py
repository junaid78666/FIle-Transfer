"""
app/crypto/hashing.py — SHA-256 File Integrity
================================================
Provides SHA-256 hashing utilities for plaintext file integrity verification.

Usage flow:
  SENDER:   hash = compute_sha256(plaintext_bytes)  → store in DB
  RECEIVER: computed = compute_sha256(decrypted_bytes)
            verify_sha256(stored_hash, computed)     → pass/fail
"""

import hashlib
import hmac
from typing import Union


def compute_sha256(data: bytes) -> str:
    """
    Compute the SHA-256 hash of a byte string.

    Args:
        data: Raw bytes to hash (plaintext file content).

    Returns:
        Lowercase hex-encoded SHA-256 digest (64 characters).

    Example:
        digest = compute_sha256(b"Hello, World!")
        # → "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986d"
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Expected bytes, got {type(data).__name__}")
    return hashlib.sha256(data).hexdigest()


def compute_sha256_stream(file_path: str, chunk_size: int = 65536) -> str:
    """
    Compute the SHA-256 hash of a file by streaming it in chunks.
    Memory-efficient for large files.

    Args:
        file_path:  Absolute path to the file.
        chunk_size: Number of bytes to read at a time (default: 64 KB).

    Returns:
        Lowercase hex-encoded SHA-256 digest.

    Raises:
        FileNotFoundError: If file_path does not exist.
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_sha256(expected: str, actual: str) -> bool:
    """
    Safely compare two SHA-256 hex digests using constant-time comparison.
    Prevents timing-based side-channel attacks.

    Args:
        expected: SHA-256 hex digest stored at upload time.
        actual:   SHA-256 hex digest computed after decryption.

    Returns:
        True if hashes match; False otherwise.

    Example:
        ok = verify_sha256(stored_hash, compute_sha256(decrypted_bytes))
        if not ok:
            raise IntegrityError("File has been tampered with!")
    """
    if not expected or not actual:
        return False
    # hmac.compare_digest is constant-time → prevents timing attacks
    return hmac.compare_digest(expected.lower(), actual.lower())


class IntegrityError(Exception):
    """Raised when SHA-256 verification fails after decryption."""
    pass
