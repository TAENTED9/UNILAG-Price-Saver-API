from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Store
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/stores", tags=["Stores"])

class StoreResponse(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[StoreResponse])
def get_all_stores(db: Session = Depends(get_db)):
    """Get all stores with their locations (lat/lng from Google Maps)."""
    stores = db.query(Store).all()
    return stores

@router.get("/search", response_model=List[StoreResponse])
def search_stores(q: str, db: Session = Depends(get_db)):
    """Search stores by name."""
    stores = db.query(Store).filter(Store.name.ilike(f"%{q}%")).all()
    return stores

@router.post("/", response_model=StoreResponse)
def create_store(name: str, lat: float, lng: float, db: Session = Depends(get_db)):
    """Create a new store with coordinates from Google Maps."""
    new_store = Store(name=name, lat=lat, lng=lng)
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store
