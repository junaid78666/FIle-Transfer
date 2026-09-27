"""
tests/test_transfer.py — Transfer Route Tests
===============================================
Tests for: /transfer/send, /transfer/download, /transfer/inbox,
           /transfer/sent, /transfer/history, /transfer/stats

Run with:
    pytest tests/test_transfer.py -v
"""

import io
import pytest
from app import create_app, db
from app.models.user import User
from app.models.ecc_key import ECCKey
from app.models.transfer import Transfer, TransferStatus


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
    """Fresh Flask test client per test (clean cookie jar)."""
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

ALICE = {
    "username": "alice", "email": "alice@example.com",
    "password": "Str0ng!Pass", "confirm_password": "Str0ng!Pass",
}
BOB = {
    "username": "bob", "email": "bob@example.com",
    "password": "Str0ng!Pass", "confirm_password": "Str0ng!Pass",
}


def register_user(client, data):
    return client.post("/auth/register", json=data)


def login_as(client, email, password="Str0ng!Pass"):
    return client.post("/auth/login", json={"email": email, "password": password})


def logout(client):
    client.post("/auth/logout")


def get_user_id(app, email):
    with app.app_context():
        return User.query.filter_by(email=email).first().id


def make_file_data(filename="test.txt", content=b"Hello, secure world!"):
    return {
        "file": (io.BytesIO(content), filename),
    }


# ══════════════════════════════════════════════════════════════
# Send File Tests
# ══════════════════════════════════════════════════════════════

class TestSendFile:

    def test_successful_transfer(self, app, client):
        """Sending a valid file to a valid recipient creates a transfer."""
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])

        bob_id = get_user_id(app, BOB["email"])

        response = client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": bob_id},
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["status"] == "success"
        assert "transfer_id" in data["transfer"]
        assert data["transfer"]["status"] == TransferStatus.PENDING

    def test_transfer_stored_in_db(self, app, client):
        """After successful send, Transfer record exists in DB."""
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])
        bob_id = get_user_id(app, BOB["email"])

        client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": bob_id},
            content_type="multipart/form-data",
        )

        with app.app_context():
            transfer = Transfer.query.first()
            assert transfer is not None
            assert transfer.status == TransferStatus.PENDING
            assert transfer.original_filename == "test.txt"

    def test_cannot_send_to_self(self, app, client):
        """Sending file to yourself returns 400."""
        register_user(client, ALICE)
        login_as(client, ALICE["email"])
        alice_id = get_user_id(app, ALICE["email"])

        response = client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": alice_id},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_send_requires_login(self, client):
        """Sending without authentication returns 401."""
        register_user(client, ALICE)
        register_user(client, BOB)
        logout(client)

        response = client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": 999},
            content_type="multipart/form-data",
        )
        assert response.status_code == 401

    def test_no_file_returns_400(self, app, client):
        """Request without file field returns 400."""
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])
        bob_id = get_user_id(app, BOB["email"])

        response = client.post(
            "/transfer/send",
            data={"receiver_id": bob_id},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_no_receiver_returns_400(self, client):
        """Request without receiver_id returns 400."""
        register_user(client, ALICE)
        login_as(client, ALICE["email"])

        response = client.post(
            "/transfer/send",
            data=make_file_data(),
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_invalid_receiver_returns_404(self, client):
        """Non-existent receiver_id returns 404."""
        register_user(client, ALICE)
        login_as(client, ALICE["email"])

        response = client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": 99999},
            content_type="multipart/form-data",
        )
        assert response.status_code in (400, 404)


# ══════════════════════════════════════════════════════════════
# Download File Tests
# ══════════════════════════════════════════════════════════════

class TestDownloadFile:

    def _send_file(self, app, client):
        """Helper: register users, log in as Alice, send Bob a file, then log out."""
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])
        bob_id = get_user_id(app, BOB["email"])
        content = b"Top secret document content."
        resp = client.post(
            "/transfer/send",
            data={
                "file": (io.BytesIO(content), "secret.txt"),
                "receiver_id": bob_id,
            },
            content_type="multipart/form-data",
        )
        logout(client)  # Always log out after sending
        transfer_id = resp.get_json()["transfer"]["transfer_id"]
        return transfer_id, content

    def test_receiver_can_download(self, app, client):
        """Receiver successfully downloads and decrypts the file."""
        transfer_id, content = self._send_file(app, client)
        login_as(client, BOB["email"])

        response = client.post(
            f"/transfer/download/{transfer_id}",
            json={"password": BOB["password"]},
        )
        assert response.status_code == 200
        assert response.data == content

    def test_download_marks_as_downloaded(self, app, client):
        """After successful download, transfer status is DOWNLOADED."""
        transfer_id, _ = self._send_file(app, client)
        login_as(client, BOB["email"])

        client.post(
            f"/transfer/download/{transfer_id}",
            json={"password": BOB["password"]},
        )

        with app.app_context():
            transfer = db.session.get(Transfer, transfer_id)
            assert transfer.status == TransferStatus.DOWNLOADED
            assert transfer.downloaded_at is not None

    def test_non_receiver_cannot_download(self, app, client):
        """Alice cannot download a transfer intended for Bob."""
        transfer_id, _ = self._send_file(app, client)
        login_as(client, ALICE["email"])

        response = client.post(
            f"/transfer/download/{transfer_id}",
            json={"password": ALICE["password"]},
        )
        assert response.status_code == 403

    def test_wrong_password_fails_decryption(self, app, client):
        """Wrong password for decryption returns 422."""
        transfer_id, _ = self._send_file(app, client)
        login_as(client, BOB["email"])

        response = client.post(
            f"/transfer/download/{transfer_id}",
            json={"password": "WrongP@ssword1"},
        )
        assert response.status_code == 422

    def test_missing_password_returns_400(self, app, client):
        """Missing password in request body returns 400."""
        transfer_id, _ = self._send_file(app, client)
        login_as(client, BOB["email"])

        response = client.post(
            f"/transfer/download/{transfer_id}",
            json={},
        )
        assert response.status_code == 400

    def test_nonexistent_transfer_returns_404(self, client):
        """Downloading non-existent transfer ID returns 404."""
        register_user(client, BOB)
        login_as(client, BOB["email"])

        response = client.post(
            "/transfer/download/00000000-0000-0000-0000-000000000000",
            json={"password": BOB["password"]},
        )
        assert response.status_code == 404

    def test_download_requires_login(self, client):
        """Download without authentication returns 401."""
        logout(client)
        response = client.post(
            "/transfer/download/some-id",
            json={"password": "irrelevant"},
        )
        assert response.status_code == 401


# ══════════════════════════════════════════════════════════════
# Inbox / Sent / History Tests
# ══════════════════════════════════════════════════════════════

class TestTransferListing:

    def _setup_transfer(self, app, client):
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])
        bob_id = get_user_id(app, BOB["email"])
        client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": bob_id},
            content_type="multipart/form-data",
        )
        logout(client)  # Ensure clean state after setup
    def test_inbox_shows_received_transfers(self, app, client):
        """Bob sees the file Alice sent him in his inbox."""
        self._setup_transfer(app, client)
        login_as(client, BOB["email"])

        response = client.get("/transfer/inbox")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 1
        assert data["transfers"][0]["sender_username"] == "alice"
        assert data["transfers"][0]["status"] == TransferStatus.PENDING

    def test_inbox_shows_only_own_transfers(self, app, client):
        """Alice's inbox is empty (she sent, not received)."""
        self._setup_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.get("/transfer/inbox")
        assert response.status_code == 200
        assert response.get_json()["total"] == 0

    def test_sent_shows_sent_transfers(self, app, client):
        """GET /transfer/sent shows what Alice sent."""
        self._setup_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.get("/transfer/sent")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total"] == 1
        assert data["transfers"][0]["receiver_username"] == "bob"

    def test_history_combines_both(self, app, client):
        """GET /transfer/history shows transfers from both directions."""
        self._setup_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.get("/transfer/history")
        assert response.status_code == 200
        assert response.get_json()["total"] >= 1

    def test_stats_returns_correct_counts(self, app, client):
        """GET /transfer/stats returns correct statistics."""
        self._setup_transfer(app, client)
        login_as(client, BOB["email"])

        response = client.get("/transfer/stats")
        assert response.status_code == 200
        stats = response.get_json()["stats"]
        assert stats["total_received"] == 1
        assert stats["pending_received"] == 1

    def test_inbox_requires_login(self, client):
        logout(client)
        assert client.get("/transfer/inbox").status_code == 401

    def test_history_pagination(self, app, client):
        """History with per_page=1 returns first page only."""
        self._setup_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.get("/transfer/history?page=1&per_page=1")
        data = response.get_json()
        assert len(data["transfers"]) <= 1


# ══════════════════════════════════════════════════════════════
# Transfer Info / Delete Tests
# ══════════════════════════════════════════════════════════════

class TestTransferManagement:

    def _create_transfer(self, app, client):
        register_user(client, ALICE)
        register_user(client, BOB)
        login_as(client, ALICE["email"])
        bob_id = get_user_id(app, BOB["email"])
        resp = client.post(
            "/transfer/send",
            data={**make_file_data(), "receiver_id": bob_id},
            content_type="multipart/form-data",
        )
        logout(client)  # Ensure clean state
        return resp.get_json()["transfer"]["transfer_id"]

    def test_sender_can_view_transfer_info(self, app, client):
        """Sender can view transfer metadata."""
        transfer_id = self._create_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.get(f"/transfer/info/{transfer_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["transfer"]["transfer_id"] == transfer_id

    def test_receiver_can_view_transfer_info(self, app, client):
        """Receiver can view transfer metadata."""
        transfer_id = self._create_transfer(app, client)
        login_as(client, BOB["email"])

        response = client.get(f"/transfer/info/{transfer_id}")
        assert response.status_code == 200

    def test_third_party_cannot_view_transfer_info(self, app, client):
        """A third user cannot view transfer metadata."""
        transfer_id = self._create_transfer(app, client)

        # Register Carol
        client.post("/auth/register", json={
            "username": "carol", "email": "carol@example.com",
            "password": "Str0ng!Pass", "confirm_password": "Str0ng!Pass",
        })
        login_as(client, "carol@example.com")

        response = client.get(f"/transfer/info/{transfer_id}")
        assert response.status_code == 403

    def test_sender_can_delete_pending_transfer(self, app, client):
        """Sender can delete a PENDING transfer."""
        transfer_id = self._create_transfer(app, client)
        login_as(client, ALICE["email"])

        response = client.delete(f"/transfer/delete/{transfer_id}")
        assert response.status_code == 200

        with app.app_context():
            assert db.session.get(Transfer, transfer_id) is None

    def test_receiver_cannot_delete_transfer(self, app, client):
        """Receiver cannot delete a transfer they received."""
        transfer_id = self._create_transfer(app, client)
        login_as(client, BOB["email"])

        response = client.delete(f"/transfer/delete/{transfer_id}")
        assert response.status_code == 403
