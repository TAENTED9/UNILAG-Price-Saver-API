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

// Format currency with Nigerian Naira symbol
export function formatCurrency(amount) {
  if (typeof amount !== 'number') {
    amount = parseFloat(amount) || 0;
  }
  return `₦${amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
}

// Safely escape HTML to prevent XSS
export function safeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// User data helpers (extending storage.js)
export function getUserData() {
  try {
    const data = localStorage.getItem('userData');
    return data ? JSON.parse(data) : null;
  } catch (e) {
    console.error('Error parsing userData:', e);
    return null;
  }
}

export function saveUserData(userData) {
  try {
    localStorage.setItem('userData', JSON.stringify(userData));
  } catch (e) {
    console.error('Error saving userData:', e);
  }
}

// Debounce helper for search inputs
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Show toast notification
export function showToast(message, type = 'info', duration = 4000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    background: ${type === 'success' ? '#34C759' : type === 'error' ? '#FF3B30' : '#007AFF'};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    z-index: 10000;
    animation: slideIn 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Validate form fields
export function validateField(value, rules = {}) {
  const errors = [];
  
  if (rules.required && !value?.trim()) {
    errors.push('This field is required');
  }
  
  if (rules.minLength && value?.length < rules.minLength) {
    errors.push(`Minimum ${rules.minLength} characters required`);
  }
  
  if (rules.maxLength && value?.length > rules.maxLength) {
    errors.push(`Maximum ${rules.maxLength} characters allowed`);
  }
  
  if (rules.pattern && !rules.pattern.test(value)) {
    errors.push(rules.patternMessage || 'Invalid format');
  }
  
  if (rules.min && parseFloat(value) < rules.min) {
    errors.push(`Minimum value is ${rules.min}`);
  }
  
  if (rules.max && parseFloat(value) > rules.max) {
    errors.push(`Maximum value is ${rules.max}`);
  }
  
  return errors;
}