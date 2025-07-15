"""Tests for sticky table headers functionality."""

import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from book_triage.api import app, initialize_app


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        csv_path = Path(tmp.name)
        # Write sample CSV headers and data
        tmp.write("id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P\n")
        tmp.write("test1,Test Book 1,https://example.com,,0.0,0.0,3,2,1,4,2,4,keep,no,,\"[]\",\"[]\"\n")
        tmp.write("test2,Test Book 2,https://example.com,,0.0,0.0,1,4,3,2,5,2,digital,no,,\"[]\",\"[]\"\n")
    
    yield csv_path
    
    # Cleanup
    if csv_path.exists():
        csv_path.unlink()


@pytest.fixture
def client(temp_csv):
    """Create a test client with initialized data."""
    initialize_app(temp_csv, scan_cost=2)
    return TestClient(app)


def test_sticky_table_headers_css_present(client):
    """Test that sticky table headers CSS is present in the HTML response."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for sticky table header CSS properties
    assert "position: sticky" in html_content
    assert "top: 280px" in html_content  # Should align with sticky form height
    assert "z-index: 999" in html_content  # Should be below control panel (z-index: 1000)
    assert "box-shadow: 0 2px 2px rgba(0,0,0,0.1)" in html_content


def test_table_header_structure(client):
    """Test that table headers are properly structured for stickiness."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for table structure
    assert '<table class="books-table">' in html_content
    assert '<thead>' in html_content
    assert '<tbody>' in html_content
    
    # Check for all expected column headers
    expected_headers = [
        '<th>ID</th>',
        '<th>Title</th>',
        '<th>ISBN</th>',
        '<th>Amazon.co.jp URL</th>',
        '<th>Amazon.com URL</th>',
        '<th>Purchase Price</th>',
        '<th>Used Price</th>',
        '<th>V</th>',
        '<th>R</th>',
        '<th>P</th>',
        '<th>F</th>',
        '<th>A</th>',
        '<th>S</th>',
        '<th>citation_R</th>',
        '<th>citation_P</th>',
        '<th>Decision</th>',
        '<th>Verified</th>',
        '<th>Actions</th>'
    ]
    
    for header in expected_headers:
        assert header in html_content


def test_table_header_css_specificity(client):
    """Test that table header CSS has proper specificity and styling."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for books-table class styling
    assert '.books-table th' in html_content
    assert 'background-color: #f2f2f2' in html_content
    
    # Check for thead specific styling
    assert '.books-table thead th' in html_content
    assert 'border-bottom: 2px solid #ddd' in html_content


def test_sticky_header_positioning(client):
    """Test that sticky headers are positioned correctly relative to control panel."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Control panel should have top: 0
    control_panel_css = html_content.find('#control-panel')
    control_panel_section = html_content[control_panel_css:control_panel_css + 500]
    assert 'top: 0' in control_panel_section
    
    # Table headers should have top: 280px (same as body padding-top)
    table_css = html_content.find('.books-table th')
    table_section = html_content[table_css:table_css + 300]
    assert 'top: 280px' in table_section


def test_z_index_layering(client):
    """Test that z-index values create proper layering."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Control panel should have highest z-index (1000)
    assert 'z-index: 1000' in html_content
    
    # Table headers should have lower z-index (999) but still above content
    assert 'z-index: 999' in html_content
    
    # Toast should also have z-index 1000 but positioned differently
    toast_section = html_content[html_content.find('id="toast"'):html_content.find('id="toast"') + 200]
    assert 'z-index:1000' in toast_section


def test_table_headers_visual_separation(client):
    """Test that table headers have proper visual separation from content."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Headers should have box shadow for visual separation
    assert 'box-shadow: 0 2px 2px rgba(0,0,0,0.1)' in html_content
    
    # Headers should have stronger border at bottom
    assert 'border-bottom: 2px solid #ddd' in html_content


def test_books_database_section_outside_control_panel(client):
    """Test that Books Database table is outside control panel but has sticky headers."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Find positions
    control_panel_start = html_content.find('<div id="control-panel">')
    control_panel_end = html_content.find('</div>', control_panel_start)
    books_table_start = html_content.find('<table class="books-table">')
    
    # Table should be outside control panel
    assert books_table_start > control_panel_end
    
    # But table should have sticky headers
    table_section = html_content[books_table_start:books_table_start + 1000]
    assert '<thead>' in table_section
    assert '<th>' in table_section


def test_complete_sticky_ui_integration(client):
    """Test that both sticky form and sticky headers work together."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Both sticky elements should be present
    assert '<div id="control-panel">' in html_content  # Sticky form
    assert 'position: sticky' in html_content  # Sticky headers
    
    # Proper layering
    assert 'z-index: 1000' in html_content  # Control panel
    assert 'z-index: 999' in html_content   # Table headers
    
    # Proper positioning
    assert 'top: 0' in html_content         # Control panel at top
    assert 'top: 280px' in html_content     # Headers below control panel
    
    # Body padding to accommodate both
    assert 'padding-top: 280px' in html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 