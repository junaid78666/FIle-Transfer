/**
 * app/static/js/api.js - JWT-Aware Centralized API Client
 * Stores access + refresh tokens in localStorage.
 * Auto-attaches Authorization: Bearer header to every request.
 * Auto-silently refreshes when access token is near expiry.
 */

const LS_ACCESS  = 'ecc_access_token';
const LS_REFRESH = 'ecc_refresh_token';
const LS_EXPIRES = 'ecc_token_expires';

export function saveTokens(t) {
  localStorage.setItem(LS_ACCESS, t.access_token);
  if (t.refresh_token) localStorage.setItem(LS_REFRESH, t.refresh_token);
  localStorage.setItem(LS_EXPIRES, String(Date.now() + t.expires_in * 1000));
}

export function clearTokens() {
  [LS_ACCESS, LS_REFRESH, LS_EXPIRES].forEach(k => localStorage.removeItem(k));
}

export function getAccessToken()  { return localStorage.getItem(LS_ACCESS)  || null; }
export function getRefreshToken() { return localStorage.getItem(LS_REFRESH) || null; }

function isNearExpiry() {
  const exp = parseInt(localStorage.getItem(LS_EXPIRES) || '0', 10);
  return exp > 0 && Date.now() >= exp - 60000;
}

let _rp = null;
async function doRefresh() {
  if (_rp) return _rp;
  _rp = (async () => {
    const rt = getRefreshToken();
    if (!rt) throw new Error('No refresh token.');
    const resp = await fetch('/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (!resp.ok) { clearTokens(); throw new Error('Refresh failed.'); }
    const d = await resp.json();
    saveTokens(d.tokens);
    return d.tokens.access_token;
  })().finally(() => { _rp = null; });
  return _rp;
}

export function getCsrfToken() {
  const m = document.querySelector('meta[name="csrf-token"]');
  return m ? m.getAttribute('content') : '';
}

export async function apiRequest(endpoint, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const h = { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' };

  let tok = getAccessToken();
  if (tok) {
    if (isNearExpiry()) { try { tok = await doRefresh(); } catch (_) {} }
    h['Authorization'] = 'Bearer ' + tok;
  }

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const csrf = getCsrfToken();
    if (csrf) h['X-CSRFToken'] = csrf;
  }

  if (options.body && !(options.body instanceof FormData) && typeof options.body === 'string') {
    h['Content-Type'] = 'application/json';
  }

  const merged = { ...h, ...(options.headers || {}) };

  try {
    const resp = await fetch(endpoint, { ...options, headers: merged });

    if (resp.status === 401 && !endpoint.includes('/auth/')) {
      const rt2 = getRefreshToken();
      if (rt2) {
        try {
          const nt = await doRefresh();
          return fetch(endpoint, { ...options, headers: { ...merged, Authorization: 'Bearer ' + nt } });
        } catch (_) {}
      }
      clearTokens();
      window.location.href = '/auth/login?session_expired=true';
      throw new Error('Session expired.');
    }

    return resp;
  } catch (err) {
    console.error('[API]', method, endpoint, err);
    throw err;
  }
}
