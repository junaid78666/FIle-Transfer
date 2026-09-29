"""
app/crypto/ecc.py — Elliptic Curve Cryptography Module
========================================================
Implements all ECC operations for the file transfer system.

Sections:
  1. ECC Key Generation
     - generate_ecc_keypair()  →  (private_key, public_key) objects
     - serialize / deserialize keys to/from PEM

  2. Private Key Protection (at rest)
     - protect_private_key()   →  AES-GCM encrypt PEM private key using
                                   a password-derived key (PBKDF2)
     - recover_private_key()   →  Reverse of above

  3. ECIES — Elliptic Curve Integrated Encryption Scheme
     - ecies_encrypt_session_key()  →  Wraps AES session key for a recipient
     - ecies_decrypt_session_key()  →  Recovers AES session key using private key

ECIES works as follows:
  ENCRYPT:
    1. Generate ephemeral ECC key pair (ephemeral_priv, ephemeral_pub)
    2. ECDH( ephemeral_priv, receiver_pub ) → shared_secret
    3. HKDF( shared_secret ) → wrapping_key (AES-256)
    4. AES-256-GCM encrypt(session_key, wrapping_key) → encrypted_session_key
    5. Store: ephemeral_pub + encrypted_session_key + wrap_nonce + wrap_tag

  DECRYPT:
    1. ECDH( receiver_priv, ephemeral_pub ) → shared_secret (same!)
    2. HKDF( shared_secret ) → wrapping_key (same!)
    3. AES-256-GCM decrypt(encrypted_session_key, wrapping_key) → session_key

Curve used: NIST P-256 (secp256r1) — 128-bit security level.
"""

import os

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

from app.crypto.aes import (
    encrypt_bytes, decrypt_bytes,
    bytes_to_hex, hex_to_bytes,
    AESDecryptionError,
)
from app.crypto.kdf import (
    derive_key_from_password,
    derive_key_from_shared_secret,
    generate_kdf_salt,
)

# ── ECC Curve ─────────────────────────────────────────────────
_CURVE = ec.SECP256R1()   # NIST P-256


class ECCError(Exception):
    """Base exception for ECC operations."""
    pass


# ══════════════════════════════════════════════════════════════
# SECTION 1 — Key Generation & Serialization
# ══════════════════════════════════════════════════════════════

def generate_ecc_keypair():
    """
    Generate a new NIST P-256 ECC key pair.

    Returns:
        Tuple (private_key, public_key) — cryptography hazmat key objects.

    Example:
        priv, pub = generate_ecc_keypair()
    """
    private_key = ec.generate_private_key(_CURVE, backend=default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key) -> str:
    """
    Serialize an ECC public key to PEM format string.

    Args:
        public_key: cryptography ECC public key object.

    Returns:
        PEM-encoded public key as a UTF-8 string.
    """
    pem_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_bytes.decode("utf-8")


def serialize_private_key(private_key) -> str:
    """
    Serialize an ECC private key to unencrypted PEM format string.

    NOTE: This raw PEM is only used internally before encryption.
    It must NEVER be stored or transmitted without encryption.

    Args:
        private_key: cryptography ECC private key object.

    Returns:
        PEM-encoded private key as a UTF-8 string.
    """
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pem_bytes.decode("utf-8")


def deserialize_public_key(pem_str: str):
    """
    Load an ECC public key from a PEM string.

    Args:
        pem_str: PEM-encoded public key string.

    Returns:
        cryptography ECC public key object.
    """
    return serialization.load_pem_public_key(
        pem_str.encode("utf-8"),
        backend=default_backend(),
    )


def deserialize_private_key(pem_str: str):
    """
    Load an unencrypted ECC private key from a PEM string.

    Args:
        pem_str: PEM-encoded private key string (unencrypted).

    Returns:
        cryptography ECC private key object.
    """
    return serialization.load_pem_private_key(
        pem_str.encode("utf-8"),
        password=None,
        backend=default_backend(),
    )


# ══════════════════════════════════════════════════════════════
# SECTION 2 — Private Key Protection at Rest
# ══════════════════════════════════════════════════════════════

def protect_private_key(private_key, password: str) -> dict:
    """
    Encrypt a private key PEM string using AES-256-GCM with a
    password-derived wrapping key (PBKDF2-SHA256).

    This is called once at user registration to protect the private key
    before it is stored in the database.

    Args:
        private_key: cryptography ECC private key object.
        password:    User's plaintext password.

    Returns:
        Dictionary with:
            {
                "private_key_enc": "<hex>",   # AES-GCM ciphertext
                "kdf_salt":        "<hex>",   # PBKDF2 salt
                "priv_nonce":      "<hex>",   # GCM nonce
                "priv_auth_tag":   "<hex>",   # GCM auth tag
            }
    """
    # 1. Serialize private key to PEM bytes
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # 2. Generate salt and derive wrapping key from password
    kdf_salt = generate_kdf_salt()
    wrapping_key = derive_key_from_password(password, kdf_salt)

    # 3. Encrypt private key PEM with AES-256-GCM
    ciphertext, nonce, auth_tag = encrypt_bytes(pem_bytes, wrapping_key)

    return {
        "private_key_enc": bytes_to_hex(ciphertext),
        "kdf_salt":        bytes_to_hex(kdf_salt),
        "priv_nonce":      bytes_to_hex(nonce),
        "priv_auth_tag":   bytes_to_hex(auth_tag),
    }


def recover_private_key(
    private_key_enc_hex: str,
    kdf_salt_hex: str,
    priv_nonce_hex: str,
    priv_auth_tag_hex: str,
    password: str,
):
    """
    Recover (decrypt) a user's ECC private key using their password.

    Called when the server needs to use the private key for ECIES decryption
    during a file download operation.

    Args:
        private_key_enc_hex: Hex-encoded AES-GCM encrypted private key PEM.
        kdf_salt_hex:        Hex-encoded PBKDF2 salt.
        priv_nonce_hex:      Hex-encoded GCM nonce.
        priv_auth_tag_hex:   Hex-encoded GCM auth tag.
        password:            User's plaintext password.

    Returns:
        cryptography ECC private key object.

    Raises:
        ECCError: If the password is wrong or data is corrupted.
    """
    try:
        # 1. Convert hex fields back to bytes
        ciphertext = hex_to_bytes(private_key_enc_hex)
        kdf_salt   = hex_to_bytes(kdf_salt_hex)
        nonce      = hex_to_bytes(priv_nonce_hex)
        auth_tag   = hex_to_bytes(priv_auth_tag_hex)

        # 2. Re-derive wrapping key from password
        wrapping_key = derive_key_from_password(password, kdf_salt)

        # 3. Decrypt private key PEM
        pem_bytes = decrypt_bytes(ciphertext, wrapping_key, nonce, auth_tag)

        # 4. Deserialize to key object
        return serialization.load_pem_private_key(
            pem_bytes,
            password=None,
            backend=default_backend(),
        )
    except AESDecryptionError:
        raise ECCError("Failed to recover private key: incorrect password or corrupted data.")
    except Exception as exc:
        raise ECCError(f"Private key recovery error: {exc}") from exc


# ══════════════════════════════════════════════════════════════
# SECTION 3 — ECIES: Session Key Encryption / Decryption
# ══════════════════════════════════════════════════════════════

def ecies_encrypt_session_key(session_key: bytes, receiver_public_key_pem: str) -> dict:
    """
    Encrypt an AES session key for a specific recipient using ECIES.

    Steps:
      1. Generate an ephemeral ECC key pair.
      2. Perform ECDH between ephemeral private key and receiver's public key.
      3. Derive a wrapping key using HKDF from the ECDH shared secret.
      4. Encrypt the AES session key using AES-256-GCM with the wrapping key.
      5. Return all data needed for the receiver to decrypt.

    Args:
        session_key:             The 32-byte AES session key to protect.
        receiver_public_key_pem: PEM string of the receiver's ECC public key.

    Returns:
        Dictionary with:
            {
                "ephemeral_public_key":   "<PEM string>",   # For ECDH by receiver
                "encrypted_session_key":  "<hex>",           # AES-GCM ciphertext
                "wrap_nonce":             "<hex>",           # GCM nonce (12 bytes)
                "wrap_auth_tag":          "<hex>",           # GCM auth tag (16 bytes)
            }

    Raises:
        ECCError: On any cryptographic failure.
    """
    try:
        # 1. Load receiver's public key
        receiver_pub_key = deserialize_public_key(receiver_public_key_pem)

        # 2. Generate ephemeral ECC key pair
        ephemeral_priv, ephemeral_pub = generate_ecc_keypair()

        # 3. ECDH: ephemeral_priv × receiver_pub → shared_secret
        shared_secret = ephemeral_priv.exchange(ec.ECDH(), receiver_pub_key)

        # 4. HKDF: shared_secret → wrapping_key (32-byte AES key)
        wrapping_key = derive_key_from_shared_secret(shared_secret)

        # 5. AES-256-GCM encrypt the session key with the wrapping key
        ciphertext, nonce, auth_tag = encrypt_bytes(session_key, wrapping_key)

        # 6. Serialize ephemeral public key for storage
        ephemeral_pub_pem = serialize_public_key(ephemeral_pub)

        return {
            "ephemeral_public_key":  ephemeral_pub_pem,
            "encrypted_session_key": bytes_to_hex(ciphertext),
            "wrap_nonce":            bytes_to_hex(nonce),
            "wrap_auth_tag":         bytes_to_hex(auth_tag),
        }

    except Exception as exc:
        raise ECCError(f"ECIES encryption failed: {exc}") from exc


def ecies_decrypt_session_key(
    ephemeral_public_key_pem: str,
    encrypted_session_key_hex: str,
    wrap_nonce_hex: str,
    wrap_auth_tag_hex: str,
    receiver_private_key,
) -> bytes:
    """
    Recover the AES session key using the receiver's ECC private key (ECIES).

    Steps:
      1. Load the ephemeral public key from the transfer record.
      2. Perform ECDH between receiver's private key and ephemeral public key.
      3. Derive the same wrapping key using HKDF.
      4. Decrypt the encrypted session key using AES-256-GCM.
      5. Return the recovered AES session key.

    Args:
        ephemeral_public_key_pem:   PEM string of sender's ephemeral public key.
        encrypted_session_key_hex:  Hex-encoded AES-GCM ciphertext of session key.
        wrap_nonce_hex:             Hex-encoded GCM nonce (12 bytes).
        wrap_auth_tag_hex:          Hex-encoded GCM auth tag (16 bytes).
        receiver_private_key:       cryptography ECC private key object.

    Returns:
        32-byte AES session key.

    Raises:
        ECCError: If decryption fails (wrong key or tampered data).
    """
    try:
        # 1. Load ephemeral public key
        ephemeral_pub = deserialize_public_key(ephemeral_public_key_pem)

        # 2. ECDH: receiver_priv × ephemeral_pub → shared_secret (same as encryption!)
        shared_secret = receiver_private_key.exchange(ec.ECDH(), ephemeral_pub)

        # 3. HKDF: shared_secret → wrapping_key
        wrapping_key = derive_key_from_shared_secret(shared_secret)

        # 4. AES-256-GCM decrypt the session key
        ciphertext = hex_to_bytes(encrypted_session_key_hex)
        nonce      = hex_to_bytes(wrap_nonce_hex)
        auth_tag   = hex_to_bytes(wrap_auth_tag_hex)

        session_key = decrypt_bytes(ciphertext, wrapping_key, nonce, auth_tag)
        return session_key

    except AESDecryptionError:
        raise ECCError(
            "ECIES decryption failed: invalid session key. "
            "Wrong private key or tampered encrypted key."
        )
    except Exception as exc:
        raise ECCError(f"ECIES decryption error: {exc}") from exc


# ══════════════════════════════════════════════════════════════
# SECTION 4 — ECDSA Digital Signatures & Authenticity Binding
# ══════════════════════════════════════════════════════════════

def compute_transfer_digest(
    plaintext_sha256: str,
    ephemeral_public_key_pem: str,
    receiver_id: int,
) -> bytes:
    """
    Compute a canonical binding digest for transfer authentication.
    Binds the file integrity hash, the ephemeral ECDH public key, and the intended recipient.

    Args:
        plaintext_sha256:         SHA-256 hex digest of the plaintext file.
        ephemeral_public_key_pem: PEM string of the ephemeral public key.
        receiver_id:              User ID of the intended recipient.

    Returns:
        32-byte SHA-256 digest.
    """
    import hashlib
    payload = f"{plaintext_sha256.strip().lower()}:{ephemeral_public_key_pem.strip()}:{receiver_id}".encode("utf-8")
    return hashlib.sha256(payload).digest()


def ecdsa_sign(private_key, data: bytes) -> str:
    """
    Cryptographically sign data using the sender's ECC private key (ECDSA-SHA256).

    Provides authenticity and non-repudiation: confirms the file transfer was
    generated and authorized by the sender.

    Args:
        private_key: cryptography ECC private key object.
        data:        Raw bytes to sign (typically the transfer binding digest).

    Returns:
        Hex-encoded DER signature string.
    """
    try:
        signature = private_key.sign(
            data,
            ec.ECDSA(hashes.SHA256()),
        )
        return bytes_to_hex(signature)
    except Exception as exc:
        raise ECCError(f"ECDSA signing failed: {exc}") from exc


def ecdsa_verify(public_key, signature_hex: str, data: bytes) -> bool:
    """
    Verify an ECDSA-SHA256 signature using the sender's ECC public key.

    Args:
        public_key:    cryptography ECC public key object.
        signature_hex: Hex-encoded DER signature string.
        data:          Raw bytes that were signed.

    Returns:
        True if the signature is valid; False otherwise.
    """
    try:
        signature = hex_to_bytes(signature_hex)
        public_key.verify(
            signature,
            data,
            ec.ECDSA(hashes.SHA256()),
        )
        return True
    except Exception:
        return False

