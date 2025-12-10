import { disableButton, showStatus, appPath } from './utils.js';
import { API_URL } from './api_url.js';

// registration logic
export function initRegister() {
  const registerBtn = document.getElementById('registerBtn');
  const registerText = document.getElementById('registerText');
  const statusEl = document.getElementById('registerStatus');

  async function registerUser() {
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const passwordConfirm = document.getElementById('regPasswordConfirm').value;

    if (!username || !password || !passwordConfirm) {
      showStatus(statusEl, 'error', '❌ Please fill all fields');
      return;
    }
    if (password !== passwordConfirm) {
      showStatus(statusEl, 'error', '❌ Passwords do not match');
      return;
    }
    if (password.length < 4) {
      showStatus(statusEl, 'error', '❌ Password must be at least 4 characters');
      return;
    }

    disableButton(registerBtn, true, '<span class="spinner"></span>Creating account...');
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed');

      showStatus(statusEl, 'success', '✅ Account created! Logging in...');
      localStorage.setItem('userId', data.user_id);
      localStorage.setItem('userName', data.user_name);
      localStorage.setItem('userRole', data.user_role);
      localStorage.setItem('loginToken', data.login_token);

      setTimeout(() => { window.location.href = appPath('user-dashboard.html'); }, 800);
    } catch (err) {
      showStatus(statusEl, 'error', `❌ ${err.message}`);
    } finally {
      disableButton(registerBtn, false, 'Create Account');
    }
  }

  if (registerBtn) registerBtn.addEventListener('click', registerUser);
}
