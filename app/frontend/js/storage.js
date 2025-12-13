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

export function getUserData() {
  try {
    const data = localStorage.getItem(SESSION_KEYS.userData);
    return data ? JSON.parse(data) : { submissions: [], reputation: { score: 3.0, badge: 'New User' } };
  } catch (e) {
    console.error('Error parsing userData:', e);
    return { submissions: [], reputation: { score: 3.0, badge: 'New User' } };
  }
}

export function saveUserData(userData) {
  try {
    localStorage.setItem(SESSION_KEYS.userData, JSON.stringify(userData));
  } catch (e) {
    console.error('Error saving userData:', e);
  }
}

// Track user submissions
export function addSubmission(priceId) {
  const userData = getUserData();
  if (!userData.submissions) userData.submissions = [];
  userData.submissions.push({
    id: priceId,
    timestamp: new Date().toISOString()
  });
  saveUserData(userData);
}

// Update user reputation
export function updateReputation(score, badge) {
  const userData = getUserData();
  userData.reputation = { score, badge };
  saveUserData(userData);
}