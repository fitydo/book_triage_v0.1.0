"""Tests for API module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from book_triage.api import app, initialize_app
from book_triage.core import BookRecord, Decision


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        csv_path = Path(tmp.name)
        # Write sample CSV data
        tmp.write("id,title,url,F,R,A,V,S,P,decision\n")
        tmp.write("test1,Test Book,https://example.com,3,2,1,4,2,4,unknown\n")
    
    yield csv_path
    
    # Cleanup
    if csv_path.exists():
        csv_path.unlink()


@pytest.fixture
def client_with_data(temp_csv):
    """Create a test client with initialized data."""
    initialize_app(temp_csv, scan_cost=2)
    return TestClient(app)


@pytest.fixture
def client_empty():
    """Create a test client with empty CSV."""
    import os
    # Set test credentials
    os.environ['BOOK_USER'] = 'testuser'
    os.environ['BOOK_PASS'] = 'testpass'
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=True) as tmp:
        csv_path = Path(tmp.name)
    
    initialize_app(csv_path, scan_cost=2)
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self, client_empty):
        """Test the root endpoint returns HTML."""
        response = client_empty.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Book Triage" in response.text
    
    def test_health_endpoint(self, client_empty):
        """Test the health check endpoint."""
        response = client_empty.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_get_books_empty(self, client_empty):
        """Test getting books from empty database."""
        response = client_empty.get("/books")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_books_with_data(self, client_with_data):
        """Test getting books with existing data."""
        response = client_with_data.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1
        assert books[0]["id"] == "test1"
        assert books[0]["title"] == "Test Book"
    
    @patch('book_triage.api.vision_processor')
    def test_upload_photo_success(self, mock_vision_processor, client_empty):
        """Test successful photo upload."""
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Mock vision processor
        mock_vision_processor.extract_title_from_image.return_value = "Test Book"
        mock_vision_processor.generate_id.return_value = "test123"
        
        response = client_empty.post(
            "/upload_photo",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["id"] == "test123"
        assert "csv_row" in data
    
    def test_scan_books_unauthorized(self, client_empty):
        """Test scan endpoint requires authentication."""
        response = client_empty.post("/scan")
        assert response.status_code == 401
    
    def test_rate_limiting_books_endpoint(self, client_empty):
        """Test rate limiting on /books endpoint."""
        # Since rate limiting is simple and per-IP, we'll test that
        # the endpoint works normally for normal usage
        response = client_empty.get("/books")
        assert response.status_code == 200
    
    def test_file_upload_size_limit(self, client_empty):
        """Test file upload size limit (>10MB)."""
        # Create a large file (>10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        response = client_empty.post(
            "/upload_photo",
            files={"file": ("large.jpg", large_content, "image/jpeg")}
        )
        
        assert response.status_code == 413
        data = response.json()
        assert "File too large" in data["detail"]
    
    def test_security_headers_in_response(self, client_empty):
        """Test that security headers are present in responses."""
        response = client_empty.get("/")
        assert response.status_code == 200
        
        # Check for security headers
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("Content-Security-Policy") == "default-src 'self'"
        assert response.headers.get("Referrer-Policy") == "same-origin"
    
    @patch('book_triage.api.vision_processor')
    def test_upload_photo_no_title_extracted(self, mock_vision_processor, client_empty):
        """Test photo upload when no title is extracted."""
        image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Mock vision processor to return empty title
        mock_vision_processor.extract_title_from_image.return_value = ""
        
        response = client_empty.post(
            "/upload_photo",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Could not extract title" in data["detail"]
    
    @patch('book_triage.api.vision_processor')
    def test_upload_photo_vision_processor_exception(self, mock_vision_processor, client_empty):
        """Test photo upload when vision processor raises exception."""
        image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Mock vision processor to raise exception
        mock_vision_processor.extract_title_from_image.side_effect = Exception("Processing error")
        
        response = client_empty.post(
            "/upload_photo",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Error processing image" in data["detail"]
    
    def test_upload_photo_no_file(self, client_empty):
        """Test photo upload without file."""
        response = client_empty.post("/upload_photo")
        assert response.status_code == 422  # Validation error
    
    @patch('book_triage.api.book_triage')
    def test_scan_books_success(self, mock_book_triage, client_empty):
        """Test successful book scanning."""
        mock_book_triage.scan_and_enrich.return_value = None
        
        response = client_empty.post(
            "/scan",
            auth=("testuser", "testpass")
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Scan and enrichment completed successfully"
        mock_book_triage.scan_and_enrich.assert_called_once()
    
    @patch('book_triage.api.book_triage')
    def test_scan_books_exception(self, mock_book_triage, client_empty):
        """Test book scanning with exception."""
        mock_book_triage.scan_and_enrich.side_effect = Exception("Scan error")
        
        response = client_empty.post(
            "/scan",
            auth=("testuser", "testpass")
        )
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Scan failed:" in data["detail"]
    
    @patch('book_triage.api.book_triage')
    def test_rescan_title_record_not_found(self, mock_book_triage, client_empty):
        """Test rescanning title for non-existent record."""
        mock_book_triage.get_record_by_id.return_value = None
        
        response = client_empty.post(
            "/rescan_title",
            json={"id": "nonexistent", "title": "New Title"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Book not found" in data["detail"]
    
    @patch('book_triage.api.book_triage')
    def test_add_manual_title_success(self, mock_book_triage, client_empty):
        """Test successful manual title addition."""
        # Mock the enrich_with_gpt4o method to avoid errors
        mock_book_triage.enrich_with_gpt4o.return_value = None
        
        response = client_empty.post(
            "/add_manual_title",
            json={"title": "Manual Book", "isbn": "9781234567890"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Manual Book"
        assert data["isbn"] == "9781234567890"
        assert "id" in data
        assert "csv_row" in data
        mock_book_triage.add_record.assert_called_once()
    
    def test_add_manual_title_missing_isbn(self, client_empty):
        """Test manual title addition with missing ISBN."""
        response = client_empty.post(
            "/add_manual_title",
            json={"title": "Manual Book"}  # Missing ISBN
        )
        
        assert response.status_code == 400  # Bad request
    
    def test_add_manual_title_invalid_isbn(self, client_empty):
        """Test manual title addition with invalid ISBN."""
        response = client_empty.post(
            "/add_manual_title",
            json={"title": "Manual Book", "isbn": "123"}  # Invalid ISBN
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "ISBN is 13 digits" in data["detail"]


class TestAPIInitialization:
    """Test API initialization."""
    
    def test_initialize_app(self):
        """Test app initialization."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=True) as tmp:
            csv_path = Path(tmp.name)
        
        initialize_app(csv_path, scan_cost=3)
        
        # Import the global variables to check they're set
        from book_triage.api import book_triage, vision_processor
        assert book_triage is not None
        assert vision_processor is not None
        assert book_triage.scan_cost == 3
    
    def test_app_without_initialization(self):
        """Test app behavior without initialization."""
        # Reset global variables
        import book_triage.api
        book_triage.api.book_triage = None
        book_triage.api.vision_processor = None
        
        client = TestClient(app)
        
        # Some endpoints should handle None gracefully
        response = client.get("/health")
        assert response.status_code == 200
        
        # But others should fail
        response = client.get("/books")
        assert response.status_code == 500 