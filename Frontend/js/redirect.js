// Check session and auto-redirect if already logged in
import { getSession } from './storage.js';
import { appPath } from './utils.js';

export function autoRedirectIfLogged() {
  const session = getSession();
  if (session && session.role && session.token) {
    if (session.role === 'admin') {
      window.location.href = appPath('admin-dashboard.html');
    } else {
      window.location.href = appPath('user-dashboard.html');
    }
  }
}
