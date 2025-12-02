from fastapi import FastAPI
from app.routers import items, prices, payments, ml, pending
from app.database import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ensure DB is created at app start
    init_db()
    print("Backend started successfully!")
    yield
    # optionally add shutdown logic here

app = FastAPI(title="UNILAG Price Saver API", version="1.0.0", lifespan=lifespan)

# Routers
app.include_router(items.router)
app.include_router(prices.router)
app.include_router(pending.router)
app.include_router(payments.router)
app.include_router(ml.router)


@app.get("/")
def home():
    return {"status": "ok", "message": "UNILAG Price Saver API is running!"}
