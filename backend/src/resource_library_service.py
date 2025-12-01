"""Service for educational resource library management."""
import os
import uuid
import tempfile
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


class ResourceLibraryService:
    """Service for managing educational resources with Azure Blob Storage."""

    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "resources")

        if not self.connection_string:
            logger.warning(
                "AZURE_STORAGE_CONNECTION_STRING not set - resource uploads disabled"
            )
            self.enabled = False
            return

        try:
            self.blob_service = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            # Ensure container exists
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {e}")
            self.enabled = False

    async def upload_document(
        self, file_content: bytes, filename: str, resource_id: str
    ) -> Dict[str, Any]:
        """Upload a document to Azure Blob Storage."""
        if not self.enabled:
            raise RuntimeError("Azure Blob Storage not configured")

        try:
            container_client = self.blob_service.get_container_client(
                self.container_name
            )

            # Upload main file
            blob_name = f"{resource_id}/{filename}"
            blob_client = container_client.upload_blob(
                name=blob_name, data=BytesIO(file_content), overwrite=True
            )

            blob_url = f"https://{self.blob_service.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

            file_info = {
                "blob_url": blob_url,
                "file_size_bytes": len(file_content),
                "file_type": filename.split(".")[-1].lower() if "." in filename else "",
            }

            # Generate thumbnail for PDFs
            if file_info["file_type"] == "pdf":
                try:
                    thumbnail_url = await self.generate_pdf_thumbnail(
                        file_content, resource_id
                    )
                    file_info["thumbnail_url"] = thumbnail_url
                except Exception as e:
                    logger.warning(f"Failed to generate PDF thumbnail: {e}")

            return file_info

        except AzureError as e:
            logger.error(f"Error uploading document to Blob Storage: {e}")
            raise

    async def generate_pdf_thumbnail(
        self, pdf_content: bytes, resource_id: str
    ) -> Optional[str]:
        """Generate thumbnail from first page of PDF."""
        try:
            from pdf2image import convert_from_bytes

            # Convert first page to image
            images = convert_from_bytes(pdf_content, first_page=1, last_page=1, dpi=72)

            if not images:
                return None

            # Resize to thumbnail
            thumbnail = images[0]
            thumbnail.thumbnail((300, 400), Image.Resampling.LANCZOS)

            # Convert to PNG bytes
            thumbnail_bytes = BytesIO()
            thumbnail.save(thumbnail_bytes, format="PNG")
            thumbnail_bytes.seek(0)

            # Upload thumbnail to Blob Storage
            container_client = self.blob_service.get_container_client(
                self.container_name
            )
            blob_name = f"{resource_id}/thumbnail.png"
            container_client.upload_blob(
                name=blob_name, data=thumbnail_bytes, overwrite=True
            )

            thumbnail_url = f"https://{self.blob_service.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

            return thumbnail_url

        except ImportError:
            logger.warning(
                "pdf2image not installed - PDF thumbnail generation unavailable"
            )
            return None
        except Exception as e:
            logger.error(f"Error generating PDF thumbnail: {e}")
            return None

    async def fetch_og_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """Fetch OpenGraph metadata from URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            metadata = {
                "og_title": self._get_meta_content(soup, "og:title")
                or soup.find("title"),
                "og_description": self._get_meta_content(soup, "og:description")
                or self._get_meta_content(soup, "description"),
                "og_image": self._get_meta_content(soup, "og:image"),
            }

            # Clean up title
            if metadata["og_title"] and hasattr(metadata["og_title"], "string"):
                metadata["og_title"] = str(metadata["og_title"].string)

            return metadata

        except requests.RequestException as e:
            logger.error(f"Error fetching OpenGraph metadata from {url}: {e}")
            return {"og_title": None, "og_description": None, "og_image": None}

    def _get_meta_content(
        self, soup: BeautifulSoup, property_name: str
    ) -> Optional[str]:
        """Extract content from meta tag."""
        tag = soup.find("meta", property=property_name) or soup.find(
            "meta", attrs={"name": property_name}
        )
        return tag.get("content") if tag else None

    async def delete_resource_files(self, resource_id: str) -> bool:
        """Delete all files associated with a resource."""
        if not self.enabled:
            return False

        try:
            container_client = self.blob_service.get_container_client(
                self.container_name
            )

            # List all blobs with the resource_id prefix
            blobs = container_client.list_blobs(name_starts_with=f"{resource_id}/")

            deleted_count = 0
            for blob in blobs:
                container_client.delete_blob(blob.name)
                deleted_count += 1

            logger.info(f"Deleted {deleted_count} blobs for resource {resource_id}")
            return True

        except AzureError as e:
            logger.error(f"Error deleting resource files: {e}")
            return False

    async def extract_pdf_text_preview(
        self, pdf_content: bytes, max_chars: int = 500
    ) -> Optional[str]:
        """Extract preview text from PDF (first 500 characters)."""
        try:
            import PyPDF2

            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))

            if len(pdf_reader.pages) == 0:
                return None

            # Extract text from first page
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()

            # Clean and truncate
            text = " ".join(text.split())  # Remove extra whitespace
            if len(text) > max_chars:
                text = text[:max_chars] + "..."

            return text

        except ImportError:
            logger.warning("PyPDF2 not installed - PDF text extraction unavailable")
            return None
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return None

    def get_page_count(self, pdf_content: bytes) -> Optional[int]:
        """Get page count from PDF."""
        try:
            import PyPDF2

            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            return len(pdf_reader.pages)

        except ImportError:
            return None
        except Exception as e:
            logger.error(f"Error getting PDF page count: {e}")
            return None
