"""
app/routers/compare.py
Basket-level comparison with net savings calculation
Factors: price difference, transport cost, time cost, effort/loyalty cost
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import math
import os
import requests
from app.database import SessionLocal
from app.models import Price, Store, Category

router = APIRouter(prefix="/compare", tags=["Compare & Net Savings"])

# Google Maps API Key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Default user preferences (can be overridden per request)
DEFAULT_TRANSPORT_MODE = "driving"
DEFAULT_PER_KM_COST = 40.0  # ₦/km
DEFAULT_BASE_TRIP_COST = 0.0  # ₦ (0 for walking, 100 for driving)
DEFAULT_VALUE_OF_TIME = 10.0  # ₦/minute
DEFAULT_LOYALTY_PENALTY = 0.0  # ₦ (penalty for leaving familiar store)

# Thresholds for verdict
THRESHOLD_HIGH = 300.0  # ₦ - "Worth switching"
THRESHOLD_LOW = 100.0   # ₦ - "Maybe"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== SCHEMAS ====================

class BasketItem(BaseModel):
    """Item in user's basket"""
    name: str  # Item name (e.g., "Rice", "Beans")
    category_id: Optional[int] = None
    quantity: float = 1.0  # Quantity to buy

class UserPreferences(BaseModel):
    """User preferences for transport and value calculations"""
    transport_mode: str = DEFAULT_TRANSPORT_MODE  # walking, driving, transit
    per_km_cost: float = DEFAULT_PER_KM_COST
    base_trip_cost: float = DEFAULT_BASE_TRIP_COST
    value_of_time_per_min: float = DEFAULT_VALUE_OF_TIME
    loyalty_penalty: float = DEFAULT_LOYALTY_PENALTY
    preferred_store_id: Optional[int] = None

class CompareRequest(BaseModel):
    """Request to compare basket across stores"""
    items: List[BasketItem]
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None
    preferences: Optional[UserPreferences] = None

class StoreComparison(BaseModel):
    """Comparison result for one store"""
    store_id: int
    store_name: str
    store_lat: Optional[float] = None
    store_lng: Optional[float] = None
    
    # Pricing
    total_price: float
    missing_items: List[str] = []
    available_items_count: int = 0
    total_items_count: int = 0
    
    # Distance & Time
    distance_km: Optional[float] = None
    travel_time_min: Optional[float] = None
    
    # Costs
    transport_cost: Optional[float] = None
    time_cost: Optional[float] = None
    loyalty_cost: float = 0.0
    
    # Net Saving
    net_saving: float = 0.0
    
    # Verdict
    verdict: str  # "worth_switching", "maybe", "not_worth"
    verdict_emoji: str
    verdict_text: str
    
    # Metadata
    is_baseline: bool = False
    confidence: str = "high"  # high, medium, low (based on missing items)

class CompareResponse(BaseModel):
    """Full comparison response"""
    success: bool
    baseline: StoreComparison
    alternatives: List[StoreComparison]
    recommendations: List[str] = []
    total_items: int
    message: str

# ==================== HELPER FUNCTIONS ====================

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km using Haversine formula"""
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def estimate_travel_time(distance_km: float, mode: str) -> float:
    """Estimate travel time in minutes based on distance and mode"""
    speeds = {
        "walking": 5.0,    # km/h
        "driving": 30.0,   # km/h (accounting for Lagos traffic)
        "transit": 20.0,   # km/h (bus/danfo average)
        "bicycling": 15.0  # km/h
    }
    speed = speeds.get(mode, 20.0)
    return (distance_km / speed) * 60.0  # Convert to minutes

def calculate_transport_cost(distance_km: float, prefs: UserPreferences) -> float:
    """Calculate transport cost"""
    return prefs.base_trip_cost + (prefs.per_km_cost * distance_km)

def calculate_time_cost(travel_time_min: float, prefs: UserPreferences) -> float:
    """Monetize travel time"""
    return travel_time_min * prefs.value_of_time_per_min

def get_google_distance_matrix(
    origin_lat: float,
    origin_lng: float,
    destinations: List[tuple],
    mode: str = "driving"
) -> Dict[int, Dict]:
    """
    Get distance/time from Google Distance Matrix API
    Returns: {store_id: {"distance_km": X, "duration_min": Y}}
    """
    if not GOOGLE_MAPS_API_KEY:
        return {}
    
    # Build destinations string
    dest_str = "|".join([f"{lat},{lng}" for lat, lng in destinations])
    
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": dest_str,
        "mode": mode.lower(),
        "key": GOOGLE_MAPS_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("status") != "OK":
            return {}
        
        results = {}
        elements = data.get("rows", [{}])[0].get("elements", [])
        
        for i, element in enumerate(elements):
            if element.get("status") == "OK":
                distance_m = element.get("distance", {}).get("value", 0)
                duration_s = element.get("duration", {}).get("value", 0)
                
                results[i] = {
                    "distance_km": distance_m / 1000.0,
                    "duration_min": duration_s / 60.0
                }
        
        return results
    except Exception as e:
        print(f"Google Maps API error: {e}")
        return {}

def find_best_price_for_item(
    item_name: str,
    store_id: int,
    category_id: Optional[int],
    db: Session
) -> Optional[float]:
    """Find best (most recent) price for an item at a store"""
    query = db.query(Price).filter(
        Price.store_id == store_id,
        Price.name.ilike(f"%{item_name}%"),
        Price.status == "approved"
    )
    
    if category_id:
        query = query.filter(Price.category_id == category_id)
    
    price = query.order_by(Price.submitted_at.desc()).first()
    return price.price if price else None

def calculate_store_total(
    items: List[BasketItem],
    store_id: int,
    db: Session
) -> tuple:
    """
    Calculate total cost for basket at a store
    Returns: (total_price, missing_items, available_count)
    """
    total = 0.0
    missing = []
    available = 0
    
    for item in items:
        price = find_best_price_for_item(
            item.name,
            store_id,
            item.category_id,
            db
        )
        
        if price is not None:
            total += price * item.quantity
            available += 1
        else:
            missing.append(item.name)
            # Penalty for missing item (use average price + 20%)
            avg_price = get_average_price_for_item(item.name, item.category_id, db)
            if avg_price:
                total += avg_price * 1.2 * item.quantity
    
    return total, missing, available

def get_average_price_for_item(
    item_name: str,
    category_id: Optional[int],
    db: Session
) -> Optional[float]:
    """Get average price for an item across all stores"""
    query = db.query(Price).filter(
        Price.name.ilike(f"%{item_name}%"),
        Price.status == "approved"
    )
    
    if category_id:
        query = query.filter(Price.category_id == category_id)
    
    prices = query.all()
    if not prices:
        return None
    
    return sum(p.price for p in prices) / len(prices)

def determine_verdict(net_saving: float) -> tuple:
    """
    Determine verdict based on net saving
    Returns: (verdict, emoji, text)
    """
    if net_saving >= THRESHOLD_HIGH:
        return "worth_switching", "✅", f"Worth switching! Save ₦{net_saving:.2f}"
    elif net_saving >= THRESHOLD_LOW:
        return "maybe", "⚠️", f"Maybe worth it. Save ₦{net_saving:.2f}"
    else:
        return "not_worth", "❌", f"Not worth switching. Save only ₦{net_saving:.2f}"

# ==================== ENDPOINTS ====================

@router.post("/net_saving", response_model=CompareResponse)
async def compare_basket_net_saving(
    request: CompareRequest,
    db: Session = Depends(get_db)
):
    """
    Compare basket across stores with net saving calculation
    
    This endpoint answers: "Is it worth switching stores?"
    
    Calculation:
    NetSaving = (BaselineTotal - StoreTotal) - TransportCost - TimeCost - LoyaltyCost
    
    Returns stores ranked by Best Value (highest net saving)
    """
    
    if not request.items:
        raise HTTPException(status_code=400, detail="Basket is empty")
    
    # Use default preferences if not provided
    prefs = request.preferences or UserPreferences()
    
    # Get all stores with coordinates
    stores = db.query(Store).filter(
        Store.lat.isnot(None),
        Store.lng.isnot(None)
    ).all()
    
    if not stores:
        raise HTTPException(status_code=404, detail="No stores with location data")
    
    # Default user location (UNILAG Main Campus) if not provided
    user_lat = request.user_lat or 6.5158
    user_lng = request.user_lng or 3.3895
    
    # Calculate store totals
    comparisons = []
    
    for store in stores:
        total_price, missing_items, available_count = calculate_store_total(
            request.items,
            store.id,
            db
        )
        
        # Calculate distance
        distance_km = haversine_distance(
            user_lat, user_lng,
            store.lat, store.lng
        )
        
        # Estimate travel time
        travel_time_min = estimate_travel_time(distance_km, prefs.transport_mode)
        
        # Calculate costs
        transport_cost = calculate_transport_cost(distance_km, prefs)
        time_cost = calculate_time_cost(travel_time_min, prefs)
        
        # Loyalty cost
        loyalty_cost = 0.0
        if prefs.preferred_store_id and store.id != prefs.preferred_store_id:
            loyalty_cost = prefs.loyalty_penalty
        
        comparison = StoreComparison(
            store_id=store.id,
            store_name=store.name,
            store_lat=store.lat,
            store_lng=store.lng,
            total_price=total_price,
            missing_items=missing_items,
            available_items_count=available_count,
            total_items_count=len(request.items),
            distance_km=round(distance_km, 2),
            travel_time_min=round(travel_time_min, 1),
            transport_cost=round(transport_cost, 2),
            time_cost=round(time_cost, 2),
            loyalty_cost=loyalty_cost,
            net_saving=0.0,  # Will calculate after baseline
            verdict="",
            verdict_emoji="",
            verdict_text="",
            confidence="high" if len(missing_items) == 0 else "medium" if len(missing_items) <= 2 else "low"
        )
        
        comparisons.append(comparison)
    
    # Find baseline (nearest store or preferred store)
    if prefs.preferred_store_id:
        baseline = next(
            (c for c in comparisons if c.store_id == prefs.preferred_store_id),
            min(comparisons, key=lambda c: c.distance_km or 999)
        )
    else:
        baseline = min(comparisons, key=lambda c: c.distance_km or 999)
    
    baseline.is_baseline = True
    baseline_total = baseline.total_price
    
    # Calculate net savings for each store
    for comp in comparisons:
        if comp.store_id == baseline.store_id:
            comp.net_saving = 0.0
            comp.verdict = "baseline"
            comp.verdict_emoji = "📍"
            comp.verdict_text = "Your current/nearest store"
        else:
            price_diff = baseline_total - comp.total_price
            comp.net_saving = round(
                price_diff - comp.transport_cost - comp.time_cost - comp.loyalty_cost,
                2
            )
            
            verdict, emoji, text = determine_verdict(comp.net_saving)
            comp.verdict = verdict
            comp.verdict_emoji = emoji
            comp.verdict_text = text
    
    # Sort by net saving (descending)
    comparisons.sort(key=lambda c: c.net_saving, reverse=True)
    
    # Separate baseline and alternatives
    alternatives = [c for c in comparisons if not c.is_baseline]
    
    # Generate recommendations
    recommendations = []
    best = alternatives[0] if alternatives else None
    
    if best and best.net_saving >= THRESHOLD_HIGH:
        recommendations.append(
            f"🎯 Best deal: {best.store_name} - Save ₦{best.net_saving:.2f} net"
        )
    elif best and best.net_saving >= THRESHOLD_LOW:
        recommendations.append(
            f"⚠️ Small saving at {best.store_name} (₦{best.net_saving:.2f}). Consider if convenient."
        )
    else:
        recommendations.append(
            f"💡 Stay at {baseline.store_name}. Other stores don't offer better value after travel costs."
        )
    
    # Add trust-building message
    recommendations.append(
        "💭 This recommendation accounts for travel cost, time, and your preferences."
    )
    
    return CompareResponse(
        success=True,
        baseline=baseline,
        alternatives=alternatives[:10],  # Top 10 alternatives
        recommendations=recommendations,
        total_items=len(request.items),
        message=f"Compared {len(request.items)} items across {len(comparisons)} stores"
    )

@router.get("/stores/nearby")
async def get_nearby_stores(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius_km: float = Query(5.0, ge=0.5, le=50, description="Search radius in km"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get nearby stores within radius"""
    stores = db.query(Store).filter(
        Store.lat.isnot(None),
        Store.lng.isnot(None)
    ).all()
    
    nearby = []
    for store in stores:
        distance = haversine_distance(lat, lng, store.lat, store.lng)
        if distance <= radius_km:
            nearby.append({
                "store_id": store.id,
                "name": store.name,
                "lat": store.lat,
                "lng": store.lng,
                "distance_km": round(distance, 2)
            })
    
    nearby.sort(key=lambda s: s["distance_km"])
    return {
        "success": True,
        "stores": nearby[:limit],
        "total_found": len(nearby)
    }

@router.post("/check_worth_switching")
async def quick_check(
    current_price: float = Query(..., description="Current total price"),
    candidate_price: float = Query(..., description="Candidate store price"),
    distance_km: float = Query(..., description="Distance to candidate store"),
    transport_mode: str = Query("driving", description="Transport mode"),
    db: Session = Depends(get_db)
):
    """
    Quick check: Is it worth switching?
    Simple calculation without full basket analysis
    """
    prefs = UserPreferences(transport_mode=transport_mode)
    
    # Calculate costs
    travel_time = estimate_travel_time(distance_km, transport_mode)
    transport_cost = calculate_transport_cost(distance_km, prefs)
    time_cost = calculate_time_cost(travel_time, prefs)
    
    # Net saving
    price_diff = current_price - candidate_price
    net_saving = price_diff - transport_cost - time_cost
    
    verdict, emoji, text = determine_verdict(net_saving)
    
    return {
        "success": True,
        "worth_switching": verdict == "worth_switching",
        "net_saving": round(net_saving, 2),
        "price_saving": round(price_diff, 2),
        "transport_cost": round(transport_cost, 2),
        "time_cost": round(time_cost, 2),
        "travel_time_min": round(travel_time, 1),
        "verdict": verdict,
        "verdict_emoji": emoji,
        "verdict_text": text,
        "breakdown": {
            "current_price": current_price,
            "candidate_price": candidate_price,
            "distance_km": distance_km,
            "transport_mode": transport_mode
        }
    }