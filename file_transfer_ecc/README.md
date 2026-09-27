# File Transfer System Using ECC — Backend

A secure web-based file transfer system using **ECC (ECIES/ECDH)** for key encapsulation and **AES-256-GCM** for file encryption.

**Author:** Sk.Md.Junaid (R220424) | RGUKT RK Valley — CSE | 2026–2027

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Cryptography | PyCA `cryptography` (ECDH, AES-GCM, HKDF, PBKDF2) |
| Password Hash | Flask-Bcrypt |
| Auth | Flask-Login |
| Database | SQLite (dev) / MySQL (prod) |

---

## Setup & Installation

### 1. Clone / Navigate to project folder
```bash
cd file_transfer_ecc
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 5. Initialize database
```bash
flask --app run:app db init
flask --app run:app db migrate -m "Initial migration"
flask --app run:app db upgrade
```

### 6. Run the server
```bash
python run.py
```
Server starts at: `http://localhost:5000`

---

## API Endpoints

### Authentication
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Login and create session |
| POST | `/auth/logout` | Destroy session |
| GET | `/auth/me` | Current user info |
| GET | `/auth/profile` | User + ECC public key |
| GET | `/auth/users/list` | List all users (for recipient dropdown) |

### File Transfer
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/transfer/send` | Encrypt and send a file |
| POST | `/transfer/download/<id>` | Decrypt and download a file |
| GET | `/transfer/inbox` | Incoming transfers |
| GET | `/transfer/sent` | Outgoing transfers |
| GET | `/transfer/history` | All transfers (paginated) |
| GET | `/transfer/info/<id>` | Transfer metadata |
| DELETE | `/transfer/delete/<id>` | Delete pending transfer |
| GET | `/transfer/stats` | Transfer statistics |

### Utility
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | API info |
| GET | `/dashboard` | Dashboard data |
| GET | `/health` | Health check |

---

## Cryptographic Design

```
SENDER                          RECEIVER
──────                          ────────
1. Generate AES-256 session key (random 32 bytes)
2. AES-256-GCM encrypt file
3. Compute SHA-256(plaintext)   
4. ECIES encrypt session key:
   - Generate ephemeral ECC key pair
   - ECDH(ephemeral_priv, receiver_pub) → shared_secret
   - HKDF(shared_secret) → wrapping_key
   - AES-GCM(session_key, wrapping_key) → encrypted_session_key
5. Store all metadata to DB
                                6. ECIES decrypt session key:
                                   - ECDH(receiver_priv, ephemeral_pub) → shared_secret
                                   - HKDF(shared_secret) → wrapping_key
                                   - AES-GCM decrypt → session_key
                                7. AES-256-GCM decrypt file
                                8. Verify SHA-256 integrity
                                9. Download original file
```

---

## Running Tests

```bash
# All tests
pytest

# Crypto tests only
pytest tests/test_crypto.py -v

# Auth tests only
pytest tests/test_auth.py -v

# Transfer tests only
pytest tests/test_transfer.py -v

# With coverage
pip install pytest-cov
pytest --cov=app --cov-report=html
```

---

## Project Structure

```
file_transfer_ecc/
├── app/
│   ├── __init__.py        ← App factory
│   ├── config.py          ← Config classes
│   ├── auth/              ← Registration, Login, Logout
│   ├── crypto/            ← ECC, AES, KDF, Hashing
│   ├── transfer/          ← Send, Download, History
│   ├── models/            ← User, ECCKey, Transfer
│   └── main/              ← Dashboard, Health
├── tests/
│   ├── test_crypto.py     ← 30+ crypto unit tests
│   ├── test_auth.py       ← Auth route tests
│   └── test_transfer.py   ← Transfer route tests
├── uploads/               ← Encrypted file storage
├── requirements.txt
├── run.py
└── .env.example
```
