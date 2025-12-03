# app/supabase_client.py
import os
import uuid
from typing import Optional
from fastapi import UploadFile
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "Mundiclass")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

async def upload_image_to_supabase(file: UploadFile, folder: str = "productos") -> str:
    """
    Sube un archivo al bucket público y devuelve la URL pública.
    Requiere SUPABASE_SERVICE_ROLE (server-side).
    """
    if supabase is None:
        raise RuntimeError("Supabase no configurado (faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE).")

    ext = (file.filename or "").split(".")[-1].lower() or "jpg"
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"
    data = await file.read()

    # Subir (upsert True por si reintentas misma clave)
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        key, data, {"content-type": file.content_type or "application/octet-stream", "upsert": True}
    )
    # URL pública (el bucket debe ser público)
    public = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(key)
    return public
