from supabase import create_client, Client
from app.config import settings
import uuid

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.bucket = "statements"

    def upload_file(self, file_bytes: bytes, filename: str, user_id: str) -> str:
        """Upload to Supabase Storage, return public URL."""
        path = f"{user_id}/{uuid.uuid4()}_{filename}"
        self.client.storage.from_(self.bucket).upload(
            path, file_bytes, {"content-type": "application/octet-stream"}
        )
        url = self.client.storage.from_(self.bucket).get_public_url(path)
        return url

    def download_file(self, url: str) -> bytes:
        """Download file bytes from Supabase Storage."""
        # Extract path from URL
        path = url.split(f"/storage/v1/object/public/{self.bucket}/")[-1]
        return self.client.storage.from_(self.bucket).download(path)
