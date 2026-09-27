/**
 * app/static/js/api.js — Centralized API Client & CSRF Handler
 */

export function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

export async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    'Accept': 'application/json',
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
  if (options.body && !(options.body instanceof FormData) && typeof options.body === 'string') {
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
    if (response.status === 401 && !endpoint.includes('/auth/login')) {
      window.location.href = '/auth/login?session_expired=true';
      throw new Error('Session expired. Redirecting to login...');
    }

    return response;
  } catch (error) {
    console.error(`[API ERROR] ${method} ${endpoint}:`, error);
    throw error;
  }
}
