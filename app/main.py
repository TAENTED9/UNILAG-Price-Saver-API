from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items, prices, payments, ml, pending, stores, admin_items, auth, google_maps, compare
from app.database import init_db, SessionLocal
from app.models import Category
from contextlib import asynccontextmanager
import os

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
            "description": "Everything else: soap, detergent, oil bottles, toothbrush, batteries, utensils, diapers, toiletries"
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
# CORS
# ------------------------------
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Change from ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# ------------------------------
# API Routers (/api)
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
app.include_router(compare.router, prefix="/api")

# ------------------------------
# Serve Frontend (STATIC + HTML)
# ------------------------------
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent              # backend/app
FRONTEND_DIR = BASE_DIR / "frontend"                    # backend/app/frontend

# Check if frontend directory exists, if not, try root level
if not FRONTEND_DIR.exists():
    # Try parent directory (if frontend was moved to backend/frontend)
    ROOT_FRONTEND = BASE_DIR.parent / "frontend"
    if ROOT_FRONTEND.exists():
        FRONTEND_DIR = ROOT_FRONTEND
    else:
        # Try current directory as fallback
        FRONTEND_DIR = BASE_DIR

# 1) Serve static files correctly (only if directory exists)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    
    # 2) Serve login.html as home page
    @app.get("/", include_in_schema=False)
    async def serve_root():
        login_path = FRONTEND_DIR / "index.html"
        if login_path.exists():
            return FileResponse(login_path)
        return {"message": "Frontend files not found"}
    
    # Serve other HTML files
    @app.get("/user-dashboard.html", include_in_schema=False)
    async def serve_user_dashboard():
        dashboard_path = FRONTEND_DIR / "user-dashboard.html"
        if dashboard_path.exists():
            return FileResponse(dashboard_path)
        return {"error": "File not found"}
    
    @app.get("/admin-dashboard.html", include_in_schema=False)
    async def serve_admin_dashboard():
        dashboard_path = FRONTEND_DIR / "admin-dashboard.html"
        if dashboard_path.exists():
            return FileResponse(dashboard_path)
        return {"error": "File not found"}

