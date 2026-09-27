"""
tests/test_crypto.py — Cryptographic Module Tests
===================================================
Tests for: AES, ECC, KDF, Hashing modules.

Run with:
    pytest tests/test_crypto.py -v
"""

import os
import pytest

from app.crypto.aes import (
    generate_aes_key, generate_nonce,
    encrypt_bytes, decrypt_bytes,
    bytes_to_hex, hex_to_bytes,
    AESDecryptionError, AES_KEY_SIZE, AES_GCM_NONCE_SIZE, AES_GCM_TAG_SIZE,
)
from app.crypto.hashing import compute_sha256, verify_sha256, IntegrityError
from app.crypto.kdf import (
    generate_kdf_salt, derive_key_from_password, derive_key_from_shared_secret,
)
from app.crypto.ecc import (
    generate_ecc_keypair,
    serialize_public_key, serialize_private_key,
    deserialize_public_key, deserialize_private_key,
    protect_private_key, recover_private_key,
    ecies_encrypt_session_key, ecies_decrypt_session_key,
    ECCError,
)


# ══════════════════════════════════════════════════════════════
# AES-256-GCM Tests
# ══════════════════════════════════════════════════════════════

class TestAES:

    def test_key_generation_length(self):
        """AES key must be 32 bytes (256 bits)."""
        key = generate_aes_key()
        assert len(key) == AES_KEY_SIZE == 32

    def test_key_randomness(self):
        """Two generated keys must not be equal."""
        assert generate_aes_key() != generate_aes_key()

    def test_nonce_generation_length(self):
        """Nonce must be 12 bytes (96 bits)."""
        nonce = generate_nonce()
        assert len(nonce) == AES_GCM_NONCE_SIZE == 12

    def test_nonce_randomness(self):
        """Two generated nonces must not be equal."""
        assert generate_nonce() != generate_nonce()

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypting then decrypting should return the original plaintext."""
        key = generate_aes_key()
        plaintext = b"Hello, ECC File Transfer!"

        ciphertext, nonce, auth_tag = encrypt_bytes(plaintext, key)
        recovered = decrypt_bytes(ciphertext, key, nonce, auth_tag)

        assert recovered == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        """Ciphertext must not equal plaintext."""
        key = generate_aes_key()
        plaintext = b"Secret document content"
        ciphertext, _, _ = encrypt_bytes(plaintext, key)
        assert ciphertext != plaintext

    def test_auth_tag_length(self):
        """GCM auth tag must be exactly 16 bytes."""
        key = generate_aes_key()
        _, _, auth_tag = encrypt_bytes(b"test data", key)
        assert len(auth_tag) == AES_GCM_TAG_SIZE == 16

    def test_wrong_key_raises_error(self):
        """Decryption with wrong key must raise AESDecryptionError."""
        key1 = generate_aes_key()
        key2 = generate_aes_key()  # Different key
        ciphertext, nonce, auth_tag = encrypt_bytes(b"secret", key1)

        with pytest.raises(AESDecryptionError):
            decrypt_bytes(ciphertext, key2, nonce, auth_tag)

    def test_tampered_ciphertext_raises_error(self):
        """Modifying ciphertext must raise AESDecryptionError (auth tag mismatch)."""
        key = generate_aes_key()
        ciphertext, nonce, auth_tag = encrypt_bytes(b"important data", key)

        # Flip first byte of ciphertext
        tampered = bytes([ciphertext[0] ^ 0xFF]) + ciphertext[1:]

        with pytest.raises(AESDecryptionError):
            decrypt_bytes(tampered, key, nonce, auth_tag)

    def test_tampered_auth_tag_raises_error(self):
        """Modifying the auth tag must raise AESDecryptionError."""
        key = generate_aes_key()
        ciphertext, nonce, auth_tag = encrypt_bytes(b"data", key)
        bad_tag = bytes([auth_tag[0] ^ 0x01]) + auth_tag[1:]

        with pytest.raises(AESDecryptionError):
            decrypt_bytes(ciphertext, key, nonce, bad_tag)

    def test_encrypt_large_data(self):
        """Encrypt and decrypt 1 MB of data successfully."""
        key = generate_aes_key()
        plaintext = os.urandom(1024 * 1024)  # 1 MB
        ciphertext, nonce, auth_tag = encrypt_bytes(plaintext, key)
        recovered = decrypt_bytes(ciphertext, key, nonce, auth_tag)
        assert recovered == plaintext

    def test_hex_conversion_roundtrip(self):
        """bytes_to_hex → hex_to_bytes must be identity."""
        data = os.urandom(32)
        assert hex_to_bytes(bytes_to_hex(data)) == data

    def test_invalid_key_size_raises_valueerror(self):
        """Key with wrong size must raise ValueError."""
        with pytest.raises(ValueError):
            encrypt_bytes(b"data", b"short_key")


# ══════════════════════════════════════════════════════════════
# SHA-256 Hashing Tests
# ══════════════════════════════════════════════════════════════

class TestHashing:

    def test_sha256_deterministic(self):
        """Same input always produces same hash."""
        data = b"Test file content 123"
        assert compute_sha256(data) == compute_sha256(data)

    def test_sha256_length(self):
        """SHA-256 output is 64 hex characters (256 bits)."""
        digest = compute_sha256(b"hello")
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_sha256_known_value(self):
        """Verify a known SHA-256 hash."""
        # SHA-256 of empty string
        digest = compute_sha256(b"")
        assert digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_sha256_different_inputs(self):
        """Different inputs produce different hashes."""
        assert compute_sha256(b"file1") != compute_sha256(b"file2")

    def test_verify_sha256_match(self):
        """verify_sha256 returns True for identical digests."""
        data = b"original content"
        digest = compute_sha256(data)
        assert verify_sha256(digest, compute_sha256(data)) is True

    def test_verify_sha256_mismatch(self):
        """verify_sha256 returns False for different digests."""
        assert verify_sha256(compute_sha256(b"original"), compute_sha256(b"tampered")) is False

    def test_verify_sha256_case_insensitive(self):
        """verify_sha256 is case-insensitive."""
        digest = compute_sha256(b"data")
        assert verify_sha256(digest.upper(), digest.lower()) is True

    def test_sha256_rejects_non_bytes(self):
        """compute_sha256 raises TypeError for non-bytes input."""
        with pytest.raises(TypeError):
            compute_sha256("string, not bytes")


# ══════════════════════════════════════════════════════════════
# KDF Tests
# ══════════════════════════════════════════════════════════════

class TestKDF:

    def test_salt_generation_length(self):
        """KDF salt must be 32 bytes."""
        salt = generate_kdf_salt()
        assert len(salt) == 32

    def test_salt_randomness(self):
        """Two salts must not be equal."""
        assert generate_kdf_salt() != generate_kdf_salt()

    def test_pbkdf2_output_length(self):
        """PBKDF2 derived key must be 32 bytes."""
        key = derive_key_from_password("MyP@ss!", generate_kdf_salt())
        assert len(key) == 32

    def test_pbkdf2_deterministic_with_same_salt(self):
        """Same password + same salt always gives same key."""
        salt = generate_kdf_salt()
        key1 = derive_key_from_password("Password1!", salt)
        key2 = derive_key_from_password("Password1!", salt)
        assert key1 == key2

    def test_pbkdf2_different_salt_different_key(self):
        """Same password + different salt gives different key."""
        key1 = derive_key_from_password("Password1!", generate_kdf_salt())
        key2 = derive_key_from_password("Password1!", generate_kdf_salt())
        assert key1 != key2

    def test_pbkdf2_different_password_different_key(self):
        """Different passwords + same salt gives different key."""
        salt = generate_kdf_salt()
        key1 = derive_key_from_password("Password1!", salt)
        key2 = derive_key_from_password("Password2!", salt)
        assert key1 != key2

    def test_hkdf_output_length(self):
        """HKDF derived key must be 32 bytes."""
        shared_secret = os.urandom(32)
        key = derive_key_from_shared_secret(shared_secret)
        assert len(key) == 32

    def test_hkdf_deterministic(self):
        """Same shared secret gives same derived key."""
        shared_secret = os.urandom(32)
        key1 = derive_key_from_shared_secret(shared_secret)
        key2 = derive_key_from_shared_secret(shared_secret)
        assert key1 == key2

    def test_hkdf_different_secrets(self):
        """Different shared secrets give different derived keys."""
        key1 = derive_key_from_shared_secret(os.urandom(32))
        key2 = derive_key_from_shared_secret(os.urandom(32))
        assert key1 != key2


# ══════════════════════════════════════════════════════════════
# ECC Key Tests
# ══════════════════════════════════════════════════════════════

class TestECCKeys:

    def test_keypair_generation(self):
        """generate_ecc_keypair returns private and public key objects."""
        priv, pub = generate_ecc_keypair()
        assert priv is not None
        assert pub is not None

    def test_public_key_serialization_roundtrip(self):
        """Serialize → deserialize public key returns equivalent key."""
        priv, pub = generate_ecc_keypair()
        pem = serialize_public_key(pub)
        assert "-----BEGIN PUBLIC KEY-----" in pem
        recovered = deserialize_public_key(pem)
        # Verify both serialize to same PEM
        assert serialize_public_key(recovered) == pem

    def test_private_key_serialization_roundtrip(self):
        """Serialize → deserialize private key returns equivalent key."""
        priv, _ = generate_ecc_keypair()
        pem = serialize_private_key(priv)
        assert "-----BEGIN PRIVATE KEY-----" in pem
        recovered = deserialize_private_key(pem)
        assert serialize_private_key(recovered) == pem

    def test_two_keypairs_are_different(self):
        """Each generated key pair must be unique."""
        _, pub1 = generate_ecc_keypair()
        _, pub2 = generate_ecc_keypair()
        assert serialize_public_key(pub1) != serialize_public_key(pub2)

    def test_protect_and_recover_private_key(self):
        """protect_private_key → recover_private_key roundtrip."""
        priv, _ = generate_ecc_keypair()
        password = "Str0ng!P@ssword"

        protected = protect_private_key(priv, password)

        assert "private_key_enc" in protected
        assert "kdf_salt" in protected
        assert "priv_nonce" in protected
        assert "priv_auth_tag" in protected

        recovered = recover_private_key(
            private_key_enc_hex=protected["private_key_enc"],
            kdf_salt_hex=protected["kdf_salt"],
            priv_nonce_hex=protected["priv_nonce"],
            priv_auth_tag_hex=protected["priv_auth_tag"],
            password=password,
        )
        assert serialize_private_key(recovered) == serialize_private_key(priv)

    def test_wrong_password_fails_recovery(self):
        """Wrong password must raise ECCError when recovering private key."""
        priv, _ = generate_ecc_keypair()
        protected = protect_private_key(priv, "CorrectP@ss1")

        with pytest.raises(ECCError):
            recover_private_key(
                private_key_enc_hex=protected["private_key_enc"],
                kdf_salt_hex=protected["kdf_salt"],
                priv_nonce_hex=protected["priv_nonce"],
                priv_auth_tag_hex=protected["priv_auth_tag"],
                password="WrongP@ss1",
            )


# ══════════════════════════════════════════════════════════════
# ECIES Tests
# ══════════════════════════════════════════════════════════════

class TestECIES:

    def test_ecies_roundtrip(self):
        """ECIES encrypt session key → decrypt recovers same key."""
        receiver_priv, receiver_pub = generate_ecc_keypair()
        receiver_pub_pem = serialize_public_key(receiver_pub)
        session_key = generate_aes_key()

        # Sender encrypts session key for receiver
        ecies_data = ecies_encrypt_session_key(session_key, receiver_pub_pem)

        assert "ephemeral_public_key" in ecies_data
        assert "encrypted_session_key" in ecies_data
        assert "wrap_nonce" in ecies_data
        assert "wrap_auth_tag" in ecies_data

        # Receiver decrypts session key
        recovered_key = ecies_decrypt_session_key(
            ephemeral_public_key_pem=ecies_data["ephemeral_public_key"],
            encrypted_session_key_hex=ecies_data["encrypted_session_key"],
            wrap_nonce_hex=ecies_data["wrap_nonce"],
            wrap_auth_tag_hex=ecies_data["wrap_auth_tag"],
            receiver_private_key=receiver_priv,
        )

        assert recovered_key == session_key

    def test_ecies_wrong_private_key_fails(self):
        """ECIES decrypt with wrong private key must raise ECCError."""
        _, receiver_pub = generate_ecc_keypair()
        wrong_priv, _ = generate_ecc_keypair()
        session_key = generate_aes_key()

        ecies_data = ecies_encrypt_session_key(
            session_key, serialize_public_key(receiver_pub)
        )

        with pytest.raises(ECCError):
            ecies_decrypt_session_key(
                ephemeral_public_key_pem=ecies_data["ephemeral_public_key"],
                encrypted_session_key_hex=ecies_data["encrypted_session_key"],
                wrap_nonce_hex=ecies_data["wrap_nonce"],
                wrap_auth_tag_hex=ecies_data["wrap_auth_tag"],
                receiver_private_key=wrong_priv,
            )

    def test_ecies_uses_unique_ephemeral_key(self):
        """Each ECIES call uses a new ephemeral key (different ephemeral pub keys)."""
        _, receiver_pub = generate_ecc_keypair()
        pub_pem = serialize_public_key(receiver_pub)
        session_key = generate_aes_key()

        result1 = ecies_encrypt_session_key(session_key, pub_pem)
        result2 = ecies_encrypt_session_key(session_key, pub_pem)

        assert result1["ephemeral_public_key"] != result2["ephemeral_public_key"]
        assert result1["encrypted_session_key"] != result2["encrypted_session_key"]

    def test_full_file_encryption_pipeline(self):
        """
        Integration test: Full encrypt → decrypt → verify SHA-256 pipeline.

        Simulates the complete transfer flow:
          1. Compute SHA-256 of plaintext
          2. Generate AES session key
          3. AES-256-GCM encrypt file
          4. ECIES wrap session key for receiver
          5. ECIES unwrap session key using receiver's private key
          6. AES-256-GCM decrypt file
          7. Verify SHA-256 integrity
        """
        # Setup
        receiver_priv, receiver_pub = generate_ecc_keypair()
        receiver_pub_pem = serialize_public_key(receiver_pub)
        plaintext = b"This is a confidential file. " * 100  # ~3 KB

        # Step 1: SHA-256 of plaintext
        original_hash = compute_sha256(plaintext)

        # Step 2 & 3: Generate AES key + encrypt file
        session_key = generate_aes_key()
        ciphertext, aes_nonce, aes_auth_tag = encrypt_bytes(plaintext, session_key)

        # Step 4: ECIES wrap session key
        ecies_data = ecies_encrypt_session_key(session_key, receiver_pub_pem)

        # Step 5: ECIES unwrap session key
        recovered_session_key = ecies_decrypt_session_key(
            ephemeral_public_key_pem=ecies_data["ephemeral_public_key"],
            encrypted_session_key_hex=ecies_data["encrypted_session_key"],
            wrap_nonce_hex=ecies_data["wrap_nonce"],
            wrap_auth_tag_hex=ecies_data["wrap_auth_tag"],
            receiver_private_key=receiver_priv,
        )

        # Step 6: AES-GCM decrypt
        recovered_plaintext = decrypt_bytes(
            ciphertext, recovered_session_key, aes_nonce, aes_auth_tag
        )

        # Step 7: Verify SHA-256
        assert recovered_plaintext == plaintext
        assert verify_sha256(original_hash, compute_sha256(recovered_plaintext))
