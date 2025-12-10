from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Price, PendingPrice, User, Transaction
from app.schemas import PriceCreate, PriceOut, PendingPriceOut
from app.services.price_engine import compute_cheapest_price
from datetime import datetime
import os, time
from typing import Optional

router = APIRouter(prefix="/prices", tags=["Prices"])

"""
Serverless note: Vercel's Python runtime has a read-only filesystem except /tmp.
Default upload dir therefore points to /tmp to avoid import-time crashes.
"""
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    # If even /tmp is not writable, fall back to /tmp directly
    UPLOAD_DIR = "/tmp"

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_required(x_admin_key: Optional[str] = Header(None)):
    if x_admin_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing admin key")
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key")
    return True

@router.post("/", response_model=PriceOut)
def submit_price(price: PriceCreate, db: Session = Depends(get_db)):
    # Handle both 'amount' and 'price' field names
    amount = price.amount or price.price
    if not amount:
        raise HTTPException(status_code=400, detail="Price/amount is required")
    
    # If store_name is provided, use it as location
    location = price.location or price.store_name or "Unknown"
    
    # Create new Price row
    new_price = Price(
        item_id=price.item_id,
        location=location,
        amount=amount,
        store_id=price.store_id
    )
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

@router.get("/compare/{item_id}")
def compare_prices(item_id: int, db: Session = Depends(get_db)):
    prices = db.query(Price).filter(Price.item_id == item_id).all()
    result = compute_cheapest_price(prices)
    return result

# Draft image uploads (student submission)
@router.post("/draft", response_model=PendingPriceOut)
async def submit_price_draft(
    item: str = Form(...),
    parsed_price: Optional[float] = Form(None),
    location_text: Optional[str] = Form(None),
    submitter_email: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Basic file type + size checks (frontend should enforce too)
    if image.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    safe_name = f"{int(time.time())}_{image.filename}"
    path = os.path.join(UPLOAD_DIR, safe_name)
    content = await image.read()
    # Enforce 8MB size limit here
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    with open(path, "wb") as f:
        f.write(content)

    submitter = None
    if submitter_email:
        submitter = db.query(User).filter(User.email == submitter_email).first()
        if not submitter:
            submitter = User(email=submitter_email, display_name=submitter_email.split("@")[0])
            db.add(submitter)
            db.commit()
            db.refresh(submitter)

    draft = PendingPrice(
        item=item,
        parsed_price=parsed_price,
        image_path=path,
        submitter_id=submitter.id if submitter else None,
        location_text=location_text
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft

# Admin endpoints to manage drafts
@router.get("/admin/drafts", dependencies=[Depends(admin_required)])
def list_drafts(db: Session = Depends(get_db)):
    drafts = db.query(PendingPrice).filter(PendingPrice.status == "pending").order_by(PendingPrice.created_at.desc()).all()
    return drafts

@router.post("/admin/drafts/{draft_id}/approve", dependencies=[Depends(admin_required)])
def approve_draft(draft_id: int, store_id: Optional[int] = None, db: Session = Depends(get_db)):
    draft = db.query(PendingPrice).get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    # create Price record
    price_row = Price(
        item_id=None,  # optional: map item name to Item table later 
        location=draft.location_text,
        amount=draft.parsed_price or 0.0,
        store_id=store_id,
        submitted_by=draft.submitter_id,
        submitted_at=datetime.utcnow()
    )
    db.add(price_row)
    draft.status = "approved"
    db.commit()
    db.refresh(price_row)
    db.refresh(draft)

    # cashback logic
    if draft.submitter_id:
        submitter = db.query(User).get(draft.submitter_id)
        # Example reward: fixed, change to percentage or dynamic logic 
        reward = 50.0
        submitter.balance = (submitter.balance or 0.0) + reward
        txn = Transaction(user_id=submitter.id, amount=reward, reason=f"Cashback for price approval of {draft.item}")
        db.add(txn)
        db.commit()

    return {"status": "approved", "price_id": price_row.id}

@router.post("/admin/drafts/{draft_id}/reject", dependencies=[Depends(admin_required)])
def reject_draft(draft_id: int, reason: Optional[str] = None, db: Session = Depends(get_db)):
    draft = db.query(PendingPrice).get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft.status = "rejected"
    draft.admin_notes = reason
    db.commit()
    return {"status": "rejected"}
