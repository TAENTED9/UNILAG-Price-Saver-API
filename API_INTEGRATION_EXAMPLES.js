// ===================================================================
// FRONTEND-BACKEND INTEGRATION EXAMPLES
// Add these to your frontend HTML <script> tag or as separate functions
// ===================================================================

// =======================
// 1. SIMPLIFIED FORM HANDLERS
// =======================

// Create Item Form Handler
async function handleCreateItem(event) {
    event.preventDefault();
    
    const name = document.getElementById('itemName').value.trim();
    const category = document.getElementById('itemCategory').value;
    const description = document.getElementById('itemDescription').value.trim();
    const image_url = document.getElementById('itemImage').value.trim();
    
    if (!name || !category) {
        alert('❌ Please fill item name and category');
        return;
    }

    try {
        console.log('📤 Creating item...');
        const result = await api.createItem({
            name,
            category,
            description,
            image_url,
            user_id: currentUserId
        });
        
        alert('✅ Item created successfully!');
        console.log('Item:', result);
        
        // Clear form
        event.target.reset();
    } catch (error) {
        alert('❌ Failed to create item: ' + error.message);
    }
}

// Add Price Form Handler
async function handleAddPrice(event) {
    event.preventDefault();
    
    const item_id = parseInt(document.getElementById('priceItemId').value);
    const store_id = parseInt(document.getElementById('priceStoreId').value);
    const price = parseFloat(document.getElementById('priceAmount').value);
    
    if (!item_id || !store_id || !price) {
        alert('❌ Please fill all price fields');
        return;
    }

    try {
        console.log('📤 Adding price...');
        const result = await api.addPrice({
            item_id,
            store_id,
            price,
            user_id: currentUserId
        });
        
        alert('✅ Price added successfully!');
        console.log('Price:', result);
        
        event.target.reset();
    } catch (error) {
        alert('❌ Failed to add price: ' + error.message);
    }
}

// =======================
// 2. DATA LOADING FUNCTIONS
// =======================

// Load all items and display
async function loadAndDisplayItems() {
    try {
        console.log('📥 Fetching all items...');
        const items = await api.getItems();
        
        // Display in a list
        const container = document.getElementById('itemsList');
        if (!container) return;
        
        container.innerHTML = '<h3>Available Items (' + items.length + ')</h3>';
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'item-card';
            div.innerHTML = `
                <strong>${item.name}</strong>
                <p>Category: ${item.category}</p>
                <p>Status: ${item.status}</p>
                <button onclick="viewItemPrices(${item.id})">View Prices</button>
                <button onclick="deleteItemUI(${item.id})">Delete</button>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

// Load prices for specific item
async function viewItemPrices(itemId) {
    try {
        console.log('📥 Fetching prices for item', itemId);
        const prices = await api.getPrices(itemId);
        
        alert(`Found ${prices.length} prices for this item:\n\n` + 
              prices.map(p => `Store ${p.store_id}: ₦${p.price}`).join('\n'));
    } catch (error) {
        alert('Error fetching prices: ' + error.message);
    }
}

// Load all stores
async function loadAndDisplayStores() {
    try {
        console.log('📥 Fetching all stores...');
        const stores = await api.getStores();
        
        const container = document.getElementById('storesList');
        if (!container) return;
        
        container.innerHTML = '<h3>Available Stores (' + stores.length + ')</h3>';
        stores.forEach(store => {
            const div = document.createElement('div');
            div.className = 'store-card';
            div.innerHTML = `
                <strong>${store.name}</strong>
                <p>Location: ${store.location}</p>
                <p>Category: ${store.category}</p>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading stores:', error);
    }
}

// =======================
// 3. ADMIN FUNCTIONS
// =======================

// Get pending items (items awaiting approval)
async function loadPendingItems() {
    try {
        console.log('📥 Fetching pending items...');
        const pending = await api.getPendingItems();
        
        console.table(pending);
        alert(`Found ${pending.length} pending items for review`);
        return pending;
    } catch (error) {
        alert('Error fetching pending items: ' + error.message);
    }
}

// Approve an item
async function approveItemUI(itemId) {
    if (!confirm('Approve this item?')) return;
    
    try {
        console.log('✅ Approving item', itemId);
        const result = await api.approveItem(itemId);
        alert('✅ Item approved successfully!');
        console.log('Result:', result);
    } catch (error) {
        alert('❌ Failed to approve: ' + error.message);
    }
}

// Reject an item
async function rejectItemUI(itemId) {
    const reason = prompt('Enter rejection reason:');
    if (reason === null) return;
    
    try {
        console.log('❌ Rejecting item', itemId);
        const result = await api.rejectItem(itemId, reason);
        alert('Item rejected successfully');
        console.log('Result:', result);
    } catch (error) {
        alert('Failed to reject: ' + error.message);
    }
}

// =======================
// 4. DELETE FUNCTIONS
// =======================

// Delete item
async function deleteItemUI(itemId) {
    if (!confirm('Delete this item? This cannot be undone.')) return;
    
    try {
        console.log('🗑️ Deleting item', itemId);
        await api.deleteItem(itemId);
        alert('✅ Item deleted');
        loadAndDisplayItems(); // Refresh list
    } catch (error) {
        alert('❌ Failed to delete: ' + error.message);
    }
}

// Delete price
async function deletePriceUI(priceId) {
    if (!confirm('Delete this price?')) return;
    
    try {
        console.log('🗑️ Deleting price', priceId);
        await api.deletePrice(priceId);
        alert('✅ Price deleted');
    } catch (error) {
        alert('❌ Failed to delete: ' + error.message);
    }
}

// =======================
// 5. SEARCH FUNCTIONS
// =======================

// Search stores by name
async function searchStoresUI(query) {
    if (!query.trim()) {
        alert('Enter a search query');
        return;
    }
    
    try {
        console.log('🔍 Searching stores:', query);
        const results = await api.searchStores(query);
        
        console.table(results);
        alert(`Found ${results.length} stores:\n\n` + 
              results.map(s => `${s.name} - ${s.location}`).join('\n'));
    } catch (error) {
        alert('Search error: ' + error.message);
    }
}

// =======================
// 6. ML/HEATMAP FUNCTIONS
// =======================

// Get heatmap for item
async function showHeatmapUI(itemId) {
    try {
        console.log('🔥 Fetching heatmap for item', itemId);
        const heatmap = await api.getHeatmap(itemId, 30);
        
        console.log('Heatmap data:', heatmap);
        
        // Display heatmap locations
        const locations = heatmap.heatmap || [];
        alert(`Heatmap for ${heatmap.item} (last ${heatmap.days} days):\n\n` +
              locations.map(l => 
                  `${l.store_id}: ₦${l.min_price}-${l.max_price} (Intensity: ${(l.intensity*100).toFixed(1)}%)`
              ).join('\n'));
    } catch (error) {
        alert('Error fetching heatmap: ' + error.message);
    }
}

// Get price prediction
async function predictPriceUI(itemId) {
    try {
        console.log('🤖 Getting price prediction for item', itemId);
        const prediction = await api.predictPrice(itemId);
        
        console.log('Prediction:', prediction);
        alert(`Price Prediction:\n${JSON.stringify(prediction, null, 2)}`);
    } catch (error) {
        alert('Prediction error: ' + error.message);
    }
}

// =======================
// 7. PAYMENT FUNCTIONS
// =======================

// Process payment
async function processPaymentUI() {
    const amount = parseFloat(prompt('Enter amount to pay:'));
    if (isNaN(amount) || amount <= 0) return;
    
    const description = prompt('Enter description (optional):') || 'Payment';
    
    try {
        console.log('💳 Processing payment...');
        const result = await api.processPayment({
            amount,
            description,
            user_id: currentUserId
        });
        
        alert('✅ Payment processed successfully!');
        console.log('Payment result:', result);
    } catch (error) {
        alert('❌ Payment failed: ' + error.message);
    }
}

// =======================
// 8. INITIALIZATION
// =======================

// Call on page load to set user ID
function initializeApp() {
    // Get or generate user ID
    let userId = localStorage.getItem('userId');
    if (!userId) {
        userId = Math.floor(Math.random() * 10000) + 1;
        localStorage.setItem('userId', userId);
    }
    currentUserId = userId;
    
    console.log(`✓ App initialized for user ${currentUserId}`);
    console.log(`✓ API URL: ${API_URL}`);
    console.log(`✓ API Service ready`, api);
}

// =======================
// 9. QUICK TEST COMMANDS
// =======================

// Run in browser console to test
window.testAPI = {
    testConnection: async () => {
        try {
            const response = await fetch(API_URL);
            const data = await response.json();
            console.log('✓ Backend is running:', data);
        } catch (e) {
            console.error('✗ Cannot reach backend:', e.message);
        }
    },
    
    getAllItems: () => api.getItems().then(console.log),
    getAllPrices: () => api.getPrices().then(console.log),
    getAllStores: () => api.getStores().then(console.log),
    getPendingItems: () => api.getPendingItems().then(console.log),
    
    createTestItem: () => api.createItem({
        name: 'Test Item ' + Date.now(),
        category: 'edibles',
        description: 'Test item',
        image_url: ''
    }).then(console.log),
    
    searchStores: (q) => api.searchStores(q).then(console.log),
    
    getHeatmap: (itemId) => api.getHeatmap(itemId).then(console.log),
};

// Usage: In browser console:
// testAPI.testConnection()
// testAPI.getAllItems()
// testAPI.createTestItem()
// testAPI.searchStores('Shoprite')
