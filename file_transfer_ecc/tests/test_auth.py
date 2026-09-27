"""
tests/test_auth.py — Authentication Route Tests
=================================================
Tests for: /auth/register, /auth/login, /auth/logout, /auth/me

Run with:
    pytest tests/test_auth.py -v
"""

import pytest
from app import create_app, db
from app.models.user import User
from app.models.ecc_key import ECCKey


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    """Create Flask app with testing config."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clear DB tables before each test."""
    with app.app_context():
        db.session.query(ECCKey).delete()
        db.session.query(User).delete()
        db.session.commit()
    yield


# ── Helper ────────────────────────────────────────────────────

VALID_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Str0ng!Pass",
    "confirm_password": "Str0ng!Pass",
}


def register(client, data=None):
    data = data or VALID_USER
    return client.post("/auth/register", json=data)


def login(client, email=None, password=None):
    return client.post("/auth/login", json={
        "email": email or VALID_USER["email"],
        "password": password or VALID_USER["password"],
    })


# ══════════════════════════════════════════════════════════════
# Registration Tests
# ══════════════════════════════════════════════════════════════

class TestRegistration:

    def test_successful_registration(self, app, client):
        """Valid registration creates user and ECC key pair."""
        response = register(client)
        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        assert "user" in data
        assert data["user"]["username"] == "testuser"

        # Verify DB records
        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            assert user is not None
            assert user.ecc_key is not None
            assert user.ecc_key.public_key is not None

    def test_duplicate_username_rejected(self, client):
        """Duplicate username returns 400 error."""
        register(client)
        response = register(client, {
            **VALID_USER,
            "email": "other@example.com",
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        assert any("username" in e.lower() for e in data.get("errors", []))

    def test_duplicate_email_rejected(self, client):
        """Duplicate email returns 400 error."""
        register(client)
        response = register(client, {
            **VALID_USER,
            "username": "other",
        })
        assert response.status_code == 400

    def test_weak_password_rejected(self, client):
        """Weak password (no uppercase/special char) returns 400."""
        response = register(client, {
            **VALID_USER,
            "password": "weakpassword",
            "confirm_password": "weakpassword",
        })
        assert response.status_code == 400

    def test_mismatched_passwords_rejected(self, client):
        """Non-matching passwords return 400."""
        response = register(client, {
            **VALID_USER,
            "confirm_password": "DifferentP@ss1",
        })
        assert response.status_code == 400

    def test_missing_email_rejected(self, client):
        """Missing email field returns 400."""
        response = register(client, {
            "username": "testuser",
            "password": "Str0ng!Pass",
            "confirm_password": "Str0ng!Pass",
        })
        assert response.status_code == 400

    def test_invalid_email_format_rejected(self, client):
        """Malformed email returns 400."""
        response = register(client, {
            **VALID_USER,
            "email": "not-an-email",
        })
        assert response.status_code == 400

    def test_password_not_stored_in_plaintext(self, app, client):
        """Password hash must not equal the plaintext password."""
        register(client)
        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            assert user.password_hash != VALID_USER["password"]
            assert user.password_hash.startswith("$2b$")  # bcrypt prefix


# ══════════════════════════════════════════════════════════════
# Login Tests
# ══════════════════════════════════════════════════════════════

class TestLogin:

    def test_successful_login(self, client):
        """Valid credentials return 200 with user data."""
        register(client)
        response = login(client)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_wrong_password_rejected(self, client):
        """Wrong password returns 401."""
        register(client)
        response = login(client, password="WrongP@ss1")
        assert response.status_code == 401
        data = response.get_json()
        assert data["status"] == "error"

    def test_unknown_email_rejected(self, client):
        """Unknown email returns 401 (not 404 — prevents user enumeration)."""
        response = login(client, email="nobody@example.com", password="Str0ng!Pass")
        assert response.status_code == 401

    def test_missing_password_rejected(self, client):
        """Missing password field returns 400."""
        response = client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 400

    def test_session_created_after_login(self, client):
        """After login, /auth/me returns current user (session active)."""
        register(client)
        login(client)
        response = client.get("/auth/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["user"]["username"] == "testuser"

    def test_me_returns_401_when_not_logged_in(self, client):
        """GET /auth/me without session returns 401."""
        with client.session_transaction() as sess:
            sess.clear()
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_last_login_updated_on_login(self, app, client):
        """last_login_at is updated on successful login."""
        register(client)
        login(client)
        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            assert user.last_login_at is not None


# ══════════════════════════════════════════════════════════════
# Logout Tests
# ══════════════════════════════════════════════════════════════

class TestLogout:

    def test_logout_destroys_session(self, client):
        """After logout, /auth/me returns 401."""
        register(client)
        login(client)

        # Verify logged in
        assert client.get("/auth/me").status_code == 200

        # Logout
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.get_json()["status"] == "success"

        # Verify session destroyed
        assert client.get("/auth/me").status_code == 401

    def test_logout_without_session_returns_401(self, client):
        """Logout without being logged in returns 401."""
        with client.session_transaction() as sess:
            sess.clear()
        response = client.post("/auth/logout")
        assert response.status_code == 401


# ══════════════════════════════════════════════════════════════
# User Listing Tests
# ══════════════════════════════════════════════════════════════

class TestUserListing:

    def test_list_users_returns_others(self, client):
        """GET /auth/users/list returns all users except current user."""
        register(client)
        # Register second user
        client.post("/auth/register", json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "Str0ng!Pass",
            "confirm_password": "Str0ng!Pass",
        })
        login(client)

        response = client.get("/auth/users/list")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        usernames = [u["username"] for u in data["users"]]
        assert "bob" in usernames
        assert "testuser" not in usernames  # Must exclude self

    def test_list_users_requires_login(self, client):
        """GET /auth/users/list requires authentication."""
        with client.session_transaction() as sess:
            sess.clear()
        response = client.get("/auth/users/list")
        assert response.status_code == 401
