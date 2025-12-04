# app/services/supabase_storage.py
import os, uuid
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client

def _client() -> Optional[Client]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        return None  # ← sin credenciales: no romper
    return create_client(url, key)

BUCKET = os.getenv("SUPABASE_BUCKET", "inventariobar")

async def upload_image_get_public_url(file: Optional[UploadFile], folder: str = "uploads") -> Optional[str]:
    # Sin archivo → nada que subir
    if file is None or not getattr(file, "filename", ""):
        return None

    sb = _client()
    # Sin cliente (faltan envs) → no subir, pero no romper
    if sb is None:
        return None

    # Leer bytes
    data = await file.read()
    ext = (file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg").lower()
    path = f"{folder}/{uuid.uuid4()}.{ext}"

    # Subir
    r = sb.storage.from_(BUCKET).upload(path, data)
    if getattr(r, "error", None):
        # Fallo de Storage → no romper el flujo de negocio
        return None

    # URL pública
    public = sb.storage.from_(BUCKET).get_public_url(path)
    return getattr(public, "get", lambda _k, _d=None: None)("publicUrl", None) if hasattr(public, "get") else public
