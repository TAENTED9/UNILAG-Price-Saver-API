import { initTabs } from './tabs.js';
import { initRegister } from './user_register.js';
import { initUserLogin } from './user_login.js';
import { initAdminLogin } from './admin_login.js';
import { autoRedirectIfLogged } from './redirect.js';

// Initialize UI and features
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initRegister();
  initUserLogin();
  initAdminLogin();
  autoRedirectIfLogged();

  // Enter key handling: submit the visible panel's primary action
  document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const active = document.querySelector('.form-content.active');
      if (!active) return;
      if (active.dataset.content === 'user' && active.id === 'userLogin') {
        document.getElementById('userLoginBtn').click();
      } else if (active.dataset.content === 'admin') {
        document.getElementById('adminLoginBtn').click();
      } else if (active.dataset.content === 'register') {
        document.getElementById('registerBtn').click();
      }
    }
  });
});
