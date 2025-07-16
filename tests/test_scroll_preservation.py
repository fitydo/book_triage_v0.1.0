"""Tests for scroll preservation functionality."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import json

from book_triage.api import app, initialize_app
from book_triage.core import BookRecord, Decision


class TestScrollPreservation:
    """Test scroll preservation in the frontend."""
    
    def test_loadbooks_accepts_preserve_scroll_parameter(self, client_empty):
        """Test that loadBooks function accepts preserveScroll parameter."""
        # Get the HTML and check if the function signature is correct
        response = client_empty.get("/")
        assert response.status_code == 200
        assert "function loadBooks(preserveScroll = false, targetId = null)" in response.text
    
    def test_savebook_calls_loadbooks_with_true(self, client_empty):
        """Test that saveBook calls loadBooks with true parameter."""
        response = client_empty.get("/")
        assert response.status_code == 200
        # Check that saveBook calls loadBooks(true)
        assert "loadBooks(true);" in response.text
        assert "// Pass true to preserve scroll position" in response.text
    
    def test_scroll_preservation_logic_exists(self, client_empty):
        """Test that scroll preservation logic is implemented."""
        response = client_empty.get("/")
        assert response.status_code == 200
        html = response.text
        
        # Check for scroll position saving logic
        assert "savedScrollTop = scrollContainer.scrollTop;" in html
        assert "savedScrollLeft = scrollContainer.scrollLeft;" in html
        
        # Check for scroll position restoration logic
        assert "currentScrollContainer.scrollTop = savedScrollTop;" in html
        assert "currentScrollContainer.scrollLeft = savedScrollLeft;" in html
    
    def test_scroll_container_selector(self, client_empty):
        """Test that the correct scroll container selector is used."""
        response = client_empty.get("/")
        assert response.status_code == 200
        html = response.text
        
        # Check that it's looking for the right container
        assert "document.querySelector('.table-scroll-container')" in html

    def test_manual_submit_calls_loadbooks_with_target(self, client_empty):
        """Ensure manual title submission calls loadBooks with target id to scroll to new row."""
        response = client_empty.get("/")
        assert response.status_code == 200
        html = response.text
        # Check the JavaScript in submitManualTitle
        assert "loadBooks(false, data.id);" in html
    
    @patch('book_triage.api.book_triage')
    def test_integration_save_preserves_scroll(self, mock_book_triage, client_empty):
        """Test the full integration of save with scroll preservation."""
        # Mock book_triage to have a record
        mock_record = BookRecord(
            id="test1",
            title="Test Book",
            isbn="1234567890123",
            url="https://example.com",
            decision=Decision.KEEP
        )
        mock_book_triage.get_record_by_id.return_value = mock_record
        mock_book_triage.records = [mock_record]
        
        # Test the rescan_title endpoint (which is called by saveBook)
        response = client_empty.post(
            "/rescan_title",
            json={
                "id": "test1",
                "title": "Updated Book",
                "isbn": "1234567890123",
                "url": "https://example.com",
                "url_com": "",
                "purchase_price": None,
                "used_price": None,
                "V": "",
                "R": "",
                "P": "",
                "F": "",
                "A": "",
                "S": ""
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "row" in data
        assert data["row"]["id"] == "test1"
        assert data["row"]["title"] == "Updated Book"


@pytest.fixture
def client_empty():
    """Create a test client with empty CSV."""
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=True) as tmp:
        csv_path = Path(tmp.name)
    
    initialize_app(csv_path, scan_cost=2)
    return TestClient(app) 