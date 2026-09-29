/**
 * app/static/js/dashboard.js — Real-Time Dashboard Polling Engine
 * ================================================================
 * Polls /dashboard every 10 seconds and updates stats + inbox live.
 * Uses smooth animated number transitions and shows a live status dot.
 */
import { apiRequest } from './api.js';
import { openDecryptModal } from './decrypt-modal.js';

/* ── Config ─────────────────────────────────────────────── */
const POLL_INTERVAL_MS = 10_000;   // 10 seconds
const ANIM_DURATION_MS = 600;      // counter animation duration

/* ── State ──────────────────────────────────────────────── */
let pollTimer       = null;
let previousStats   = null;
let previousPending = null;

/* ── Boot ───────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  injectStatusIndicator();
  fetchAndRender();
  pollTimer = setInterval(fetchAndRender, POLL_INTERVAL_MS);

  // Pause polling when tab is hidden, resume when visible
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      clearInterval(pollTimer);
    } else {
      fetchAndRender();
      pollTimer = setInterval(fetchAndRender, POLL_INTERVAL_MS);
    }
  });
});

/* ── Fetch & Render ─────────────────────────────────────── */
async function fetchAndRender() {
  pulseStatusDot('syncing');
  try {
    const resp = await apiRequest('/dashboard');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      updateStats(data.stats);
      updatePendingInbox(data.recent_received.filter(t => t.status === 'PENDING'));
      pulseStatusDot('live');
    } else {
      pulseStatusDot('error');
    }
  } catch {
    pulseStatusDot('error');
  }
}

/* ── Stat Counters with Animated Number Roll ────────────── */
function updateStats(stats) {
  animateCounter('stat-pending',  stats.pending_received);
  animateCounter('stat-received', stats.total_received);
  animateCounter('stat-sent',     stats.total_sent);

  if (previousStats !== null) {
    if (stats.pending_received > previousStats.pending_received) {
      flashCard('stat-pending');
      showNewTransferBadge();
    }
    if (stats.total_received > previousStats.total_received) {
      flashCard('stat-received');
    }
    if (stats.total_sent > previousStats.total_sent) {
      flashCard('stat-sent');
    }
  }

  previousStats = { ...stats };
}

function animateCounter(elementId, newValue) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const current = parseInt(el.textContent, 10) || 0;
  if (current === newValue) return;

  const start = performance.now();
  const delta = newValue - current;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / ANIM_DURATION_MS, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);  // ease-out cubic
    el.textContent = Math.round(current + delta * eased);
    if (progress < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}

/* ── Pending Inbox ──────────────────────────────────────── */
function updatePendingInbox(transfers) {
  const container = document.getElementById('pending-transfer-list');
  if (!container) return;

  // Only re-render if transfer IDs changed
  const key = transfers.map(t => t.transfer_id).join(',');
  if (key === previousPending) return;
  previousPending = key;

  if (transfers.length === 0) {
    container.style.opacity = '0';
    setTimeout(() => {
      container.innerHTML = `<div class="empty-state"><p>No files currently waiting for decryption.</p></div>`;
      container.style.opacity = '1';
    }, 220);
    return;
  }

  container.style.opacity = '0';
  container.style.transition = 'opacity 0.22s ease';

  setTimeout(() => {
    container.innerHTML = transfers.map(t => `
      <div class="transfer-item" data-id="${t.transfer_id}">
        <div class="file-info-col">
          <span class="filename">${escapeHtml(t.original_filename)}</span>
          <span class="filesize">${formatBytes(t.file_size_bytes)} • From: ${escapeHtml(t.sender_username)}</span>
        </div>
        <div class="action-col">
          <button class="btn btn-primary btn-sm decrypt-trigger"
            data-id="${t.transfer_id}"
            data-filename="${t.original_filename}">
            Decrypt &amp; Download
          </button>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.decrypt-trigger').forEach(btn => {
      btn.addEventListener('click', () => {
        openDecryptModal(btn.getAttribute('data-id'), btn.getAttribute('data-filename'));
      });
    });

    container.style.opacity = '1';
  }, 220);
}

/* ── Live Status Indicator ──────────────────────────────── */
function injectStatusIndicator() {
  const header = document.querySelector('.dashboard-header');
  if (!header || document.getElementById('rt-status')) return;

  const indicator = document.createElement('div');
  indicator.id        = 'rt-status';
  indicator.className = 'rt-status';
  indicator.innerHTML = `
    <span class="rt-dot" id="rt-dot"></span>
    <span class="rt-label" id="rt-label">Connecting…</span>
  `;
  // Insert before the CTA button group
  const cta = header.querySelector('.dashboard-cta');
  if (cta) header.insertBefore(indicator, cta);
  else header.appendChild(indicator);
}

function pulseStatusDot(state) {
  const dot   = document.getElementById('rt-dot');
  const label = document.getElementById('rt-label');
  if (!dot || !label) return;

  dot.className = 'rt-dot';

  if (state === 'live') {
    dot.classList.add('rt-live');
    label.textContent = 'Live';
  } else if (state === 'syncing') {
    dot.classList.add('rt-syncing');
    label.textContent = 'Syncing…';
  } else {
    dot.classList.add('rt-error');
    label.textContent = 'Offline';
  }
}

/* ── Flash Highlight on Stat Change ─────────────────────── */
function flashCard(statId) {
  const el = document.getElementById(statId);
  if (!el) return;
  const card = el.closest('.metric-card');
  if (!card) return;
  card.classList.add('metric-flash');
  setTimeout(() => card.classList.remove('metric-flash'), 1200);
}

function showNewTransferBadge() {
  const header = document.querySelector('.card-header-flex h3');
  if (!header) return;

  let badge = document.getElementById('new-transfer-badge');
  if (!badge) {
    badge = document.createElement('span');
    badge.id        = 'new-transfer-badge';
    badge.className = 'new-arrival-badge';
    badge.textContent = 'New';
    header.appendChild(badge);
  }
  badge.classList.add('badge-pop');
  setTimeout(() => badge.classList.remove('badge-pop'), 2000);
}

/* ── Utilities ──────────────────────────────────────────── */
function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 Bytes';
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

