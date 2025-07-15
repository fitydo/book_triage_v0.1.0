"""Tests for security module."""

import os
import io
import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import tempfile

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from book_triage.security import (
    get_current_user,
    admin_required,
    validate_file_upload,
    sanitize_image
)


class TestGetCurrentUser:
    """Tests for get_current_user function."""
    
    def test_valid_credentials_default(self):
        """Test authentication with default credentials."""
        credentials = HTTPBasicCredentials(username="admin", password="password")
        
        with patch.dict(os.environ, {"BOOK_USER": "admin", "BOOK_PASS": "password"}):
            result = get_current_user(credentials)
            assert result == "admin"
    
    def test_valid_credentials_custom(self):
        """Test authentication with custom credentials."""
        credentials = HTTPBasicCredentials(username="testuser", password="testpass")
        
        with patch.dict(os.environ, {"BOOK_USER": "testuser", "BOOK_PASS": "testpass"}):
            result = get_current_user(credentials)
            assert result == "testuser"
    
    def test_invalid_username(self):
        """Test authentication failure with invalid username."""
        credentials = HTTPBasicCredentials(username="wronguser", password="password")
        
        with patch.dict(os.environ, {"BOOK_USER": "admin", "BOOK_PASS": "password"}):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 401
            assert "Incorrect username or password" in exc_info.value.detail
            assert exc_info.value.headers == {"WWW-Authenticate": "Basic"}
    
    def test_invalid_password(self):
        """Test authentication failure with invalid password."""
        credentials = HTTPBasicCredentials(username="admin", password="wrongpass")
        
        with patch.dict(os.environ, {"BOOK_USER": "admin", "BOOK_PASS": "password"}):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 401
            assert "Incorrect username or password" in exc_info.value.detail
    
    def test_both_invalid(self):
        """Test authentication failure with both invalid username and password."""
        credentials = HTTPBasicCredentials(username="wronguser", password="wrongpass")
        
        with patch.dict(os.environ, {"BOOK_USER": "admin", "BOOK_PASS": "password"}):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 401
    
    def test_empty_credentials(self):
        """Test authentication failure with empty credentials."""
        credentials = HTTPBasicCredentials(username="", password="")
        
        with patch.dict(os.environ, {"BOOK_USER": "admin", "BOOK_PASS": "password"}):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 401


class TestAdminRequired:
    """Tests for admin_required decorator."""
    
    @pytest.mark.asyncio
    async def test_admin_required_with_user(self):
        """Test admin_required decorator with valid user."""
        @admin_required
        async def protected_function(current_user=None):
            return f"Hello {current_user}"
        
        result = await protected_function(current_user="admin")
        assert result == "Hello admin"
    
    @pytest.mark.asyncio
    async def test_admin_required_without_user(self):
        """Test admin_required decorator without user (should raise exception)."""
        @admin_required
        async def protected_function(current_user=None):
            return "Hello"
        
        with pytest.raises(HTTPException) as exc_info:
            await protected_function()
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail
        assert exc_info.value.headers == {"WWW-Authenticate": "Basic"}
    
    @pytest.mark.asyncio
    async def test_admin_required_with_none_user(self):
        """Test admin_required decorator with None user."""
        @admin_required
        async def protected_function(current_user=None):
            return "Hello"
        
        with pytest.raises(HTTPException) as exc_info:
            await protected_function(current_user=None)
        
        assert exc_info.value.status_code == 401


class TestValidateFileUpload:
    """Tests for validate_file_upload function."""
    
    def test_valid_small_image(self):
        """Test validation of small valid image."""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        file_content = img_bytes.getvalue()
        
        with patch('book_triage.security.magic.from_buffer', return_value='image/jpeg'):
            # Should not raise exception
            validate_file_upload(file_content, max_size_mb=10)
    
    def test_file_too_large(self):
        """Test validation failure for file too large."""
        # Create large content (larger than max_size_mb)
        large_content = b'x' * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        
        with pytest.raises(HTTPException) as exc_info:
            validate_file_upload(large_content, max_size_mb=5)
        
        assert exc_info.value.status_code == 413
        assert "File too large" in exc_info.value.detail
        assert "5MB" in exc_info.value.detail
    
    def test_non_image_file(self):
        """Test validation failure for non-image file."""
        text_content = b"This is not an image file"
        
        with patch('book_triage.security.magic.from_buffer', return_value='text/plain'):
            with pytest.raises(HTTPException) as exc_info:
                validate_file_upload(text_content)
            
            assert exc_info.value.status_code == 400
            assert "File must be an image" in exc_info.value.detail
    
    def test_magic_exception(self):
        """Test validation failure when magic library throws exception."""
        file_content = b"some content"
        
        with patch('book_triage.security.magic.from_buffer', side_effect=Exception("Magic error")):
            with pytest.raises(HTTPException) as exc_info:
                validate_file_upload(file_content)
            
            assert exc_info.value.status_code == 400
            assert "Invalid file format" in exc_info.value.detail
    
    def test_different_image_types(self):
        """Test validation of different image MIME types."""
        file_content = b"fake image content"
        
        valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        for mime_type in valid_types:
            with patch('book_triage.security.magic.from_buffer', return_value=mime_type):
                # Should not raise exception
                validate_file_upload(file_content)


class TestSanitizeImage:
    """Tests for sanitize_image function."""
    
    def test_sanitize_valid_rgb_image(self):
        """Test sanitizing a valid RGB image."""
        # Create a test RGB image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        input_content = img_bytes.getvalue()
        
        result = sanitize_image(input_content)
        
        # Verify result is valid JPEG
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Verify can be loaded as image
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'JPEG'
        assert result_img.size == (100, 100)
    
    def test_sanitize_rgba_image(self):
        """Test sanitizing RGBA image (should convert to RGB)."""
        # Create a test RGBA image
        img = Image.new('RGBA', (50, 50), color=(255, 0, 0, 128))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        input_content = img_bytes.getvalue()
        
        result = sanitize_image(input_content)
        
        # Verify result is RGB JPEG
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'JPEG'
        assert result_img.mode == 'RGB'
        assert result_img.size == (50, 50)
    
    def test_sanitize_palette_image(self):
        """Test sanitizing palette mode image (should convert to RGB)."""
        # Create a test palette image
        img = Image.new('P', (30, 30))
        img.putpixel((10, 10), 255)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        input_content = img_bytes.getvalue()
        
        result = sanitize_image(input_content)
        
        # Verify result is RGB JPEG
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'JPEG'
        assert result_img.mode == 'RGB'
    
    def test_sanitize_invalid_image_data(self):
        """Test sanitizing invalid image data."""
        invalid_content = b"This is not image data"
        
        with pytest.raises(HTTPException) as exc_info:
            sanitize_image(invalid_content)
        
        assert exc_info.value.status_code == 400
        assert "Invalid image file" in exc_info.value.detail
    
    def test_sanitize_corrupted_image(self):
        """Test sanitizing corrupted image data."""
        # Create partially corrupted image data
        img = Image.new('RGB', (10, 10), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        corrupted_content = img_bytes.getvalue()[:50]  # Truncate the image data
        
        with pytest.raises(HTTPException) as exc_info:
            sanitize_image(corrupted_content)
        
        assert exc_info.value.status_code == 400
        assert "Invalid image file" in exc_info.value.detail
    
    def test_sanitize_quality_setting(self):
        """Test that sanitized images use quality=85."""
        # Create a test image
        img = Image.new('RGB', (200, 200), color='yellow')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=100)
        input_content = img_bytes.getvalue()
        
        result = sanitize_image(input_content)
        
        # The exact quality can't be tested directly, but we can verify
        # the result is smaller than the original high-quality version
        assert len(result) < len(input_content)
        
        # Verify it's still a valid image
        result_img = Image.open(io.BytesIO(result))
        assert result_img.format == 'JPEG'
        assert result_img.size == (200, 200)


class TestSecurityIntegration:
    """Integration tests for security functions."""
    
    def test_full_file_security_pipeline(self):
        """Test the complete file security pipeline."""
        # Create a test image
        img = Image.new('RGB', (150, 150), color='purple')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        file_content = img_bytes.getvalue()
        
        # Mock magic to return image MIME type
        with patch('book_triage.security.magic.from_buffer', return_value='image/jpeg'):
            # Step 1: Validate upload
            validate_file_upload(file_content, max_size_mb=10)
            
            # Step 2: Sanitize image
            sanitized = sanitize_image(file_content)
            
            # Verify sanitized result
            assert isinstance(sanitized, bytes)
            assert len(sanitized) > 0
            
            # Verify it's a valid JPEG
            result_img = Image.open(io.BytesIO(sanitized))
            assert result_img.format == 'JPEG'
            assert result_img.mode == 'RGB'


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 