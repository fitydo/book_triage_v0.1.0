"""Basic tests for layout improvements."""

import pytest
from fastapi.testclient import TestClient
from book_triage.api import app, initialize_app
import tempfile
import os


@pytest.fixture
def test_client():
    """Create a test client with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,isbn,url,url_com,purchase_price,used_price,V,R,P,F,A,S,citation_R,citation_P,decision,verified\n")
        f.write("test1,Sample Book,9781234567890,,,1000,800,4,3,2,1,5,3,,,keep,yes\n")
        csv_path = f.name
    
    try:
        initialize_app(csv_path, scan_cost=2)
        with TestClient(app) as client:
            yield client
    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)


class TestBasicLayout:
    """Test basic layout functionality."""
    
    def test_homepage_loads(self, test_client):
        """Test that the homepage loads successfully."""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "Book Triage" in response.text
    
    def test_modern_css_included(self, test_client):
        """Test that modern CSS is included."""
        response = test_client.get("/")
        content = response.text
        
        # Check for modern font family
        assert "BlinkMacSystemFont" in content
        assert "Segoe UI" in content
        
        # Check for modern colors
        assert "#f5f7fa" in content  # Background color
        assert "#2c3e50" in content  # Header color
        
        # Check for box-sizing
        assert "box-sizing: border-box" in content
    
    def test_sticky_header_css(self, test_client):
        """Test sticky header CSS is present."""
        response = test_client.get("/")
        content = response.text
        
        assert "position: fixed" in content
        assert "z-index: 1000" in content
        assert "#control-panel" in content
    
    def test_table_container_css(self, test_client):
        """Test table container CSS for scrolling."""
        response = test_client.get("/")
        content = response.text
        
        assert "table-container" in content
        assert "overflow-x: auto" in content
        assert "min-width: 1800px" in content
    
    def test_form_styling(self, test_client):
        """Test form has proper styling."""
        response = test_client.get("/")
        content = response.text
        
        assert "display: flex" in content
        assert "gap: 10px" in content
        assert "manualTitleForm" in content
    
    def test_button_styling(self, test_client):
        """Test buttons have modern styling."""
        response = test_client.get("/")
        content = response.text
        
        assert "upload-btn" in content
        assert "transition: background 0.3s ease" in content
        assert "border-radius: 6px" in content
    
    def test_upload_section_present(self, test_client):
        """Test upload section is present."""
        response = test_client.get("/")
        content = response.text
        
        assert "Upload Book Photo" in content
        assert "Select Image" in content
        assert "upload-section" in content
    
    def test_manual_input_section(self, test_client):
        """Test manual input section is present."""
        response = test_client.get("/")
        content = response.text
        
        assert "Or, post the title on text" in content
        assert "Enter book title" in content
        assert "Enter ISBN 13 digits" in content
    
    def test_table_headers_present(self, test_client):
        """Test table headers are included in JavaScript."""
        response = test_client.get("/")
        content = response.text
        
        # Check for table headers in the JavaScript
        assert "ID" in content
        assert "Title" in content
        assert "ISBN" in content
        assert "Amazon.co.jp URL" in content
        assert "Purchase Price" in content
        assert "Decision" in content
        assert "Actions" in content


class TestLayoutComponents:
    """Test individual layout components."""
    
    def test_control_panel_structure(self, test_client):
        """Test control panel has proper structure."""
        response = test_client.get("/")
        content = response.text
        
        assert 'id="control-panel"' in content
        assert "<h1>Book Triage</h1>" in content
    
    def test_main_content_wrapper(self, test_client):
        """Test main content wrapper exists."""
        response = test_client.get("/")
        content = response.text
        
        assert 'class="main-content"' in content
        assert "<h2>Books Database</h2>" in content
    
    def test_css_organization(self, test_client):
        """Test CSS is well organized."""
        response = test_client.get("/")
        content = response.text
        
        # Check for CSS comments
        assert "/* Main content area */" in content
        assert "/* Table styling */" in content
        assert "/* Input styling */" in content
    
    def test_decision_colors_css(self, test_client):
        """Test decision row colors are defined."""
        response = test_client.get("/")
        content = response.text
        
        assert "decision-sell" in content
        assert "decision-digital" in content
        assert "decision-keep" in content
        assert "decision-unknown" in content


class TestAPIEndpoints:
    """Test API endpoints work with new layout."""
    
    def test_books_endpoint(self, test_client):
        """Test books endpoint returns data."""
        response = test_client.get("/books")
        assert response.status_code == 200
        
        books = response.json()
        assert len(books) == 1
        assert books[0]["id"] == "test1"
        assert books[0]["title"] == "Sample Book"
    
    def test_health_endpoint(self, test_client):
        """Test health endpoint still works."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 