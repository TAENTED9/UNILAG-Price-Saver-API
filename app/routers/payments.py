from fastapi import APIRouter
from app.services.squad import create_payment_link

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/pay")
def pay(amount: float, description: str):
    link = create_payment_link(amount, description)
    return {"payment_link": link}

@router.post("/topup")
def topup(user_email: str, amount: float):
    # In production you'd create an invoice and tie it to a user; return a paylink
    link = create_payment_link(amount, f"Topup for {user_email}")
    return {"payment_link": link}
