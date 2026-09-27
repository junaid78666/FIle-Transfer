"""
app/auth/utils.py — Authentication Helper Functions
=====================================================
Provides utilities used by auth routes:
  - register_user()    — Creates User + ECCKey records atomically
  - authenticate_user()— Validates credentials, returns User or None
  - collect_form_errors()— Collects WTForms errors into a list
"""

from datetime import datetime, timezone
from typing import Optional

from flask import current_app
from app import db, bcrypt
from app.models.user import User
from app.models.ecc_key import ECCKey
from app.crypto.ecc import generate_ecc_keypair, protect_private_key, serialize_public_key
from app.crypto.aes import bytes_to_hex


def register_user(username: str, email: str, password: str) -> User:
    """
    Register a new user with:
      1. Hashed password stored in the users table.
      2. ECC key pair generated; private key encrypted with their password.
      3. All written atomically in a single DB transaction.

    Args:
        username: Chosen username (already validated as unique).
        email:    Email address (already validated as unique).
        password: Plaintext password (will be hashed; NOT stored as-is).

    Returns:
        Newly created User object.

    Raises:
        Exception: On any database or cryptographic failure.
    """
    # 1. Hash the password with bcrypt
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # 2. Create User record
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        password_hash=password_hash,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(user)
    db.session.flush()  # Flush to get user.id before creating ECCKey

    # 3. Generate ECC key pair
    private_key, public_key = generate_ecc_keypair()
    public_key_pem = serialize_public_key(public_key)

    # 4. Protect (encrypt) private key using user's password
    protected = protect_private_key(private_key, password)

    # 5. Create ECCKey record
    ecc_key = ECCKey(
        user_id=user.id,
        public_key=public_key_pem,
        private_key_enc=protected["private_key_enc"],
        kdf_salt=protected["kdf_salt"],
        priv_nonce=protected["priv_nonce"],
        priv_auth_tag=protected["priv_auth_tag"],
        curve="P-256",
    )
    db.session.add(ecc_key)

    # 6. Commit both records atomically
    db.session.commit()

    current_app.logger.info(
        f"[AUTH] New user registered: username='{user.username}' "
        f"email='{user.email}' user_id={user.id}"
    )
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Validate login credentials.

    Args:
        email:    User-provided email address.
        password: User-provided plaintext password.

    Returns:
        User object if credentials are valid and account is active.
        None if email not found, password incorrect, or account inactive.

    Security note:
        We always run bcrypt.check_password_hash() even for unknown emails
        to prevent timing-based user enumeration. (However, this simple
        implementation still leaks via query timing. For full protection,
        use a dummy hash comparison.)
    """
    user = User.query.filter_by(email=email.strip().lower()).first()

    if user is None:
        # Run a dummy hash check to prevent timing attacks
        bcrypt.check_password_hash(
            "$2b$12$/39k9qGg6mgVYp7Uy1NQNus4NxvSFNMhWEB4aGrIL/2a7o0PDxzdS", password
        )
        return None

    if not bcrypt.check_password_hash(user.password_hash, password):
        current_app.logger.warning(
            f"[AUTH] Failed login attempt for email='{email}'"
        )
        return None

    if not user.is_active:
        current_app.logger.warning(
            f"[AUTH] Login attempt on inactive account: user_id={user.id}"
        )
        return None

    return user


def collect_form_errors(form) -> list:
    """
    Flatten WTForms validation errors into a list of strings.

    Args:
        form: A submitted WTForms form object with errors.

    Returns:
        List of error message strings, e.g.:
        ["Username is required.", "Password must be at least 8 characters."]
    """
    errors = []
    for field_name, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(error)
    return errors
