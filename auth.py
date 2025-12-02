# app/auth.py
import os
from fastapi import Header, HTTPException, status, Depends

ADMIN_KEY = os.getenv("ADMIN_API_KEY", "change-me-in-env")

def admin_required(x_admin_key: str = Header(None)):
    if x_admin_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing admin key")
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key")
    return True
