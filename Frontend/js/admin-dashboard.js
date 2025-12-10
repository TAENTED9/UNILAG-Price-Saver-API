/**
 * Admin dashboard entrypoint (ES module)
 * Handles access control, loading stats, approving/rejecting prices.
 */
import { API_URL } from './api_url.js';
import { appPath } from './utils.js';

let allPrices = [];
let allCategories = [];

document.addEventListener('DOMContentLoaded', () => {
  guardAccess();
  setupNav();
  setupDarkMode();
  setupTabs();
  loadInitialData();
});

function guardAccess() {
  const role = localStorage.getItem('userRole');
  if (role !== 'admin') {
    alert('❌ Access Denied. Admin access required.');
    localStorage.clear();
    window.location.href = 'login.html';
  }
}

function setupNav() {
  const navToggleBtn = document.getElementById('navToggleBtn');
  const navPanel = document.getElementById('navPanel');
  const navOverlay = document.getElementById('navOverlay');

  navToggleBtn?.addEventListener('click', () => {
    navPanel.classList.toggle('open');
    navOverlay.classList.toggle('open');
  });
  navOverlay?.addEventListener('click', () => {
    navPanel.classList.remove('open');
    navOverlay.classList.remove('open');
  });

  navPanel?.addEventListener('click', (e) => {
    const action = e.target.closest('[data-action]')?.dataset.action;
    if (action === 'logout') logout();
  });
}

function setupTabs() {
  const buttons = Array.from(document.querySelectorAll('.tab-btn'));
  const contents = Array.from(document.querySelectorAll('.tab-content'));
  const activate = (tabId) => {
    buttons.forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
    contents.forEach(c => c.classList.toggle('active', c.id === tabId));
    if (tabId === 'pending') loadPendingTable();
    if (tabId === 'approved') loadApprovedTable();
    if (tabId === 'categories') renderCategoriesTab();
  };
  buttons.forEach(btn => btn.addEventListener('click', () => activate(btn.dataset.tab)));
  activate('overview');
}

function setupDarkMode() {
  const darkModeBtn = document.getElementById('darkModeBtn');
  const applyPref = () => {
    const isDark = localStorage.getItem('adminDark') === 'true';
    document.body.classList.toggle('dark-mode', isDark);
    if (darkModeBtn) darkModeBtn.textContent = isDark ? '☀️' : '🌙';
  };
  applyPref();
  darkModeBtn?.addEventListener('click', () => {
    const next = !(localStorage.getItem('adminDark') === 'true');
    localStorage.setItem('adminDark', next);
    applyPref();
  });
}

async function loadInitialData() {
  await Promise.all([loadCategories(), loadAllPrices()]);
  await loadPendingTable();
  await loadApprovedTable();
  renderCategoriesTab();
}

async function loadCategories() {
  try {
    const res = await fetch(`${API_URL}/items/categories/all`);
    allCategories = await res.json();
  } catch (err) {
    console.error('Error loading categories', err);
    allCategories = [];
  }
}

async function loadAllPrices() {
  try {
    const res = await fetch(`${API_URL}/items/prices/all`);
    allPrices = await res.json();
    updateOverview();
    renderRecentActivity();
  } catch (err) {
    console.error('Error loading prices', err);
    allPrices = [];
  }
}

async function loadPendingTable() {
  const container = document.getElementById('pendingTable');
  try {
    const res = await fetch(`${API_URL}/items/prices/pending/`);
    const pending = await res.json();
    renderPricesTable(container, pending, true);
  } catch (err) {
    console.error('Error loading pending prices', err);
    renderPricesTable(container, [], true);
  }
}

async function loadApprovedTable() {
  const container = document.getElementById('approvedTable');
  const approved = allPrices.filter(p => p.status === 'approved');
  renderPricesTable(container, approved, false);
}

function renderCategoriesTab() {
  const container = document.getElementById('categoriesList');
  if (!allCategories.length) {
    container.innerHTML = '<div class="empty-state"><p>No categories</p></div>';
    return;
  }
  container.innerHTML = `
    <table class="prices-table">
      <thead><tr><th>Icon</th><th>Name</th><th>Description</th></tr></thead>
      <tbody>
        ${allCategories.map(cat => `
          <tr>
            <td>${cat.icon || '-'}</td>
            <td><strong>${cat.name}</strong></td>
            <td>${cat.description || '-'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function renderPricesTable(container, prices, showActions) {
  if (!container) return;
  if (!prices || !prices.length) {
    container.innerHTML = '<div class="empty-state"><p>No data</p></div>';
    return;
  }
  container.innerHTML = `
    <table class="prices-table">
      <thead>
        <tr>
          <th>Category</th><th>Item</th><th>Brand</th><th>Pack</th>
          <th>Price</th><th>Retailer</th><th>Location</th><th>Status</th>
          ${showActions ? '<th>Action</th>' : ''}
        </tr>
      </thead>
      <tbody>
        ${prices.map(p => `
          <tr>
            <td><span class="category-badge">${lookupCategory(p.category_id)}</span></td>
            <td>${p.name}</td>
            <td>${p.brand || '-'}</td>
            <td>${p.pack_size ? `${p.pack_size}${p.pack_unit ? ' ' + p.pack_unit : ''}` : '-'}</td>
            <td class="price-value">₦${Number(p.price || 0).toFixed(2)}</td>
            <td>${p.retailer || '-'}</td>
            <td>${p.location || '-'}</td>
            <td><span class="status-badge status-${p.status}">${p.status}</span></td>
            ${showActions ? `
              <td>
                <div class="action-buttons">
                  <button class="btn-small btn-approve" data-action="approve" data-id="${p.id}">Approve</button>
                  <button class="btn-small btn-reject" data-action="reject" data-id="${p.id}">Reject</button>
                </div>
              </td>` : ''}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  if (showActions) {
    container.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const action = btn.dataset.action;
        if (action === 'approve') approvePrice(id);
        if (action === 'reject') rejectPrice(id);
      });
    });
  }
}

function lookupCategory(categoryId) {
  const cat = allCategories.find(c => c.id === categoryId);
  return cat ? `${cat.icon || ''} ${cat.name}` : 'Unknown';
}

async function approvePrice(id) {
  try {
    const res = await fetch(`${API_URL}/items/prices/${id}/approve`, { method: 'PUT', headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) throw new Error();
    await loadInitialData();
    alert('✅ Price approved');
  } catch {
    alert('Error approving price');
  }
}

async function rejectPrice(id) {
  try {
    const res = await fetch(`${API_URL}/items/prices/${id}/reject`, { method: 'PUT', headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) throw new Error();
    await loadInitialData();
    alert('❌ Price rejected');
  } catch {
    alert('Error rejecting price');
  }
}

function updateOverview() {
  const pending = allPrices.filter(p => p.status === 'pending').length;
  const approved = allPrices.filter(p => p.status === 'approved').length;
  const rejected = allPrices.filter(p => p.status === 'rejected').length;

  document.getElementById('totalPrices').textContent = allPrices.length;
  document.getElementById('pendingCount').textContent = pending;
  document.getElementById('approvedCount').textContent = approved;
  document.getElementById('rejectedCount').textContent = rejected;
}

function renderRecentActivity() {
  const container = document.getElementById('recentActivityTable');
  const recent = allPrices.slice(0, 10);
  renderPricesTable(container, recent, false);
}

function logout() {
  localStorage.clear();
  window.location.href = appPath('login.html');
}

