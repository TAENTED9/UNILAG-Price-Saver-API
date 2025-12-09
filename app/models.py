from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
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
