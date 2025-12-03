# app/routes/health.py
import os
from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/health", tags=["health"])

EXPECTED = os.getenv("PROJECT_KEY", "adsfhkdjashgfdjashgkfdjashgfdjashgfdjashg")

@router.get("/header-check")
async def header_check(request: Request):
    got = request.headers.get("x-proyecto-key")
    if got != EXPECTED:
        raise HTTPException(status_code=401, detail="Header x-proyecto-key inválido o ausente")
    return {"ok": True}
