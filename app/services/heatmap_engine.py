import json
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Price, Store, Item
from typing import Tuple

def _normalize_list(values: list[float]) -> list[float]:
    if not values:
        return []
    mn = min(values)
    mx = max(values)
    if mx == mn:
        return [1.0 for _ in values]
    return [(v - mn) / (mx - mn) for v in values]

def generate_item_heatmap(item_name: str, days: int = 7, output_path: str = "heatmap.json") -> Tuple[str, dict]:
    """
    Query DB for prices of `item_name` within last `days` days and compute
    per-location aggregates + an intensity score which favors locations where:
      - more submissions (higher count) AND
      - lower average price (cheaper)
    Returns (output_path, heatmap_dict).
    """
    db = SessionLocal()
    try:
        time_cutoff = datetime.utcnow() - timedelta(days=days)

        # We'll find the item id if Item exists
        item_row = db.query(Item).filter(Item.name.ilike(item_name)).first() if db.query(Item).count() > 0 else None
        item_id = item_row.id if item_row else None

        # Query Price rows in the timeframe, optionally filtering by item_id when Item table exists
        if item_id:
            q = db.query(Price, Store).outerjoin(Store, Price.store_id == Store.id).filter(
                Price.item_id == item_id,
                Price.submitted_at >= time_cutoff
            )
        else:
            # fallback: match by textual draft or legacy Price rows with null item_id if item table empty
            q = db.query(Price, Store).outerjoin(Store, Price.store_id == Store.id).filter(
                Price.submitted_at >= time_cutoff
            )

        location_map = {}
        for price, store in q.all():
            # If we have item_id filtering above, all rows match requested item; otherwise we include rows whose Item name matches if available
            # Build key: either store-based (preferred) or textual location
            if store and store.lat is not None and store.lng is not None:
                key = f"store:{store.id}"
                loc_info = {"name": store.name or "", "lat": store.lat, "lng": store.lng, "store_id": store.id}
            else:
                key = f"text:{(price.location or 'unknown')}"
                loc_info = {"name": price.location or "unknown", "lat": None, "lng": None, "store_id": None}

            entry = location_map.setdefault(key, {"prices": [], "qty": 0, "info": loc_info})
            entry["prices"].append(price.amount)
            entry["qty"] += 1

        location_stats = []
        for key, v in location_map.items():
            prices = v["prices"]
            avgp = sum(prices) / len(prices) if prices else 0.0
            mins = min(prices) if prices else 0.0
            maxs = max(prices) if prices else 0.0
            cnt = v["qty"]
            location_stats.append({
                "key": key,
                "name": v["info"]["name"],
                "store_id": v["info"]["store_id"],
                "lat": v["info"]["lat"],
                "lng": v["info"]["lng"],
                "count": cnt,
                "avg_price": avgp,
                "min_price": mins,
                "max_price": maxs,
            })

        # compute normalized counts and inverted price factor
        counts = [s["count"] for s in location_stats]
        norm_counts = _normalize_list([float(c) for c in counts]) if counts else []

        inverted_prices = [1.0 / (s["avg_price"] + 1e-6) for s in location_stats]
        norm_price_factor = _normalize_list(inverted_prices) if inverted_prices else []

        for i, s in enumerate(location_stats):
            c = norm_counts[i] if norm_counts else 0.0
            p = norm_price_factor[i] if norm_price_factor else 0.0
            intensity = 0.7 * c + 0.3 * p
            s["intensity"] = float(intensity)

        heatmap_data = {
            "item": item_name,
            "days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "heatmap": location_stats,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(heatmap_data, f, indent=2)

        return output_path, heatmap_data
    finally:
        db.close()
