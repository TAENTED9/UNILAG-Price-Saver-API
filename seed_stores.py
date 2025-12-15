from app.database import SessionLocal
from app.models import Store
import random

db = SessionLocal()

# UNILAG area stores with realistic coordinates
stores_data = [
    {"name": "Shoprite Express", "lat": 6.5158, "lng": 3.3895},
    {"name": "Campus Mini-Mart", "lat": 6.5165, "lng": 3.3880},
    {"name": "Moremi Provisions", "lat": 6.5170, "lng": 3.3900},
    {"name": "Faculty Store", "lat": 6.5145, "lng": 3.3910},
    {"name": "Jaja Hall Shop", "lat": 6.5180, "lng": 3.3870},
]

for store_data in stores_data:
    # Check if store exists
    existing = db.query(Store).filter(Store.name == store_data["name"]).first()
    if not existing:
        store = Store(**store_data)
        db.add(store)
        print(f"✅ Added: {store_data['name']}")
    else:
        # Update coordinates if missing
        if not existing.lat or not existing.lng:
            existing.lat = store_data["lat"]
            existing.lng = store_data["lng"]
            print(f"🔄 Updated coordinates: {store_data['name']}")

db.commit()
print(f"\n✅ Seeded {len(stores_data)} stores!")
db.close()