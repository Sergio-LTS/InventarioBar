# app/supabase_service.py
import os
import uuid
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET", "inventariobar")  # puedes cambiarlo

_supabase: Client | None = None

def get_client() -> Client:
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Faltan SUPABASE_URL o SUPABASE_KEY en variables de entorno")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase

def upload_bytes_and_get_public_url(content: bytes, content_type: str, folder: str = "productos") -> str:
    """
    Sube bytes al bucket y devuelve la URL pública.
    """
    sp = get_client()
    ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }.get(content_type, "bin")
    path = f"{folder}/{uuid.uuid4()}.{ext}"
    # upsert=True para sobreescribir si llegara a existir el mismo nombre (muy improbable con uuid)
    sp.storage.from_(BUCKET_NAME).upload(
        path=path,
        file=content,
        file_options={"contentType": content_type, "upsert": True},
    )
    public_url = sp.storage.from_(BUCKET_NAME).get_public_url(path)
    return public_url
