from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Price, Category, Store, Item
from app.schemas import (
    PriceCreate, PriceOut,
    CategoryCreate, CategoryOut
)
from typing import List

router = APIRouter(prefix="/items", tags=["Items"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ CATEGORIES (3-Level) ============

@router.get("/categories/all", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return db.query(Category).all()

@router.post("/categories/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    new_cat = Category(**category.dict())
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat

# ============ PRICES (with enhanced details) ============

@router.get("/prices/all", response_model=List[PriceOut])
def get_all_prices(db: Session = Depends(get_db)):
    """Get all approved prices"""
    return db.query(Price).filter(Price.status == "approved").all()

@router.get("/prices/category/{category_id}", response_model=List[PriceOut])
def get_prices_for_category(category_id: int, db: Session = Depends(get_db)):
    """Get all prices for a specific category"""
    return db.query(Price).filter(
        Price.category_id == category_id,
        Price.status == "approved"
    ).all()

@router.post("/prices/", response_model=PriceOut)
def submit_price(price: PriceCreate, db: Session = Depends(get_db)):
    """Submit a new price"""
    new_price = Price(**price.dict())
    if not new_price.status:
        new_price.status = "pending"
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

@router.get("/prices/pending/", response_model=List[PriceOut])
def get_pending_prices(db: Session = Depends(get_db)):
    """Get all pending price submissions"""
    return db.query(Price).filter(Price.status == "pending").all()

@router.put("/prices/{price_id}/approve")
def approve_price(price_id: int, db: Session = Depends(get_db)):
    """Admin: Approve a pending price"""
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    price.status = "approved"
    db.commit()
    return {"status": "approved", "id": price_id}

@router.put("/prices/{price_id}/reject")
def reject_price(price_id: int, db: Session = Depends(get_db)):
    """Admin: Reject a pending price"""
    price = db.query(Price).filter(Price.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    price.status = "rejected"
    db.commit()
    return {"status": "rejected", "id": price_id}
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}