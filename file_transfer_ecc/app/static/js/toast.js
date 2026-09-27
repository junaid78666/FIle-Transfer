/**
 * app/static/js/toast.js — Dynamic Notification System
 */

export function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content" style="display: flex; align-items: center; gap: 8px;">
      <span class="toast-message">${escapeHtml(message)}</span>
    </div>
    <button class="toast-close" aria-label="Close" style="background: none; border: none; cursor: pointer;">&times;</button>
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
  setTimeout(() => {
    toast.remove();
  }, 300);
}

function escapeHtml(str) {
  const p = document.createElement('p');
  p.textContent = str;
  return p.innerHTML;
}
