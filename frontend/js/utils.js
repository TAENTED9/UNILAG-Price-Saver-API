// Small utility helpers
export function hashPassword(password = '') {
    // Same simple hash for parity with previous impl (not secure for production)
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
      const char = password.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString();
  }
  
  export function disableButton(btn, disabled = true, text = null) {
    if (!btn) return;
    btn.disabled = disabled;
    const span = btn.querySelector('span');
    if (text !== null && span) span.innerHTML = text;
  }
  
  export function showStatus(el, type, message) {
    if (!el) return;
    el.className = `status-message ${type}`;
    el.textContent = message;
  }
  
// Resolve path whether app is served from / or /Frontend/
export function appPath(page = '') {
  const base = window.location.pathname.includes('/Frontend/') ? '/Frontend/' : '/';
  return `${base}${page}`;
}
  