from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)  # For auth
    password_hash = Column(String, nullable=True)  # Hashed password
    email = Column(String, unique=True, index=True, nullable=True)  # Made nullable for backward compat
    display_name = Column(String, nullable=True)
    role = Column(String, default="student")
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    pending_prices = relationship("PendingPrice", back_populates="submitter")
    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    """Simple category: EDIBLES, DRINKS, or NON-EDIBLES"""
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # EDIBLES, DRINKS, NON-EDIBLES
    icon = Column(String, nullable=True)  # emoji or icon
    description = Column(String, nullable=True)
    
    prices = relationship("Price", back_populates="category", cascade="all, delete-orphan")


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("Price", back_populates="store")


class Price(Base):
    """Price entry with brand, pack size, and normalized unit"""
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    
    # Item details (name required, others optional)
    name = Column(String, nullable=False, index=True)  # e.g., "Rice", "Peak Milk"
    brand = Column(String, nullable=True)  # e.g., "Peak Milk"
    pack_size = Column(String, nullable=True)  # e.g., "500"
    pack_unit = Column(String, nullable=True)  # e.g., "g", "kg", "ml", "L", "pcs", "pack"
    
    # Pricing (price required)
    price = Column(Float, nullable=False)  # ₦
    price_per_unit = Column(Float, nullable=True)  # ₦ per unit for comparison
    
    # Location & metadata
    retailer = Column(String, nullable=True)  # Store/shop name
    location = Column(String, nullable=True)  # Location/area
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Status
    status = Column(String, default="pending", index=True)  # pending, approved, rejected
    
    category = relationship("Category", back_populates="prices")
    store = relationship("Store", back_populates="prices")


class PendingPrice(Base):
    __tablename__ = "pending_prices"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String, nullable=False)
    parsed_price = Column(Float, nullable=True)
    image_path = Column(String, nullable=True)    # path to uploaded image
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    location_text = Column(String, nullable=True)     # user-entered location/canteen name
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # e.g., pending, approved, rejected
    admin_notes = Column(Text, nullable=True)

    submitter = relationship("User", back_populates="pending_prices")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class Item(Base):
    """Legacy Item model - kept for backward compatibility"""
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="pending", index=True)
    is_public = Column(Boolean, default=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ItemSubmission(Base):
    """User submissions of items - awaiting admin approval"""
    __tablename__ = "item_submissions"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    item_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    location = Column(String, nullable=True)
    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_folder = Column(String, nullable=True)
    status = Column(String, default="pending")
    admin_notes = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    submitter = relationship("User", foreign_keys=[submitter_id])
    approver = relationship("User", foreign_keys=[approved_by])



"""
Add to app/models.py - User Preferences for personalized comparison
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class UserPreference(Base):
    """
    Store user preferences for smart shopping comparison
    Enables personalized recommendations and learning
    """
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Transport preferences
    transport_mode = Column(String, default="walking")  # walking, driving, transit, bicycling
    per_km_cost = Column(Float, default=40.0)  # ₦/km
    base_trip_cost = Column(Float, default=0.0)  # ₦ (fixed cost per trip)
    
    # Time valuation
    value_of_time_per_min = Column(Float, default=10.0)  # ₦ per minute
    
    # Loyalty & behavior
    preferred_store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    loyalty_penalty = Column(Float, default=0.0)  # ₦ (psychological cost of switching)
    
    # Personalization (learned from behavior)
    willingness_to_travel_score = Column(Float, default=0.5)  # 0-1 scale
    avg_basket_size = Column(Float, default=5.0)  # Average number of items
    
    # Display preferences
    preferred_sort = Column(String, default="best_value")  # best_value, closest, cheapest
    show_low_confidence_stores = Column(Boolean, default=False)
    
    # Alert settings
    alert_threshold_high = Column(Float, default=300.0)  # ₦ for "worth switching"
    alert_threshold_low = Column(Float, default=100.0)   # ₦ for "maybe"
    enable_push_alerts = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, mode={self.transport_mode})>"


class SwitchingEvent(Base):
    """
    Track when users act on switching recommendations
    Used for personalization and metric tracking
    """
    __tablename__ = "switching_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Recommendation details
    from_store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    to_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    
    # Net saving calculation
    net_saving_shown = Column(Float, nullable=False)  # What we told them
    distance_km = Column(Float, nullable=False)
    travel_time_min = Column(Float, nullable=False)
    
    # User action
    user_accepted = Column(Boolean, nullable=False)  # Did they follow recommendation?
    accepted_at = Column(DateTime, nullable=True)
    
    # Context
    basket_item_count = Column(Integer, nullable=False)
    basket_total_value = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SwitchingEvent(user_id={self.user_id}, accepted={self.user_accepted})>"


class PriceAlert(Base):
    """
    User-configured price alerts with net saving triggers
    """
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Alert criteria
    item_name = Column(String, nullable=False)  # Item to watch
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Trigger conditions
    target_price = Column(Float, nullable=True)  # Alert if price drops below this
    min_net_saving = Column(Float, nullable=True)  # Alert if net saving exceeds this
    max_distance_km = Column(Float, default=5.0)  # Only consider stores within radius
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PriceAlert(user_id={self.user_id}, item={self.item_name})>"


# ==================== HELPER FUNCTIONS ====================

def get_or_create_user_preferences(user_id: int, db) -> UserPreference:
    """
    Get user preferences or create with defaults
    """
    prefs = db.query(UserPreference).filter(
        UserPreference.user_id == user_id
    ).first()
    
    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


def update_willingness_to_travel(user_id: int, accepted: bool, net_saving: float, distance_km: float, db):
    """
    Update user's willingness to travel score based on behavior
    
    Learning algorithm:
    - If user accepts high net saving at long distance → increase score
    - If user rejects low net saving at short distance → decrease score
    - Score range: 0 (never travels) to 1 (always travels for savings)
    """
    prefs = get_or_create_user_preferences(user_id, db)
    
    # Current score
    current_score = prefs.willingness_to_travel_score
    
    # Calculate expected behavior (simple heuristic)
    value_per_km = net_saving / (distance_km + 0.1)  # Avoid division by zero
    
    if accepted:
        # User accepted - they're willing to travel for this value
        if value_per_km < 50:  # Low value per km
            # They're more willing than expected
            adjustment = 0.05
        else:
            # Expected behavior
            adjustment = 0.02
    else:
        # User rejected
        if value_per_km > 100:  # High value per km
            # They're less willing than expected
            adjustment = -0.05
        else:
            # Expected behavior
            adjustment = -0.02
    
    # Update score (with bounds)
    new_score = max(0.0, min(1.0, current_score + adjustment))
    prefs.willingness_to_travel_score = new_score
    
    # Also update average basket size
    db.commit()
    
    return new_score


def adjust_thresholds_for_user(base_threshold_high: float, base_threshold_low: float, prefs: UserPreference) -> tuple:
    """
    Personalize thresholds based on user's willingness to travel
    
    High willingness → lower thresholds (they'll travel for smaller savings)
    Low willingness → higher thresholds (need bigger savings to motivate)
    """
    willingness = prefs.willingness_to_travel_score
    
    # Scale thresholds inversely with willingness
    # willingness=0.5 (default) → no change
    # willingness=1.0 → thresholds * 0.5
    # willingness=0.0 → thresholds * 1.5
    scale_factor = 1.5 - willingness
    
    adjusted_high = base_threshold_high * scale_factor
    adjusted_low = base_threshold_low * scale_factor
    
    return adjusted_high, adjusted_low
