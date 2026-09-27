"""
tests/test_frontend.py — Frontend UI & Template Rendering Tests
================================================================
Verifies that all HTML5 Jinja2 templates, static assets, and view routes
render with HTTP 200 and expected DOM elements.

Run with:
    pytest tests/test_frontend.py -v
"""

import pytest
from app import create_app, db
from app.models.user import User
from app.models.ecc_key import ECCKey
from app.models.transfer import Transfer


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.query(Transfer).delete()
        db.session.query(ECCKey).delete()
        db.session.query(User).delete()
        db.session.commit()
        db.session.remove()
    yield
    with app.app_context():
        db.session.remove()


# ── Helpers ───────────────────────────────────────────────────

USER_DATA = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "Str0ng!Pass",
    "confirm_password": "Str0ng!Pass",
}


def register_and_login(client):
    client.post("/auth/register", json=USER_DATA)
    client.post("/auth/login", json={
        "email": USER_DATA["email"],
        "password": USER_DATA["password"],
    })


# ══════════════════════════════════════════════════════════════
# Public Pages Tests
# ══════════════════════════════════════════════════════════════

class TestPublicPages:

    def test_landing_page_renders_html(self, client):
        """GET / with HTML Accept header renders landing page."""
        response = client.get("/", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert b"Zero-Trust File Transfer" in response.data
        assert b"NIST P-256" in response.data
        assert b"tokens.css" in response.data

    def test_login_page_renders_html(self, client):
        """GET /auth/login renders login template."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Account Sign In" in response.data
        assert b"email" in response.data
        assert b"password" in response.data

    def test_register_page_renders_html(self, client):
        """GET /auth/register renders registration template with password meter."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Create ECC Account" in response.data
        assert b"meter-bar" in response.data
        assert b"PBKDF2-HMAC-SHA256" in response.data


# ══════════════════════════════════════════════════════════════
# Authenticated Views Tests
# ══════════════════════════════════════════════════════════════

class TestAuthenticatedPages:

    def test_dashboard_renders_for_logged_in_user(self, client):
        """GET /dashboard renders dashboard template when authenticated."""
        register_and_login(client)
        response = client.get("/dashboard", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert b"Welcome back" in response.data
        assert b"alice" in response.data
        assert b"Pending Decryption" in response.data

    def test_send_file_page_renders(self, client):
        """GET /transfer/send renders file dropzone interface."""
        register_and_login(client)
        response = client.get("/transfer/send")
        assert response.status_code == 200
        assert b"Send Encrypted File" in response.data
        assert b"dropzone" in response.data
        assert b"progress-container" in response.data

    def test_inbox_page_renders(self, client):
        """GET /transfer/inbox renders secure inbox template."""
        register_and_login(client)
        response = client.get("/transfer/inbox", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert b"Secure Inbound Transfers" in response.data
        assert b"inbox-table" in response.data

    def test_history_page_renders(self, client):
        """GET /transfer/history renders audit table template."""
        register_and_login(client)
        response = client.get("/transfer/history", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert b"Transfer Audit Ledger" in response.data
        assert b"history-table" in response.data

    def test_profile_page_renders(self, client):
        """GET /profile renders cryptographic public key viewer."""
        register_and_login(client)
        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Cryptographic Profile" in response.data
        assert b"NIST P-256" in response.data
        assert b"BEGIN PUBLIC KEY" in response.data


# ══════════════════════════════════════════════════════════════
# Static Asset Serving Tests
# ══════════════════════════════════════════════════════════════

class TestStaticAssets:

    def test_tokens_css_served(self, client):
        response = client.get("/static/css/tokens.css")
        assert response.status_code == 200
        assert b"--bg-base" in response.data

    def test_components_css_served(self, client):
        response = client.get("/static/css/components.css")
        assert response.status_code == 200
        assert b".crypto-badge" in response.data

    def test_api_js_served(self, client):
        response = client.get("/static/js/api.js")
        assert response.status_code == 200
        assert b"apiRequest" in response.data

    def test_animations_css_served(self, client):
        response = client.get("/static/css/animations.css")
        assert response.status_code == 200
        assert b"fadeInUp" in response.data

    def test_three_background_js_served(self, client):
        response = client.get("/static/js/three-background.js")
        assert response.status_code == 200
        assert b"initHeroBackground" in response.data

