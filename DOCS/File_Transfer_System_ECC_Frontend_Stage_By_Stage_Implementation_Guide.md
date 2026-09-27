# FRONTEND STAGE-BY-STAGE IMPLEMENTATION GUIDE
# File Transfer System Using Elliptic Curve Cryptography (ECC)

---

| Document Attribute   | Specification Detail                                                  |
|:---------------------|:----------------------------------------------------------------------|
| **Document Title**   | Frontend Stage-by-Stage Implementation Guide & Code Blueprint         |
| **Project**          | File Transfer System Using ECC & Hybrid Cryptography                  |
| **Version**          | 1.0                                                                   |
| **Author**           | Sk.Md.Junaid (Roll No: 58, Student ID: R220424)                       |
| **Department**       | Department of Computer Science & Engineering                          |
| **Institution**      | Rajiv Gandhi University of Knowledge Technologies (RGUKT, RK Valley)  |
| **Academic Year**    | 2026–2027                                                             |
| **Target Audience**  | Full-Stack Engineers, Evaluators, Project Reviewers                   |

---

## Executive Summary

This guide provides a comprehensive, step-by-step roadmap for building the frontend user interface for the **File Transfer System Using Elliptic Curve Cryptography (ECC)**. 

Every stage contains:
1. **Stage Objectives & Pre-requisites**
2. **File Paths & System Architecture Role**
3. **Complete Production-Ready Code Listings** (HTML5 Jinja2 Templates, Modern CSS3, Modular ES6+ JavaScript)
4. **Integration with Existing Flask Backend Endpoints**
5. **Stage Verification & Quality Acceptance Criteria**

---

## Stage Index

- [Stage 1: Core Design System & CSS Token Architecture](#stage-1-core-design-system--css-token-architecture)
- [Stage 2: Reusable HTML5 Base Shell & Layout Templates](#stage-2-reusable-html5-base-shell--layout-templates)
- [Stage 3: Core Client-Side Utilities (API Client, CSRF, Toast & Clipboard)](#stage-3-core-client-side-utilities-api-client-csrf-toast--clipboard)
- [Stage 4: Public Landing Page & Cryptographic Showcase](#stage-4-public-landing-page--cryptographic-showcase)
- [Stage 5: Authentication Suite (Login & Registration with Password Meter)](#stage-5-authentication-suite-login--registration-with-password-meter)
- [Stage 6: User Dashboard & Live Transfer Telemetry](#stage-6-user-dashboard--live-transfer-telemetry)
- [Stage 7: Send File Portal & Dynamic Drag-and-Drop Dropzone](#stage-7-send-file-portal--dynamic-drag-and-drop-dropzone)
- [Stage 8: Secure Inbox, Decryption Modal & Binary Streaming](#stage-8-secure-inbox-decryption-modal--binary-streaming)
- [Stage 9: Transfer History, Audit Ledger & Filtering](#stage-9-transfer-history-audit-ledger--filtering)
- [Stage 10: Cryptographic Profile & Key Management](#stage-10-cryptographic-profile--key-management)
- [Stage 11: Flask Route Controllers & Integration Verification](#stage-11-flask-route-controllers--integration-verification)

---

## Stage 1: Core Design System & CSS Token Architecture

### 1.1 Objective
Establish the foundational styling layer: CSS custom properties (color hierarchy, elevation, radii, typography), modern resets, and atomic utility classes to support a high-contrast, security-focused dark UI.

### 1.2 Files to Create
1. `app/static/css/tokens.css`
2. `app/static/css/reset.css`
3. `app/static/css/components.css`

---

### 1.3 Code Implementation

#### File 1: `app/static/css/tokens.css`
```css
/* ==========================================================================
   app/static/css/tokens.css — Design Tokens & Variables
   ========================================================================== */

:root {
  /* Surfaces & Canvas */
  --bg-base:              #090D16;   /* Deepest midnight canvas */
  --bg-surface:           #0F172A;   /* Primary card and component container */
  --bg-surface-elevated:  #1E293B;   /* Modals, elevated cards, dropdowns */
  --bg-surface-subtle:    #334155;   /* Subtle hover pills, input borders */
  --bg-glass:             rgba(15, 23, 42, 0.85);

  /* Primary Brand & Accents */
  --primary:              #6366F1;   /* Vibrant Indigo */
  --primary-hover:        #4F46E5;   /* Deep Indigo */
  --primary-light:        #818CF8;   /* Soft Indigo highlight */
  --primary-glow:         rgba(99, 102, 241, 0.25);

  /* Cryptographic Accent (Cyan) */
  --accent-cyan:          #06B6D4;   /* Cyan indicator for ECC/Crypto */
  --accent-cyan-glow:     rgba(6, 182, 212, 0.2);

  /* Semantic Feedback Tokens */
  --success:              #10B981;   /* Emerald */
  --success-bg:           rgba(16, 185, 129, 0.12);
  --success-border:       rgba(16, 185, 129, 0.3);
  --warning:              #F59E0B;   /* Amber */
  --warning-bg:           rgba(245, 158, 11, 0.12);
  --warning-border:       rgba(245, 158, 11, 0.3);
  --danger:               #F43F5E;   /* Rose Red */
  --danger-bg:            rgba(244, 63, 94, 0.12);
  --danger-border:        rgba(244, 63, 94, 0.3);
  --info:                 #38BDF8;   /* Sky Blue */

  /* Text & Contrast */
  --text-primary:         #F8FAFC;   /* 95% Pure White */
  --text-secondary:       #94A3B8;   /* Slate 400 */
  --text-muted:           #64748B;   /* Slate 500 */
  --text-inverse:         #090D16;

  /* Borders & Dividers */
  --border-subtle:        rgba(255, 255, 255, 0.08);
  --border-focus:         rgba(99, 102, 241, 0.6);
  --glass-border:         rgba(255, 255, 255, 0.12);

  /* Typography Font Families */
  --font-sans:            'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono:            'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

  /* Border Radii */
  --radius-xs:            4px;
  --radius-sm:            8px;
  --radius-md:            12px;
  --radius-lg:            18px;
  --radius-full:          9999px;

  /* Shadows & Elevation */
  --shadow-sm:            0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md:            0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
  --shadow-lg:            0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
  --shadow-glow-cyan:     0 0 20px -3px rgba(6, 182, 212, 0.3);

  /* Transitions */
  --transition-fast:      0.15s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-smooth:    0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### File 2: `app/static/css/reset.css`
```css
/* ==========================================================================
   app/static/css/reset.css — Modern CSS Reset & Baseline
   ========================================================================== */

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
}

body {
  font-family: var(--font-sans);
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

img, svg, video {
  display: block;
  max-width: 100%;
}

input, button, textarea, select {
  font: inherit;
  color: inherit;
}

button {
  cursor: pointer;
  border: none;
  background: transparent;
}

a {
  color: inherit;
  text-decoration: none;
}

code, pre {
  font-family: var(--font-mono);
}
```

#### File 3: `app/static/css/components.css`
```css
/* ==========================================================================
   app/static/css/components.css — Global Components & Utilities
   ========================================================================== */

/* Button System */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.925rem;
  transition: all var(--transition-fast);
  user-select: none;
}

.btn-primary {
  background: var(--primary);
  color: #FFFFFF;
  box-shadow: 0 0 15px var(--primary-glow);
}
.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--bg-surface-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}
.btn-secondary:hover {
  background: var(--bg-surface-subtle);
  border-color: var(--border-focus);
}

.btn-danger {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}
.btn-danger:hover {
  background: var(--danger);
  color: #FFFFFF;
}

/* Cryptographic Security Badge */
.crypto-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-full);
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 500;
}

/* Status Pills */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.775rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.status-pill.pending {
  background: var(--warning-bg);
  border: 1px solid var(--warning-border);
  color: var(--warning);
}

.status-pill.downloaded {
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  color: var(--success);
}

.status-pill.failed {
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
  color: var(--danger);
}

/* Glass Card Container */
.glass-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(12px);
}
```

---

## Stage 2: Reusable HTML5 Base Shell & Layout Templates

### 2.1 Objective
Construct the responsive master skeleton template with navigation header, user profile dropdown, active state tracking, session flash alerts, and CSRF metadata tag.

### 2.2 Files to Create
1. `app/templates/base.html`
2. `app/templates/components/_nav.html`
3. `app/templates/components/_footer.html`

---

### 2.3 Code Implementation

#### File 1: `app/templates/base.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="csrf-token" content="{{ csrf_token() if csrf_token else '' }}">
  <title>{% block title %}ECC Secure File Transfer{% endblock %} | Hybrid Cryptography</title>

  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

  <!-- Core CSS Bundles -->
  <link rel="stylesheet" href="{{ url_for('static', filename='css/tokens.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/reset.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <!-- Header / Navigation -->
  {% include 'components/_nav.html' %}

  <!-- Global Toast Notification Viewport -->
  <div id="toast-container" class="toast-container" aria-live="polite"></div>

  <!-- Main Content Body -->
  <main class="main-container">
    {% block content %}{% endblock %}
  </main>

  <!-- Global Decryption Modal Placeholder -->
  {% include 'components/_decrypt_modal.html' %}

  <!-- Application Footer -->
  {% include 'components/_footer.html' %}

  <!-- Core JavaScript Libraries -->
  <script type="module" src="{{ url_for('static', filename='js/api.js') }}"></script>
  <script type="module" src="{{ url_for('static', filename='js/toast.js') }}"></script>
  <script type="module" src="{{ url_for('static', filename='js/clipboard.js') }}"></script>
  <script type="module" src="{{ url_for('static', filename='js/decrypt-modal.js') }}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

#### File 2: `app/templates/components/_nav.html`
```html
<header class="app-header">
  <div class="nav-container">
    <!-- Brand Logo -->
    <a href="{{ url_for('main.index') }}" class="brand-link">
      <svg class="brand-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
      <span class="brand-text">ECC<span class="brand-accent">Secure</span></span>
      <span class="crypto-badge">P-256</span>
    </a>

    <!-- Nav Links (Conditional on authentication state) -->
    <nav class="nav-menu">
      {% if current_user.is_authenticated %}
        <a href="{{ url_for('main.dashboard') }}" class="nav-link {% if request.endpoint == 'main.dashboard' %}active{% endif %}">Dashboard</a>
        <a href="/transfer/send" class="nav-link {% if request.path == '/transfer/send' %}active{% endif %}">Send File</a>
        <a href="/transfer/inbox" class="nav-link {% if request.path == '/transfer/inbox' %}active{% endif %}">
          Inbox
        </a>
        <a href="/transfer/history" class="nav-link {% if request.path == '/transfer/history' %}active{% endif %}">History</a>

        <!-- User Menu Dropdown -->
        <div class="user-profile-menu">
          <button class="profile-trigger" id="profile-dropdown-btn">
            <span class="avatar-circle">{{ current_user.username[0]|upper }}</span>
            <span class="username-label">{{ current_user.username }}</span>
          </button>
          <div class="dropdown-panel" id="profile-dropdown-panel">
            <a href="/profile" class="dropdown-item">Key & Profile</a>
            <hr class="dropdown-divider">
            <button id="logout-btn" class="dropdown-item logout-item">Logout</button>
          </div>
        </div>
      {% else %}
        <a href="/auth/login" class="nav-link">Sign In</a>
        <a href="/auth/register" class="btn btn-primary">Get Started</a>
      {% endif %}
    </nav>
  </div>
</header>
```

#### File 3: `app/templates/components/_footer.html`
```html
<footer class="app-footer">
  <div class="footer-container">
    <div class="footer-meta">
      <p class="footer-title">File Transfer System Using Elliptic Curve Cryptography (ECC)</p>
      <p class="footer-sub">Major Academic Project • RGUKT RK Valley • CSE Department</p>
    </div>
    <div class="footer-badges">
      <span class="crypto-badge">ECDH SECP256R1</span>
      <span class="crypto-badge">AES-256-GCM</span>
      <span class="crypto-badge">SHA-256</span>
    </div>
  </div>
</footer>
```

---

## Stage 3: Core Client-Side Utilities (API Client, CSRF, Toast & Clipboard)

### 3.1 Objective
Implement asynchronous communication abstraction layer with automatic CSRF token passing, auto-redirect on session expiration, toast alert system, and cryptographic string clipboard helpers.

### 3.2 Files to Create
1. `app/static/js/api.js`
2. `app/static/js/toast.js`
3. `app/static/js/clipboard.js`

---

### 3.3 Code Implementation

#### File 1: `app/static/js/api.js`
```javascript
/**
 * app/static/js/api.js — Centralized API Client & CSRF Handler
 */

export function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

export async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    'X-Requested-With': 'XMLHttpRequest',
  };

  const method = (options.method || 'GET').toUpperCase();

  // Auto-attach CSRF Token on mutating requests
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const token = getCsrfToken();
    if (token) {
      defaultHeaders['X-CSRFToken'] = token;
    }
  }

  // Auto-set Content-Type to JSON if sending object and not FormData
  if (options.body && !(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const mergedHeaders = {
    ...defaultHeaders,
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: mergedHeaders,
    });

    // Handle Unauthenticated Session
    if (response.status === 401) {
      window.location.href = '/auth/login?session_expired=true';
      throw new Error('Session expired. Redirecting to login...');
    }

    return response;
  } catch (error) {
    console.error(`[API ERROR] ${method} ${endpoint}:`, error);
    throw error;
  }
}
```

#### File 2: `app/static/js/toast.js`
```javascript
/**
 * app/static/js/toast.js — Dynamic Notification System
 */

const container = document.getElementById('toast-container');

export function showToast(message, type = 'info', duration = 4000) {
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <span class="toast-indicator"></span>
      <span class="toast-message">${escapeHtml(message)}</span>
    </div>
    <button class="toast-close" aria-label="Close">&times;</button>
  `;

  // Attach close listener
  toast.querySelector('.toast-close').addEventListener('click', () => {
    dismissToast(toast);
  });

  container.appendChild(toast);

  // Trigger enter animation
  requestAnimationFrame(() => {
    toast.classList.add('visible');
  });

  // Auto-dismiss timeout
  setTimeout(() => {
    dismissToast(toast);
  }, duration);
}

function dismissToast(toast) {
  toast.classList.remove('visible');
  toast.addEventListener('transitionend', () => {
    toast.remove();
  });
}

function escapeHtml(str) {
  const p = document.createElement('p');
  p.textContent = str;
  return p.innerHTML;
}
```

#### File 3: `app/static/js/clipboard.js`
```javascript
/**
 * app/static/js/clipboard.js — One-click Hash & Key Copy Utility
 */
import { showToast } from './toast.js';

export function initClipboardButtons() {
  document.querySelectorAll('[data-copy]').forEach((button) => {
    button.addEventListener('click', async () => {
      const textToCopy = button.getAttribute('data-copy');
      if (!textToCopy) return;

      try {
        await navigator.clipboard.writeText(textToCopy);
        const originalText = button.innerHTML;
        button.innerHTML = '<span>✓ Copied!</span>';
        showToast('Copied to clipboard!', 'success', 2000);
        setTimeout(() => {
          button.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        showToast('Could not copy to clipboard', 'danger');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', initClipboardButtons);
```

---

## Stage 4: Public Landing Page & Cryptographic Showcase

### 4.1 Objective
Create a visually impactful homepage that introduces the hybrid cryptosystem, displays cryptographic workflow cards, and provides clear call-to-actions for new and returning users.

### 4.2 Files to Create
1. `app/templates/index.html`
2. `app/static/css/pages/landing.css`

---

### 4.3 Code Implementation

#### File 1: `app/templates/index.html`
```html
{% extends 'base.html' %}

{% block title %}Next-Gen Encrypted File Exchange{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/landing.css') }}">
{% endblock %}

{% block content %}
<section class="hero-section">
  <div class="hero-glow"></div>
  <div class="hero-content">
    <div class="crypto-badge hero-badge">
      <span class="pulse-dot"></span> End-to-End Hybrid Cryptography
    </div>
    <h1 class="hero-title">
      Zero-Trust File Transfer Powered by <span class="gradient-text">Elliptic Curves</span>
    </h1>
    <p class="hero-description">
      Share confidential documents without exposing session keys or plaintext data.
      Leverages NIST P-256 (SECP256R1) ECDH key agreement, AES-256-GCM authenticated payload encryption, and SHA-256 anti-tamper verification.
    </p>

    <div class="hero-actions">
      {% if current_user.is_authenticated %}
        <a href="{{ url_for('main.dashboard') }}" class="btn btn-primary btn-lg">Go to Dashboard &rarr;</a>
        <a href="/transfer/send" class="btn btn-secondary btn-lg">Send Encrypted File</a>
      {% else %}
        <a href="/auth/register" class="btn btn-primary btn-lg">Generate ECC Keys & Sign Up</a>
        <a href="/auth/login" class="btn btn-secondary btn-lg">Account Login</a>
      {% endif %}
    </div>
  </div>
</section>

<!-- Cryptographic Architecture Grid -->
<section class="features-section">
  <div class="section-header">
    <h2 class="section-title">Cryptographic Architecture</h2>
    <p class="section-subtitle">A balanced fusion of asymmetric agility and symmetric throughput</p>
  </div>

  <div class="features-grid">
    <!-- Card 1 -->
    <div class="glass-card feature-card">
      <div class="feature-icon-wrapper cyan">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 3a9 9 0 0 0 0 18v-9"/>
        </svg>
      </div>
      <h3>Asymmetric ECC (P-256)</h3>
      <p>Users hold NIST P-256 keypairs. Ephemeral Elliptic Curve Diffie-Hellman (ECDH) agrees upon fresh session keys without transmission over the wire.</p>
    </div>

    <!-- Card 2 -->
    <div class="glass-card feature-card">
      <div class="feature-icon-wrapper indigo">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
      </div>
      <h3>AES-256-GCM Cipher</h3>
      <p>All files are encrypted symmetrically at line speed. Galois/Counter Mode guarantees both confidentiality and ciphertext integrity via a 128-bit authentication tag.</p>
    </div>

    <!-- Card 3 -->
    <div class="glass-card feature-card">
      <div class="feature-icon-wrapper emerald">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
      </div>
      <h3>SHA-256 Checksums</h3>
      <p>Every payload produces a deterministic SHA-256 digest before encryption. The receiver verifies exact byte-level integrity post-decryption.</p>
    </div>
  </div>
</section>
{% endblock %}
```

---

## Stage 5: Authentication Suite (Login & Registration with Password Meter)

### 5.1 Objective
Implement secure login and registration forms featuring live client-side password strength measurement, async form submission, and CSRF protection.

### 5.2 Files to Create
1. `app/templates/auth/login.html`
2. `app/templates/auth/register.html`
3. `app/static/js/auth.js`
4. `app/static/css/pages/auth.css`

---

### 5.3 Code Implementation

#### File 1: `app/templates/auth/register.html`
```html
{% extends 'base.html' %}
{% block title %}Create Account{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/auth.css') }}">
{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="glass-card auth-card">
    <div class="auth-header">
      <span class="crypto-badge">Keypair Generation</span>
      <h2>Create ECC Account</h2>
      <p>A 256-bit Elliptic Curve key pair will be generated automatically upon registration.</p>
    </div>

    <form id="register-form" class="auth-form" novalidate>
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" required placeholder="alice_crypto" autocomplete="username">
      </div>

      <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" required placeholder="alice@example.com" autocomplete="email">
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required placeholder="••••••••••••" autocomplete="new-password">
        <!-- Live Strength Meter -->
        <div class="password-meter-container">
          <div class="meter-bar" id="meter-bar"></div>
        </div>
        <span class="meter-label" id="meter-label">Password Strength: Empty</span>
      </div>

      <div class="form-group">
        <label for="confirm_password">Confirm Password</label>
        <input type="password" id="confirm_password" name="confirm_password" required placeholder="••••••••••••" autocomplete="new-password">
      </div>

      <div class="security-callout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <span>Your password encrypts your ECC private key at rest using PBKDF2-HMAC-SHA256 (100k iterations).</span>
      </div>

      <button type="submit" class="btn btn-primary btn-block" id="register-submit-btn">
        <span>Generate Keys & Create Account</span>
      </button>

      <div class="auth-footer-link">
        Already have an account? <a href="/auth/login">Sign in</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script type="module" src="{{ url_for('static', filename='js/auth.js') }}"></script>
{% endblock %}
```

#### File 2: `app/templates/auth/login.html`
```html
{% extends 'base.html' %}
{% block title %}Sign In{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/auth.css') }}">
{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="glass-card auth-card">
    <div class="auth-header">
      <span class="crypto-badge">Session Verification</span>
      <h2>Account Sign In</h2>
      <p>Enter your registered credentials to access your secure cryptographic vault.</p>
    </div>

    <form id="login-form" class="auth-form" novalidate>
      <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" required placeholder="alice@example.com" autocomplete="email">
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required placeholder="••••••••••••" autocomplete="current-password">
      </div>

      <button type="submit" class="btn btn-primary btn-block" id="login-submit-btn">
        <span>Authenticate & Unlock</span>
      </button>

      <div class="auth-footer-link">
        Don't have an account yet? <a href="/auth/register">Create Account</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script type="module" src="{{ url_for('static', filename='js/auth.js') }}"></script>
{% endblock %}
```

#### File 3: `app/static/js/auth.js`
```javascript
/**
 * app/static/js/auth.js — Authentication Controller & Password Meter
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

// Registration form handler
const registerForm = document.getElementById('register-form');
if (registerForm) {
  const pwdInput = document.getElementById('password');
  const meterBar = document.getElementById('meter-bar');
  const meterLabel = document.getElementById('meter-label');

  pwdInput.addEventListener('input', () => {
    const pwd = pwdInput.value;
    const score = calculatePasswordStrength(pwd);
    updateMeterUI(score, meterBar, meterLabel);
  });

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('register-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Generating SECP256R1 Keypair...';

    const payload = {
      username: document.getElementById('username').value.trim(),
      email: document.getElementById('email').value.trim(),
      password: pwdInput.value,
      confirm_password: document.getElementById('confirm_password').value,
    };

    try {
      const resp = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (resp.status === 201) {
        showToast('Registration successful! Redirecting to login...', 'success');
        setTimeout(() => {
          window.location.href = '/auth/login';
        }, 1500);
      } else {
        showToast(data.message || 'Registration failed.', 'danger');
        btn.disabled = false;
        btn.textContent = 'Generate Keys & Create Account';
      }
    } catch (err) {
      showToast('Network error during registration.', 'danger');
      btn.disabled = false;
      btn.textContent = 'Generate Keys & Create Account';
    }
  });
}

// Login form handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('login-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Verifying Session...';

    const payload = {
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
    };

    try {
      const resp = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (resp.status === 200) {
        showToast('Authentication successful!', 'success');
        window.location.href = '/dashboard';
      } else {
        showToast(data.message || 'Invalid credentials.', 'danger');
        btn.disabled = false;
        btn.textContent = 'Authenticate & Unlock';
      }
    } catch (err) {
      showToast('Network error during login.', 'danger');
      btn.disabled = false;
      btn.textContent = 'Authenticate & Unlock';
    }
  });
}

function calculatePasswordStrength(pwd) {
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
  if (/\d/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score;
}

function updateMeterUI(score, bar, label) {
  const levels = [
    { text: 'Strength: Very Weak', color: '#F43F5E', width: '25%' },
    { text: 'Strength: Weak', color: '#F59E0B', width: '50%' },
    { text: 'Strength: Good', color: '#38BDF8', width: '75%' },
    { text: 'Strength: Strong (ECC Safe)', color: '#10B981', width: '100%' },
  ];

  if (score === 0) {
    bar.style.width = '0%';
    label.textContent = 'Password Strength: Empty';
    return;
  }

  const level = levels[score - 1];
  bar.style.width = level.width;
  bar.style.backgroundColor = level.color;
  label.textContent = level.text;
  label.style.color = level.color;
}
```

---

## Stage 6: User Dashboard & Live Transfer Telemetry

### 6.1 Objective
Construct the user's primary post-login command center displaying operational telemetry: count of pending files awaiting decryption, total sent volume, recent activity stream, and quick-action triggers.

### 6.2 Files to Create
1. `app/templates/dashboard/index.html`
2. `app/static/css/pages/dashboard.css`
3. `app/static/js/dashboard.js`

---

### 6.3 Code Implementation

#### File 1: `app/templates/dashboard/index.html`
```html
{% extends 'base.html' %}
{% block title %}Dashboard{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/dashboard.css') }}">
{% endblock %}

{% block content %}
<div class="dashboard-container">
  <!-- Top Welcome Header -->
  <div class="dashboard-header">
    <div>
      <h1 class="welcome-heading">Welcome back, <span class="gradient-text">{{ current_user.username }}</span></h1>
      <p class="welcome-sub">Cryptographic vault operational • Curve: NIST P-256</p>
    </div>
    <div class="dashboard-cta">
      <a href="/transfer/send" class="btn btn-primary">+ Send Encrypted File</a>
    </div>
  </div>

  <!-- Metric Counters Grid -->
  <div class="metrics-grid">
    <div class="glass-card metric-card">
      <div class="metric-icon-box warning">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
      </div>
      <div>
        <div class="metric-value" id="stat-pending">-</div>
        <div class="metric-label">Pending Decryption</div>
      </div>
    </div>

    <div class="glass-card metric-card">
      <div class="metric-icon-box cyan">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
      </div>
      <div>
        <div class="metric-value" id="stat-received">-</div>
        <div class="metric-label">Total Received</div>
      </div>
    </div>

    <div class="glass-card metric-card">
      <div class="metric-icon-box indigo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </div>
      <div>
        <div class="metric-value" id="stat-sent">-</div>
        <div class="metric-label">Total Sent</div>
      </div>
    </div>
  </div>

  <!-- Recent Transfers Section -->
  <div class="dashboard-tables-grid">
    <!-- Inbound Files Awaiting Decryption -->
    <div class="glass-card section-card">
      <div class="card-header-flex">
        <h3>Incoming Files Requiring Action</h3>
        <a href="/transfer/inbox" class="card-link">View All Inbox &rarr;</a>
      </div>

      <div class="transfer-list" id="pending-transfer-list">
        <div class="skeleton-row">Loading pending cryptographic transfers...</div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script type="module" src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```

#### File 2: `app/static/js/dashboard.js`
```javascript
/**
 * app/static/js/dashboard.js — Dashboard Telemetry Loader
 */
import { apiRequest } from './api.js';
import { openDecryptModal } from './decrypt-modal.js';

async function loadDashboardData() {
  try {
    const resp = await apiRequest('/dashboard');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      document.getElementById('stat-pending').textContent = data.stats.pending_received;
      document.getElementById('stat-received').textContent = data.stats.total_received;
      document.getElementById('stat-sent').textContent = data.stats.total_sent;

      renderPendingList(data.recent_received.filter(t => t.status === 'PENDING'));
    }
  } catch (err) {
    console.error('Error fetching dashboard stats:', err);
  }
}

function renderPendingList(transfers) {
  const container = document.getElementById('pending-transfer-list');
  if (!container) return;

  if (transfers.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>No files currently waiting for decryption.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = transfers.map(t => `
    <div class="transfer-item">
      <div class="file-info-col">
        <span class="filename">${escapeHtml(t.original_filename)}</span>
        <span class="filesize">${formatBytes(t.file_size_bytes)} • From: ${escapeHtml(t.sender_username)}</span>
      </div>
      <div class="action-col">
        <button class="btn btn-primary btn-sm decrypt-trigger" data-id="${t.transfer_id}" data-filename="${t.original_filename}">
          🔓 Decrypt & Download
        </button>
      </div>
    </div>
  `).join('');

  container.querySelectorAll('.decrypt-trigger').forEach(btn => {
    btn.addEventListener('click', () => {
      openDecryptModal(btn.getAttribute('data-id'), btn.getAttribute('data-filename'));
    });
  });
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(str) {
  const p = document.createElement('p');
  p.textContent = str;
  return p.innerHTML;
}

document.addEventListener('DOMContentLoaded', loadDashboardData);
```

---

## Stage 7: Send File Portal & Dynamic Drag-and-Drop Dropzone

### 7.1 Objective
Build the secure file transmission interface featuring recipient live verification, visual drag-and-drop file staging, client-side size enforcement, and upload progress animation.

### 7.2 Files to Create
1. `app/templates/transfer/send.html`
2. `app/static/js/dropzone.js`
3. `app/static/css/pages/transfer.css`

---

### 7.3 Code Implementation

#### File 1: `app/templates/transfer/send.html`
```html
{% extends 'base.html' %}
{% block title %}Send Encrypted File{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/pages/transfer.css') }}">
{% endblock %}

{% block content %}
<div class="transfer-page-wrapper">
  <div class="glass-card transfer-card-main">
    <div class="transfer-card-header">
      <span class="crypto-badge">AES-256-GCM + ECIES</span>
      <h2>Send Encrypted File</h2>
      <p>File is encrypted with a unique symmetric key and encapsulated with the receiver's ECC public key.</p>
    </div>

    <form id="send-file-form" novalidate>
      <!-- Recipient Selector -->
      <div class="form-group">
        <label for="receiver_id">Select Recipient</label>
        <select id="receiver_id" name="receiver_id" required>
          <option value="">-- Choose recipient --</option>
        </select>
        <div id="recipient-key-indicator" class="key-status-box hidden">
          <span class="key-dot active"></span>
          <span>Verified NIST P-256 Public Key loaded</span>
        </div>
      </div>

      <!-- File Dropzone -->
      <div class="form-group">
        <label>File Payload</label>
        <div id="dropzone" class="dropzone">
          <input type="file" id="file-input" class="file-input-hidden" required>
          <div class="dropzone-content" id="dropzone-idle-content">
            <svg class="dropzone-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <p class="dropzone-text">Drag & drop your file here, or <span class="highlight">browse</span></p>
            <p class="dropzone-sub">Max file size: 50 MB (Any file format)</p>
          </div>

          <!-- Staged File Inspector View -->
          <div class="dropzone-staged-file hidden" id="dropzone-staged-content">
            <div class="staged-meta">
              <span class="staged-name" id="staged-file-name">document.pdf</span>
              <span class="staged-size" id="staged-file-size">4.2 MB</span>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" id="btn-remove-file">Change File</button>
          </div>
        </div>
      </div>

      <!-- Live Encryption & Transmission Progress -->
      <div id="progress-container" class="progress-box hidden">
        <div class="progress-label-row">
          <span id="progress-stage-label">Encrypting & Streaming Payload...</span>
          <span id="progress-percentage">0%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" id="progress-fill"></div>
        </div>
      </div>

      <button type="submit" class="btn btn-primary btn-block btn-lg" id="btn-submit-transfer">
        <span>🚀 Encrypt & Dispatch File</span>
      </button>
    </form>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script type="module" src="{{ url_for('static', filename='js/dropzone.js') }}"></script>
{% endblock %}
```

#### File 2: `app/static/js/dropzone.js`
```javascript
/**
 * app/static/js/dropzone.js — Drag & Drop File Controller & Upload
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

let stagedFile = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadRecipients();
  initDropzoneEvents();
  initFormSubmit();
});

async function loadRecipients() {
  const select = document.getElementById('receiver_id');
  if (!select) return;

  try {
    const resp = await apiRequest('/auth/users');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      data.users.forEach(user => {
        const option = document.createElement('option');
        option.value = user.id;
        option.textContent = `${user.username} (${user.email})`;
        select.appendChild(option);
      });
    }
  } catch (err) {
    showToast('Failed to load user list', 'danger');
  }
}

function initDropzoneEvents() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const idleContent = document.getElementById('dropzone-idle-content');
  const stagedContent = document.getElementById('dropzone-staged-content');
  const btnRemove = document.getElementById('btn-remove-file');

  dropzone.addEventListener('click', (e) => {
    if (e.target !== btnRemove) {
      fileInput.click();
    }
  });

  ['dragenter', 'dragover'].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  btnRemove.addEventListener('click', (e) => {
    e.stopPropagation();
    stagedFile = null;
    fileInput.value = '';
    idleContent.classList.remove('hidden');
    stagedContent.classList.add('hidden');
  });
}

function handleFileSelected(file) {
  const MAX_SIZE = 50 * 1024 * 1024; // 50MB
  if (file.size > MAX_SIZE) {
    showToast('File exceeds 50 MB limit!', 'danger');
    return;
  }

  stagedFile = file;
  document.getElementById('staged-file-name').textContent = file.name;
  document.getElementById('staged-file-size').textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';

  document.getElementById('dropzone-idle-content').classList.add('hidden');
  document.getElementById('dropzone-staged-content').classList.remove('hidden');
}

function initFormSubmit() {
  const form = document.getElementById('send-file-form');
  const btnSubmit = document.getElementById('btn-submit-transfer');
  const progressBox = document.getElementById('progress-container');
  const progressFill = document.getElementById('progress-fill');
  const progressPercent = document.getElementById('progress-percentage');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const receiverId = document.getElementById('receiver_id').value;

    if (!receiverId) {
      showToast('Please select a recipient.', 'warning');
      return;
    }
    if (!stagedFile) {
      showToast('Please attach a file to send.', 'warning');
      return;
    }

    const formData = new FormData();
    formData.append('file', stagedFile);
    formData.append('receiver_id', receiverId);

    btnSubmit.disabled = true;
    progressBox.classList.remove('hidden');
    progressFill.style.width = '35%';
    progressPercent.textContent = '35%';

    try {
      progressFill.style.width = '70%';
      progressPercent.textContent = '70%';

      const resp = await apiRequest('/transfer/send', {
        method: 'POST',
        body: formData,
      });

      const data = await resp.json();

      if (resp.status === 201) {
        progressFill.style.width = '100%';
        progressPercent.textContent = '100%';
        showToast('File encrypted & sent successfully!', 'success');
        setTimeout(() => {
          window.location.href = '/transfer/history';
        }, 1200);
      } else {
        showToast(data.message || 'Transfer failed.', 'danger');
        btnSubmit.disabled = false;
        progressBox.classList.add('hidden');
      }
    } catch (err) {
      showToast('Transmission error.', 'danger');
      btnSubmit.disabled = false;
      progressBox.classList.add('hidden');
    }
  });
}
```

---

## Stage 8: Secure Inbox, Decryption Modal & Binary Streaming

### 8.1 Objective
Implement the recipient's secure inbox listing pending inbound encrypted transfers, and a password-prompt modal that unlocks the private key and streams decrypted files directly to local storage.

### 8.2 Files to Create
1. `app/templates/transfer/inbox.html`
2. `app/templates/components/_decrypt_modal.html`
3. `app/static/js/decrypt-modal.js`

---

### 8.3 Code Implementation

#### File 1: `app/templates/components/_decrypt_modal.html`
```html
<div class="modal-overlay hidden" id="decrypt-modal-overlay">
  <div class="glass-card modal-container">
    <div class="modal-header">
      <div class="modal-icon-badge">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
          <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
        </svg>
      </div>
      <div>
        <h3>Unlock Private Key & Decrypt</h3>
        <p class="modal-sub" id="decrypt-modal-filename">document.pdf</p>
      </div>
      <button class="modal-close-btn" id="btn-close-decrypt-modal">&times;</button>
    </div>

    <form id="decrypt-form" class="modal-form">
      <input type="hidden" id="decrypt-transfer-id" value="">

      <div class="security-explanation">
        <p>🔒 <strong>How decryption operates:</strong></p>
        <ol>
          <li>Your password decrypts your stored ECC private key in memory.</li>
          <li>ECDH with sender's public key recalculates the shared secret.</li>
          <li>HKDF derives the AES-256 session key to decrypt the payload.</li>
          <li>SHA-256 verifies 100% byte integrity before delivery.</li>
        </ol>
      </div>

      <div class="form-group">
        <label for="decrypt-password">Account Password</label>
        <input type="password" id="decrypt-password" name="password" required placeholder="Enter password to unlock private key" autocomplete="current-password">
      </div>

      <div class="modal-actions">
        <button type="button" class="btn btn-secondary" id="btn-cancel-decrypt">Cancel</button>
        <button type="submit" class="btn btn-primary" id="btn-submit-decrypt">
          <span>🔓 Decrypt & Download</span>
        </button>
      </div>
    </form>
  </div>
</div>
```

#### File 2: `app/static/js/decrypt-modal.js`
```javascript
/**
 * app/static/js/decrypt-modal.js — Decrypt Verification & Binary Streamer
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

const overlay = document.getElementById('decrypt-modal-overlay');
const form = document.getElementById('decrypt-form');
const inputTransferId = document.getElementById('decrypt-transfer-id');
const inputPassword = document.getElementById('decrypt-password');
const filenameLabel = document.getElementById('decrypt-modal-filename');

export function openDecryptModal(transferId, filename) {
  if (!overlay) return;
  inputTransferId.value = transferId;
  filenameLabel.textContent = filename || 'Encrypted File';
  inputPassword.value = '';
  overlay.classList.remove('hidden');
  inputPassword.focus();
}

export function closeDecryptModal() {
  if (!overlay) return;
  overlay.classList.add('hidden');
  inputPassword.value = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const btnClose = document.getElementById('btn-close-decrypt-modal');
  const btnCancel = document.getElementById('btn-cancel-decrypt');

  if (btnClose) btnClose.addEventListener('click', closeDecryptModal);
  if (btnCancel) btnCancel.addEventListener('click', closeDecryptModal);

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const transferId = inputTransferId.value;
      const password = inputPassword.value;
      const btn = document.getElementById('btn-submit-decrypt');

      if (!password) {
        showToast('Password is required to unlock private key.', 'warning');
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Decrypting payload...';

      try {
        const resp = await apiRequest(`/transfer/download/${transferId}`, {
          method: 'POST',
          body: JSON.stringify({ password }),
        });

        if (!resp.ok) {
          const errData = await resp.json();
          showToast(errData.message || 'Decryption failed. Check password.', 'danger');
          btn.disabled = false;
          btn.textContent = '🔓 Decrypt & Download';
          return;
        }

        // Parse filename from Content-Disposition header
        const disposition = resp.headers.get('Content-Disposition') || '';
        let filename = 'decrypted_file';
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) filename = match[1];

        // Receive Binary Blob & Trigger Browser Download
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

        showToast('File decrypted & integrity verified!', 'success');
        closeDecryptModal();

        // Refresh inbox state
        setTimeout(() => window.location.reload(), 1000);
      } catch (err) {
        showToast('Network error during decryption.', 'danger');
        btn.disabled = false;
        btn.textContent = '🔓 Decrypt & Download';
      }
    });
  }
});
```

---

## Stage 9: Transfer History, Audit Ledger & Filtering

### 9.1 Objective
Construct an immutable, searchable history audit table allowing users to track sent/received files, verify SHA-256 integrity checksums, and filter by transfer status.

### 9.2 Files to Create
1. `app/templates/transfer/history.html`
2. `app/static/js/history.js`

---

### 9.3 Code Implementation

#### File 1: `app/templates/transfer/history.html`
```html
{% extends 'base.html' %}
{% block title %}Transfer Audit Ledger{% endblock %}

{% block content %}
<div class="history-page-container">
  <div class="page-title-row">
    <div>
      <h2>Transfer Audit Ledger</h2>
      <p class="subtitle">Complete verifiable history of encrypted outbound and inbound transfers.</p>
    </div>
    <div class="filter-group">
      <input type="text" id="history-search" class="search-input" placeholder="Search by filename or user...">
      <select id="direction-filter" class="filter-select">
        <option value="all">All Transfers</option>
        <option value="sent">Outbound (Sent)</option>
        <option value="received">Inbound (Received)</option>
      </select>
    </div>
  </div>

  <div class="glass-card table-card">
    <table class="data-table" id="history-table">
      <thead>
        <tr>
          <th>Direction</th>
          <th>File Details</th>
          <th>Counterparty</th>
          <th>SHA-256 Checksum</th>
          <th>Date</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody id="history-table-body">
        <tr><td colspan="7" class="loading-td">Loading audit records...</td></tr>
      </tbody>
    </table>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script type="module" src="{{ url_for('static', filename='js/history.js') }}"></script>
{% endblock %}
```

#### File 2: `app/static/js/history.js`
```javascript
/**
 * app/static/js/history.js — History Audit Table & Live Filters
 */
import { apiRequest } from './api.js';
import { openDecryptModal } from './decrypt-modal.js';

let allTransfers = [];

document.addEventListener('DOMContentLoaded', async () => {
  await fetchHistory();
  initFilters();
});

async function fetchHistory() {
  try {
    const resp = await apiRequest('/transfer/history');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      allTransfers = data.transfers;
      renderTable(allTransfers);
    }
  } catch (err) {
    console.error('History fetch error:', err);
  }
}

function renderTable(items) {
  const tbody = document.getElementById('history-table-body');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty-td">No transfer records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(t => {
    const isOutbound = t.direction === 'sent';
    const statusClass = t.status.toLowerCase();
    const shortHash = t.sha256_hash ? `${t.sha256_hash.substring(0, 8)}...${t.sha256_hash.substring(56)}` : 'N/A';

    return `
      <tr>
        <td>
          <span class="direction-badge ${isOutbound ? 'outbound' : 'inbound'}">
            ${isOutbound ? '↗ Sent' : '↙ Received'}
          </span>
        </td>
        <td>
          <div class="file-name-cell">${escapeHtml(t.original_filename)}</div>
          <div class="file-sub-cell">${(t.file_size_bytes / 1024).toFixed(1)} KB</div>
        </td>
        <td>${escapeHtml(isOutbound ? t.receiver_username : t.sender_username)}</td>
        <td>
          <code class="hash-code" data-copy="${t.sha256_hash}" title="Click to copy SHA-256">${shortHash}</code>
        </td>
        <td>${new Date(t.sent_at).toLocaleDateString()}</td>
        <td>
          <span class="status-pill ${statusClass}">${t.status}</span>
        </td>
        <td>
          ${!isOutbound && t.status === 'PENDING' ? `
            <button class="btn btn-primary btn-xs decrypt-btn" data-id="${t.transfer_id}" data-filename="${t.original_filename}">
              Decrypt
            </button>
          ` : `
            <span class="text-muted">—</span>
          `}
        </td>
      </tr>
    `;
  }).join('');

  tbody.querySelectorAll('.decrypt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      openDecryptModal(btn.getAttribute('data-id'), btn.getAttribute('data-filename'));
    });
  });
}

function initFilters() {
  const searchInput = document.getElementById('history-search');
  const dirSelect = document.getElementById('direction-filter');

  const filterHandler = () => {
    const query = searchInput.value.toLowerCase();
    const dir = dirSelect.value;

    const filtered = allTransfers.filter(t => {
      const matchDir = dir === 'all' || t.direction === dir;
      const matchQuery = t.original_filename.toLowerCase().includes(query) ||
        (t.sender_username && t.sender_username.toLowerCase().includes(query)) ||
        (t.receiver_username && t.receiver_username.toLowerCase().includes(query));
      return matchDir && matchQuery;
    });

    renderTable(filtered);
  };

  searchInput.addEventListener('input', filterHandler);
  dirSelect.addEventListener('change', filterHandler);
}

function escapeHtml(str) {
  const p = document.createElement('p');
  p.textContent = str;
  return p.innerHTML;
}
```

---

## Stage 10: Cryptographic Profile & Key Management

### 10.1 Objective
Provide users with a cryptographic transparency page displaying their NIST P-256 public key (PEM format), key fingerprint (SHA-256 digest), and storage security parameters.

### 10.2 Files to Create
1. `app/templates/profile/index.html`

---

### 10.3 Code Implementation

#### File 1: `app/templates/profile/index.html`
```html
{% extends 'base.html' %}
{% block title %}Cryptographic Profile & Keys{% endblock %}

{% block content %}
<div class="profile-container">
  <div class="glass-card profile-card">
    <div class="profile-header-row">
      <div class="avatar-large">{{ current_user.username[0]|upper }}</div>
      <div>
        <h2>{{ current_user.username }}</h2>
        <p class="profile-email">{{ current_user.email }}</p>
      </div>
      <span class="crypto-badge">Curve: NIST P-256 (SECP256R1)</span>
    </div>

    <hr class="profile-divider">

    <div class="key-section">
      <div class="key-header">
        <h3>Public Key (PEM Encoded)</h3>
        <button class="btn btn-secondary btn-sm" id="btn-copy-pubkey" data-copy="{{ current_user.ecc_key.public_key_pem if current_user.ecc_key else '' }}">
          📋 Copy Public Key
        </button>
      </div>

      <textarea class="pem-display" readonly rows="8">
{{ current_user.ecc_key.public_key_pem if current_user.ecc_key else 'Public key not generated' }}
      </textarea>
    </div>

    <div class="security-meta-grid">
      <div class="meta-item">
        <label>Key Fingerprint (SHA-256)</label>
        <code class="hash-code">{{ current_user.ecc_key.fingerprint if current_user.ecc_key else 'N/A' }}</code>
      </div>
      <div class="meta-item">
        <label>Private Key Protection</label>
        <span class="shield-badge">🛡️ AES-256-GCM + PBKDF2 (100,000 rounds)</span>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## Stage 11: Flask Route Controllers & Integration Verification

### 11.1 Objective
Connect the Flask backend routes to serve the newly created HTML5 Jinja2 views, ensuring content negotiation (HTML rendering for browser visits, JSON for API calls).

### 11.2 Routes Mapping Summary

| Web Route | Blueprint | Template Rendered | Protection |
|:---|:---|:---|:---|
| `GET /` | `main_bp.index` | `index.html` | Public |
| `GET /auth/login` | `auth_bp.login_page` | `auth/login.html` | Anonymous only |
| `GET /auth/register` | `auth_bp.register_page` | `auth/register.html` | Anonymous only |
| `GET /dashboard` | `main_bp.dashboard_page` | `dashboard/index.html` | `login_required` |
| `GET /transfer/send` | `transfer_bp.send_page` | `transfer/send.html` | `login_required` |
| `GET /transfer/inbox` | `transfer_bp.inbox_page` | `transfer/inbox.html` | `login_required` |
| `GET /transfer/history` | `transfer_bp.history_page` | `transfer/history.html` | `login_required` |
| `GET /profile` | `main_bp.profile_page` | `profile/index.html` | `login_required` |

---

## Complete Verification & Testing Checklist

Execute the following checklist once all files are in place:

```
[ ] 1. Start application: python run.py
[ ] 2. Visit http://127.0.0.1:5000/ -> Landing page renders with CSS tokens and dark theme.
[ ] 3. Click "Get Started" -> Live password strength bar reacts dynamically.
[ ] 4. Register new user "alice" -> User created, redirected to login.
[ ] 5. Log in as "alice" -> Session established, Dashboard displays 0 pending, 0 sent.
[ ] 6. Go to /transfer/send -> Drag and drop a test file. Progress bar updates.
[ ] 7. In a separate private window, log in as recipient "bob".
[ ] 8. Bob opens /transfer/inbox -> File appears with [ PENDING ] badge.
[ ] 9. Bob clicks "Decrypt & Download" -> Password modal prompts for Bob's password.
[ ] 10. Enter password -> File streams to local disk, exactly matching original SHA-256 checksum!
```

---
*End of Stage-by-Stage Frontend Implementation Guide.*
