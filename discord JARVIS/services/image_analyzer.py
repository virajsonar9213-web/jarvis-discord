"""
JARVIS Image Analyzer Service

Handles image and attachment analysis using Gemini.
Phase 6 feature - currently a placeholder.
"""

from typing import Optional

from discord import Attachment

from utils.logger import get_logger

logger = get_logger("image_analyzer")


class ImageAnalyzerService:
    """
    Service for analyzing images and documents.
    Phase 6 will implement:
    - Image understanding via Gemini
    - Screenshot analysis
    - Diagram explanation
    - Text extraction from images
    - Document reading and summarization
    """

    def __init__(self):
        self._supported_image_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }

    def is_image_supported(self, attachment: Attachment) -> bool:
        """Check if an attachment is a supported image type."""
        ext = attachment.filename.split(".")[-1].lower()
        return ext in self._supported_image_types

    def is_document_supported(self, attachment: Attachment) -> bool:
        """Check if an attachment is a supported document type."""
        # Phase 6+ will expand supported document types
        supported_exts = {"txt", "md", "pdf"}
        ext = attachment.filename.split(".")[-1].lower()
        return ext in supported_exts

    async def analyze_image(
        self,
        attachment: Attachment,
        question: Optional[str] = None,
    ) -> Optional[str]:
        """
        Analyze an image using Gemini.
        Returns analysis result or None if analysis fails.
        """
        if not self.is_image_supported(attachment):
            logger.warning(f"Unsupported image type: {attachment.content_type}")
            return None

        logger.info(f"Image analysis requested for: {attachment.url}")

        # TODO: Phase 6 - implement Gemini image analysis
        # Will download image and send to Gemini with the question

        return None

    async def extract_text_from_image(
        self,
        attachment: Attachment,
    ) -> Optional[str]:
        """
        Extract visible text from an image.
        Phase 6 will use Gemini's OCR capabilities.
        """
        if not self.is_image_supported(attachment):
            return None

        logger.info(f"Text extraction requested for: {attachment.url}")

        # TODO: Phase 6 - implement OCR via Gemini

        return None

    async def summarize_document(
        self,
        attachment: Attachment,
    ) -> Optional[str]:
        """
        Summarize a document attachment.
        Phase 6 will implement document analysis.
        """
        if not self.is_document_supported(attachment):
            logger.warning(f"Unsupported document type: {attachment.content_type}")
            return None

        logger.info(f"Document summarization requested for: {attachment.url}")

        # TODO: Phase 6 - implement document analysis

        return None

    def get_supported_types(self) -> dict:
        """Get supported image and document types."""
        return {
            "images": list(self._supported_image_types.keys()),
            "documents": ["txt", "md", "pdf"],  # Phase 6+
        }
