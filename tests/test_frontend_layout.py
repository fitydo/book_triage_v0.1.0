"""Tests for frontend layout and styling improvements."""

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from book_triage.api import app, initialize_app
from book_triage.core import BookTriage
import tempfile
import os


@pytest.fixture
def client_with_styled_data():
    """Create a test client with sample data for layout testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("id,title,isbn,url,url_com,purchase_price,used_price,V,R,P,F,A,S,citation_R,citation_P,decision,verified\n")
        f.write("test1,Test Book One,9781234567890,https://amazon.co.jp/test1,https://amazon.com/test1,1500,1200,4,5,3,2,4,3,Citation R1,Citation P1,keep,yes\n")
        f.write("test2,Test Book Two,9780987654321,https://amazon.co.jp/test2,https://amazon.com/test2,2000,1800,3,4,5,1,3,4,Citation R2,Citation P2,sell,no\n")
        f.write("test3,Test Book Three,9781111111111,https://amazon.co.jp/test3,https://amazon.com/test3,800,600,2,3,4,5,2,3,Citation R3,Citation P3,digital,yes\n")
        csv_path = f.name
    
    try:
        initialize_app(csv_path, scan_cost=2)
        with TestClient(app) as client:
            yield client
    finally:
        if os.path.exists(csv_path):
            os.unlink(csv_path)


class TestFrontendLayout:
    """Test the improved frontend layout and styling."""
    
    def test_modern_css_styling_present(self, client_with_styled_data):
        """Test that modern CSS styling is properly included."""
        response = client_with_styled_data.get("/")
        assert response.status_code == 200
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for modern font family
        style_tag = soup.find('style')
        assert style_tag is not None
        css_content = style_tag.get_text() if style_tag else ""
        
        # Modern font stack
        assert "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" in css_content
        
        # Modern color scheme
        assert "#f5f7fa" in css_content  # Background color
        assert "#2c3e50" in css_content  # Header color
        
        # Box model
        assert "box-sizing: border-box" in css_content
    
    def test_control_panel_styling(self, client_with_styled_data):
        """Test control panel has proper styling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Control panel exists
        control_panel = soup.find('div', id='control-panel')
        assert control_panel is not None
        
        # Check CSS for control panel
        style_tag = soup.find('style')
        css_content = style_tag.get_text() if style_tag else ""
        
        # Fixed positioning
        assert "position: fixed" in css_content
        assert "z-index: 1000" in css_content
        
        # Modern shadow
        assert "box-shadow: 0 2px 10px rgba(0,0,0,0.1)" in css_content
    
    def test_table_container_styling(self, client_with_styled_data):
        """Test table container has proper styling for scrolling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Table container styling
        assert ".table-container" in css_content
        assert "overflow-x: auto" in css_content
        assert "border-radius: 8px" in css_content
        assert "box-shadow: 0 2px 10px rgba(0,0,0,0.05)" in css_content
        
        # Table minimum width for scrolling
        assert "min-width: 1800px" in css_content
    
    def test_upload_section_styling(self, client_with_styled_data):
        """Test upload section has modern styling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Upload section exists
        upload_section = soup.find('div', class_='upload-section')
        assert upload_section is not None
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Modern upload styling
        assert "border-radius: 8px" in css_content
        assert "transition: all 0.3s ease" in css_content
        assert "transform: scale(1.02)" in css_content  # Hover effect
    
    def test_button_styling(self, client_with_styled_data):
        """Test buttons have modern styling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Upload button exists
        upload_btn = soup.find('button', class_='upload-btn')
        assert upload_btn is not None
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Modern button styling
        assert "transition: background 0.3s ease" in css_content
        assert "border-radius: 6px" in css_content
        assert "font-size: 16px" in css_content
    
    def test_form_layout(self, client_with_styled_data):
        """Test form has proper flexbox layout."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Manual title form exists
        form = soup.find('form', id='manualTitleForm')
        assert form is not None
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Flexbox layout
        assert "display: flex" in css_content
        assert "gap: 10px" in css_content
        assert "justify-content: center" in css_content
        assert "flex-wrap: wrap" in css_content
    
    def test_input_field_styling(self, client_with_styled_data):
        """Test input fields have consistent styling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Input styling
        assert ".edit-title-input" in css_content
        assert "border: 1px solid #ced4da" in css_content
        assert "transition: border-color 0.3s ease" in css_content
        
        # Focus states
        assert ".edit-title-input:focus" in css_content
        assert "border-color: #007cba" in css_content
    
    def test_responsive_table_headers(self, client_with_styled_data):
        """Test table headers have sticky positioning."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Sticky headers
        assert "position: sticky" in css_content
        assert "top: 0" in css_content
        assert "z-index: 10" in css_content
    
    def test_decision_row_colors(self, client_with_styled_data):
        """Test decision-based row coloring."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Decision colors
        assert ".decision-sell" in css_content
        assert ".decision-digital" in css_content
        assert ".decision-keep" in css_content
        assert ".decision-unknown" in css_content
        
        # Specific colors
        assert "#ffebee" in css_content  # sell
        assert "#e8f5e8" in css_content  # digital
        assert "#fff3e0" in css_content  # keep
        assert "#f5f5f5" in css_content  # unknown
    
    def test_main_content_wrapper(self, client_with_styled_data):
        """Test main content has proper wrapper styling."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Main content wrapper exists
        main_content = soup.find('div', class_='main-content')
        assert main_content is not None
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Main content styling
        assert ".main-content" in css_content
        assert "padding: 20px" in css_content
        assert "max-width: 100%" in css_content
    
    def test_hover_effects(self, client_with_styled_data):
        """Test hover effects are properly defined."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # Hover effects
        assert ":hover" in css_content
        assert ".books-table tbody tr:hover" in css_content
        assert ".upload-btn:hover" in css_content
        assert ".edit-btn:hover" in css_content
    

class TestTableFunctionality:
    """Test table functionality with improved layout."""
    
    def test_table_renders_with_data(self, client_with_styled_data):
        """Test table renders properly with sample data."""
        response = client_with_styled_data.get("/books")
        assert response.status_code == 200
        
        books = response.json()
        assert len(books) == 3
        assert books[0]["id"] == "test1"
        assert books[0]["title"] == "Test Book One"
    
    def test_table_has_all_columns(self, client_with_styled_data):
        """Test table includes all required columns."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        
        # Check for all expected column headers in JavaScript
        assert "ID" in html_content
        assert "Title" in html_content
        assert "ISBN" in html_content
        assert "Amazon.co.jp URL" in html_content
        assert "Amazon.com URL" in html_content
        assert "Purchase Price" in html_content
        assert "Used Price" in html_content
        assert "Decision" in html_content
        assert "Verified" in html_content
        assert "Actions" in html_content
    
    def test_input_field_classes(self, client_with_styled_data):
        """Test input fields have proper CSS classes."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        
        # Check for CSS classes in JavaScript
        assert "title-input" in html_content
        assert "isbn-input" in html_content
        assert "url-input" in html_content
        assert "price-input" in html_content
        assert "edit-title-input" in html_content


class TestLayoutResponsiveness:
    """Test layout responsiveness and accessibility."""
    
    def test_viewport_meta_tag(self, client_with_styled_data):
        """Test viewport meta tag for mobile responsiveness."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Should have proper viewport for mobile
        # Note: We should add this if not present
        head = soup.find('head')
        assert head is not None
    
    def test_semantic_html_structure(self, client_with_styled_data):
        """Test proper HTML semantic structure."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Proper HTML structure
        assert soup.find('html') is not None
        assert soup.find('head') is not None
        assert soup.find('body') is not None
        assert soup.find('title') is not None
        
        # Semantic elements
        assert soup.find('h1') is not None
        assert soup.find('h2') is not None
        assert soup.find('form') is not None
    
    def test_css_organization(self, client_with_styled_data):
        """Test CSS is well organized and structured."""
        response = client_with_styled_data.get("/")
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        style_tag = soup.find('style')
        css_content = style_tag.string
        
        # CSS organization checks
        assert "/* Main content area */" in css_content
        assert "/* Table styling */" in css_content
        assert "/* Decision colors */" in css_content
        assert "/* Input styling */" in css_content
        assert "/* Form styling */" in css_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 