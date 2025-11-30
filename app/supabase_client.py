import os
import uuid
from typing import Optional
from fastapi import UploadFile

try:
    from supabase import create_client, Client  # supabase-py v2
except Exception:
    create_client = None
    Client = None  # type: ignore

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "inventariobar")

_client: Optional["Client"] = None

def get_client() -> Optional["Client"]:
    """Devuelve el cliente supabase si hay credenciales; si no, None."""
    global _client
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

async def upload_image(file: UploadFile, folder: str = "productos") -> Optional[str]:
    """
    Sube la imagen a Storage y devuelve URL pública, o None si falla
    o si no hay credenciales configuradas.
    """
    client = get_client()
    if client is None or file is None:
        return None

    try:
        ext = (file.filename or "jpg").split(".")[-1].lower()
        fname = f"{uuid.uuid4()}.{ext}"
        path = f"{folder}/{fname}"

        content = await file.read()
        client.storage.from_(SUPABASE_BUCKET).upload(
            path,
            content,
            {"content-type": file.content_type or "application/octet-stream", "upsert": False},
        )

        # v2 suele devolver un dict con 'publicUrl'
        public = client.storage.from_(SUPABASE_BUCKET).get_public_url(path)
        if isinstance(public, dict):
            return public.get("publicUrl") or public.get("public_url")
        return str(public)
    except Exception as e:
        # No romper el flujo de tu app si falla el upload
        print("WARN: Supabase upload error:", e)
        return None
