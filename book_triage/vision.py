"""Vision processing for extracting book titles from photos."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Optional
import os
import re

import pytesseract
from openai import OpenAI
from PIL import Image

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")

class VisionProcessor:
    """Process images to extract book titles."""
    
    def __init__(self, use_openai_vision: bool = True):
        """Initialize vision processor.
        
        Args:
            use_openai_vision: Whether to use OpenAI Vision API as primary method
        """
        self.use_openai_vision = use_openai_vision
        self.client = None  # Initialize OpenAI client only when needed
    
    def extract_title_from_image(self, image_path: str | Path) -> str:
        """Extract book title from image using available methods.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted title or empty string if failed
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return ""
        
        # Try OpenAI Vision API first if enabled
        if self.use_openai_vision:
            try:
                title = self._extract_with_openai_vision(image_path)
                if title:
                    logger.info(f"Successfully extracted title with OpenAI Vision: {title}")
                    return title
            except Exception as e:
                logger.warning(f"OpenAI Vision failed: {e}")
        
        # Fallback to pytesseract
        try:
            title = self._extract_with_tesseract(image_path)
            if title:
                logger.info(f"Successfully extracted title with Tesseract: {title}")
                return title
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
        
        logger.warning("Failed to extract title from image")
        return ""
    
    def _extract_with_openai_vision(self, image_path: Path) -> str:
        """Extract title using OpenAI Vision API."""
        # Initialize OpenAI client only when needed
        if not self.client and self.use_openai_vision:
            try:
                self.client = OpenAI()
            except Exception as e:
                raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        
        if not self.client:
            raise RuntimeError("OpenAI client not available")
            
        try:
            with open(image_path, "rb") as image_file:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Extract the book title from this image. Look for the largest, most prominent text that appears to be the book title. Return only the title, nothing else."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_file.read()}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=100,
                    temperature=0.1,
                )
                
                content = response.choices[0].message.content
                if content:
                    # Clean up the response
                    title = content.strip().strip('"').strip("'")
                    return title
                
        except Exception as e:
            logger.error(f"Error in OpenAI Vision extraction: {e}")
            raise
        
        return ""
    
    def _extract_with_tesseract(self, image_path: Path) -> str:
        """Extract title using pytesseract OCR."""
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(image, lang='eng+jpn')
            
            # Split into lines and find the most likely title
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if not lines:
                return ""
            
            # Simple heuristic: return the first non-empty line
            # In practice, you might want more sophisticated logic
            return lines[0]
            
        except Exception as e:
            logger.error(f"Error in Tesseract extraction: {e}")
            raise
        
        return ""
    
    def generate_id(self) -> str:
        """Generate a unique ID for new records."""
        return str(uuid.uuid4())[:8]
    
    def extract_title_and_isbn_from_image(self, image_path: str | Path) -> tuple[str, str]:
        """Extract book title and ISBN from image using available methods.
        Returns (title, isbn) tuple."""
        image_path = Path(image_path)
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return "", ""
        # Try OpenAI Vision API first if enabled
        text = ""
        if self.use_openai_vision:
            try:
                text = self._extract_with_openai_vision(image_path)
            except Exception as e:
                logger.warning(f"OpenAI Vision failed: {e}")
        if not text:
            try:
                # Get full text for ISBN extraction, not just title
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                text = pytesseract.image_to_string(image, lang='eng+jpn')
            except Exception as e:
                logger.error(f"Tesseract extraction failed: {e}")
        if not text:
            logger.warning("Failed to extract text from image")
            return "", ""
        # Extract ISBN (first 13-digit number found)
        isbn_match = re.search(r"\b\d{13}\b", text)
        isbn = isbn_match.group(0) if isbn_match else ""
        # Extract title (first non-empty line)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        title = lines[0] if lines else ""
        return title, isbn 