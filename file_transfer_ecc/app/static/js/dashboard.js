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
      const pCount = document.getElementById('stat-pending');
      const rCount = document.getElementById('stat-received');
      const sCount = document.getElementById('stat-sent');

      if (pCount) pCount.textContent = data.stats.pending_received;
      if (rCount) rCount.textContent = data.stats.total_received;
      if (sCount) sCount.textContent = data.stats.total_sent;

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
          Decrypt & Download
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

document.addEventListener('DOMContentLoaded', loadDashboardData);
