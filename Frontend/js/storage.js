// localStorage helpers for users and sessions
const SESSION_KEYS = {
  id: 'userId',
  name: 'userName',
  role: 'userRole',
  token: 'loginToken',
  userData: 'userData'
};

export function saveSession({ id, username, role = 'user', token, extra = {} } = {}) {
  if (id) localStorage.setItem(SESSION_KEYS.id, id);
  if (username) localStorage.setItem(SESSION_KEYS.name, username);
  if (role) localStorage.setItem(SESSION_KEYS.role, role);
  if (token) localStorage.setItem(SESSION_KEYS.token, token);
  if (extra.userData) localStorage.setItem(SESSION_KEYS.userData, JSON.stringify(extra.userData));
}

export function clearSession() {
  Object.values(SESSION_KEYS).forEach(k => localStorage.removeItem(k));
}

export function getSession() {
  return {
    id: localStorage.getItem(SESSION_KEYS.id),
    name: localStorage.getItem(SESSION_KEYS.name),
    role: localStorage.getItem(SESSION_KEYS.role),
    token: localStorage.getItem(SESSION_KEYS.token),
    userData: (() => {
      const d = localStorage.getItem(SESSION_KEYS.userData);
      try { return d ? JSON.parse(d) : null; } catch(e){ return null; }
    })()
  };
}
