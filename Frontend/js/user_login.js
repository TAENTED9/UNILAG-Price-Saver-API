import { saveSession } from './storage.js';
import { disableButton, showStatus, appPath } from './utils.js';
import { API_URL } from './api_url.js';

export function initUserLogin() {
  const loginBtn = document.getElementById('userLoginBtn');
  const loginText = document.getElementById('userLoginText');
  const statusEl = document.getElementById('userStatus');

  function loginUser() {
    const username = document.getElementById('userUsername').value.trim();
    const password = document.getElementById('userPassword').value;

    if (!username || !password) {
      showStatus(statusEl, 'error', '❌ Please enter username and password');
      return;
    }

    disableButton(loginBtn, true, '<span class="spinner"></span>Logging in...');

    (async () => {
      try {
        const resp = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Invalid credentials');

        showStatus(statusEl, 'success', '✅ Login successful! Redirecting...');
        saveSession({ id: data.user_id, username: data.user_name, role: data.user_role, token: data.login_token });
        setTimeout(() => { window.location.href = appPath('user-dashboard.html'); }, 800);
      } catch (err) {
        showStatus(statusEl, 'error', `❌ ${err.message}`);
      } finally {
        disableButton(loginBtn, false, 'Login');
      }
    })();
  }

  if (loginBtn) loginBtn.addEventListener('click', loginUser);
}
