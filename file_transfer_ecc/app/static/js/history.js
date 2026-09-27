/**
 * app/static/js/history.js — History Audit Table & Live Filters
 */
import { apiRequest } from './api.js';
import { openDecryptModal } from './decrypt-modal.js';
import { initClipboardButtons } from './clipboard.js';

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
            ${isOutbound ? 'Sent' : 'Received'}
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

  initClipboardButtons();
}

function initFilters() {
  const searchInput = document.getElementById('history-search');
  const dirSelect = document.getElementById('direction-filter');

  if (!searchInput || !dirSelect) return;

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
