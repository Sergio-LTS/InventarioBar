# app/services/supabase_storage.py
import os
import uuid
import httpx
from fastapi import UploadFile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "inventario")

def _ensure_env():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
        raise RuntimeError("Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE en las variables de entorno.")
    if not SUPABASE_BUCKET:
        raise RuntimeError("Configura SUPABASE_BUCKET en las variables de entorno.")

async def upload_image_to_supabase(file: UploadFile, folder: str = "productos") -> str:
    """
    Sube un archivo al bucket público de Supabase Storage usando el Service Role (solo en servidor).
    Devuelve la URL pública para guardarla en la DB (columna imagen_url).
    """
    _ensure_env()

    # nombre único
    ext = (file.filename or "jpg").split(".")[-1].lower()
    key = f"{folder}/{uuid.uuid4()}.{ext}"

    data = await file.read()
    if not data:
        raise ValueError("El archivo de imagen está vacío.")

    endpoint = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{key}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
        "Content-Type": file.content_type or "application/octet-stream",
        "x-upsert": "true",   # permitir sobrescribir si casualmente se repite
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(endpoint, headers=headers, content=data)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Fallo subiendo a Supabase ({resp.status_code}): {resp.text}")

    # URL pública (bucket debe ser público)
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{key}"
    return public_url
