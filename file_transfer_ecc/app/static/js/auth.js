/**
 * app/static/js/auth.js — Authentication Controller & Password Meter
 */
import { apiRequest } from './api.js';
import { showToast } from './toast.js';

// Registration form handler
const registerForm = document.getElementById('register-form');
if (registerForm) {
  const pwdInput = document.getElementById('password');
  const meterBar = document.getElementById('meter-bar');
  const meterLabel = document.getElementById('meter-label');

  if (pwdInput && meterBar && meterLabel) {
    pwdInput.addEventListener('input', () => {
      const pwd = pwdInput.value;
      const score = calculatePasswordStrength(pwd);
      updateMeterUI(score, meterBar, meterLabel);
    });
  }

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('register-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Generating SECP256R1 Keypair...';

    const payload = {
      username: document.getElementById('username').value.trim(),
      email: document.getElementById('email').value.trim(),
      password: pwdInput.value,
      confirm_password: document.getElementById('confirm_password').value,
    };

    try {
      const resp = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (resp.status === 201) {
        showToast('Registration successful! Redirecting to login...', 'success');
        setTimeout(() => {
          window.location.href = '/auth/login';
        }, 1200);
      } else {
        const errorMsg = data.errors ? data.errors.join(' ') : (data.message || 'Registration failed.');
        showToast(errorMsg, 'danger');
        btn.disabled = false;
        btn.textContent = 'Generate Keys & Create Account';
      }
    } catch (err) {
      showToast('Network error during registration.', 'danger');
      btn.disabled = false;
      btn.textContent = 'Generate Keys & Create Account';
    }
  });
}

// Login form handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('login-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Verifying Session...';

    const payload = {
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
    };

    try {
      const resp = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (resp.status === 200) {
        showToast('Authentication successful!', 'success');
        window.location.href = '/dashboard';
      } else {
        showToast(data.message || 'Invalid credentials.', 'danger');
        btn.disabled = false;
        btn.textContent = 'Authenticate & Unlock';
      }
    } catch (err) {
      showToast('Network error during login.', 'danger');
      btn.disabled = false;
      btn.textContent = 'Authenticate & Unlock';
    }
  });
}

function calculatePasswordStrength(pwd) {
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++;
  if (/\d/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score;
}

function updateMeterUI(score, bar, label) {
  const levels = [
    { text: 'Strength: Very Weak', color: '#F43F5E', width: '25%' },
    { text: 'Strength: Weak', color: '#F59E0B', width: '50%' },
    { text: 'Strength: Good', color: '#38BDF8', width: '75%' },
    { text: 'Strength: Strong (ECC Safe)', color: '#10B981', width: '100%' },
  ];

  if (score === 0) {
    bar.style.width = '0%';
    label.textContent = 'Password Strength: Empty';
    return;
  }

  const level = levels[score - 1];
  bar.style.width = level.width;
  bar.style.backgroundColor = level.color;
  label.textContent = level.text;
  label.style.color = level.color;
}
