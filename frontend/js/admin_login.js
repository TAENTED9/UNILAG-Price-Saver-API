import { API_URL } from './api_url.js';
import { saveSession } from './storage.js';
import { disableButton, showStatus, appPath } from './utils.js';

export function initAdminLogin() {
  const btn = document.getElementById('adminLoginBtn');
  const btnText = document.getElementById('adminLoginText');
  const statusEl = document.getElementById('adminStatus');

  async function loginAdmin() {
    const username = document.getElementById('adminUsername').value.trim();
    const apiKey = document.getElementById('adminKey').value.trim();

    if (!username || !apiKey) {
      showStatus(statusEl, 'error', '❌ Please enter both username and API key');
      return;
    }

    disableButton(btn, true, '<span class="spinner"></span>Verifying...');

    try {
      const resp = await fetch(`${API_URL}/auth/admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, admin_key: apiKey })
      });

      const data = await resp.json();

      if (resp.ok) {
        showStatus(statusEl, 'success', '✅ Admin login successful! Redirecting...');
        saveSession({ id: data.admin_id || Date.now(), username: data.admin_name || username, role: 'admin', token: data.login_token || `adm_${Date.now()}` });
        setTimeout(() => { window.location.href = appPath('admin-dashboard.html'); }, 800);
      } else {
        showStatus(statusEl, 'error', '❌ ' + (data.detail || 'Invalid credentials'));
      }
    } catch (err) {
      console.error(err);
      showStatus(statusEl, 'error', '❌ Connection error. Backend running?');
    } finally {
      disableButton(btn, false, 'Login as Admin');
    }
  }

  if (btn) btn.addEventListener('click', loginAdmin);
}
