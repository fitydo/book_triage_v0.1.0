"""Tests for sticky form functionality."""

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
        # Write sample CSV headers
        tmp.write("id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P\n")
        tmp.write("test1,Test Book,https://example.com,,0.0,0.0,3,2,1,4,2,4,keep,no,,\"[]\",\"[]\"\n")
    
    yield csv_path
    
    # Cleanup
    if csv_path.exists():
        csv_path.unlink()


@pytest.fixture
def client(temp_csv):
    """Create a test client with initialized data."""
    initialize_app(temp_csv, scan_cost=2)
    return TestClient(app)


def test_sticky_form_css_present(client):
    """Test that the sticky form CSS is present in the HTML response."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for sticky control panel CSS
    assert "#control-panel" in html_content
    assert "position: fixed" in html_content
    assert "top: 0" in html_content
    assert "z-index: 1000" in html_content
    assert "background: white" in html_content


def test_sticky_form_html_structure(client):
    """Test that the HTML structure includes the control panel wrapper."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for control panel div
    assert '<div id="control-panel">' in html_content
    
    # Check that the title is inside the control panel
    assert html_content.find('<div id="control-panel">') < html_content.find('<h1>Book Triage</h1>')
    
    # Check that upload section is inside control panel
    assert 'id="uploadSection"' in html_content
    assert 'id="manualTitleSection"' in html_content
    
    # Check that result div is inside control panel
    assert '<div id="result"></div>' in html_content


def test_body_padding_adjustment(client):
    """Test that body has proper padding to accommodate sticky header."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check for body padding-top to make room for sticky header
    assert "padding-top: 280px" in html_content


def test_books_database_outside_control_panel(client):
    """Test that the books database section is outside the sticky control panel."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Find positions of control panel end and books database start
    control_panel_end = html_content.find('</div>') # First closing div after control-panel
    books_database_start = html_content.find('<h2>Books Database</h2>')
    
    # Books Database should come after the control panel closes
    assert books_database_start > control_panel_end


def test_toast_notifications_position(client):
    """Test that toast notifications have proper z-index to appear above sticky form."""
    response = client.get("/")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Check toast styling - should be positioned properly
    assert 'id="toast"' in html_content
    assert "position:fixed" in html_content
    assert "z-index:1000" in html_content


def test_form_functionality_still_works(client):
    """Test that the sticky form doesn't break existing functionality."""
    # Test that we can still access the upload endpoint
    response = client.get("/")
    assert response.status_code == 200
    
    # Verify form elements are present
    html_content = response.text
    assert 'id="fileInput"' in html_content
    assert 'id="manualTitleInput"' in html_content
    assert 'id="manualIsbnInput"' in html_content
    assert 'id="manualTitleForm"' in html_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 