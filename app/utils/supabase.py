# app/utils/supabase.py
import os
import uuid
import mimetypes
import httpx
from fastapi import HTTPException

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "")

def _ensure_env():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE or not SUPABASE_BUCKET:
        raise HTTPException(status_code=500, detail="Supabase env vars missing")

def _guess_ext(filename: str, content_type: str | None) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    if content_type:
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext
    return ".bin"

async def upload_to_supabase(file_bytes: bytes, *, filename: str | None, folder: str, content_type: str | None):
    _ensure_env()
    ext = _guess_ext(filename or "", content_type)
    unique = f"{uuid.uuid4()}{ext}"
    path = f"{folder}/{unique}"

    # Subir objeto (upsert)
    put_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
        "Content-Type": content_type or "application/octet-stream",
        "x-upsert": "true",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.put(put_url, content=file_bytes, headers=headers)

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Supabase upload failed: {resp.text}")

    # URL pública
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"
    return public_url
