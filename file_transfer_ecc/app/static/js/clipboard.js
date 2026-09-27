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
        button.innerHTML = '<span>Copied!</span>';
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
