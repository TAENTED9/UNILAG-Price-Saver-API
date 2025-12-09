"""Price prediction engine using Rust for heavy calculations."""

try:
    import rust_engine
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("Warning: Rust engine not available, using fallback predictions")


def compute_cheapest_price(prices):
    """Find the cheapest price from a list of prices using Rust."""
    amounts = [p.amount for p in prices]
    if RUST_AVAILABLE:
        cheapest = rust_engine.cheapest(amounts)
    else:
        cheapest = min(amounts) if amounts else 0
    return {"cheapest_price": cheapest}


def predict_price(item: str, location: str) -> dict:
    """Predict price for an item at a given location.
    
    Uses Rust for fast calculation, falls back to Python if not available.
    """
    if RUST_AVAILABLE and hasattr(rust_engine, "predict_price"):
        prediction = rust_engine.predict_price(item, location)
    else:
        # Simple Python fallback: hash-based prediction
        hash_val = (len(item) * 100.0 + len(location) * 50.0) % 1000.0
        prediction = 400.0 + hash_val
    
    return {
        "item": item,
        "location": location,
        "predicted_price": prediction
    }


def calculate_savings(current_price: float, cheapest_price: float) -> dict:
    """Calculate savings between current and cheapest price."""
    if RUST_AVAILABLE and hasattr(rust_engine, "savings"):
        savings_amount = rust_engine.savings(current_price, cheapest_price)
    else:
        savings_amount = current_price - cheapest_price
    
    return {
        "current_price": current_price,
        "cheapest_price": cheapest_price,
        "savings": savings_amount,
        "savings_percentage": (savings_amount / current_price * 100) if current_price > 0 else 0
    }

