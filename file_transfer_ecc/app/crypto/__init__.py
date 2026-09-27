# app/crypto/__init__.py
# Exposes the public API of the crypto package.

from app.crypto.ecc import (
    generate_ecc_keypair,
    serialize_public_key,
    serialize_private_key,
    deserialize_public_key,
    deserialize_private_key,
    protect_private_key,
    recover_private_key,
    ecies_encrypt_session_key,
    ecies_decrypt_session_key,
    ECCError,
)
from app.crypto.aes import (
    generate_aes_key,
    encrypt_bytes,
    decrypt_bytes,
    bytes_to_hex,
    hex_to_bytes,
    AESDecryptionError,
)
from app.crypto.hashing import (
    compute_sha256,
    compute_sha256_stream,
    verify_sha256,
    IntegrityError,
)
from app.crypto.kdf import (
    generate_kdf_salt,
    derive_key_from_password,
    derive_key_from_shared_secret,
)

__all__ = [
    # ECC
    "generate_ecc_keypair",
    "serialize_public_key",
    "serialize_private_key",
    "deserialize_public_key",
    "deserialize_private_key",
    "protect_private_key",
    "recover_private_key",
    "ecies_encrypt_session_key",
    "ecies_decrypt_session_key",
    "ECCError",
    # AES
    "generate_aes_key",
    "encrypt_bytes",
    "decrypt_bytes",
    "bytes_to_hex",
    "hex_to_bytes",
    "AESDecryptionError",
    # Hashing
    "compute_sha256",
    "compute_sha256_stream",
    "verify_sha256",
    "IntegrityError",
    # KDF
    "generate_kdf_salt",
    "derive_key_from_password",
    "derive_key_from_shared_secret",
]
