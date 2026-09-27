# PRODUCT REQUIREMENTS DOCUMENT (PRD)
# File Transfer System Using Elliptic Curve Cryptography (ECC)

---

| Field              | Details                                                    |
|--------------------|------------------------------------------------------------|
| Document Type      | Product Requirements Document (PRD)                        |
| Version            | 1.0                                                        |
| Status             | Draft                                                      |
| Project Name       | File Transfer System Using ECC                             |
| Author             | Sk.Md.Junaid (R220424, Roll No: 58)                        |
| Department         | Computer Science and Engineering, RGUKT RK Valley          |
| Academic Year      | 2026–2027                                                  |
| Last Updated       | September 2026                                             |

---

## Version History

| Version | Date           | Author        | Description                        |
|---------|----------------|---------------|------------------------------------|
| 1.0     | September 2026 | Sk.Md.Junaid  | Initial PRD based on approved SRS  |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Goals](#2-product-vision--goals)
3. [Target Users & Personas](#3-target-users--personas)
4. [Problem Statement](#4-problem-statement)
5. [Solution Overview](#5-solution-overview)
6. [User Stories & Acceptance Criteria](#6-user-stories--acceptance-criteria)
7. [Feature Specifications](#7-feature-specifications)
8. [Technical Architecture](#8-technical-architecture)
9. [Database Design](#9-database-design)
10. [API Contract](#10-api-contract)
11. [UI/UX Requirements](#11-uiux-requirements)
12. [Security Model](#12-security-model)
13. [Cryptographic Design](#13-cryptographic-design)
14. [Non-Functional Requirements](#14-non-functional-requirements)
15. [Testing Strategy](#15-testing-strategy)
16. [Success Metrics & KPIs](#16-success-metrics--kpis)
17. [Development Roadmap & Milestones](#17-development-roadmap--milestones)
18. [Risks & Mitigations](#18-risks--mitigations)
19. [Future Scope](#19-future-scope)
20. [Glossary](#20-glossary)

---

## 1. Executive Summary

The **File Transfer System Using Elliptic Curve Cryptography (ECC)** is an academic web-based application that provides end-to-end encrypted file sharing between authenticated users. It demonstrates a practical hybrid cryptographic approach: **ECC** for secure key agreement / session-key protection and **AES** for high-performance file encryption, combined with **SHA-256** integrity verification.

The product solves the real-world problem of insecure file sharing over untrusted networks. By delivering this as a web application (Python/Flask backend), the project demonstrates competency in applied cryptography, secure networking, backend development, database management, and frontend design.

---

## 2. Product Vision & Goals

### 2.1 Vision Statement

> *"To provide any authenticated user with a simple, fast, and cryptographically strong mechanism to share files over a network without fear of interception, tampering, or unauthorized access."*

### 2.2 Product Goals

| # | Goal | Priority |
|---|------|----------|
| G-01 | Demonstrate a working hybrid ECC + AES encryption pipeline | Must Have |
| G-02 | Provide a user-friendly web interface requiring no cryptographic knowledge | Must Have |
| G-03 | Ensure file confidentiality, integrity, and authenticity throughout transfer | Must Have |
| G-04 | Implement user authentication and role-based access control | Must Have |
| G-05 | Maintain a verifiable transfer history per user | Should Have |
| G-06 | Support common file types (documents, images, PDFs, ZIPs, text) | Must Have |
| G-07 | Be deployable on a local server or LAN environment | Must Have |
| G-08 | Achieve clean, maintainable, modular code suitable for academic review | Must Have |
| G-09 | Lay a foundation extensible to cloud storage, digital signatures, and 2FA | Nice to Have |

### 2.3 Out of Scope (v1.0)

- Cloud storage integration (e.g., AWS S3, Google Drive)
- Multi-recipient (group) file transfers
- Digital signatures for non-repudiation
- Two-factor authentication (2FA)
- Expiring / time-limited download links
- Native mobile application
- Real-time notifications (WebSocket/push)

---

## 3. Target Users & Personas

### 3.1 Persona 1 — Alice the Sender

| Field       | Detail                                                              |
|-------------|---------------------------------------------------------------------|
| Name        | Alice                                                               |
| Role        | Registered user who wants to share a confidential file              |
| Tech Level  | Basic — knows how to use a browser, upload a file, and click buttons|
| Goals       | Upload a file, pick a recipient, and know the transfer is secure    |
| Pain Points | Does not understand encryption; worried about file leakage          |
| Motivation  | Needs a simple "upload and send" experience with security guarantee |

### 3.2 Persona 2 — Bob the Receiver

| Field       | Detail                                                              |
|-------------|---------------------------------------------------------------------|
| Name        | Bob                                                                 |
| Role        | Registered user who receives encrypted files from other users       |
| Tech Level  | Basic                                                               |
| Goals       | Log in, see incoming transfers, click download, get the original file|
| Pain Points | Does not want to manage keys manually                               |
| Motivation  | Needs a seamless decryption and download experience                 |

### 3.3 Persona 3 — Prof. Evaluator

| Field       | Detail                                                              |
|-------------|---------------------------------------------------------------------|
| Name        | Faculty Evaluator                                                   |
| Role        | Academic reviewer assessing the project                             |
| Tech Level  | Expert in cryptography and software engineering                     |
| Goals       | Review correctness of ECC/AES implementation, code quality, security|
| Motivation  | Verify that the project meets academic and security standards        |

---

## 4. Problem Statement

### 4.1 Current Problem

Files shared over standard channels (email, messaging apps, plain HTTP) are:

- **Unencrypted in transit** → susceptible to man-in-the-middle (MITM) attacks.
- **Unverified for integrity** → a tampered file may be delivered without detection.
- **Not access-controlled** → anyone with the link/share can access the file.
- **Reliant on third parties** → cloud services may have access to file contents.

### 4.2 Why ECC?

Elliptic Curve Cryptography provides equivalent security to RSA but with **much smaller key sizes**:

| Algorithm | Key Size for ~128-bit security |
|-----------|-------------------------------|
| RSA       | 3072 bits                     |
| ECC       | 256 bits                      |
| AES       | 128 bits                      |

Smaller keys → **faster computation**, **less bandwidth**, **better for constrained environments**.

### 4.3 Why Hybrid (ECC + AES)?

- **ECC alone** is slow for large data.
- **AES alone** has no built-in secure key exchange.
- **Hybrid**: AES encrypts the file (fast, symmetric), ECC protects the AES session key (secure, asymmetric).

---

## 5. Solution Overview

### 5.1 High-Level Architecture

```
┌────────────┐       HTTPS / Local Network       ┌────────────┐
│   SENDER   │ ──────────────────────────────── │  RECEIVER  │
│  (Browser) │                                   │  (Browser) │
└─────┬──────┘                                   └──────┬─────┘
      │                                                 │
      ▼                                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                                                              │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Auth Module │  │  Crypto Module  │  │ Transfer Mgr  │  │
│  │  (Register,  │  │  (ECC + AES +   │  │ (Upload, Store│  │
│  │   Login)     │  │   SHA-256)      │  │  Download)    │  │
│  └──────────────┘  └─────────────────┘  └───────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               DATABASE (SQLite / MySQL)               │   │
│  │  Users | ECC Keys | Transfers | Transfer Metadata    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 End-to-End Transfer Flow

```
SENDER SIDE                          SYSTEM                        RECEIVER SIDE
─────────────                       ────────                      ─────────────────
1. Login ──────────────────────► Authenticate
2. Select File ─────────────►  Validate file type/size
3. Select Recipient ────────►  Lookup receiver's ECC public key
                                4. Generate AES-256 session key (random)
                                5. Encrypt file with AES-256-GCM
                                6. Encrypt AES key using receiver's ECC public key
                                   (ECDH + KDF or ECIES)
                                7. Compute SHA-256 hash of plaintext file
                                8. Store: encrypted file + encrypted key + hash
                                9. Record transfer metadata in DB
                                                              10. Login ──────────►
                                                              11. View inbox ─────►
                                                                  Validate access
                                                              12. Request decrypt ►
                                                                  Recover AES key
                                                                  using receiver's
                                                                  ECC private key
                                                                  Decrypt file
                                                                  Verify SHA-256
                                                              13. Download file ◄──
```

---

## 6. User Stories & Acceptance Criteria

### 6.1 Authentication Stories

#### US-01: User Registration

**As a** new user,
**I want to** create an account with a username, email, and password,
**So that** I can access the secure file transfer system.

**Acceptance Criteria:**

- [ ] Registration form collects: username, email, password, confirm password.
- [ ] Password must be at least 8 characters with at least one uppercase, one number, and one special character.
- [ ] System rejects duplicate usernames or emails with a clear error message.
- [ ] On successful registration, system auto-generates an ECC key pair and associates it with the user.
- [ ] Private key is stored securely (encrypted with user's password-derived key or stored server-side with access control).
- [ ] User is redirected to login page with a success message.

---

#### US-02: User Login

**As a** registered user,
**I want to** log in with my credentials,
**So that** I can access my dashboard and perform secure file transfers.

**Acceptance Criteria:**

- [ ] Login form collects: username/email and password.
- [ ] System validates credentials against hashed password (bcrypt/argon2).
- [ ] On success: session is created and user is redirected to dashboard.
- [ ] On failure: generic error message shown (no disclosure of which field is wrong — security best practice).
- [ ] Session expires after a configurable idle timeout (default: 30 minutes).

---

#### US-03: User Logout

**As a** logged-in user,
**I want to** log out,
**So that** my session is terminated securely.

**Acceptance Criteria:**

- [ ] Logout button is visible on all authenticated pages.
- [ ] On logout, server-side session is invalidated.
- [ ] User is redirected to the login page.
- [ ] Browser back-button does not return to authenticated pages after logout.

---

### 6.2 Sender Stories

#### US-04: Select and Upload File for Transfer

**As a** sender,
**I want to** select a file from my device and choose a recipient,
**So that** the system can securely encrypt and transfer it.

**Acceptance Criteria:**

- [ ] File selection via drag-and-drop or file picker.
- [ ] Supported formats: `.pdf`, `.docx`, `.xlsx`, `.txt`, `.png`, `.jpg`, `.jpeg`, `.zip`, `.mp4` and other common types.
- [ ] Maximum file size enforced (configurable, default: 100 MB).
- [ ] Recipient selected from a dropdown/searchable list of registered users.
- [ ] User cannot select themselves as the recipient.
- [ ] File name, size, and type are displayed before confirming transfer.

---

#### US-05: Initiate Secure Transfer

**As a** sender,
**I want to** click "Send Securely" after selecting a file and recipient,
**So that** the system encrypts and transmits the file without my manual involvement in cryptographic steps.

**Acceptance Criteria:**

- [ ] On confirmation, system:
  - Generates a 256-bit AES session key (random).
  - Encrypts the file using AES-256-GCM.
  - Computes SHA-256 hash of the plaintext file.
  - Retrieves receiver's ECC public key.
  - Encrypts the AES session key using ECC (ECIES or ECDH + KDF).
  - Stores encrypted file, encrypted key, GCM auth tag, IV/nonce, and SHA-256 hash.
  - Records transfer metadata in the database.
- [ ] Progress indicator shown during encryption and upload.
- [ ] Success message displayed on completion with transfer ID.
- [ ] Failure results in a clear error message; no partial/corrupted transfer is recorded as successful.

---

#### US-06: View Sent Transfers

**As a** sender,
**I want to** view a history of files I have sent,
**So that** I can track my outgoing transfers.

**Acceptance Criteria:**

- [ ] Sent transfers listed with: file name, recipient username, date/time, transfer status, transfer ID.
- [ ] List is paginated (default: 10 per page).
- [ ] Transfers sorted by most recent first.
- [ ] Sender can see whether the recipient has downloaded the file.

---

### 6.3 Receiver Stories

#### US-07: View Incoming Transfers

**As a** receiver,
**I want to** see a list of files sent to me,
**So that** I know when I have received a secure transfer.

**Acceptance Criteria:**

- [ ] Inbox shows: sender username, original file name, date/time sent, transfer status (Pending / Downloaded).
- [ ] Transfers are shown only to the intended recipient.
- [ ] Unread/new transfers are visually highlighted.

---

#### US-08: Decrypt and Download File

**As a** receiver,
**I want to** click "Decrypt & Download" on an incoming transfer,
**So that** the system recovers the original file and lets me download it.

**Acceptance Criteria:**

- [ ] System performs:
  - Retrieves encrypted AES session key and encrypted file for the transfer.
  - Recovers AES session key using receiver's ECC private key.
  - Decrypts file using AES-256-GCM (including auth tag verification).
  - Verifies SHA-256 hash of decrypted file against stored hash.
- [ ] If integrity check passes: original file is streamed to the user's browser for download.
- [ ] If integrity check fails: download is blocked; error message "File integrity verification failed" is shown.
- [ ] Transfer status updated to "Downloaded" with timestamp.
- [ ] No plaintext file content is persisted on the server after delivery.

---

#### US-09: Deny Unauthorized Access

**As a** system,
**I must** prevent any user other than the intended recipient from accessing or decrypting a transfer,
**So that** file confidentiality is maintained.

**Acceptance Criteria:**

- [ ] Any attempt by a non-recipient user to access a transfer ID returns HTTP 403 Forbidden.
- [ ] The encrypted file is not downloadable by anyone other than the intended recipient.
- [ ] The encrypted AES session key is tied to the recipient's ECC public key — it is mathematically unusable by others.

---

### 6.4 Management Stories

#### US-10: Transfer History

**As a** user,
**I want to** see a complete history of my sent and received transfers,
**So that** I can audit and manage my file sharing activity.

**Acceptance Criteria:**

- [ ] A unified History page shows both sent and received transfers.
- [ ] Filters: by date range, by transfer status, by direction (sent/received).
- [ ] Each row is expandable to show: file type, file size, transfer ID, encryption algorithm used.

---

#### US-11: ECC Key Management (View Public Key)

**As a** user,
**I want to** view my ECC public key,
**So that** I can verify or share it if needed.

**Acceptance Criteria:**

- [ ] Profile/Settings page displays the user's ECC public key in PEM or hex format.
- [ ] Private key is NEVER displayed in the UI.
- [ ] Option to regenerate the ECC key pair (with a warning that existing encrypted transfers cannot be recovered after regeneration).

---

## 7. Feature Specifications

### 7.1 Feature: User Authentication Module

| Field              | Detail                                                             |
|--------------------|--------------------------------------------------------------------|
| Feature ID         | F-01                                                               |
| Priority           | P0 — Critical                                                      |
| Description        | Registration, login, logout, session management                    |
| Key Components     | Registration form, login form, password hashing, session handling  |
| Password Hashing   | bcrypt (cost factor >= 12) or Argon2id                             |
| Session Storage    | Flask server-side sessions (flask-session) with signed cookies     |
| Password Policy    | Min 8 chars, 1 uppercase, 1 digit, 1 special character            |
| Dependencies       | Flask, Flask-Login, Flask-WTF, bcrypt/argon2-cffi                  |

---

### 7.2 Feature: ECC Key Generation & Management Module

| Field             | Detail                                                              |
|-------------------|---------------------------------------------------------------------|
| Feature ID        | F-02                                                                |
| Priority          | P0 — Critical                                                       |
| Description       | Auto-generate ECC key pair on user registration; manage storage     |
| ECC Curve         | NIST P-256 (secp256r1) or Curve25519 (X25519 for ECDH)             |
| Key Generation    | On registration, system generates (private_key, public_key) pair    |
| Public Key Storage| Stored in `users` table (DB), associated with user ID              |
| Private Key Storage| Server-side: encrypted with AES-256 using a key derived from the user's password (PBKDF2/Argon2). Stored in `ecc_keys` table. |
| Key Format        | PEM or DER encoded                                                  |
| Library           | Python `cryptography` library (hazmat layer) or `tinyec`           |

---

### 7.3 Feature: File Encryption Module (AES-256-GCM)

| Field               | Detail                                                            |
|---------------------|-------------------------------------------------------------------|
| Feature ID          | F-03                                                              |
| Priority            | P0 — Critical                                                     |
| Description         | Encrypt uploaded file using AES-256-GCM before storage/transfer   |
| Algorithm           | AES-256-GCM (provides confidentiality + authentication)           |
| Key Size            | 256 bits (32 bytes), randomly generated per transfer              |
| Nonce / IV          | 96-bit (12 bytes), randomly generated per transfer                |
| Auth Tag            | 128-bit (16 bytes), stored alongside ciphertext                   |
| Integrity           | SHA-256 hash of plaintext computed before encryption              |
| Library             | Python `cryptography` — `Cipher`, `algorithms.AES`, `modes.GCM`  |
| Storage             | Encrypted file stored in `uploads/` directory on server           |

---

### 7.4 Feature: ECC-Based Session Key Protection Module

| Field               | Detail                                                             |
|---------------------|--------------------------------------------------------------------|
| Feature ID          | F-04                                                               |
| Priority            | P0 — Critical                                                      |
| Description         | Use ECC to securely protect the AES session key for the recipient  |
| Approach            | ECIES (Elliptic Curve Integrated Encryption Scheme) or ECDH + KDF  |
| ECIES Steps (Send)  | 1. Generate ephemeral ECC key pair. 2. ECDH with ephemeral private + receiver's public key -> shared secret. 3. KDF (HKDF-SHA256) -> wrapping key. 4. Encrypt AES session key with wrapping key (AES-GCM). 5. Store: ephemeral public key + encrypted session key + auth tag. |
| ECIES Steps (Recv)  | 1. Retrieve ephemeral public key + encrypted session key. 2. ECDH with receiver's ECC private key + ephemeral public key -> shared secret. 3. KDF -> wrapping key. 4. Decrypt AES session key. |
| Library             | Python `cryptography` — ECDH, HKDF                                |

---

### 7.5 Feature: Secure File Transfer Module

| Field             | Detail                                                              |
|-------------------|---------------------------------------------------------------------|
| Feature ID        | F-05                                                               |
| Priority          | P0 — Critical                                                       |
| Description       | Handle uploading, storing, and retrieving encrypted files           |
| Upload            | Multipart form upload; file saved as encrypted binary on server    |
| File Naming       | Stored with UUID-based name; original name in DB metadata          |
| Storage Path      | `uploads/<uuid>.enc`                                               |
| Access Control    | Only the intended recipient's authenticated session can trigger decrypt-and-download |
| Download          | File decrypted in memory, streamed as HTTP response attachment      |
| Cleanup           | Option to delete server-side file after successful download         |

---

### 7.6 Feature: Integrity Verification Module

| Field             | Detail                                                             |
|-------------------|--------------------------------------------------------------------|
| Feature ID        | F-06                                                               |
| Priority          | P0 — Critical                                                      |
| Description       | Verify that the decrypted file matches the original using SHA-256  |
| Hash Computed     | Before encryption, on the sender side (server-side after upload)   |
| Hash Stored       | In `transfers` table, linked to transfer ID                        |
| Hash Verified     | After AES-GCM decryption, recompute SHA-256 and compare           |
| Note              | AES-GCM auth tag provides ciphertext integrity; SHA-256 provides plaintext integrity confirmation |
| Failure Action    | Block download; log the event; show error to receiver              |

---

### 7.7 Feature: Transfer History Module

| Field             | Detail                                                             |
|-------------------|--------------------------------------------------------------------|
| Feature ID        | F-07                                                               |
| Priority          | P1 — High                                                          |
| Description       | Store and display metadata about all transfers                     |
| Metadata Stored   | Transfer ID, sender ID, receiver ID, original filename, file size, file type, timestamp sent, timestamp downloaded, status |
| UI                | Paginated table view; filterable by status and date               |

---

### 7.8 Feature: Dashboard

| Field             | Detail                                                             |
|-------------------|--------------------------------------------------------------------|
| Feature ID        | F-08                                                               |
| Priority          | P1 — High                                                          |
| Description       | Main landing page after login showing summary and quick actions    |
| Contents          | Welcome message, pending received transfers count, recent activity, quick-send button |

---

## 8. Technical Architecture

### 8.1 Technology Stack

| Layer           | Technology                        | Version     |
|-----------------|-----------------------------------|-------------|
| Language        | Python                            | 3.10+       |
| Web Framework   | Flask                             | 3.x         |
| ORM             | Flask-SQLAlchemy                  | 3.x         |
| Database        | SQLite (dev) / MySQL (production) | —           |
| Crypto Library  | `cryptography` (PyCA)             | 42.x+       |
| Password Hash   | bcrypt / argon2-cffi              | Latest      |
| Forms           | Flask-WTF / WTForms               | Latest      |
| Session Mgmt    | Flask-Login                       | Latest      |
| Frontend        | HTML5, CSS3, Vanilla JavaScript   | —           |
| Icons           | Font Awesome (CDN)                | 6.x         |
| Fonts           | Google Fonts (Inter / Poppins)    | —           |
| Version Control | Git / GitHub                      | —           |

### 8.2 Directory Structure

```
file_transfer_ecc/
│
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration (Dev/Prod/Test)
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py            # /register, /login, /logout
│   │   ├── forms.py             # RegistrationForm, LoginForm
│   │   └── utils.py             # Password hashing helpers
│   │
│   ├── crypto/
│   │   ├── __init__.py
│   │   ├── ecc.py               # ECC key generation, ECDH, ECIES
│   │   ├── aes.py               # AES-256-GCM encrypt/decrypt
│   │   ├── hashing.py           # SHA-256 helpers
│   │   └── kdf.py               # HKDF / key derivation
│   │
│   ├── transfer/
│   │   ├── __init__.py
│   │   ├── routes.py            # /send, /inbox, /download/<id>, /history
│   │   ├── forms.py             # TransferForm
│   │   └── utils.py             # File handling, storage
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── ecc_key.py           # ECC key model
│   │   └── transfer.py          # Transfer model
│   │
│   ├── templates/
│   │   ├── base.html            # Base layout
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard.html
│   │   ├── transfer/
│   │   │   ├── send.html
│   │   │   ├── inbox.html
│   │   │   └── history.html
│   │   └── profile.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── images/
│
├── uploads/                     # Encrypted file storage (gitignored)
├── instance/
│   └── config.py                # Instance-specific secrets
├── tests/
│   ├── test_auth.py
│   ├── test_crypto.py
│   └── test_transfer.py
├── requirements.txt
├── run.py                       # Entry point
└── README.md
```

### 8.3 Request-Response Flow

```
Browser --POST /send--> Flask Router --> Transfer Route Handler
                                               |
                              ┌────────────────▼───────────────────┐
                              │         Transfer Service            │
                              │  1. Validate form & file           │
                              │  2. Read file bytes                 │
                              │  3. Compute SHA-256(plaintext)      │
                              │  4. Generate AES session key (rand) │
                              │  5. AES-256-GCM encrypt file        │
                              │  6. Lookup receiver's ECC pub key   │
                              │  7. ECIES: encrypt AES session key  │
                              │  8. Save .enc file to uploads/      │
                              │  9. Insert transfer record in DB    │
                              └────────────────────────────────────┘
                                               |
                              <---- HTTP 200 + success message -----
```

---

## 9. Database Design

### 9.1 Entity Relationship Diagram (ERD)

```
┌─────────────────────┐          ┌──────────────────────────┐
│        USERS        │          │         ECC_KEYS          │
├─────────────────────┤          ├──────────────────────────┤
│ PK  user_id (INT)   │◄────────►│ PK  key_id (INT)         │
│     username (STR)  │  1 : 1  │ FK  user_id (INT)         │
│     email (STR)     │          │     public_key (TEXT)     │
│     password_hash   │          │     private_key_enc (TEXT)│
│     created_at      │          │     curve (STR)           │
│     is_active (BOOL)│          │     created_at            │
└─────────────────────┘          └──────────────────────────┘
          │
          │ 1 : N (sender)
          │ 1 : N (receiver)
          ▼
┌──────────────────────────────────────────────────────┐
│                      TRANSFERS                        │
├──────────────────────────────────────────────────────┤
│ PK  transfer_id (STR / UUID)                         │
│ FK  sender_id (INT) -> users.user_id                 │
│ FK  receiver_id (INT) -> users.user_id               │
│     original_filename (STR)                          │
│     file_size_bytes (INT)                            │
│     file_mime_type (STR)                             │
│     stored_filename (STR)      <- UUID.enc path      │
│     plaintext_sha256 (STR)     <- integrity hash     │
│     encrypted_session_key (TEXT) <- ECIES ciphertext │
│     ephemeral_public_key (TEXT) <- for ECDH recovery │
│     aes_nonce (STR)            <- GCM nonce (hex)    │
│     aes_auth_tag (STR)         <- GCM tag (hex)      │
│     status (ENUM: PENDING, DOWNLOADED, FAILED)       │
│     sent_at (DATETIME)                               │
│     downloaded_at (DATETIME, nullable)               │
└──────────────────────────────────────────────────────┘
```

### 9.2 Table Definitions

#### Table: `users`

| Column        | Type         | Constraints                  | Description                  |
|---------------|--------------|------------------------------|------------------------------|
| user_id       | INTEGER      | PK, AUTO_INCREMENT           | Unique user identifier       |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL             | Display name                 |
| email         | VARCHAR(150) | UNIQUE, NOT NULL             | Login email                  |
| password_hash | VARCHAR(255) | NOT NULL                     | bcrypt/argon2 hash           |
| created_at    | DATETIME     | DEFAULT CURRENT_TIMESTAMP    | Account creation time        |
| is_active     | BOOLEAN      | DEFAULT TRUE                 | Account active flag          |

#### Table: `ecc_keys`

| Column            | Type        | Constraints        | Description                          |
|-------------------|-------------|--------------------|--------------------------------------|
| key_id            | INTEGER     | PK, AUTO_INCREMENT | Key record ID                        |
| user_id           | INTEGER     | FK -> users, UNIQUE| Associated user                      |
| public_key        | TEXT        | NOT NULL           | PEM-encoded ECC public key           |
| private_key_enc   | TEXT        | NOT NULL           | AES-encrypted PEM ECC private key    |
| curve             | VARCHAR(20) | NOT NULL           | e.g., "P-256" or "X25519"           |
| created_at        | DATETIME    | DEFAULT NOW        | Key generation timestamp             |

#### Table: `transfers`

| Column                | Type         | Constraints     | Description                              |
|-----------------------|--------------|-----------------|------------------------------------------|
| transfer_id           | VARCHAR(36)  | PK (UUID)       | Unique transfer identifier               |
| sender_id             | INTEGER      | FK -> users     | Sender's user ID                         |
| receiver_id           | INTEGER      | FK -> users     | Receiver's user ID                       |
| original_filename     | VARCHAR(255) | NOT NULL        | Original file name                       |
| file_size_bytes       | BIGINT       | NOT NULL        | File size before encryption              |
| file_mime_type        | VARCHAR(100) |                 | MIME type of original file               |
| stored_filename       | VARCHAR(255) | NOT NULL        | Server-side UUID-based filename          |
| plaintext_sha256      | VARCHAR(64)  | NOT NULL        | SHA-256 hex digest of plaintext file     |
| encrypted_session_key | TEXT         | NOT NULL        | ECIES-encrypted AES key (hex/base64)     |
| ephemeral_public_key  | TEXT         | NOT NULL        | Ephemeral ECC public key (for ECDH)      |
| aes_nonce             | VARCHAR(32)  | NOT NULL        | AES-GCM nonce (hex, 12 bytes)            |
| aes_auth_tag          | VARCHAR(32)  | NOT NULL        | AES-GCM auth tag (hex, 16 bytes)         |
| status                | VARCHAR(20)  | DEFAULT PENDING | PENDING / DOWNLOADED / FAILED            |
| sent_at               | DATETIME     | DEFAULT NOW     | Transfer creation timestamp              |
| downloaded_at         | DATETIME     | NULLABLE        | Download completion timestamp            |

---

## 10. API Contract

### 10.1 Authentication Endpoints

#### POST /auth/register

**Request:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "SecureP@ss1",
  "confirm_password": "SecureP@ss1"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Account created successfully. Please log in.",
  "user_id": 1
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Username already exists."
}
```

---

#### POST /auth/login

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "SecureP@ss1"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logged in successfully.",
  "user": {
    "user_id": 1,
    "username": "alice"
  }
}
```

---

#### POST /auth/logout

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Logged out successfully."
}
```

---

### 10.2 Transfer Endpoints

#### POST /transfer/send

**Request:** `multipart/form-data`

| Field       | Type   | Description                     |
|-------------|--------|---------------------------------|
| file        | File   | File to be transferred          |
| receiver_id | int    | Target recipient's user ID      |

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "File transferred securely.",
  "transfer_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### GET /transfer/inbox

**Response (200 OK):**
```json
{
  "status": "success",
  "transfers": [
    {
      "transfer_id": "550e8400-...",
      "sender_username": "alice",
      "original_filename": "report.pdf",
      "file_size_bytes": 204800,
      "sent_at": "2026-09-27T10:00:00",
      "status": "PENDING"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

#### POST /transfer/download/{transfer_id}

**Response (200 OK):** Binary file stream with headers:
```
Content-Disposition: attachment; filename="report.pdf"
Content-Type: application/pdf
```

**Response (403 Forbidden):**
```json
{
  "status": "error",
  "message": "You are not authorized to access this transfer."
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "status": "error",
  "message": "File integrity verification failed. Download rejected."
}
```

---

#### GET /transfer/history

**Query Parameters:** `?page=1&per_page=10&direction=all&status=all`

**Response (200 OK):**
```json
{
  "status": "success",
  "transfers": [...],
  "total": 25,
  "page": 1,
  "pages": 3
}
```

---

#### GET /users/list

**Response (200 OK):**
```json
{
  "status": "success",
  "users": [
    { "user_id": 2, "username": "bob" },
    { "user_id": 3, "username": "carol" }
  ]
}
```
> *Note: Excludes the currently logged-in user.*

---

## 11. UI/UX Requirements

### 11.1 Design Principles

- **Simplicity First:** Users should complete a file transfer in 3 clicks after login.
- **Security Transparency:** Show encryption status but hide cryptographic complexity.
- **Feedback Rich:** Every action produces a clear success/error/loading state.
- **Responsive:** Works on 1280px+ desktop screens; basic usability on 768px tablets.

### 11.2 Color Palette

| Role              | Color         | Hex       |
|-------------------|---------------|-----------|
| Primary           | Deep Indigo   | `#4F46E5` |
| Primary Light     | Indigo 400    | `#818CF8` |
| Accent            | Cyan          | `#06B6D4` |
| Success           | Emerald       | `#10B981` |
| Warning           | Amber         | `#F59E0B` |
| Danger / Error    | Rose          | `#F43F5E` |
| Background Dark   | Slate 900     | `#0F172A` |
| Surface           | Slate 800     | `#1E293B` |
| Text Primary      | White         | `#F8FAFC` |
| Text Secondary    | Slate 400     | `#94A3B8` |

### 11.3 Page Inventory

| Page          | Route              | Description                                      |
|---------------|--------------------|--------------------------------------------------|
| Landing       | `/`                | Project intro, login/register CTA                |
| Register      | `/auth/register`   | Registration form                                |
| Login         | `/auth/login`      | Login form                                       |
| Dashboard     | `/dashboard`       | Overview: pending count, recent transfers, quick-send |
| Send File     | `/transfer/send`   | File picker + recipient selector + send button   |
| Inbox         | `/transfer/inbox`  | List of incoming transfers with decrypt-download |
| History       | `/transfer/history`| All transfers (sent + received) with filters     |
| Profile       | `/profile`         | User info, public key display, settings          |

### 11.4 Key UI Components

- **Secure Transfer Badge:** A lock icon with "AES-256-GCM + ECC Protected" label shown on every transfer card.
- **Progress Bar:** Shown during encryption and upload, with step labels: Encrypting -> Uploading -> Complete.
- **Status Pills:** `PENDING` (amber), `DOWNLOADED` (green), `FAILED` (red).
- **Drag-and-Drop Zone:** Large dropzone area with dashed border, file icon, and "Drop your file here" label.
- **Transfer Card:** File icon + name + size + sender + date + status pill + action button.

---

## 12. Security Model

### 12.1 Threat Model

| Threat                        | Attack Vector                             | Mitigation                                         |
|-------------------------------|-------------------------------------------|----------------------------------------------------|
| Eavesdropping                 | Network packet sniffing                   | HTTPS in deployment; AES-256-GCM encryption of all file data |
| MITM (Man-in-the-Middle)      | Intercepting session key or file          | ECC key exchange; TLS; integrity verification      |
| Unauthorized file access      | Guessing transfer ID or direct DB access  | Access control checks on all endpoints; UUID transfer IDs |
| File tampering                | Modifying encrypted bytes in transit/storage | AES-GCM auth tag + SHA-256 plaintext hash       |
| Credential theft              | Brute-force, credential stuffing          | bcrypt/argon2 hashing; login rate limiting         |
| SQL Injection                 | Malicious input in forms                  | SQLAlchemy ORM parameterized queries               |
| Cross-Site Scripting (XSS)    | Malicious JS in file name or input        | Jinja2 auto-escaping; Content-Security-Policy header |
| CSRF                          | Forged requests from malicious sites      | Flask-WTF CSRF tokens on all forms                 |
| Private key theft             | Access to server storage                  | Private keys encrypted at rest with user-derived key |
| Path traversal                | Malicious filename for directory traversal| `werkzeug.utils.secure_filename`; UUID-based storage names |

### 12.2 Security Controls Summary

| Control                  | Implementation                                              |
|--------------------------|-------------------------------------------------------------|
| Transport Security       | HTTPS (TLS 1.2+) recommended for deployment                 |
| Authentication           | Session-based with Flask-Login                              |
| Password Storage         | bcrypt (cost=12) or Argon2id                                |
| Input Validation         | WTForms validators + server-side checks                     |
| CSRF Protection          | Flask-WTF CSRFProtect on all state-changing requests        |
| File Upload Security     | MIME type validation, extension whitelist, size limit       |
| Secure Headers           | `X-Content-Type-Options`, `X-Frame-Options`, `CSP`          |
| Encrypted Storage        | All files stored as AES-256-GCM ciphertext                  |
| Key Protection           | Private keys stored AES-encrypted; never exposed in UI      |
| Access Control           | User-session check + DB ownership check on every transfer   |

---

## 13. Cryptographic Design

### 13.1 Algorithm Selection Rationale

| Algorithm     | Role                          | Justification                                         |
|---------------|-------------------------------|-------------------------------------------------------|
| ECDH (P-256)  | Key agreement                 | 128-bit security, standardized (NIST), small key size |
| HKDF-SHA256   | Key derivation from ECDH      | Standard, secure KDF; salt + info context binding     |
| AES-256-GCM   | File encryption               | Authenticated encryption; fast; NIST approved         |
| SHA-256       | Plaintext integrity           | Standard, collision-resistant hash                    |
| bcrypt/Argon2 | Password hashing              | Memory-hard; resistant to GPU brute-force             |
| PBKDF2/Argon2 | Key derivation from password  | Used to derive wrapping key for private key storage   |

### 13.2 Encryption Flow (Technical Detail)

#### Sender Side — Encrypting File for Bob

```python
import os, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Step 1: Generate AES session key
session_key = os.urandom(32)          # 256-bit

# Step 2: Encrypt file with AES-256-GCM
nonce = os.urandom(12)                # 96-bit nonce
aesgcm = AESGCM(session_key)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)
# ciphertext includes the 16-byte GCM auth tag appended

# Step 3: Compute SHA-256 of plaintext
sha256_hash = hashlib.sha256(plaintext).hexdigest()

# Step 4: ECIES — Encrypt session key for Bob
# 4a. Generate ephemeral key pair
ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
ephemeral_public_key = ephemeral_private_key.public_key()

# 4b. ECDH with Bob's public key
shared_secret = ephemeral_private_key.exchange(ec.ECDH(), bob_public_key)

# 4c. HKDF to derive wrapping key
wrapping_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'file-transfer-key-wrap'
).derive(shared_secret)

# 4d. Wrap (encrypt) the AES session key
wrap_nonce = os.urandom(12)
aesgcm_wrap = AESGCM(wrapping_key)
encrypted_session_key = aesgcm_wrap.encrypt(wrap_nonce, session_key, None)

# Step 5: Store in DB:
# ephemeral_public_key (PEM), encrypted_session_key (hex),
# wrap_nonce (hex), nonce (hex), sha256_hash, ciphertext (file)
```

#### Receiver Side — Decrypting File

```python
# Step 1: Recover wrapping key via ECDH
shared_secret = bob_private_key.exchange(ec.ECDH(), ephemeral_public_key)
wrapping_key = HKDF(
    algorithm=hashes.SHA256(), length=32,
    salt=None, info=b'file-transfer-key-wrap'
).derive(shared_secret)

# Step 2: Unwrap AES session key
session_key = AESGCM(wrapping_key).decrypt(wrap_nonce, encrypted_session_key, None)

# Step 3: Decrypt file
plaintext = AESGCM(session_key).decrypt(nonce, ciphertext, None)
# GCM automatically verifies auth tag; raises InvalidTag on tampering

# Step 4: Verify SHA-256
computed_hash = hashlib.sha256(plaintext).hexdigest()
assert computed_hash == stored_sha256_hash  # Integrity check
```

---

## 14. Non-Functional Requirements

### 14.1 Performance

| Metric                              | Target                                      |
|-------------------------------------|---------------------------------------------|
| File encryption time (10 MB file)   | < 2 seconds                                 |
| File upload time (10 MB, LAN)       | < 10 seconds                                |
| Key generation time                 | < 1 second                                  |
| Page load time (dashboard)          | < 3 seconds                                 |
| Maximum supported file size         | 100 MB (configurable)                       |
| Concurrent users (dev/local)        | 10–20 (single-threaded Flask dev server)    |

### 14.2 Reliability

- System shall report errors without presenting a failed transfer as successful.
- All cryptographic operations shall be wrapped in try/except; failures return clear error messages.
- Database transactions shall be atomic (rollback on failure).

### 14.3 Usability

- New users shall complete registration in under 2 minutes.
- Sending a file shall require no more than 4 steps: login -> select file -> select recipient -> send.
- All error messages shall be user-friendly (no raw stack traces in UI).

### 14.4 Compatibility

- Tested on: Chrome 120+, Firefox 120+, Edge 120+.
- Minimum screen width: 768px.
- Python 3.10+ required for server.

### 14.5 Maintainability

- Code organized into separate modules: `auth`, `crypto`, `transfer`, `models`.
- All cryptographic logic isolated in the `crypto/` module.
- Code documented with docstrings.
- Unit tests cover all crypto functions and core routes.

---

## 15. Testing Strategy

### 15.1 Test Categories

| Category              | Scope                                        | Tools                     |
|-----------------------|----------------------------------------------|---------------------------|
| Unit Tests            | Crypto functions, utility functions          | pytest                    |
| Integration Tests     | API routes, DB interactions                  | pytest + Flask test client|
| Security Tests        | Auth bypass, unauthorized access, CSRF       | Manual + pytest           |
| Cryptographic Tests   | Encrypt -> Decrypt round-trip correctness    | pytest                    |
| UI/UX Tests           | Manual browser testing                       | Chrome DevTools           |

### 15.2 Key Test Cases

#### Cryptographic Tests

| Test ID  | Test Case                                       | Expected Result                             |
|----------|-------------------------------------------------|---------------------------------------------|
| TC-CR-01 | AES-256-GCM encrypt then decrypt                | Plaintext recovered matches original        |
| TC-CR-02 | AES-GCM with tampered ciphertext                | `InvalidTag` exception raised               |
| TC-CR-03 | ECIES: encrypt session key -> decrypt session key| Session key recovered correctly            |
| TC-CR-04 | ECIES with wrong private key                    | Decryption fails / wrong session key        |
| TC-CR-05 | SHA-256 hash consistency                        | Same file always produces same hash         |
| TC-CR-06 | SHA-256 hash of tampered file                   | Different hash detected                     |

#### Authentication Tests

| Test ID  | Test Case                          | Expected Result                     |
|----------|------------------------------------|-------------------------------------|
| TC-AU-01 | Register with valid data           | Account created, ECC keys generated |
| TC-AU-02 | Register with duplicate email      | Error: email already exists         |
| TC-AU-03 | Login with correct credentials     | Session created, redirect dashboard |
| TC-AU-04 | Login with wrong password          | Generic error, no session created   |
| TC-AU-05 | Access protected page without login| Redirect to login page              |

#### Transfer Tests

| Test ID  | Test Case                                      | Expected Result                              |
|----------|------------------------------------------------|----------------------------------------------|
| TC-TR-01 | Send file to valid recipient                   | Transfer record created; file encrypted      |
| TC-TR-02 | Download as intended recipient                 | File decrypted, integrity verified, downloaded|
| TC-TR-03 | Download as non-recipient                      | HTTP 403 returned                            |
| TC-TR-04 | Download with tampered stored file             | Integrity failure; download blocked          |
| TC-TR-05 | Upload file exceeding size limit               | HTTP 413 / error message                     |
| TC-TR-06 | Upload disallowed file type                    | Validation error message                     |

---

## 16. Success Metrics & KPIs

| Metric                                         | Target / Definition                              |
|------------------------------------------------|--------------------------------------------------|
| End-to-end transfer success rate               | >= 99% of valid transfers complete without error |
| Cryptographic correctness                      | 100% encrypt-decrypt round-trip accuracy         |
| Integrity violation detection rate             | 100% of tampered files detected and rejected     |
| Unauthorized access prevention rate            | 100% of non-recipient access attempts blocked    |
| Registration completion rate (academic demo)   | All test users register successfully             |
| UI task completion (send file)                 | <= 4 clicks from dashboard to confirmed send     |
| Academic evaluation score                      | Pass all academic review checkpoints             |

---

## 17. Development Roadmap & Milestones

### Phase 1 — Foundation (Week 1–2)

| Task                                              | Status |
|---------------------------------------------------|--------|
| Set up project structure and Git repository       | [ ]    |
| Configure Flask app factory and config files      | [ ]    |
| Set up SQLite DB with SQLAlchemy models           | [ ]    |
| Implement User model and auth module              | [ ]    |
| Implement registration (with ECC key generation)  | [ ]    |
| Implement login / logout / session management     | [ ]    |

### Phase 2 — Cryptographic Core (Week 2–3)

| Task                                              | Status |
|---------------------------------------------------|--------|
| Implement AES-256-GCM encrypt/decrypt module      | [ ]    |
| Implement ECC key generation (P-256)              | [ ]    |
| Implement ECIES (ECDH + HKDF + AES-GCM wrap)     | [ ]    |
| Implement SHA-256 integrity hashing               | [ ]    |
| Write unit tests for all crypto functions         | [ ]    |
| Verify encrypt -> decrypt round-trip correctness  | [ ]    |

### Phase 3 — Transfer System (Week 3–4)

| Task                                              | Status |
|---------------------------------------------------|--------|
| Implement file upload route and form              | [ ]    |
| Integrate encryption pipeline with upload         | [ ]    |
| Store transfer metadata in DB                     | [ ]    |
| Implement inbox route and display                 | [ ]    |
| Implement download/decrypt route                  | [ ]    |
| Implement integrity check on download             | [ ]    |
| Implement transfer history route                  | [ ]    |

### Phase 4 — Frontend & UI (Week 4–5)

| Task                                              | Status |
|---------------------------------------------------|--------|
| Design and implement base HTML template           | [ ]    |
| Build login and registration pages                | [ ]    |
| Build dashboard page                              | [ ]    |
| Build send file page (drag-and-drop + form)       | [ ]    |
| Build inbox page with transfer cards              | [ ]    |
| Build history page with filters                   | [ ]    |
| Build profile/settings page                       | [ ]    |
| Apply CSS styling (color palette, animations)     | [ ]    |

### Phase 5 — Testing & Polish (Week 5–6)

| Task                                              | Status |
|---------------------------------------------------|--------|
| Write and run integration tests for all routes    | [ ]    |
| Perform security testing (CSRF, access control)   | [ ]    |
| Test on Chrome, Firefox, Edge                     | [ ]    |
| Fix identified bugs                               | [ ]    |
| Write README and documentation                    | [ ]    |
| Prepare project demo / presentation               | [ ]    |

---

## 18. Risks & Mitigations

| Risk ID | Risk                                            | Likelihood | Impact   | Mitigation                                               |
|---------|-------------------------------------------------|------------|----------|----------------------------------------------------------|
| R-01    | Incorrect ECC implementation breaks decryption  | Medium     | High     | Use well-tested library (`cryptography`); unit test thoroughly |
| R-02    | Private key exposure via bug or misconfiguration| Low        | Critical | Encrypt private keys at rest; never expose in UI or logs |
| R-03    | Large file causes memory issues (in-memory)     | Medium     | Medium   | Stream file in chunks; set size limits                   |
| R-04    | SQLite not suitable for concurrent access       | Low        | Medium   | Use MySQL/PostgreSQL if multi-user load is needed        |
| R-05    | CSRF attack on transfer endpoints               | Low        | High     | Flask-WTF CSRF tokens on all forms                       |
| R-06    | Path traversal in file upload                   | Low        | High     | `secure_filename()`; UUID-based file naming              |
| R-07    | Session hijacking                               | Low        | High     | HTTPS; `HttpOnly` + `Secure` cookie flags                |
| R-08    | Project scope creep delaying delivery           | Medium     | Medium   | Strict phase gating; defer Future Scope items to v2      |
| R-09    | Dependency vulnerabilities in crypto libraries  | Low        | High     | Pin dependency versions; run `pip audit`                 |

---

## 19. Future Scope

These features are explicitly deferred to a future version (v2.0+):

| Feature                        | Description                                                    |
|--------------------------------|----------------------------------------------------------------|
| Digital Signatures             | ECC-based signing (ECDSA) for non-repudiation                  |
| Two-Factor Authentication      | TOTP (Google Authenticator) for stronger login security        |
| Cloud Storage Integration      | Store encrypted files on AWS S3 / Google Cloud Storage         |
| Multiple Recipients            | Encrypt file for multiple recipients simultaneously            |
| Expiring Download Links        | Time-limited, one-time-use download tokens                     |
| Real-time Notifications        | WebSocket push alerts for new incoming transfers               |
| File Compression               | Compress before encryption to reduce storage size              |
| Mobile Application             | React Native or Flutter app for iOS/Android                    |
| Audit Logging                  | Admin-visible log of all security events                       |
| Admin Panel                    | User management, system statistics, transfer oversight         |

---

## 20. Glossary

| Term                  | Definition                                                                              |
|-----------------------|-----------------------------------------------------------------------------------------|
| AES                   | Advanced Encryption Standard — symmetric block cipher used for file encryption          |
| AES-256-GCM           | AES in Galois/Counter Mode with 256-bit key — provides confidentiality + integrity      |
| Auth Tag              | 16-byte authentication tag produced by GCM — used to verify ciphertext integrity        |
| bcrypt                | Password hashing algorithm with adaptive cost factor                                    |
| Ciphertext            | Encrypted (unreadable) form of data                                                     |
| ECDH                  | Elliptic Curve Diffie-Hellman — key agreement protocol                                  |
| ECIES                 | Elliptic Curve Integrated Encryption Scheme — hybrid encryption using ECC + symmetric   |
| ECC                   | Elliptic Curve Cryptography — public-key cryptography based on elliptic curve math      |
| Ephemeral Key Pair    | A temporary key pair generated per transfer; discarded after use                        |
| GCM                   | Galois/Counter Mode — authenticated encryption mode for AES                            |
| HKDF                  | HMAC-based Key Derivation Function — derives keys from shared secrets                  |
| Integrity Verification| Confirming a file has not been altered during transit (SHA-256 hash comparison)         |
| IV / Nonce            | Initialization Vector / Number used Once — ensures encryption uniqueness                |
| KDF                   | Key Derivation Function — derives one or more keys from a source secret                 |
| P-256 / secp256r1     | NIST standardized elliptic curve offering 128-bit security level                       |
| Plaintext             | Original, unencrypted data                                                              |
| Private Key           | Secret ECC key known only to its owner; used for decryption/key recovery               |
| PRD                   | Product Requirements Document — defines what a product must do and why                  |
| Public Key            | ECC key shareable with others; used by sender to encrypt the session key                |
| Session Key           | Temporary random AES key generated per transfer for file encryption                     |
| SHA-256               | Secure Hash Algorithm — produces a 256-bit fingerprint for integrity checking           |
| SRS                   | Software Requirements Specification — technical specification of system requirements    |
| UUID                  | Universally Unique Identifier — used for unique transfer IDs and file naming            |

---

*End of Product Requirements Document*

---
> **Document prepared by:** Sk.Md.Junaid (R220424)
> **Institution:** RGUKT RK Valley, Department of Computer Science and Engineering
> **Academic Year:** 2026–2027
> **Based on:** File_Transfer_System_ECC_SRS.md v1.0
