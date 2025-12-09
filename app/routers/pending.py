"""Pending prices router - handles user-submitted price entries awaiting approval."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import PendingPrice, User
from app.schemas import PendingPriceCreate, PendingPriceOut
from typing import List

router = APIRouter(prefix="/pending", tags=["Pending Prices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[PendingPriceOut])
def get_pending_prices(
    db: Session = Depends(get_db),
    status: str = Query(None, description="Filter by status: pending, approved, rejected"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get pending price submissions, optionally filtered by status."""
    query = db.query(PendingPrice)
    if status:
        query = query.filter(PendingPrice.status == status)
    return query.limit(limit).all()


@router.post("/", response_model=PendingPriceOut)
def create_pending_price(
    pending_price: PendingPriceCreate,
    db: Session = Depends(get_db)
):
    """Submit a pending price entry (image + parsed price)."""
    db_pending = PendingPrice(**pending_price.dict())
    db.add(db_pending)
    db.commit()
    db.refresh(db_pending)
    return db_pending


@router.get("/{pending_id}", response_model=PendingPriceOut)
def get_pending_price(pending_id: int, db: Session = Depends(get_db)):
    """Get a specific pending price entry."""
    pending = db.query(PendingPrice).filter(PendingPrice.id == pending_id).first()
    if not pending:
        return {"error": "Pending price not found"}
    return pending


@router.patch("/{pending_id}/status")
def update_pending_status(
    pending_id: int,
    status: str = Query(..., description="New status: approved, rejected"),
    admin_notes: str = Query(None),
    db: Session = Depends(get_db)
):
    """Update pending price status (admin action)."""
    pending = db.query(PendingPrice).filter(PendingPrice.id == pending_id).first()
    if not pending:
        return {"error": "Pending price not found"}
    
    pending.status = status
    if admin_notes:
        pending.admin_notes = admin_notes
    
    db.commit()
    db.refresh(pending)
    return {"status": "updated", "pending_price": pending}
