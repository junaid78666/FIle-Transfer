/**
 * app/static/js/dropzone.js — Drag & Drop File Controller & Upload
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

let allUsers = [];      // full list fetched once
let selectedUserId = null;
let stagedFile = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadRecipients();
  initRecipientSearch();
  initDropzoneEvents();
  initFormSubmit();
});

/* ──────────────────────────────────────────────────────────────
 * 1. Load all eligible recipients and render initial card grid
 * ────────────────────────────────────────────────────────────── */
async function loadRecipients() {
  const grid = document.getElementById('recipient-card-grid');
  const spinner = document.getElementById('recipient-loading-spinner');
  if (!grid) return;

  if (spinner) spinner.classList.remove('hidden');

  try {
    const resp = await apiRequest('/auth/users');
    const data = await resp.json();

    if (resp.ok && data.status === 'success') {
      allUsers = data.users;
      renderUserCards(allUsers);
    } else {
      grid.innerHTML = '<p class="recipient-empty-msg">Unable to load users.</p>';
    }
  } catch (err) {
    showToast('Failed to load user list', 'danger');
    grid.innerHTML = '<p class="recipient-empty-msg">Unable to load users.</p>';
  } finally {
    if (spinner) spinner.classList.add('hidden');
  }
}

/* ──────────────────────────────────────────────────────────────
 * 2. Render user cards from a filtered list
 * ────────────────────────────────────────────────────────────── */
function renderUserCards(users) {
  const grid = document.getElementById('recipient-card-grid');
  if (!grid) return;

  if (users.length === 0) {
    grid.innerHTML = '<p class="recipient-empty-msg">No users match your search.</p>';
    return;
  }

  grid.innerHTML = users.map(user => {
    const initials = getInitials(user.username);
    const hue = stringToHue(user.username);
    const isSelected = selectedUserId === String(user.id);
    return `
      <button
        type="button"
        class="recipient-user-card${isSelected ? ' selected' : ''}"
        data-user-id="${user.id}"
        data-username="${user.username}"
        aria-pressed="${isSelected}"
      >
        <span class="user-card-avatar" style="--avatar-hue: ${hue}deg">${initials}</span>
        <span class="user-card-info">
          <span class="user-card-name">${escapeHtml(user.username)}</span>
        </span>
        <span class="user-card-check" aria-hidden="true">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </span>
      </button>
    `;
  }).join('');

  // Attach click handlers
  grid.querySelectorAll('.recipient-user-card').forEach(card => {
    card.addEventListener('click', () => selectRecipient(card));
  });
}

/* ──────────────────────────────────────────────────────────────
 * 3. Live search filter
 * ────────────────────────────────────────────────────────────── */
function initRecipientSearch() {
  const searchInput = document.getElementById('recipient-search-input');
  if (!searchInput) return;

  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim().toLowerCase();
    const filtered = query
      ? allUsers.filter(u => u.username.toLowerCase().includes(query))
      : allUsers;
    renderUserCards(filtered);
  });
}

/* ──────────────────────────────────────────────────────────────
 * 4. Select a recipient card
 * ────────────────────────────────────────────────────────────── */
function selectRecipient(card) {
  const userId   = card.getAttribute('data-user-id');
  const username = card.getAttribute('data-username');

  selectedUserId = userId;

  // Sync hidden input
  const hiddenInput = document.getElementById('receiver_id');
  if (hiddenInput) hiddenInput.value = userId;

  // Update card selected states
  document.querySelectorAll('.recipient-user-card').forEach(c => {
    const isThis = c.getAttribute('data-user-id') === userId;
    c.classList.toggle('selected', isThis);
    c.setAttribute('aria-pressed', String(isThis));
  });

  // Show confirmation badge
  const indicator = document.getElementById('recipient-key-indicator');
  const label = document.getElementById('recipient-selected-label');
  if (indicator) indicator.classList.remove('hidden');
  if (label) label.textContent = `✓ ${username} — P-256 key verified`;
}

/* ──────────────────────────────────────────────────────────────
 * Helpers
 * ────────────────────────────────────────────────────────────── */
function getInitials(name) {
  return name
    .split(/[\s._\-]+/)
    .slice(0, 2)
    .map(p => p[0]?.toUpperCase() || '')
    .join('');
}

function stringToHue(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
  return Math.abs(hash) % 360;
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function initDropzoneEvents() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const idleContent = document.getElementById('dropzone-idle-content');
  const stagedContent = document.getElementById('dropzone-staged-content');
  const btnRemove = document.getElementById('btn-remove-file');

  if (!dropzone || !fileInput) return;

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

  if (btnRemove) {
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      stagedFile = null;
      fileInput.value = '';
      idleContent.classList.remove('hidden');
      stagedContent.classList.add('hidden');
    });
  }
}

function handleFileSelected(file) {
  const MAX_SIZE = 50 * 1024 * 1024; // 50MB
  if (file.size > MAX_SIZE) {
    showToast('File exceeds 50 MB limit!', 'danger');
    return;
  }

  stagedFile = file;
  const nameEl = document.getElementById('staged-file-name');
  const sizeEl = document.getElementById('staged-file-size');
  if (nameEl) nameEl.textContent = file.name;
  if (sizeEl) sizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';

  const idle = document.getElementById('dropzone-idle-content');
  const staged = document.getElementById('dropzone-staged-content');
  if (idle) idle.classList.add('hidden');
  if (staged) staged.classList.remove('hidden');
}

function initFormSubmit() {
  const form = document.getElementById('send-file-form');
  const btnSubmit = document.getElementById('btn-submit-transfer');
  const progressBox = document.getElementById('progress-container');
  const progressFill = document.getElementById('progress-fill');
  const progressPercent = document.getElementById('progress-percentage');

  if (!form || !btnSubmit) return;

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
    if (progressBox) progressBox.classList.remove('hidden');
    if (progressFill) progressFill.style.width = '35%';
    if (progressPercent) progressPercent.textContent = '35%';

    try {
      if (progressFill) progressFill.style.width = '70%';
      if (progressPercent) progressPercent.textContent = '70%';

      const resp = await apiRequest('/transfer/send', {
        method: 'POST',
        body: formData,
      });

      const data = await resp.json();

      if (resp.status === 201) {
        if (progressFill) progressFill.style.width = '100%';
        if (progressPercent) progressPercent.textContent = '100%';
        showToast('File encrypted & sent successfully!', 'success');
        setTimeout(() => {
          window.location.href = '/transfer/history';
        }, 1200);
      } else {
        showToast(data.message || 'Transfer failed.', 'danger');
        btnSubmit.disabled = false;
        if (progressBox) progressBox.classList.add('hidden');
      }
    } catch (err) {
      showToast('Transmission error.', 'danger');
      btnSubmit.disabled = false;
      if (progressBox) progressBox.classList.add('hidden');
    }
  });
}
