/**
 * User dashboard entrypoint (ES module) - FIXED VERSION
 * - Loads categories/prices
 * - Handles navigation, filters, alerts and submissions
 */
import { API_URL } from './api_url.js';
import { getSession, getUserData, saveUserData, addSubmission } from './storage.js';
import { formatCurrency, safeHTML, appPath, showToast } from './utils.js';

let allPrices = [];
let allCategories = [];
let priceAlerts = JSON.parse(localStorage.getItem('priceAlerts') || '[]');
let mapInstance = null;
let selectedLocation = null;

document.addEventListener('DOMContentLoaded', () => {
  guardAccess();
  setupNav();
  setupDarkMode();
  setupFilters();
  setupAlerts();
  setupLocationModal();
  bindFormSubmit();
  loadInitialData();
  setupMobileNav();
});

function guardAccess() {
  const session = getSession();
  if (!session.role || session.role !== 'user' || !session.token) {
    window.location.href = appPath('login.html');
  }
}

// ==================== NAVIGATION ====================

function setupNav() {
  const navToggleBtn = document.getElementById('navToggleBtn');
  const navPanel = document.getElementById('navPanel');
  const navOverlay = document.getElementById('navOverlay');

  if (navToggleBtn) {
    navToggleBtn.addEventListener('click', () => {
      navPanel?.classList.toggle('open');
      navOverlay?.classList.toggle('open');
    });
  }

  if (navOverlay) {
    navOverlay.addEventListener('click', () => {
      navPanel?.classList.remove('open');
      navOverlay?.classList.remove('open');
    });
  }

  if (navPanel) {
    navPanel.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action]');
      if (btn) {
        const action = btn.dataset.action;
        navPanel.classList.remove('open');
        navOverlay?.classList.remove('open');
        handleNavAction(action);
      }
    });
  }
}

function setupMobileNav() {
  const mobileNav = document.getElementById('mobileBottomNav');
  if (!mobileNav) return;

  // Show mobile nav on mobile devices
  if (window.innerWidth <= 768) {
    mobileNav.classList.add('active');
  }

  // Handle mobile nav clicks
  mobileNav.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    
    // Update active state
    mobileNav.querySelectorAll('.mobile-nav-item').forEach(item => {
      item.classList.remove('active');
    });
    btn.classList.add('active');

    handleNavAction(action);
  });

  // Handle window resize
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) {
      mobileNav.classList.add('active');
    } else {
      mobileNav.classList.remove('active');
    }
  });
}

function setupDarkMode() {
  const darkModeBtn = document.getElementById('darkModeBtn');
  if (!darkModeBtn) return;

  const applyPref = () => {
    const isDark = localStorage.getItem('dashboardDark') === 'true';
    document.body.classList.toggle('dark-mode', isDark);
    darkModeBtn.textContent = isDark ? '☀️' : '🌙';
  };

  applyPref();
  
  darkModeBtn.addEventListener('click', () => {
    const isDark = localStorage.getItem('dashboardDark') === 'true';
    localStorage.setItem('dashboardDark', (!isDark).toString());
    applyPref();
  });
}

// ==================== MODAL HANDLERS ====================

function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

function handleNavAction(action) {
  console.log('Nav action:', action);
  
  switch (action) {
    case 'home':
      window.scrollTo({ top: 0, behavior: 'smooth' });
      break;
      
    case 'trends':
    case 'insights':
      populateCategoryInsights();
      openModal('categoryInsightsModal');
      break;
      
    case 'alerts':
      populateAlertsModal();
      openModal('alertModal');
      break;

    case 'basket-compare':
      window.location.href = 'basket-compare.html';
      break;  
      
    case 'profile':
      populateProfileModal();
      openModal('profileModal');
      break;
      
    case 'logout':
      if (confirm('Are you sure you want to logout?')) {
        // Clear all session data
        localStorage.clear();
        sessionStorage.clear();
        
        // Redirect to login page
        window.location.href = '/login.html';
      }
      break;
      
    case 'submit':
      document.getElementById('priceForm')?.scrollIntoView({ behavior: 'smooth' });
      break;
      
    case 'map':
      openModal('locationModal');
      initializeMap();
      break;
      
    default:
      console.log('Unknown action:', action);
  }
}

// ==================== MODAL CONTENT POPULATORS ====================

function populateCategoryInsights() {
  const content = document.getElementById('categoryInsightsContent');
  if (!content) return;

  if (!allCategories.length) {
    content.innerHTML = '<p style="padding:2rem;text-align:center;">No category data available yet.</p>';
    return;
  }

  const insights = allCategories.map(cat => {
    const catPrices = allPrices.filter(p => p.category_id === cat.id);
    const avgPrice = catPrices.length 
      ? (catPrices.reduce((sum, p) => sum + (p.price || 0), 0) / catPrices.length)
      : 0;
    const minPrice = catPrices.length ? Math.min(...catPrices.map(p => p.price || 0)) : 0;
    const maxPrice = catPrices.length ? Math.max(...catPrices.map(p => p.price || 0)) : 0;

    return `
      <div style="padding:1.5rem;border-bottom:1px solid var(--border);background:var(--bg);margin-bottom:0.5rem;border-radius:8px;">
        <h4 style="font-size:1.1rem;margin-bottom:0.5rem;">${cat.icon || '📦'} ${cat.name}</h4>
        <p style="color:#888;margin-bottom:0.5rem;">${cat.description || ''}</p>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0.5rem;margin-top:1rem;">
          <div><strong>Total Prices:</strong> ${catPrices.length}</div>
          <div><strong>Avg Price:</strong> ${formatCurrency(avgPrice)}</div>
          <div><strong>Min Price:</strong> ${formatCurrency(minPrice)}</div>
          <div><strong>Max Price:</strong> ${formatCurrency(maxPrice)}</div>
        </div>
      </div>
    `;
  }).join('');

  content.innerHTML = insights || '<p style="padding:2rem;text-align:center;">No insights available.</p>';
}

function populateAlertsModal() {
  const content = document.getElementById('alertModalBody');
  if (!content) return;

  const activeAlerts = priceAlerts.filter(a => !a.triggered);
  const triggeredAlerts = priceAlerts.filter(a => a.triggered);

  let html = '<h4 style="margin-bottom:1rem;">Active Alerts</h4>';
  
  if (activeAlerts.length === 0) {
    html += '<p style="color:#888;margin-bottom:1rem;">No active price alerts. Set one below!</p>';
  } else {
    html += '<div style="max-height:200px;overflow-y:auto;margin-bottom:1rem;">';
    activeAlerts.forEach(alert => {
      html += `
        <div style="padding:0.8rem;background:var(--light);border-radius:8px;margin-bottom:0.5rem;display:flex;justify-content:space-between;align-items:center;">
          <div>
            <strong>${alert.itemName}</strong><br>
            <small>Alert when ≤ ${formatCurrency(alert.threshold)}</small>
          </div>
          <button onclick="window.deleteAlert(${alert.id})" style="padding:0.3rem 0.6rem;background:var(--danger);color:white;border:none;border-radius:4px;cursor:pointer;">Delete</button>
        </div>
      `;
    });
    html += '</div>';
  }

  if (triggeredAlerts.length > 0) {
    html += '<h4 style="margin:1.5rem 0 1rem;">Triggered Alerts</h4>';
    html += '<div style="max-height:150px;overflow-y:auto;">';
    triggeredAlerts.forEach(alert => {
      html += `
        <div style="padding:0.8rem;background:var(--success);color:white;border-radius:8px;margin-bottom:0.5rem;">
          ✅ <strong>${alert.itemName}</strong> reached ${formatCurrency(alert.threshold)}
        </div>
      `;
    });
    html += '</div>';
  }

  content.innerHTML = html;
}

// Global function for deleting alerts
window.deleteAlert = function(alertId) {
  priceAlerts = priceAlerts.filter(a => a.id !== alertId);
  localStorage.setItem('priceAlerts', JSON.stringify(priceAlerts));
  populateAlertsModal();
  updateAlertBadges();
  showToast('Alert deleted', 'success');
};

function populateProfileModal() {
  const content = document.getElementById('profileContent');
  if (!content) return;

  const session = getSession();
  const userData = getUserData();
  const submissions = allPrices.filter(p => p.submitted_by === parseInt(session.id || '0'));
  const submissionCount = submissions.length;
  const score = Math.min(5, 3 + submissionCount * 0.1).toFixed(1);
  const badge = score >= 4.5 ? '🏆 Trusted User' : score >= 3.5 ? '⭐ Active' : '🆕 New User';

  content.innerHTML = `
    <div style="padding:2rem;text-align:center;">
      <div style="font-size:4rem;margin-bottom:1rem;">👤</div>
      <h3 style="margin-bottom:0.5rem;">${safeHTML(session.name || 'User')}</h3>
      <p style="color:#888;margin-bottom:2rem;">${badge}</p>
      
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:2rem;">
        <div style="padding:1rem;background:var(--light);border-radius:8px;">
          <div style="font-size:2rem;font-weight:bold;color:var(--primary);">${submissionCount}</div>
          <div style="font-size:0.9rem;color:#888;">Submissions</div>
        </div>
        <div style="padding:1rem;background:var(--light);border-radius:8px;">
          <div style="font-size:2rem;font-weight:bold;color:var(--primary);">⭐ ${score}</div>
          <div style="font-size:0.9rem;color:#888;">Reputation</div>
        </div>
      </div>
      
      <div style="text-align:left;background:var(--light);padding:1rem;border-radius:8px;">
        <p><strong>Role:</strong> ${safeHTML(session.role || 'user')}</p>
        <p><strong>Account Status:</strong> Active</p>
        <p><strong>Member Since:</strong> ${new Date().toLocaleDateString()}</p>
      </div>
    </div>
  `;
}

// Setup close buttons for all modals
document.addEventListener('DOMContentLoaded', () => {
  const closeButtons = [
    { id: 'categoryInsightsClose', modal: 'categoryInsightsModal' },
    { id: 'profileCloseBtn', modal: 'profileModal' },
    { id: 'locationModalClose', modal: 'locationModal' },
    { id: 'alertCancelBtn', modal: 'alertModal' }
  ];

  closeButtons.forEach(({ id, modal }) => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', () => closeModal(modal));
    }
  });
});

// ==================== FILTERS ====================

function setupFilters() {
  const filterIds = ['filterCategory', 'filterMinPrice', 'filterMaxPrice', 'filterRetailer', 'filterLocation'];
  
  filterIds.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.addEventListener('input', applyFilters);
      element.addEventListener('change', applyFilters);
    }
  });

  const resetBtn = document.getElementById('resetFiltersBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      filterIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.value = '';
      });
      displayPrices(allPrices);
    });
  }

  setupGlobalSearch();
}

function setupGlobalSearch() {
  const searchInput = document.getElementById('globalSearch');
  const resultsDiv = document.getElementById('searchResults');
  if (!searchInput || !resultsDiv) return;

  let searchTimeout;
  
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const query = searchInput.value.trim().toLowerCase();

    if (!query) {
      resultsDiv.classList.remove('open');
      displayPrices(allPrices);
      return;
    }

    searchTimeout = setTimeout(() => {
      const filtered = allPrices.filter(p =>
        (p.name && p.name.toLowerCase().includes(query)) ||
        (p.retailer && p.retailer.toLowerCase().includes(query)) ||
        (p.location && p.location.toLowerCase().includes(query)) ||
        (p.brand && p.brand.toLowerCase().includes(query))
      );

      if (filtered.length > 0) {
        resultsDiv.innerHTML = filtered.slice(0, 6).map(p => `
          <div class="search-result-item" data-id="${p.id}">
            ${safeHTML(p.name)} — ${formatCurrency(p.price)}
            ${p.retailer ? `<br><small style="color:#888;">at ${safeHTML(p.retailer)}</small>` : ''}
          </div>
        `).join('');
        
        resultsDiv.classList.add('open');
        
        // Add click handlers
        resultsDiv.querySelectorAll('.search-result-item').forEach(item => {
          item.addEventListener('click', () => {
            const priceId = parseInt(item.dataset.id);
            const price = allPrices.find(p => p.id === priceId);
            if (price) {
              searchInput.value = price.name;
              resultsDiv.classList.remove('open');
              displayPrices([price]);
            }
          });
        });
      } else {
        resultsDiv.innerHTML = '<div class="search-result-item">No results found</div>';
        resultsDiv.classList.add('open');
      }
    }, 300);
  });

  // Close results when clicking outside
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
      resultsDiv.classList.remove('open');
    }
  });
}

function applyFilters() {
  const categoryId = document.getElementById('filterCategory')?.value;
  const minPrice = parseFloat(document.getElementById('filterMinPrice')?.value) || 0;
  const maxPrice = parseFloat(document.getElementById('filterMaxPrice')?.value) || Number.POSITIVE_INFINITY;
  const retailer = document.getElementById('filterRetailer')?.value.toLowerCase() || '';
  const location = document.getElementById('filterLocation')?.value.toLowerCase() || '';

  const filtered = allPrices.filter(p => {
    const matchCategory = !categoryId || String(p.category_id) === String(categoryId);
    const matchPrice = typeof p.price === 'number' && p.price >= minPrice && p.price <= maxPrice;
    const matchRetailer = !retailer || (p.retailer && p.retailer.toLowerCase().includes(retailer));
    const matchLocation = !location || (p.location && p.location.toLowerCase().includes(location));
    return matchCategory && matchPrice && matchRetailer && matchLocation;
  });

  displayPrices(filtered);
}

// ==================== PRICE ALERTS ====================

function setupAlerts() {
  const saveBtn = document.getElementById('alertSaveBtn');
  const cancelBtn = document.getElementById('alertCancelBtn');

  if (saveBtn) {
    saveBtn.addEventListener('click', savePriceAlert);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => closeModal('alertModal'));
  }

  updateAlertBadges();
}

function savePriceAlert() {
  const itemName = document.getElementById('alertItemName')?.value.trim();
  const threshold = parseFloat(document.getElementById('alertThreshold')?.value);

  if (!itemName || isNaN(threshold) || threshold <= 0) {
    showToast('Please fill all alert fields correctly', 'error');
    return;
  }

  priceAlerts.push({
    id: Date.now(),
    itemName,
    threshold,
    triggered: false,
    createdAt: new Date().toISOString()
  });

  localStorage.setItem('priceAlerts', JSON.stringify(priceAlerts));
  closeModal('alertModal');
  updateAlertBadges();
  showToast(`Alert set for ${itemName}`, 'success');
  
  // Clear inputs
  document.getElementById('alertItemName').value = '';
  document.getElementById('alertThreshold').value = '';
}

function checkPriceAlerts(prices) {
  let triggered = 0;
  
  priceAlerts.forEach(alert => {
    if (alert.triggered) return;
    
    const match = prices.find(p => 
      p.name?.toLowerCase() === alert.itemName.toLowerCase() && 
      p.price <= alert.threshold
    );
    
    if (match) {
      alert.triggered = true;
      triggered++;
      showToast(`🔔 Price Alert: ${alert.itemName} is now ${formatCurrency(match.price)}!`, 'success', 6000);
    }
  });

  if (triggered > 0) {
    localStorage.setItem('priceAlerts', JSON.stringify(priceAlerts));
    updateAlertBadges();
  }
}

function updateAlertBadges() {
  const activeCount = priceAlerts.filter(a => !a.triggered).length;
  document.querySelectorAll('.alert-badge').forEach(badge => {
    badge.textContent = activeCount > 0 ? activeCount : '';
    badge.style.display = activeCount > 0 ? 'inline-block' : 'none';
  });
}

// ==================== LOCATION MODAL ====================

function setupLocationModal() {
  const mapBtn = document.getElementById('mapPickerBtn');
  const closeBtn = document.getElementById('locationModalClose');
  const cancelBtn = document.getElementById('locationModalCancel');
  const confirmBtn = document.getElementById('locationModalConfirm');

  if (mapBtn) {
    mapBtn.addEventListener('click', () => {
      openModal('locationModal');
      setTimeout(() => initializeMap(), 300);
    });
  }

  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('locationModal'));
  if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('locationModal'));
  
  if (confirmBtn) {
    confirmBtn.addEventListener('click', () => {
      const manual = document.getElementById('manualLocation')?.value.trim();
      const locationInput = document.getElementById('location');
      
      if (selectedLocation) {
        locationInput.value = selectedLocation.address;
        closeModal('locationModal');
        showToast('Location selected', 'success');
      } else if (manual) {
        locationInput.value = manual;
        closeModal('locationModal');
        showToast('Location entered', 'success');
      } else {
        showToast('Please select or enter a location', 'error');
      }
    });
  }
}

function initializeMap() {
  if (!window.google || !window.google.maps) {
    console.warn('Google Maps not loaded');
    return;
  }

  const mapDiv = document.getElementById('map');
  if (!mapDiv || mapInstance) return;

  // Default to UNILAG location
  const defaultLocation = { lat: 6.5158, lng: 3.3895 };

  mapInstance = new google.maps.Map(mapDiv, {
    center: defaultLocation,
    zoom: 15,
    mapTypeControl: false
  });

  const marker = new google.maps.Marker({
    map: mapInstance,
    position: defaultLocation,
    draggable: true
  });

  // Handle map clicks
  mapInstance.addListener('click', (e) => {
    marker.setPosition(e.latLng);
    reverseGeocode(e.latLng);
  });

  // Handle marker drag
  marker.addListener('dragend', () => {
    reverseGeocode(marker.getPosition());
  });
}

function reverseGeocode(latLng) {
  const geocoder = new google.maps.Geocoder();
  
  geocoder.geocode({ location: latLng }, (results, status) => {
    if (status === 'OK' && results[0]) {
      selectedLocation = {
        lat: latLng.lat(),
        lng: latLng.lng(),
        address: results[0].formatted_address
      };
      
      const coordsDiv = document.getElementById('locationCoordinates');
      const addressSpan = document.getElementById('selectedAddress');
      const latSpan = document.getElementById('selectedLat');
      const lngSpan = document.getElementById('selectedLng');
      
      if (coordsDiv) coordsDiv.classList.add('show');
      if (addressSpan) addressSpan.textContent = selectedLocation.address;
      if (latSpan) latSpan.textContent = selectedLocation.lat.toFixed(6);
      if (lngSpan) lngSpan.textContent = selectedLocation.lng.toFixed(6);
    }
  });
}

// ==================== FORM SUBMISSION ====================

function bindFormSubmit() {
  const form = document.getElementById('priceForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await submitPrice();
  });

  // Auto-calculate price per unit when pack size changes
  const packSize = document.getElementById('packSize');
  const price = document.getElementById('price');
  const pricePerUnit = document.getElementById('pricePerUnit');

  if (packSize && price && pricePerUnit) {
    const calculatePerUnit = () => {
      const size = parseFloat(packSize.value);
      const totalPrice = parseFloat(price.value);
      
      if (size > 0 && totalPrice > 0) {
        // Calculate per 100g/ml
        const perUnit = (totalPrice / size) * 100;
        pricePerUnit.value = perUnit.toFixed(2);
      }
    };

    packSize.addEventListener('input', calculatePerUnit);
    price.addEventListener('input', calculatePerUnit);
  }
}

async function submitPrice() {
  const payload = {
    category_id: parseInt(document.getElementById('category')?.value) || null,
    name: document.getElementById('itemName')?.value.trim(),
    brand: document.getElementById('brand')?.value.trim() || null,
    pack_size: document.getElementById('packSize')?.value.trim() || null,
    pack_unit: document.getElementById('packUnit')?.value || null,
    price: parseFloat(document.getElementById('price')?.value),
    price_per_unit: parseFloat(document.getElementById('pricePerUnit')?.value) || null,
    retailer: document.getElementById('retailer')?.value.trim() || null,
    location: document.getElementById('location')?.value.trim() || null,
    store_id: null,
    submitted_by: getSession().id ? parseInt(getSession().id) : null
  };

  // Validation
  if (!payload.category_id) {
    showToast('Please select a category', 'error');
    return;
  }

  if (!payload.name) {
    showToast('Please enter item name', 'error');
    return;
  }

  if (!payload.price || payload.price <= 0) {
    showToast('Please enter a valid price', 'error');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/items/prices/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error('Failed to submit price');
    }

    const data = await response.json();
    
    // Track submission
    addSubmission(data.id);
    
    // Show success message
    const successMsg = document.getElementById('successMsg');
    if (successMsg) {
      successMsg.classList.add('show');
      setTimeout(() => successMsg.classList.remove('show'), 3000);
    }

    showToast('✅ Price submitted successfully!', 'success');
    
    // Reset form
    document.getElementById('priceForm')?.reset();
    
    // Reload prices
    await loadPrices();
    
    // Update user info
    updateUserInfo();
    
  } catch (error) {
    console.error('Error submitting price:', error);
    showToast('❌ Error submitting price. Please try again.', 'error');
  }
}

// ==================== DATA LOADING ====================

async function loadInitialData() {
  try {
    await Promise.all([loadCategories(), loadPrices()]);
    updateUserInfo();
  } catch (error) {
    console.error('Error loading initial data:', error);
    showToast('Error loading data', 'error');
  }
}

async function loadCategories() {
  try {
    const response = await fetch(`${API_URL}/items/categories/all`);
    if (!response.ok) throw new Error('Failed to load categories');
    
    const categories = await response.json();
    allCategories = Array.isArray(categories) ? categories : [];

    // Populate category selects
    const categorySelect = document.getElementById('category');
    const filterSelect = document.getElementById('filterCategory');

    if (categorySelect) {
      categorySelect.innerHTML = '<option value="">Select category...</option>';
      allCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = `${cat.icon || '📦'} ${cat.name}`;
        categorySelect.appendChild(option);
      });
    }

    if (filterSelect) {
      filterSelect.innerHTML = '<option value="">All Categories</option>';
      allCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = `${cat.icon || '📦'} ${cat.name}`;
        filterSelect.appendChild(option);
      });
    }

  } catch (error) {
    console.error('Error loading categories:', error);
    allCategories = [];
  }
}

async function loadPrices() {
  try {
    const response = await fetch(`${API_URL}/items/prices/all`);
    if (!response.ok) throw new Error('Failed to load prices');
    
    const prices = await response.json();
    allPrices = Array.isArray(prices) ? prices : [];
    
    displayPrices(allPrices);
    updateStats(allPrices);
    checkPriceAlerts(allPrices);
    
  } catch (error) {
    console.error('Error loading prices:', error);
    allPrices = [];
    displayPrices([]);
  }
}

function displayPrices(prices) {
  const container = document.getElementById('pricesContainer');
  if (!container) return;

  if (!prices || prices.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>📊 No prices available yet.</p>
        <p style="color:#888;margin-top:0.5rem;">Start by submitting a price above!</p>
      </div>
    `;
    return;
  }

  const isMobile = window.innerWidth <= 768;

  if (isMobile) {
    // Mobile card view
    container.innerHTML = prices.map(p => {
      const cat = allCategories.find(c => c.id === p.category_id);
      return `
        <article class="price-card" data-id="${p.id}" style="background:var(--light);padding:1rem;border-radius:12px;margin-bottom:1rem;border:1px solid var(--border);">
          <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.8rem;">
            <div>
              <span class="category-badge">${cat?.icon || '📦'} ${cat?.name || 'Unknown'}</span>
              <h4 style="margin:0.5rem 0;font-size:1.1rem;">${safeHTML(p.name)}</h4>
            </div>
            <button class="alert-bell" data-name="${safeHTML(p.name)}" title="Set Alert" style="background:none;border:none;font-size:1.5rem;cursor:pointer;">🔔</button>
          </div>
          <div style="font-size:1.8rem;font-weight:bold;color:var(--success);margin-bottom:0.8rem;">${formatCurrency(p.price)}</div>
          <div style="font-size:0.85rem;color:#888;line-height:1.6;">
            ${p.brand ? `<div>🏷️ Brand: ${safeHTML(p.brand)}</div>` : ''}
            ${p.pack_size ? `<div>📦 Pack: ${safeHTML(p.pack_size)}${p.pack_unit ? ' ' + safeHTML(p.pack_unit) : ''}</div>` : ''}
            ${p.price_per_unit ? `<div>💰 Per Unit: ${formatCurrency(p.price_per_unit)}</div>` : ''}
            <div>🏪 ${safeHTML(p.retailer || 'Unknown')}</div>
            <div>📍 ${safeHTML(p.location || 'Unknown')}</div>
            ${p.submitted_at ? `<div style="margin-top:0.5rem;">🕒 ${new Date(p.submitted_at).toLocaleDateString()}</div>` : ''}
          </div>
        </article>
      `;
    }).join('');
  } else {
    // Desktop table view
    const table = document.createElement('table');
    table.className = 'prices-table';
    table.innerHTML = `
      <thead>
        <tr>
          <th>Category</th>
          <th>Item</th>
          <th>Brand</th>
          <th>Pack Size</th>
          <th>Price</th>
          <th>Per Unit</th>
          <th>Retailer</th>
          <th>Location</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        ${prices.map(p => {
          const cat = allCategories.find(c => c.id === p.category_id);
          return `
            <tr>
              <td><span class="category-badge">${cat?.icon || '📦'} ${cat?.name || 'Unknown'}</span></td>
              <td>
                ${safeHTML(p.name)}
                <button class="alert-bell" data-name="${safeHTML(p.name)}" title="Set Alert" style="background:none;border:none;font-size:1.2rem;cursor:pointer;margin-left:0.5rem;">🔔</button>
              </td>
              <td>${safeHTML(p.brand || '-')}</td>
              <td>${p.pack_size ? `${safeHTML(p.pack_size)}${p.pack_unit ? ' ' + safeHTML(p.pack_unit) : ''}` : '-'}</td>
              <td class="price-value">${formatCurrency(p.price)}</td>
              <td>${p.price_per_unit ? formatCurrency(p.price_per_unit) : '-'}</td>
              <td>${safeHTML(p.retailer || '-')}</td>
              <td>${safeHTML(p.location || '-')}</td>
              <td>${p.submitted_at ? new Date(p.submitted_at).toLocaleDateString() : '-'}</td>
            </tr>
          `;
        }).join('')}
      </tbody>
    `;
    container.innerHTML = '';
    container.appendChild(table);
  }

  // Bind alert buttons
  container.querySelectorAll('.alert-bell').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const itemName = btn.dataset.name;
      document.getElementById('alertItemName').value = itemName;
      openModal('alertModal');
    });
  });

  updateAlertBadges();
}

function updateStats(prices) {
  const totalPrices = prices.length;
  const avgPrice = prices.length 
    ? prices.reduce((sum, p) => sum + (p.price || 0), 0) / prices.length 
    : 0;
  const locations = new Set(prices.map(p => p.location).filter(Boolean));
  const retailers = new Set(prices.map(p => p.retailer).filter(Boolean));

  const totalPricesEl = document.getElementById('totalPrices');
  const avgPriceEl = document.getElementById('avgPrice');
  const totalLocationsEl = document.getElementById('totalLocations');
  const totalRetailersEl = document.getElementById('totalRetailers');

  if (totalPricesEl) totalPricesEl.textContent = totalPrices;
  if (avgPriceEl) avgPriceEl.textContent = formatCurrency(avgPrice);
  if (totalLocationsEl) totalLocationsEl.textContent = locations.size;
  if (totalRetailersEl) totalRetailersEl.textContent = retailers.size;
}

function updateUserInfo() {
  const session = getSession();
  const userData = getUserData();
  const submissionCount = userData?.submissions?.length || 0;
  const score = Math.min(5, 3 + submissionCount * 0.1).toFixed(1);
  
  const userInfo = document.getElementById('user-info');
  if (userInfo) {
    userInfo.innerHTML = `User: ${safeHTML(session.name || 'Student')} • ⭐ ${score}`;
  }

  // Update reputation
  const badge = score >= 4.5 ? 'Trusted User' : score >= 3.5 ? 'Active' : 'New User';
  if (userData) {
    userData.reputation = { score: parseFloat(score), badge };
    saveUserData(userData);
  }
}