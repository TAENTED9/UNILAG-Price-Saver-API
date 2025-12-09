from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items, prices, payments, ml, pending, stores, admin_items, auth, google_maps
from app.database import init_db, SessionLocal
from app.models import Category
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ensure DB is created at app start
    init_db()
    
    db = SessionLocal()
    if db.query(Category).count() == 0:
        seed_categories(db)
    db.close()
    
    print("Backend started successfully!")
    yield


def seed_categories(db):
    """Populate database with 3 simple categories: EDIBLES, DRINKS, NON-EDIBLES"""
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


app = FastAPI(title="UNILAG Price Saver API", version="1.0.0", lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(items.router)
app.include_router(prices.router)
app.include_router(pending.router)
app.include_router(payments.router)
app.include_router(ml.router)
app.include_router(stores.router)
app.include_router(admin_items.router)
app.include_router(admin_items.router_user)
app.include_router(auth.router)
app.include_router(google_maps.router)


@app.get("/")
def home():
    return {"status": "ok", "message": "UNILAG Price Saver API is running!"}

