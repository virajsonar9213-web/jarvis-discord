"""
JARVIS Gemini Client

Google Gemini API integration using google-genai SDK.
Provides the AI brain for JARVIS.
"""

import os
from typing import Optional

from google import genai
from google.genai import types

from utils.logger import get_logger

logger = get_logger("gemini")


class GeminiClient:
    """
    Client for Google Gemini API.
    Handles all AI interactions for JARVIS.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.client: Optional[genai.Client] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the Gemini client."""
        try:
            self.client = genai.Client(api_key=self.api_key)
            self._initialized = True
            logger.info(f"Gemini client initialized with model: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """Check if the client is initialized and ready."""
        return self._initialized and self.client is not None

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """
        Generate a text response from Gemini.
        Returns the response text or None if generation fails.
        """
        if not self.is_ready:
            logger.error("Gemini client not initialized")
            return None

        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            if system_instruction:
                config.system_instruction = system_instruction

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            if response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return None

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None

    async def generate_with_context(
        self,
        messages: list[dict],
        system_instruction: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a response considering conversation history.
        messages: list of {"role": "user"|"assistant", "content": "..."}
        """
        if not self.is_ready:
            return None

        try:
            # Build content from message history
            contents = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    contents.append(types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=content)],
                    ))
                elif role == "assistant":
                    contents.append(types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=content)],
                    ))

            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

            return response.text.strip() if response.text else None

        except Exception as e:
            logger.error(f"Gemini context generation error: {e}")
            return None

    async def analyze_image(
        self,
        image_url: str,
        prompt: str,
    ) -> Optional[str]:
        """
        Analyze an image with Gemini.
        Phase 6 implementation.
        """
        if not self.is_ready:
            return None

        logger.info(f"Image analysis requested for: {image_url}")

        # TODO: Phase 6 - implement image analysis with Gemini
        # Will download image and send with prompt

        return None

    async def check_rate_limit(self) -> bool:
        """
        Check if we're being rate limited.
        Returns True if we should wait.
        """
        # TODO: Implement rate limit tracking
        return False

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        try:
            # Simple test call
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents="Test",
            )
            return response.text is not None
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
