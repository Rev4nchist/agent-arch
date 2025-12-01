"""Azure Blob Storage service for file uploads."""
from azure.storage.blob import BlobServiceClient, ContentSettings
from src.config import settings
import logging
from typing import Optional
import uuid

logger = logging.getLogger(__name__)


class BlobService:
    """Azure Blob Storage wrapper for file operations."""

    def __init__(self):
        """Initialize Blob Service client."""
        try:
            self.client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
            self.container_name = settings.azure_storage_container_name
            self._ensure_container_exists()
        except Exception as e:
            logger.error(f"Failed to initialize Blob Service: {e}")
            raise

    def _ensure_container_exists(self):
        """Ensure the container exists, create if not."""
        try:
            container_client = self.client.get_container_client(self.container_name)
            if not container_client.exists():
                self.client.create_container(self.container_name)
                logger.info(f"Created container '{self.container_name}'")
            else:
                logger.info(f"Container '{self.container_name}' exists")
        except Exception as e:
            logger.error(f"Container check/creation error: {e}")
            raise

    async def upload_file(
        self, file_content: bytes, file_name: str, content_type: Optional[str] = None
    ) -> str:
        """
        Upload file to blob storage.

        Args:
            file_content: File content as bytes
            file_name: Original file name (will be prefixed with UUID)
            content_type: MIME type of the file

        Returns:
            Blob URL of uploaded file
        """
        try:
            # Generate unique blob name
            blob_name = f"{uuid.uuid4()}_{file_name}"

            # Get blob client
            blob_client = self.client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Set content settings if provided
            content_settings = None
            if content_type:
                content_settings = ContentSettings(content_type=content_type)

            # Upload file
            blob_client.upload_blob(
                file_content, content_settings=content_settings, overwrite=True
            )

            # Return blob URL
            blob_url = blob_client.url
            logger.info(f"Uploaded file to {blob_url}")
            return blob_url

        except Exception as e:
            logger.error(f"File upload error: {e}")
            raise

    async def download_file(self, blob_url: str) -> bytes:
        """
        Download file from blob storage.

        Args:
            blob_url: Full blob URL

        Returns:
            File content as bytes
        """
        try:
            # Extract blob name from URL
            blob_name = blob_url.split("/")[-1]

            # Get blob client
            blob_client = self.client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Download file
            download_stream = blob_client.download_blob()
            file_content = download_stream.readall()

            logger.info(f"Downloaded file from {blob_url}")
            return file_content

        except Exception as e:
            logger.error(f"File download error: {e}")
            raise

    async def delete_file(self, blob_url: str) -> bool:
        """
        Delete file from blob storage.

        Args:
            blob_url: Full blob URL

        Returns:
            True if successful
        """
        try:
            # Extract blob name from URL
            blob_name = blob_url.split("/")[-1]

            # Get blob client
            blob_client = self.client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Delete file
            blob_client.delete_blob()

            logger.info(f"Deleted file from {blob_url}")
            return True

        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False


# Global blob service instance
blob_service = BlobService()
