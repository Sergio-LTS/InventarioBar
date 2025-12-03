# app/services/storage_supabase.py
import os
import uuid
from supabase import create_client, Client
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "inventario")

def _client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
        raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE en variables de entorno")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

async def upload_image_get_public_url(file: UploadFile, folder: str = "productos") -> str | None:
    """
    Sube el archivo al bucket público y devuelve la URL pública (o None si no hay archivo).
    """
    if not file or not file.filename:
        return None

    ext = (file.filename.split(".")[-1] or "jpg").lower()
    filename = f"{uuid.uuid4()}.{ext}"
    path_in_bucket = f"{folder}/{filename}"

    sb = _client()
    data = await file.read()  # lee bytes del UploadFile
    # sube con upsert=True para no fallar si el nombre ya existiera (muy improbable con uuid)
    res = sb.storage.from_(SUPABASE_BUCKET).upload(path_in_bucket, data, {"upsert": True})
    # obtener URL pública
    pub = sb.storage.from_(SUPABASE_BUCKET).get_public_url(path_in_bucket)
    return pub
