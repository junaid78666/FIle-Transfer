/**
 * app/static/js/main.js - Global UI Handlers
 */
import { apiRequest, clearTokens } from './api.js';
import { showToast } from './toast.js';

document.addEventListener('DOMContentLoaded', () => {
  // User profile dropdown toggle
  const profileBtn = document.getElementById('profile-dropdown-btn');
  const profilePanel = document.getElementById('profile-dropdown-panel');

  if (profileBtn && profilePanel) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profilePanel.classList.toggle('open');
    });

    document.addEventListener('click', () => {
      profilePanel.classList.remove('open');
    });
  }

  // Logout button handler
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      try {
        const resp = await apiRequest('/auth/logout', { method: 'POST' });
        if (resp.ok) {
          clearTokens();               // wipe JWT from localStorage
          showToast('Logged out successfully.', 'info');
          setTimeout(() => { window.location.href = '/'; }, 800);
        }
      } catch (err) {
        clearTokens();
        window.location.href = '/';
      }
    });
  }
});
