# FRONTEND IMPLEMENTATION SPECIFICATION & DESIGN DOCUMENT
# File Transfer System Using Elliptic Curve Cryptography (ECC)

---

| Document Attribute   | Specification Detail                                        |
|:---------------------|:------------------------------------------------------------|
| **Document Title**   | Frontend Implementation Specification & Technical Blueprint |
| **System**           | File Transfer System Using ECC & Hybrid Cryptography        |
| **Document Version** | 1.0                                                         |
| **Status**           | Approved for Implementation                                 |
| **Author**           | Sk.Md.Junaid (Roll No: 58, ID: R220424)                     |
| **Department**       | Department of Computer Science & Engineering                |
| **Institution**      | Rajiv Gandhi University of Knowledge Technologies (RK Valley)|
| **Academic Year**    | 2026–2027                                                   |
| **Target Audience**  | Frontend Developers, System Architects, Project Evaluators  |

---

## Table of Contents

1. [Executive Summary & Purpose](#1-executive-summary--purpose)
2. [Frontend Architecture & Technology Stack](#2-frontend-architecture--technology-stack)
3. [Design System & Visual Language](#3-design-system--visual-language)
4. [Component Hierarchy & UI Library](#4-component-hierarchy--ui-library)
5. [Page Specifications & Interactive Wireframes](#5-page-specifications--interactive-wireframes)
   - 5.1 [Base Layout & Navigation Shell](#51-base-layout--navigation-shell)
   - 5.2 [Landing Page (`/`)](#52-landing-page-)
   - 5.3 [Authentication Suite (`/auth/login`, `/auth/register`)](#53-authentication-suite-authlogin-authregister)
   - 5.4 [Main Dashboard (`/dashboard`)](#54-main-dashboard-dashboard)
   - 5.5 [Send File Portal (`/transfer/send`)](#55-send-file-portal-transfersend)
   - 5.6 [Secure Inbox (`/transfer/inbox`) & Decrypt Modal](#56-secure-inbox-transferinbox--decrypt-modal)
   - 5.7 [Transfer History & Audit Logs (`/transfer/history`)](#57-transfer-history--audit-logs-transferhistory)
   - 5.8 [Cryptographic Profile & Key Management (`/profile`)](#58-cryptographic-profile--key-management-profile)
6. [Client-Side State Management & API Integration Layer](#6-client-side-state-management--api-integration-layer)
7. [Cryptographic UX & Security Safeguards](#7-cryptographic-ux--security-safeguards)
8. [File Structure & Directory Organization](#8-file-structure--directory-organization)
9. [Step-by-Step Implementation Roadmap](#9-step-by-step-implementation-roadmap)
10. [Quality Assurance, Accessibility & Verification Checklist](#10-quality-assurance-accessibility--verification-checklist)

---

## 1. Executive Summary & Purpose

The **File Transfer System Using Elliptic Curve Cryptography (ECC)** frontend is an interface designed to bridge complex hybrid cryptography (SECP256R1 ECDH, HKDF-SHA256, AES-256-GCM) with an intuitive, seamless user experience.

### 1.1 Core Objectives
1. **Cryptographic Transparency Without Cognitive Overload:** Expose verification indicators (SHA-256 checksums, ECC key fingerprints, AES-GCM authentication statuses) clearly while keeping file upload and download flows effortless.
2. **Deterministic Feedback Loop:** Real-time visual feedback for asynchronous states: client-side hashing, multi-stage upload progress, decryption verification, and file download streaming.
3. **Zero Compromise Security UX:** Client-side input validation, CSRF auto-injection, safe credential zeroing, XSS immunization, and secure password-prompting for private key decryption.
4. **State-of-the-Art Aesthetic:** High-density, professional dark-mode UI utilizing deep slate palettes, vibrant indigo and cyan accents, glassmorphic card overlays, responsive CSS Grid/Flexbox layouts, and buttery micro-animations.

---

## 2. Frontend Architecture & Technology Stack

To ensure seamless integration with the Flask backend, high render speed, security compliance, and zero external build toolchain bloat, the frontend is architected as a **Modern Server-Rendered Architecture enhanced with Component-Driven Vanilla JavaScript (ES6+) and Custom CSS Design Tokens**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        BROWSER PRESENTATION LAYER                      │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                 Jinja2 HTML5 Semantic Templates                │   │
│   │   (Base Shell, Navbars, Modals, Forms, Tables, Status Badges)  │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│   ┌───────────────────────────────┴────────────────────────────────┐   │
│   │                 Custom CSS3 Design Token System                │   │
│   │       (Modern Glassmorphism, HSL Variables, Responsive Grid)   │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│   ┌───────────────────────────────┴────────────────────────────────┐   │
│   │                 Modular Vanilla ES6+ Scripts                   │   │
│   │  ┌───────────────┐ ┌────────────────┐ ┌─────────────────────┐  │   │
│   │  │   api.js      │ │   dropzone.js  │ │   decrypt-modal.js  │  │   │
│   │  │ (Fetch/CSRF)  │ │  (Upload/Hash) │ │ (Passwd/Stream DL)  │  │   │
│   │  └──────┬────────┘ └───────┬────────┘ └──────────┬──────────┘  │   │
│   │         │                  │                     │             │   │
│   │  ┌──────┴──────────────────┴─────────────────────┴──────────┐  │   │
│   │  │                    app.js (Main Controller)              │  │   │
│   │  └─────────────────────────┬────────────────────────────────┘  │   │
│   └────────────────────────────┼───────────────────────────────────┘   │
└────────────────────────────────┼───────────────────────────────────────┘
                                 │ HTTP / JSON / Multipart
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FLASK REST / ROUTE BACKEND                      │
│         /auth/*            /transfer/*            /dashboard           │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Technology Decisions

| Technology Component | Selection | Justification |
|:---|:---|:---|
| **Templating Engine** | **Jinja2 (Flask Built-in)** | Native SSR provides SEO support, instant first-contentful-paint (FCP), secure CSRF token interpolation, and server-side route guarding without bundle overhead. |
| **Styling Framework** | **Vanilla Modern CSS3** | Maximum flexibility without heavy dependencies (e.g. Tailwind runtime). Uses CSS Custom Properties (`--var`), Flexbox, CSS Grid, clamp() responsive typography, and glassmorphism. |
| **Logic & Interactivity** | **ES6+ Vanilla JavaScript** | Native `fetch()`, `Blob`, `FileReader`, `URL.createObjectURL()`, and modular DOM handlers. Zero bundle compilation required; clean, readable, academic codebase. |
| **Typography** | **Inter + JetBrains Mono** | `Inter` for clean application typography; `JetBrains Mono` for cryptographic hashes, public keys, and hex values. Loaded via Google Fonts. |
| **Icons** | **Heroicons / Feather SVG** | Clean, inline or lightweight SVG icons embedded directly to eliminate font-file network latency and layout shift. |

---

## 3. Design System & Visual Language

### 3.1 Color Palette & Token Architecture

The design uses a high-contrast dark theme calibrated for security software.

```css
:root {
  /* Surface & Background Hierarchy */
  --bg-base:        #090D16;   /* Deepest background slate */
  --bg-surface:     #0F172A;   /* Primary card and component container */
  --bg-surface-elevated: #1E293B; /* Dropdowns, modals, elevated cards */
  --bg-surface-subtle:   #334155; /* Dividers, hover pills, disabled areas */

  /* Primary Brand & Cryptographic Accents */
  --primary:        #6366F1;   /* Vibrant Indigo - action buttons, active links */
  --primary-hover:  #4F46E5;   /* Deep Indigo */
  --primary-light:  #818CF8;   /* Soft Indigo glow */
  --accent-cyan:    #06B6D4;   /* Cyan - cryptographic security badges */
  --accent-cyan-glow: rgba(6, 182, 212, 0.15);

  /* Semantic Feedback Colors */
  --success:        #10B981;   /* Emerald - verified hashes, complete transfers */
  --success-bg:     rgba(16, 185, 129, 0.12);
  --warning:        #F59E0B;   /* Amber - pending downloads, warnings */
  --warning-bg:     rgba(245, 158, 11, 0.12);
  --danger:         #F43F5E;   /* Rose Red - decryption failure, delete action */
  --danger-bg:      rgba(244, 63, 94, 0.12);
  --info:           #38BDF8;   /* Sky Blue - information toasts */

  /* Text & Typography */
  --text-primary:   #F8FAFC;   /* 95% White - main headings, high emphasis */
  --text-secondary: #94A3B8;   /* Slate 400 - descriptions, metadata, labels */
  --text-muted:     #64748B;   /* Slate 500 - disabled placeholders */
  --text-link:      #818CF8;

  /* Borders & Glassmorphism */
  --border-subtle:  rgba(255, 255, 255, 0.08);
  --border-focus:   rgba(99, 102, 241, 0.5);
  --glass-bg:       rgba(15, 23, 42, 0.75);
  --glass-border:   rgba(255, 255, 255, 0.12);
  --glass-blur:     blur(12px);

  /* Shadows & Elevation */
  --shadow-sm:      0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md:      0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
  --shadow-lg:      0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3);
  --shadow-glow:    0 0 20px -2px rgba(99, 102, 241, 0.25);

  /* Radii & Transitions */
  --radius-sm:      6px;
  --radius-md:      10px;
  --radius-lg:      16px;
  --radius-full:    9999px;
  --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
```

### 3.2 Typography Scale

- **Display 1:** `2.5rem (40px)` / Line Height: 1.2 / Bold / Inter / Tracking: -0.02em
- **Heading 1:** `1.875rem (30px)` / Line Height: 1.25 / Semi-Bold / Inter
- **Heading 2:** `1.5rem (24px)` / Line Height: 1.3 / Semi-Bold / Inter
- **Heading 3:** `1.25rem (20px)` / Line Height: 1.4 / Medium / Inter
- **Body Regular:** `1.0rem (16px)` / Line Height: 1.5 / Regular / Inter
- **Body Small:** `0.875rem (14px)` / Line Height: 1.4 / Regular / Inter
- **Code / Cryptographic Hash:** `0.8125rem (13px)` / Regular / JetBrains Mono / Tracking: 0.05em

---

## 4. Component Hierarchy & UI Library

The frontend is composed of reusable UI building blocks designed with atomic consistency:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REUSABLE COMPONENT SYSTEM                       │
├─────────────────┬──────────────────┬─────────────────┬─────────────────┤
│    NAVIGATION   │   CRYPTO BADGES  │  INPUT & FORMS  │  DATA DISPLAY   │
├─────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ • AppHeader     │ • SecurityBadge  │ • FileDropzone  │ • TransferCard  │
│ • SidebarNav    │ • HashInspector  │ • FormInput     │ • StatsWidget   │
│ • UserMenu      │ • KeyFingerprint │ • PasswordField │ • TableView     │
│ • Breadcrumbs   │ • StatusPill     │ • ReceiverSelect│ • PaginationNav │
├─────────────────┼──────────────────┼─────────────────┼─────────────────┤
│    FEEDBACK     │     MODALS       │     BUTTONS     │     STATES      │
├─────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ • ToastAlert    │ • DecryptModal   │ • PrimaryBtn    │ • EmptyState    │
│ • ProgressBar   │ • ConfirmDelete  │ • SecondaryBtn  │ • SkeletonRow   │
│ • HashChecksum  │ • KeyExportModal │ • DangerBtn     │ • ErrorBanner   │
└─────────────────┴──────────────────┴─────────────────┴─────────────────┘
```

### 4.1 Component Details

#### 1. SecurityBadge
- **Purpose:** Visually confirms that transfers utilize hybrid encryption.
- **Visuals:** Lock SVG + text "AES-256-GCM + SECP256R1".
- **Styling:** Slate-800 pill with cyan border and subtle glow.

#### 2. StatusPill
- **PENDING:** Amber background (`rgba(245,158,11,0.15)`), amber text, pulsating dot animation indicating awaiting receiver download.
- **DOWNLOADED:** Emerald background (`rgba(16,185,129,0.15)`), emerald text, checkmark SVG icon.
- **FAILED:** Rose background (`rgba(244,63,94,0.15)`), rose text, cross SVG icon.

#### 3. FileDropzone
- Interactive drag-and-drop region with drag-over border highlighting (`border: 2px dashed var(--primary)`).
- Instant file inspector showing: File name, formatted size (KB/MB), MIME type badge.
- Client-side size constraint enforcement (max 50 MB) before network upload begins.

#### 4. DecryptModal
- Triggered when receiver clicks "Decrypt & Download".
- Prompts for account password to unlock the encrypted ECC private key.
- Includes a security notice: *"Your private key is protected with AES-256-GCM using PBKDF2 key derivation. Entering your password unlocks your private key in memory to compute ECDH session key agreement."*
- Decrypt button with loading spinner state and inline error presentation.

#### 5. HashInspector & KeyFingerprint
- Displays SHA-256 integrity hash or ECC public key in monospace font.
- Features one-click **"Copy to Clipboard"** button with a temporary `"Copied!"` tooltip.
- Collapsible view showing first 8 and last 8 characters with toggle to view full 64-character hash.

---

## 5. Page Specifications & Interactive Wireframes

### 5.1 Base Layout & Navigation Shell

All application pages inherit from a shared base template ([`base.html`](file:///c:/Users/pc/OneDrive/Desktop/FIle%20Transfer/file_transfer_ecc/app/templates/base.html)) providing a cohesive shell, navigation, global notifications, and modal injection containers.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [🔒 ECC SecureTransfer]      [Inbox (2)]  [Send File]  [History]   (Alice ▼)│
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  MAIN CONTENT CONTAINER (Responsive Grid / Dynamic Views)                 │
│                                                                            │
│                                                                            │
│                                                                            │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│ © 2026 ECC File Transfer System • RGUKT RK Valley • E2E Hybrid Encryption  │
└────────────────────────────────────────────────────────────────────────────┘
```

#### Navigation States:
- **Unauthenticated View:** Brand Logo | Feature Highlights | "Login" Button | "Register" Button (CTA).
- **Authenticated View:** Brand Logo | "Dashboard" | "Send File" | "Inbox" (with pending badge count) | "History" | User Profile Avatar Dropdown (Username, Public Key Fingerprint, Logout).

---

### 5.2 Landing Page (`/`)

The public entry point introduces visitors and academic evaluators to the core security mechanics of the project.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                             HERO SECTION                                   │
│                                                                            │
│          🔒 End-to-End File Encryption Powered by Elliptic Curves          │
│                                                                            │
│    Transfer confidential files with military-grade hybrid cryptography.    │
│    ECDH (P-256) Key Agreement • AES-256-GCM Encryption • SHA-256 Integrity │
│                                                                            │
│             [ Get Started — Create Account ]    [ Sign In ]                │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                        THREE-PILLAR ARCHITECTURE                           │
│                                                                            │
│  ┌──────────────────────┐ ┌──────────────────────┐ ┌─────────────────────┐ │
│  │   1. Asymmetric ECC  │ │  2. Symmetric AES    │ │  3. SHA-256 Hashing │ │
│  │ NIST P-256 (secp256r1│ │ AES-256-GCM cipher   │ │ Cryptographic hash  │ │
│  │ for zero-knowledge   │ │ protects file payload│ │ guarantees complete │ │
│  │ session key agreement│ │ at maximum throughput│ │ anti-tamper security│ │
│  └──────────────────────┘ └──────────────────────┘ └─────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.3 Authentication Suite (`/auth/login`, `/auth/register`)

#### 5.3.1 User Registration (`/auth/register`)
- **Fields:** Username, Email Address, Password, Confirm Password.
- **Client-Side Live Password Strength Meter:**
  - Length >= 8 characters
  - Lowercase & Uppercase letters
  - Numeric digit
  - Special character (`!@#$%^&*`)
- **Key Generation Notice:** An informational callout explaining: *"Upon registration, a 256-bit ECC Key Pair (SECP256R1) will be generated for your account. Your private key will be encrypted at rest using AES-256-GCM derived from your password."*

#### 5.3.2 User Login (`/auth/login`)
- **Fields:** Email Address, Plaintext Password, Remember Me checkbox.
- **Interactive Behavior:** Async submission with button loading spinner; immediate redirect to `/dashboard` upon verification; error banner displaying invalid credentials without revealing whether email or password failed (anti-enumeration).

---

### 5.4 Main Dashboard (`/dashboard`)

The central operational hub providing situational awareness of transfers and quick action links.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Dashboard Overview                                          [+ Send File]  │
│ Welcome back, Alice! Your cryptographic session is active.                 │
├────────────────────────────────────────────────────────────────────────────┤
│ STATS COUNTER CARDS                                                        │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐│
│ │ 📥 Pending     │ │ 📤 Sent Files  │ │ 📦 Total Volume│ │ 🔑 Key Status  ││
│ │   3 Files      │ │   18 Files     │ │   142.8 MB     │ │   secp256r1 OK ││
│ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘│
├────────────────────────────────────────────────────────────────────────────┤
│ RECENT INCOMING TRANSFERS (Action Required)                                │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ 📄 financial_audit_2026.pdf (4.2 MB)                Sender: Bob        │ │
│ │ Status: [⏳ PENDING]    Checksum: a1f8...3e90       [ Decrypt & DL ]   │ │
│ ├────────────────────────────────────────────────────────────────────────┤ │
│ │ 🗜️ dataset_rkv_v2.zip (18.6 MB)                     Sender: Charlie    │ │
│ │ Status: [⏳ PENDING]    Checksum: 5d12...89bb       [ Decrypt & DL ]   │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────┤
│ QUICK SEND WIDGET                                                          │
│ [ Drag and drop file here or click to browse...                          ] │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.5 Send File Portal (`/transfer/send`)

The primary sending interface providing intuitive recipient selection, file attachment, and multi-stage status visualization.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Send Encrypted File                                                        │
├────────────────────────────────────────────────────────────────────────────┤
│ 1. SELECT RECIPIENT                                                        │
│ Recipient: [ Select user (e.g. bob@example.com)                   ▼ ]      │
│ [🔒 Recipient Public Key Verified: 04a2bc9...e41f (NIST P-256)]           │
├────────────────────────────────────────────────────────────────────────────┤
│ 2. CHOOSE FILE                                                             │
│ ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐ │
│   📁 Drag & drop your file here, or click to browse                        │
│   Supported: PDF, DOCX, ZIP, PNG, JPG, TXT (Max size: 50 MB)              │
│ └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘ │
│ Selected: project_source.zip (14.2 MB)  •  Type: application/zip           │
├────────────────────────────────────────────────────────────────────────────┤
│ 3. ENCRYPTION PIPELINE PREVIEW                                             │
│ • Symmetric Key: Random 256-bit AES-GCM session key generated on send      │
│ • Key Encapsulation: Receiver's ECC public key used to wrap session key    │
│ • Integrity Check: SHA-256 digest calculated before encryption             │
├────────────────────────────────────────────────────────────────────────────┤
│ [ 🚀 Encrypt & Send File Securely ]                                        │
│                                                                            │
│ UPLOAD PROGRESS BAR (Active during submission)                             │
│ [██████████████████████████████░░░░░░░░] 78% (Encrypting & Streaming...)   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### 5.6 Secure Inbox (`/transfer/inbox`) & Decrypt Modal

The receiver's secure repository for pending and received files.

#### 5.6.1 Inbox Card View
Each transfer is displayed as a high-density card showing:
1. **File Identity:** Original filename, formatted size, MIME badge.
2. **Sender Identity:** Username and email of the sender.
3. **Transmission Timestamp:** Exact date/time sent.
4. **Security Details:** SHA-256 plaintext integrity hash (inspectable).
5. **Status Badge:** PENDING (Amber) or DOWNLOADED (Green).
6. **Action:** "Decrypt & Download" button (for PENDING), or "Re-download" button (for DOWNLOADED).

#### 5.6.2 The Decrypt & Download Modal Workflow

```
┌────────────────────────────────────────────────────────────────┐
│ 🔐 Decrypt & Download File                                 [X] │
├────────────────────────────────────────────────────────────────┤
│ File: research_paper_final.pdf (3.8 MB)                        │
│ Sender: alice (alice@example.com)                              │
│                                                                │
│ 🛡️ Security Verification Notice:                               │
│ To decrypt this file, your ECC Private Key must be unlocked.   │
│ Please enter your account password to verify your identity     │
│ and decrypt the session key.                                   │
│                                                                │
│ Account Password:                                              │
│ [•••••••••••••••••••••] [👁️ Show]                             │
│                                                                │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ ℹ️ How this works:                                         │ │
│ │ 1. Your password decrypts your stored private key.         │ │
│ │ 2. ECDH derives the shared secret with sender's key.       │ │
│ │ 3. AES-256-GCM decrypts the file payload.                  │ │
│ │ 4. SHA-256 verifies zero byte tampering.                   │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ [ Cancel ]                         [ 🔓 Decrypt & Download ]  │
└────────────────────────────────────────────────────────────────┘
```

---

### 5.7 Transfer History & Audit Logs (`/transfer/history`)

Comprehensive audit ledger showing all inbound and outbound encrypted transfers.

- **Filters & Search Bar:**
  - Search by filename or counterparty username.
  - Filter by direction: "All Transfers", "Sent Only", "Received Only".
  - Filter by status: "All", "Pending", "Downloaded".
- **Data Table Columns:**
  1. Direction Icon (Outgoing `↗` vs Incoming `↙`)
  2. Filename & Size
  3. Counterparty (Recipient or Sender)
  4. Timestamp
  5. SHA-256 Integrity Checksum (click-to-copy button)
  6. Status Pill
  7. Actions (Info Modal, Delete pending file, Download)
- **Pagination Navigation:** Clean `Previous / Page X of Y / Next` controls.

---

### 5.8 Cryptographic Profile & Key Management (`/profile`)

Provides the user with complete cryptographic visibility into their credentials.

- **Account Overview:** Username, Email, Registered Date, Last Login Timestamp.
- **ECC Key Pair Details:**
  - **Curve:** NIST P-256 / SECP256R1
  - **Key Format:** PEM (Privacy-Enhanced Mail) & Raw Uncompressed Hex
  - **Public Key Display Box:** Read-only monospace text area with quick "Copy PEM" button.
  - **Key Fingerprint:** SHA-256 hash of the uncompressed public key point.
  - **Private Key Storage Indicator:** *"Encrypted at Rest with AES-256-GCM (PBKDF2-HMAC-SHA256, 100,000 iterations)"*.

---

## 6. Client-Side State Management & API Integration Layer

All asynchronous communications are routed through a centralized, standardized client module: `api.js`.

### 6.1 CSRF Auto-Injection Architecture
Flask-WTF provides CSRF tokens on every session. The frontend injects this token into an HTML `<meta>` tag in [`base.html`](file:///c:/Users/pc/OneDrive/Desktop/FIle%20Transfer/file_transfer_ecc/app/templates/base.html):

```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

The `api.js` client intercepts all outgoing state-changing HTTP requests (`POST`, `PUT`, `DELETE`) and automatically attaches the `X-CSRFToken` header:

```javascript
// static/js/api.js
const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

export async function request(url, options = {}) {
  const headers = {
    'X-Requested-With': 'XMLHttpRequest',
    ...options.headers,
  };

  if (CSRF_TOKEN && !['GET', 'HEAD', 'OPTIONS'].includes(options.method?.toUpperCase())) {
    headers['X-CSRFToken'] = CSRF_TOKEN;
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    // Session expired or unauthenticated
    window.location.href = '/auth/login?session_expired=1';
    throw new Error('Authentication required');
  }

  return response;
}
```

### 6.2 Decrypt & Download Streaming Mechanism

When downloading a decrypted file, the frontend:
1. Dispatches `POST /transfer/download/<transfer_id>` containing the receiver's password in JSON format.
2. If credentials or decryption fails (401, 403, 422), parses JSON error and displays it in the modal.
3. If successful (HTTP 200), streams the binary response into a `Blob`:
4. Extracts original filename from `Content-Disposition` header.
5. Generates an ephemeral object URL via `URL.createObjectURL(blob)`.
6. Simulates a hidden anchor click to trigger native browser file saving.
7. Automatically revokes the object URL via `URL.revokeObjectURL()` to prevent memory leaks.

```javascript
// Decrypt and stream trigger
export async function downloadDecryptedFile(transferId, password) {
  const resp = await request(`/transfer/download/${transferId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });

  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.message || 'Decryption failed.');
  }

  // Extract filename
  const disposition = resp.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match ? match[1] : 'decrypted_file';

  const blob = await resp.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(downloadUrl);
  a.remove();
}
```

---

## 7. Cryptographic UX & Security Safeguards

To prevent vulnerabilities on the client side, the frontend enforces strict defensive rules:

1. **Anti-XSS Sanitization:** All user-controlled text (usernames, filenames, email addresses) is escaped by default through Jinja2 auto-escaping (`{{ value }}`). In JavaScript, DOM manipulation strictly uses `.textContent` and `.setAttribute()`, never `innerHTML` with unsanitized data.
2. **Password Zeroing & Exposure Prevention:** Password input fields use `type="password"`. In memory, password variables are overwritten (`password = null`) immediately following dispatch of the decryption request.
3. **No Private Key In LocalStorage:** Private keys are NEVER sent to or stored in client storage (`localStorage`, `sessionStorage`, or IndexedDB). Decryption keys are held strictly in server memory during the request lifecycle.
4. **Pre-flight File Verification:** Before uploading, the frontend validates file size (`file.size <= 50 * 1024 * 1024`) and alerts the user with an inline error before any bandwidth is expended.

---

## 8. File Structure & Directory Organization

The frontend codebase is organized directly within the Flask `app/` folder, respecting Flask's standard static/templates convention while maintaining modular separation:

```
file_transfer_ecc/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   ├── tokens.css           # Color variables, typography, shadows, radii
│   │   │   ├── reset.css            # Modern CSS reset & base normalization
│   │   │   ├── layout.css           # Header, navbar, container grid, footer
│   │   │   ├── components.css       # Buttons, cards, pills, dropzone, modal, toasts
│   │   │   └── pages/               # Page-specific stylesheets
│   │   │       ├── auth.css         # Login & Register layouts
│   │   │       ├── dashboard.css    # Stats cards, metrics, quick actions
│   │   │       ├── transfer.css     # Send dropzone, progress bar, inbox cards
│   │   │       └── profile.css      # Key inspector, monospace viewers
│   │   │
│   │   ├── js/
│   │   │   ├── api.js               # Centralized fetch wrapper + CSRF management
│   │   │   ├── toast.js             # Toast notification dispatcher
│   │   │   ├── dropzone.js          # Drag-and-drop handler + client validation
│   │   │   ├── decrypt-modal.js     # Password verification & download trigger
│   │   │   ├── clipboard.js         # One-click copy for hashes and public keys
│   │   │   └── main.js              # Application bootstrapper & global handlers
│   │   │
│   │   └── img/
│   │       ├── logo.svg             # Project brand logo with lock symbol
│   │       └── empty-inbox.svg      # Empty state visual illustration
│   │
│   └── templates/
│       ├── base.html                # Master HTML5 skeleton & navbar
│       ├── index.html               # Public landing page
│       ├── auth/
│       │   ├── login.html           # Login screen
│       │   └── register.html        # Registration screen with password meter
│       ├── dashboard/
│       │   └── index.html           # Main user dashboard
│       ├── transfer/
│       │   ├── send.html            # File upload & recipient picker
│       │   ├── inbox.html           # Incoming files & decrypt modal trigger
│       │   ├── history.html         # Comprehensive audit table & pagination
│       │   └── info.html            # Transfer metadata inspector
│       ├── profile/
│       │   └── index.html           # Public key view, fingerprint & user stats
│       └── components/
│           ├── _nav.html            # Header navigation bar
│           ├── _footer.html         # Application footer
│           ├── _decrypt_modal.html  # Decrypt password verification modal
│           └── _toast_container.html# Alert notification viewport
```

---

## 9. Step-by-Step Implementation Roadmap

The implementation is structured into 7 sequential stages to allow iterative validation:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND IMPLEMENTATION ROADMAP                         │
├───────┬─────────────────────────────────────────────────┬──────────────────┤
│ Stage │ Phase Name                                      │ Deliverables     │
├───────┼─────────────────────────────────────────────────┼──────────────────┤
│ **1** │ **Design System & Base Shell**                  │ CSS tokens, base │
│       │                                                 │ template, nav    │
│ **2** │ **Authentication & Landing UI**                 │ Login, Register, │
│       │                                                 │ Password meter   │
│ **3** │ **Dashboard & Operational View**                │ Metric counters, │
│       │                                                 │ recent transfers │
│ **4** │ **Send File Portal & Dropzone Interaction**     │ Recipient search,│
│       │                                                 │ drag-and-drop UI │
│ **5** │ **Secure Inbox & Decrypt-Download Modal**       │ Inbox list view, │
│       │                                                 │ password modal   │
│ **6** │ **Transfer History, Audit Table & Filters**     │ Paginated ledger,│
│       │                                                 │ filter controls  │
│ **7** │ **Cryptographic Profile & UI Polish**           │ Public key view, │
│       │                                                 │ toast alerts, QA │
└───────┴─────────────────────────────────────────────────┴──────────────────┘
```

### Stage 1: Design System & Base Shell
- Implement `tokens.css`, `reset.css`, and `layout.css`.
- Create `base.html` including responsive `<nav>` header, `<main>` content container, and `<footer>`.
- Configure CSRF meta tag and toast container markup.

### Stage 2: Authentication & Landing UI
- Build `index.html` with product showcase and security architecture cards.
- Implement `auth/login.html` and `auth/register.html`.
- Add client-side password strength calculator in `auth.js`.

### Stage 3: Dashboard & Operational View
- Implement `dashboard/index.html`.
- Render summary statistics cards (Pending, Sent, Volume).
- Render pending files requiring decryption.

### Stage 4: Send File Portal & Dropzone Interaction
- Implement `transfer/send.html`.
- Build `dropzone.js` for drag-and-drop interactions, file size checks, and visual states.
- Connect recipient selector with recipient public key verification indicators.
- Implement animated progress bar for file transmission.

### Stage 5: Secure Inbox & Decrypt-Download Modal
- Implement `transfer/inbox.html` with card-based transfer listing.
- Build `_decrypt_modal.html` and `decrypt-modal.js`.
- Integrate password verification, error display, and binary stream downloading.

### Stage 6: Transfer History, Audit Table & Filters
- Implement `transfer/history.html`.
- Build filter tabs (All, Sent, Received) and search box.
- Implement pagination controls and click-to-copy SHA-256 hash inspectors.

### Stage 7: Cryptographic Profile & UI Polish
- Implement `profile/index.html` with SECP256R1 public key display in PEM format.
- Add clipboard copying utility `clipboard.js`.
- Conduct cross-browser verification, mobile responsiveness adjustments, and final accessibility sweep.

---

## 10. Quality Assurance, Accessibility & Verification Checklist

| Area | Verification Criteria | Target |
|:---|:---|:---|
| **Design Integrity** | Color contrast ratio for text vs background meets WCAG AA standards (>= 4.5:1). | 100% compliant |
| **Responsiveness** | Fluid layout across 1920px (Desktop), 1366px (Laptop), 768px (Tablet), and 375px (Mobile). | Clean layout on all devices |
| **CSRF Protection** | Every state-changing form and fetch request includes valid `X-CSRFToken`. | Zero 400 Bad Request errors |
| **Feedback Latency** | Instant visual response (<100ms) on button clicks, drag-over states, and form inputs. | Zero lag |
| **File Download** | Binary file decrypted cleanly without byte corruption, matches SHA-256 digest. | Exact checksum match |
| **Error Handling** | Graceful error toasts on network failure, 401 unauthenticated, 403 forbidden, and 422 decrypt errors. | User-friendly alert messages |
| **Console Hygiene** | Zero JavaScript errors, zero unhandled promise rejections, zero deprecation warnings in developer tools. | Clean console log |

---
*End of Frontend Implementation Specification Document.*
