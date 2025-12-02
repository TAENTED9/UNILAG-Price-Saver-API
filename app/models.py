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
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, nullable=True)

    prices = relationship("Price", back_populates="item")


class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    location = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="prices")
    item = relationship("Item", back_populates="prices")
    submitter = relationship("User")
    