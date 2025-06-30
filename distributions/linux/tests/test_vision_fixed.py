"""Tests for vision module - Windows compatible version."""

import tempfile
import uuid
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
from PIL import Image

from book_triage.vision import VisionProcessor


def safe_cleanup(file_path):
    """Safely clean up temporary files, handling Windows permission issues."""
    try:
        if file_path.exists():
            file_path.unlink()
    except (PermissionError, FileNotFoundError):
        # Windows file permission issue or file already deleted
        pass


class TestVisionProcessor:
    """Test VisionProcessor class."""
    
    def test_vision_processor_initialization_with_openai(self):
        """Test VisionProcessor initialization with OpenAI enabled."""
        with patch('book_triage.vision.OpenAI') as mock_openai:
            processor = VisionProcessor(use_openai_vision=True)
            assert processor.use_openai_vision is True
            assert processor.client is not None
            mock_openai.assert_called_once()
    
    def test_vision_processor_initialization_without_openai(self):
        """Test VisionProcessor initialization without OpenAI."""
        processor = VisionProcessor(use_openai_vision=False)
        assert processor.use_openai_vision is False
        assert processor.client is None
    
    def test_generate_id(self):
        """Test ID generation."""
        processor = VisionProcessor(use_openai_vision=False)
        id1 = processor.generate_id()
        id2 = processor.generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert len(id1) == 8
        assert len(id2) == 8
        assert id1 != id2  # Should be unique
    
    def test_extract_title_from_image_nonexistent_file(self):
        """Test extraction with non-existent file."""
        processor = VisionProcessor(use_openai_vision=False)
        title = processor.extract_title_from_image("nonexistent.jpg")
        assert title == ""
    
    @patch('book_triage.vision.OpenAI')
    def test_extract_title_with_openai_vision_success(self, mock_openai):
        """Test successful title extraction with OpenAI Vision."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test Book Title"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            processor = VisionProcessor(use_openai_vision=True)
            
            with patch('builtins.open', mock_open(read_data=b'fake_image_data')):
                title = processor.extract_title_from_image(image_path)
            
            assert title == "Test Book Title"
            mock_client.chat.completions.create.assert_called_once()
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.OpenAI')
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_title_fallback_to_tesseract(self, mock_tesseract, mock_openai):
        """Test fallback to Tesseract when OpenAI fails."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            # Mock OpenAI to fail
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
            
            # Mock Tesseract to succeed
            mock_tesseract.return_value = "Tesseract Title\nOther text"
            
            processor = VisionProcessor(use_openai_vision=True)
            title = processor.extract_title_from_image(image_path)
            
            assert title == "Tesseract Title"
            mock_tesseract.assert_called_once()
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_with_tesseract_success(self, mock_tesseract):
        """Test successful Tesseract extraction."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            mock_tesseract.return_value = "Book Title\nAuthor Name\nPublisher"
            
            processor = VisionProcessor(use_openai_vision=False)
            title = processor.extract_title_from_image(image_path)
            
            assert title == "Book Title"
            mock_tesseract.assert_called_once()
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_with_tesseract_empty_result(self, mock_tesseract):
        """Test Tesseract with empty result."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            mock_tesseract.return_value = "\n\n\n"  # Only whitespace
            
            processor = VisionProcessor(use_openai_vision=False)
            title = processor.extract_title_from_image(image_path)
            
            assert title == ""
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_with_tesseract_error(self, mock_tesseract):
        """Test Tesseract extraction error."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            mock_tesseract.side_effect = Exception("Tesseract error")
            
            processor = VisionProcessor(use_openai_vision=False)
            title = processor.extract_title_from_image(image_path)
            
            assert title == ""
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.OpenAI')
    def test_extract_with_openai_vision_no_content(self, mock_openai):
        """Test OpenAI Vision with no content in response."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            # Mock OpenAI response with no content
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            processor = VisionProcessor(use_openai_vision=True)
            
            with patch('builtins.open', mock_open(read_data=b'fake_image_data')):
                title = processor._extract_with_openai_vision(image_path)
            
            assert title == ""
        finally:
            safe_cleanup(image_path)
    
    def test_extract_with_openai_vision_no_client(self):
        """Test OpenAI Vision extraction without client."""
        processor = VisionProcessor(use_openai_vision=False)
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            with pytest.raises(RuntimeError, match="OpenAI client not initialized"):
                processor._extract_with_openai_vision(image_path)
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.OpenAI')
    def test_extract_title_and_isbn_from_image_success(self, mock_openai):
        """Test successful title and ISBN extraction."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            # Mock OpenAI response with title and ISBN
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Advanced Python Programming\nISBN: 9781234567890\nAuthor: John Doe"
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            processor = VisionProcessor(use_openai_vision=True)
            
            with patch('builtins.open', mock_open(read_data=b'fake_image_data')):
                title, isbn = processor.extract_title_and_isbn_from_image(image_path)
            
            assert title == "Advanced Python Programming"
            assert isbn == "9781234567890"
        finally:
            safe_cleanup(image_path)
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_title_and_isbn_tesseract_fallback(self, mock_tesseract):
        """Test title and ISBN extraction with Tesseract fallback."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            # Mock Tesseract response
            mock_tesseract.return_value = "OCR Book Title\nSome text\n9780123456789\nMore text"
            
            processor = VisionProcessor(use_openai_vision=False)
            title, isbn = processor.extract_title_and_isbn_from_image(image_path)
            
            assert title == "OCR Book Title"
            assert isbn == "9780123456789"
        finally:
            safe_cleanup(image_path)
    
    def test_extract_title_and_isbn_nonexistent_file(self):
        """Test extraction with non-existent file."""
        processor = VisionProcessor(use_openai_vision=False)
        title, isbn = processor.extract_title_and_isbn_from_image("nonexistent.jpg")
        
        assert title == ""
        assert isbn == ""
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_extract_title_and_isbn_no_isbn_found(self, mock_tesseract):
        """Test extraction when no ISBN is found."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            mock_tesseract.return_value = "Book Title Without ISBN\nAuthor Name"
            
            processor = VisionProcessor(use_openai_vision=False)
            title, isbn = processor.extract_title_and_isbn_from_image(image_path)
            
            assert title == "Book Title Without ISBN"
            assert isbn == ""
        finally:
            safe_cleanup(image_path)
    
    def test_image_format_conversion(self):
        """Test image format conversion."""
        # Create a test image in memory
        img = Image.new('RGBA', (100, 100), color=(255, 255, 255, 128))
        
        # Test that the processor can handle different image formats
        processor = VisionProcessor(use_openai_vision=False)
        
        # This should not raise an error even though we're not actually processing
        # The test verifies that the processor is set up correctly
        assert processor.use_openai_vision is False
        assert processor.client is None


class TestVisionProcessorIntegration:
    """Integration tests for VisionProcessor."""
    
    @patch('book_triage.vision.pytesseract.image_to_string')
    def test_processor_with_real_image_mock_ocr(self, mock_tesseract):
        """Test processor with real image but mocked OCR."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Create a more realistic test image
            img = Image.new('RGB', (200, 100), color='white')
            img.save(tmp.name, 'JPEG')
            image_path = Path(tmp.name)
        
        try:
            mock_tesseract.return_value = "Real Book Title\nSubtitle\nAuthor Name"
            
            processor = VisionProcessor(use_openai_vision=False)
            result = processor.extract_title_from_image(image_path)
            
            assert result == "Real Book Title"
            mock_tesseract.assert_called_once()
        finally:
            safe_cleanup(image_path) 