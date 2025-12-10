// Tab logic: convert data-mode buttons into content visibility
export function initTabs() {
    const tabs = Array.from(document.querySelectorAll('.form-tab'));
    const contents = Array.from(document.querySelectorAll('.form-content'));
  
    function activateMode(mode) {
      tabs.forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
      contents.forEach(c => c.classList.toggle('active', c.dataset.content === mode || (mode === 'user' && c.dataset.content === 'user')));
      // If switching to user, make sure userLogin shows by default
      if (mode === 'user') {
        document.getElementById('userLogin').classList.add('active');
        document.getElementById('userRegister').classList.remove('active');
      }
    }
  
    tabs.forEach(tab => {
      tab.addEventListener('click', () => activateMode(tab.dataset.mode));
    });
  
    // Buttons that switch between login/register
    const toRegisterBtn = document.getElementById('toRegisterBtn');
    const toLoginBtn = document.getElementById('toLoginBtn');
    if (toRegisterBtn) toRegisterBtn.addEventListener('click', () => {
      document.getElementById('userLogin').classList.remove('active');
      document.getElementById('userRegister').classList.add('active');
      document.querySelector('.form-tab[data-mode="user"]').classList.add('active');
    });
    if (toLoginBtn) toLoginBtn.addEventListener('click', () => {
      document.getElementById('userRegister').classList.remove('active');
      document.getElementById('userLogin').classList.add('active');
      document.querySelector('.form-tab[data-mode="user"]').classList.add('active');
    });
  }
  