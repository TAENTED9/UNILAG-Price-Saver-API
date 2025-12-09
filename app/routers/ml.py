from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Price, Store, Item
from app.services.heatmap_engine import generate_item_heatmap
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/heatmap")
def heatmap(item: str, days: int = Query(7, ge=1, le=365)):
    """
    Generate heatmap for a specific item over the last `days` days.
    Returns a path to a JSON file and the heatmap dict.
    """
    heatmap_path, heatmap_data = generate_item_heatmap(item_name=item, days=days, output_path=f"heatmap_{item}.json")
    return {"status": "success", "heatmap_path": heatmap_path, "heatmap": heatmap_data}

@router.get("/search")
def search_item(item: str, days: int = Query(7, ge=1, le=365)):
    """
    Returns cheapest current price and top5 cheapest locations for an item.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    db = SessionLocal()
    try:
        # join Item if exists; allow search by item name string using Item table when available
        # We'll query Price rows for the last `days` and group per store/text location, taking most recent per location
        q = db.query(Price, Store).outerjoin(Store, Price.store_id == Store.id).filter(
            Price.submitted_at >= cutoff
        ).order_by(Price.submitted_at.desc())

        per_location = {}
        for price, store in q.all():
            # try to check if price belongs to the requested item name:
            # If you maintain Item table and price.item_id is linked, you could join and check; for now
            # check textual item match by comparing Item table (if exists) - fallback: assume price.item_id is None => match opt
            # Simpler approach: accept any price rows whose linked Item name equals `item` if present
            match = False
            if price.item_id:
                item_row = db.query(Item).filter(Item.id == price.item_id).first()
                if item_row and item_row.name.lower() == item.lower():
                    match = True
            else:
                # If no item_id, try matching location_text or other heuristics - skip unless item matches
                # We will skip rows without matching item when item table exists
                # If no Item rows at all, treat all prices as candidate and use price.item_id is None rows
                existing_items = db.query(Item).count()
                if existing_items == 0:
                    # treat every price row as candidate (legacy)
                    match = True

            if not match:
                continue

            loc_key = f"store:{store.id}" if store else f"text:{(price.location or 'unknown')}"
            if loc_key not in per_location:
                per_location[loc_key] = {
                    "price": price.amount,
                    "store": {"id": store.id, "name": store.name, "lat": store.lat, "lng": store.lng} if store else None,
                    "submitted_at": price.submitted_at
                }

        if not per_location:
            return {"item": item, "cheapest": None, "message": "No recent prices found", "heatmap_path": None}

        entries = list(per_location.values())
        entries.sort(key=lambda e: e["price"])
        cheapest = entries[0]
        top5 = entries[:5]

        heatmap_path, _ = generate_item_heatmap(item_name=item, days=days, output_path=f"heatmap_{item}.json")

        def serial(e):
            return {"price": e["price"], "store": e["store"], "submitted_at": e["submitted_at"].isoformat()}

        return {"item": item, "cheapest": serial(cheapest), "top5": [serial(x) for x in top5], "heatmap_path": heatmap_path}
    finally:
        db.close()
