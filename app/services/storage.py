import logging
from typing import Optional
from supabase import Client
from app.db.supabase import supabase_client
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class StorageService:
    """Service for interacting with Supabase Storage."""
    
    def __init__(self, client: Optional[Client] = supabase_client):
        self.client = client
        self.bucket_name = "documents"
        
        if not self.client:
            logger.warning("StorageService initialized without a Supabase client.")
            
    def _ensure_client(self):
        if not self.client:
            raise AppException("Storage service is currently unavailable.", status_code=503)

    async def upload_file(self, file_path: str, file_bytes: bytes, content_type: str) -> str:
        """Uploads a file to Supabase storage.
        
        Args:
            file_path: The destination path in the bucket.
            file_bytes: The file contents.
            content_type: The MIME type of the file.
            
        Returns:
            The file path on success.
            
        Raises:
            AppException: If the upload fails.
        """
        self._ensure_client()
        try:
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            logger.info(f"Successfully uploaded file to {self.bucket_name}/{file_path}")
            # Supabase python client upload returns a Response object or dict, but if it fails it might raise an exception
            # Just return the path as success
            return file_path
        except Exception as e:
            logger.error(f"Failed to upload file to storage: {e}")
            raise AppException("Failed to upload file to storage.", status_code=500)

    async def delete_file(self, file_path: str) -> bool:
        """Deletes a file from Supabase storage.
        
        Args:
            file_path: The path of the file to delete.
            
        Returns:
            True if successful.
            
        Raises:
            AppException: If deletion fails.
        """
        self._ensure_client()
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"Successfully deleted file from {self.bucket_name}/{file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from storage: {e}")
            raise AppException("Failed to delete file from storage.", status_code=500)

    async def create_signed_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Generates a signed URL for a file.
        
        Args:
            file_path: The file path in the bucket.
            expires_in: Expiration time in seconds.
            
        Returns:
            The signed URL.
            
        Raises:
            AppException: If generating URL fails.
        """
        self._ensure_client()
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(file_path, expires_in)
            if "signedURL" in response:
                return response["signedURL"]
            # Fallback based on different client versions returning different dict keys
            if "signedUrl" in response:
                return response["signedUrl"]
            logger.error(f"Unexpected response format for signed URL: {response}")
            raise ValueError("signedURL key not found in response")
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise AppException("Failed to generate download URL.", status_code=500)
