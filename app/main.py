from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items, prices, payments, ml, pending, stores, admin_items, auth, google_maps
from app.database import init_db, SessionLocal
from app.models import Category
from contextlib import asynccontextmanager

# ------------------------------
# Lifespan: DB init + seed
# ------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    
    db = SessionLocal()
    if db.query(Category).count() == 0:
        seed_categories(db)
    db.close()
    
    print("Backend started successfully!")
    yield


def seed_categories(db):
    categories_data = [
        {
            "name": "EDIBLES",
            "description": "Things you eat: rice, bread, yam, meat, eggs, beans, fruits, vegetables, noodles"
        },
        {
            "name": "DRINKS",
            "description": "Things you drink: water, soda, juice, milk, beer, sachet water, powdered drinks"
        },
        {
            "name": "NON-EDIBLES",
            "description": "Everything else: soap, detergent, cooking oil bottles, toothbrush, batteries, kitchen utensils, diapers, toiletries"
        }
    ]
    
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
    
    db.commit()
    print("✅ 3 main categories seeded! (EDIBLES, DRINKS, NON-EDIBLES)")

# ------------------------------
# FastAPI App
# ------------------------------
app = FastAPI(title="UNILAG Price Saver API", version="1.0.0", lifespan=lifespan)

# ------------------------------
# CORS Middleware
# ------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# API Routers (all prefixed with /api)
# ------------------------------
app.include_router(items.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(pending.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(ml.router, prefix="/api")
app.include_router(stores.router, prefix="/api")
app.include_router(admin_items.router, prefix="/api")
app.include_router(admin_items.router_user, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(google_maps.router, prefix="/api")

# ------------------------------
# Serve frontend static files
# ------------------------------
from pathlib import Path
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

