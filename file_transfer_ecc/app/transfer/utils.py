"""
app/transfer/utils.py — Transfer Helper Functions
===================================================
Provides the core business logic for:

1. validate_file()        — Check file type, size, and sanitize filename
2. encrypt_and_store()    — Full pipeline: SHA-256 → AES encrypt → ECIES wrap → save
3. decrypt_and_stream()   — Full pipeline: ECIES unwrap → AES decrypt → verify SHA-256
4. get_stored_file_path() — Resolve on-disk path for an encrypted file
5. delete_stored_file()   — Remove encrypted file after successful download
6. format_file_size()     — Human-readable file size string
"""

import os
import uuid
import mimetypes
from typing import Optional, Tuple

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.crypto.aes import (
    generate_aes_key, encrypt_bytes, decrypt_bytes,
    bytes_to_hex, hex_to_bytes,
)
from app.crypto.ecc import (
    ecies_encrypt_session_key, ecies_decrypt_session_key,
    recover_private_key, ECCError,
)
from app.crypto.hashing import compute_sha256, verify_sha256, IntegrityError


# ── Constants ─────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt",
    "txt", "csv", "json", "xml",
    "png", "jpg", "jpeg", "gif", "bmp", "webp",
    "zip", "tar", "gz", "7z",
    "mp4", "avi", "mkv", "mov",
    "mp3", "wav",
    "py", "js", "html", "css", "md",
}

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB default


class FileValidationError(Exception):
    """Raised when an uploaded file fails validation."""
    pass


# ══════════════════════════════════════════════════════════════
# 1. File Validation
# ══════════════════════════════════════════════════════════════

def validate_file(file: FileStorage) -> Tuple[str, str, int]:
    """
    Validate an uploaded file's name, extension, and size.

    Args:
        file: Werkzeug FileStorage object from the upload.

    Returns:
        Tuple of (safe_filename, mime_type, file_size_bytes).

    Raises:
        FileValidationError: On validation failure.
    """
    if not file or not file.filename:
        raise FileValidationError("No file was provided.")

    # 1. Sanitize filename (strip path traversal, special chars)
    original_name = secure_filename(file.filename)
    if not original_name:
        raise FileValidationError("Invalid filename.")

    # 2. Check extension
    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", ALLOWED_EXTENSIONS)
    if ext not in allowed:
        raise FileValidationError(
            f"File type '.{ext}' is not allowed. "
            f"Allowed types: {', '.join(sorted(allowed))}."
        )

    # 3. Read file content for size check
    file_content = file.read()
    file.seek(0)   # Reset stream position after reading

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", MAX_FILE_SIZE_BYTES)
    if len(file_content) > max_size:
        size_mb = max_size / (1024 * 1024)
        raise FileValidationError(
            f"File is too large. Maximum allowed size is {size_mb:.0f} MB."
        )

    if len(file_content) == 0:
        raise FileValidationError("File is empty. Please upload a non-empty file.")

    # 4. Detect MIME type
    mime_type = mimetypes.guess_type(original_name)[0] or "application/octet-stream"

    return original_name, mime_type, len(file_content)


# ══════════════════════════════════════════════════════════════
# 2. Encrypt and Store
# ══════════════════════════════════════════════════════════════

def encrypt_and_store(
    plaintext: bytes,
    receiver_public_key_pem: str,
    upload_folder: str,
) -> dict:
    """
    Full encryption pipeline for a file transfer:

    Step 1: Compute SHA-256 hash of plaintext (for integrity check later)
    Step 2: Generate a random AES-256 session key
    Step 3: Encrypt plaintext with AES-256-GCM
    Step 4: Use ECIES to encrypt the AES session key for the receiver
    Step 5: Save the ciphertext to disk as <uuid>.enc
    Step 6: Return all cryptographic metadata for DB storage

    Args:
        plaintext:               Raw plaintext file bytes.
        receiver_public_key_pem: PEM string of receiver's ECC public key.
        upload_folder:           Server directory path for storing encrypted files.

    Returns:
        Dictionary with:
            stored_filename:       "<uuid>.enc"
            plaintext_sha256:      "<hex>"
            encrypted_session_key: "<hex>"
            ephemeral_public_key:  "<PEM>"
            wrap_nonce:            "<hex>"
            wrap_auth_tag:         "<hex>"
            aes_nonce:             "<hex>"
            aes_auth_tag:          "<hex>"

    Raises:
        ECCError:  On ECIES key encapsulation failure.
        IOError:   On file write failure.
    """
    # Step 1: SHA-256 integrity hash of plaintext
    sha256_hash = compute_sha256(plaintext)

    # Step 2: Generate random AES session key
    session_key = generate_aes_key()

    # Step 3: AES-256-GCM encrypt the file
    aes_ciphertext, aes_nonce, aes_auth_tag = encrypt_bytes(plaintext, session_key)

    # Step 4: ECIES — wrap the session key for the receiver
    ecies_result = ecies_encrypt_session_key(session_key, receiver_public_key_pem)

    # Step 5: Save encrypted file to disk
    stored_filename = f"{uuid.uuid4().hex}.enc"
    file_path = os.path.join(upload_folder, stored_filename)

    os.makedirs(upload_folder, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(aes_ciphertext)

    current_app.logger.info(
        f"[TRANSFER] Encrypted file saved: {stored_filename} "
        f"({len(aes_ciphertext)} bytes ciphertext)"
    )

    # Step 6: Return all metadata for DB storage
    return {
        "stored_filename":       stored_filename,
        "plaintext_sha256":      sha256_hash,
        "encrypted_session_key": ecies_result["encrypted_session_key"],
        "ephemeral_public_key":  ecies_result["ephemeral_public_key"],
        "wrap_nonce":            ecies_result["wrap_nonce"],
        "wrap_auth_tag":         ecies_result["wrap_auth_tag"],
        "aes_nonce":             bytes_to_hex(aes_nonce),
        "aes_auth_tag":          bytes_to_hex(aes_auth_tag),
    }


# ══════════════════════════════════════════════════════════════
# 3. Decrypt and Stream
# ══════════════════════════════════════════════════════════════

def decrypt_and_verify(
    transfer,
    receiver_ecc_key_record,
    password: str = None,
    upload_folder: str = None,
    private_key_pem: str = None,
) -> bytes:
    """
    Full decryption pipeline for a file download:

    Step 1: Recover receiver's ECC private key (using session cache or password PBKDF2)
    Step 2: ECIES — recover the AES session key using receiver's private key
    Step 3: Read encrypted file from disk
    Step 4: AES-256-GCM decrypt the file (auto-verifies auth tag)
    Step 5: SHA-256 integrity verification
    Step 6: Return plaintext bytes

    Args:
        transfer:                Transfer DB record (contains all crypto metadata).
        receiver_ecc_key_record: ECCKey DB record for the receiver.
        password:                Receiver's plaintext password (for private key recovery).
        upload_folder:           Server directory containing encrypted files.
        private_key_pem:         Optional cached PEM private key to avoid re-derivation.

    Returns:
        Plaintext bytes of the original file.

    Raises:
        ECCError:           On private key recovery or ECIES decryption failure.
        AESDecryptionError: On AES-GCM failure (auth tag mismatch).
        IntegrityError:     On SHA-256 mismatch.
        FileNotFoundError:  If encrypted file is missing from disk.
    """
    from app.crypto.aes import AESDecryptionError

    # Step 1: Recover receiver's ECC private key
    if private_key_pem:
        from app.crypto.ecc import deserialize_private_key
        private_key = deserialize_private_key(private_key_pem)
    elif password:
        private_key = recover_private_key(
            private_key_enc_hex=receiver_ecc_key_record.private_key_enc,
            kdf_salt_hex=receiver_ecc_key_record.kdf_salt,
            priv_nonce_hex=receiver_ecc_key_record.priv_nonce,
            priv_auth_tag_hex=receiver_ecc_key_record.priv_auth_tag,
            password=password,
        )
    else:
        raise ECCError("No password or private key provided for decryption.")

    # Step 2: ECIES — recover AES session key
    session_key = ecies_decrypt_session_key(
        ephemeral_public_key_pem=transfer.ephemeral_public_key,
        encrypted_session_key_hex=transfer.encrypted_session_key,
        wrap_nonce_hex=transfer.wrap_nonce,
        wrap_auth_tag_hex=transfer.wrap_auth_tag,
        receiver_private_key=private_key,
    )

    # Step 3: Read encrypted file from disk
    file_path = get_stored_file_path(transfer.stored_filename, upload_folder)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Encrypted file not found on server: {transfer.stored_filename}"
        )

    with open(file_path, "rb") as f:
        aes_ciphertext = f.read()

    # Step 4: AES-256-GCM decrypt (auth tag verified automatically)
    plaintext = decrypt_bytes(
        ciphertext=aes_ciphertext,
        key=session_key,
        nonce=hex_to_bytes(transfer.aes_nonce),
        auth_tag=hex_to_bytes(transfer.aes_auth_tag),
    )

    # Step 5: SHA-256 integrity verification
    computed_hash = compute_sha256(plaintext)
    if not verify_sha256(transfer.plaintext_sha256, computed_hash):
        current_app.logger.error(
            f"[TRANSFER] SHA-256 integrity FAILED for transfer_id={transfer.id}. "
            f"Expected: {transfer.plaintext_sha256}, Got: {computed_hash}"
        )
        raise IntegrityError(
            "File integrity verification failed. "
            "The file may have been corrupted or tampered with."
        )

    current_app.logger.info(
        f"[TRANSFER] Decryption + integrity OK for transfer_id={transfer.id}"
    )

    return plaintext


# ══════════════════════════════════════════════════════════════
# 4. File Path Utilities
# ══════════════════════════════════════════════════════════════

def get_stored_file_path(stored_filename: str, upload_folder: str) -> str:
    """
    Return the absolute filesystem path of a stored encrypted file.

    Args:
        stored_filename: UUID-based filename (e.g., "abc123.enc").
        upload_folder:   Base upload directory.

    Returns:
        Absolute path string.
    """
    # Security: Use basename only to prevent path traversal
    safe_name = os.path.basename(stored_filename)
    return os.path.join(upload_folder, safe_name)


def delete_stored_file(stored_filename: str, upload_folder: str) -> bool:
    """
    Delete an encrypted file from the server after successful download.

    Args:
        stored_filename: UUID-based filename.
        upload_folder:   Base upload directory.

    Returns:
        True if deleted; False if file did not exist.
    """
    file_path = get_stored_file_path(stored_filename, upload_folder)
    if os.path.exists(file_path):
        os.remove(file_path)
        current_app.logger.info(
            f"[TRANSFER] Deleted stored file after download: {stored_filename}"
        )
        return True
    return False


# ══════════════════════════════════════════════════════════════
# 5. Formatting Helpers
# ══════════════════════════════════════════════════════════════

def format_file_size(size_bytes: int) -> str:
    """
    Convert byte count to human-readable string.

    Examples:
        format_file_size(500)         → "500 B"
        format_file_size(2048)        → "2.0 KB"
        format_file_size(10485760)    → "10.0 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
