/**
 * app/static/js/decrypt-modal.js — Decrypt Verification & Binary Streamer
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

export function openDecryptModal(transferId, filename) {
  const overlay = document.getElementById('decrypt-modal-overlay');
  const inputTransferId = document.getElementById('decrypt-transfer-id');
  const inputPassword = document.getElementById('decrypt-password');
  const filenameLabel = document.getElementById('decrypt-modal-filename');

  if (!overlay) return;
  inputTransferId.value = transferId;
  if (filenameLabel) filenameLabel.textContent = filename || 'Encrypted File';
  if (inputPassword) {
    inputPassword.value = '';
    setTimeout(() => inputPassword.focus(), 100);
  }
  overlay.classList.remove('hidden');
}

export function closeDecryptModal() {
  const overlay = document.getElementById('decrypt-modal-overlay');
  const inputPassword = document.getElementById('decrypt-password');
  if (!overlay) return;
  overlay.classList.add('hidden');
  if (inputPassword) inputPassword.value = '';
}

document.addEventListener('DOMContentLoaded', () => {
  const btnClose = document.getElementById('btn-close-decrypt-modal');
  const btnCancel = document.getElementById('btn-cancel-decrypt');
  const form = document.getElementById('decrypt-form');
  const inputTransferId = document.getElementById('decrypt-transfer-id');
  const inputPassword = document.getElementById('decrypt-password');

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
          showToast(errData.message || 'Decryption failed. Invalid password.', 'danger');
          btn.disabled = false;
          btn.textContent = 'Decrypt & Download';
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

        // Refresh view state after brief pause
        setTimeout(() => window.location.reload(), 1200);
      } catch (err) {
        showToast('Decryption error.', 'danger');
        btn.disabled = false;
        btn.textContent = 'Decrypt & Download';
      }
    });
  }
});
