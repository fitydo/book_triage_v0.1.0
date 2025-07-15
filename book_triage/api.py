"""FastAPI application for book triage web interface."""

from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict

from fastapi import FastAPI, File, HTTPException, UploadFile, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

from .core import BookTriage, BookRecord, Decision
from .vision import VisionProcessor
from .security import get_current_user, validate_file_upload, sanitize_image

logger = logging.getLogger(__name__)

# Simple rate limiting storage
_rate_limit_storage = defaultdict(list)

def check_rate_limit(client_ip: str, endpoint: str, limit_per_minute: int) -> None:
    """Simple rate limiting implementation."""
    current_time = time.time()
    
    # Clean old entries (older than 1 minute)
    key = f"{client_ip}:{endpoint}"
    _rate_limit_storage[key] = [
        timestamp for timestamp in _rate_limit_storage[key]
        if current_time - timestamp < 60
    ]
    
    # Check if limit exceeded
    if len(_rate_limit_storage[key]) >= limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )
    
    # Add current request
    _rate_limit_storage[key].append(current_time)

app = FastAPI(title="Book Triage API", version="0.1.0")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: StarletteRequest, call_next) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "same-origin"
        
        # Only add HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Global variables for book triage instance
book_triage: BookTriage | None = None
vision_processor: VisionProcessor | None = None


def initialize_app(csv_path: str | Path, scan_cost: int = 2) -> None:
    """Initialize the FastAPI app with book triage instance."""
    global book_triage, vision_processor
    book_triage = BookTriage(csv_path, scan_cost)
    vision_processor = VisionProcessor()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> str:
    """Serve the main HTML interface."""
    check_rate_limit(request.client.host if request.client else "unknown", "root", 60)
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Book Triage</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin-left: 0; margin-right: auto; padding: 20px; }
            .upload-section { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
            .upload-section.dragover { border-color: #007cba; background-color: #f0f8ff; }
            #fileInput { display: none; }
            .upload-btn { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .upload-btn:hover { background: #005a8b; }
            .result { margin: 20px 0; padding: 15px; border-radius: 5px; }
            .success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .books-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            .books-table th, .books-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .books-table th { background-color: #f2f2f2; }
            .decision-sell { background-color: #ffebee; }
            .decision-digital { background-color: #e8f5e8; }
            .decision-keep { background-color: #fff3e0; }
            .decision-unknown { background-color: #f5f5f5; }
            .edit-title-input { padding: 4px 6px; }
            .edit-title-input[type="number"] { width: 50px; font-size: 1.1em; text-align: center; background: #f8f8ff; border: 1px solid #aaa; border-radius: 4px; }
            .price-input { width: 90px !important; font-size: 1.1em; text-align: right; background: #f8f8ff; border: 1px solid #aaa; border-radius: 4px; }
            .edit-btn, .save-btn, .cancel-btn { padding: 4px 8px; margin-left: 2px; }
        </style>
    </head>
    <body>
        <h1>Book Triage</h1>
        
        <div class="upload-section" id="uploadSection">
            <h3>Upload Book Photo</h3>
            <p>Drag and drop an image here or click to select</p>
            <input type="file" id="fileInput" accept="image/*">
            <button class="upload-btn" onclick="document.getElementById('fileInput').click()">Select Image</button>
        </div>

        <!-- Manual Title Input Section -->
        <div class="upload-section" id="manualTitleSection" style="margin-top: 20px;">
            <h3>Or, post the title on text</h3>
            <form id="manualTitleForm" onsubmit="submitManualTitle(event)">
                <input type="text" id="manualTitleInput" placeholder="Enter book title" style="padding: 8px; width: 300px; font-size: 1.1em; border: 1px solid #aaa; border-radius: 4px;" required />
                <input type="text" id="manualIsbnInput" placeholder="Enter ISBN 13 digits" maxlength="13" style="padding: 8px; width: 180px; font-size: 1.1em; border: 1px solid #aaa; border-radius: 4px; margin-left: 10px;" required />
                <button type="submit" class="upload-btn" style="margin-left: 10px;">Submit</button>
            </form>
        </div>
        
        <div id="result"></div>
        <div id="toast" style="display:none;position:fixed;top:20px;right:20px;z-index:1000;padding:10px 20px;background:#4caf50;color:white;border-radius:5px;font-weight:bold;"></div>
        <h2>Books Database</h2>
        <div id="booksList">Loading...</div>
        
        <script>
            const uploadSection = document.getElementById('uploadSection');
            const fileInput = document.getElementById('fileInput');
            const resultDiv = document.getElementById('result');
            
            // Drag and drop functionality
            uploadSection.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadSection.classList.add('dragover');
            });
            
            uploadSection.addEventListener('dragleave', () => {
                uploadSection.classList.remove('dragover');
            });
            
            uploadSection.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadSection.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    uploadFile(files[0]);
                }
            });
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    uploadFile(e.target.files[0]);
                }
            });
            
            function uploadFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                resultDiv.innerHTML = '<div class="result">Uploading...</div>';
                
                fetch('/upload_photo', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.title) {
                        resultDiv.innerHTML = `
                            <div class="result success">
                                <h4>Success!</h4>
                                <p><strong>Title:</strong> ${data.title}</p>
                                <p><strong>ID:</strong> ${data.id}</p>
                                <p>Book added to database. Please fill in the remaining fields manually.</p>
                            </div>
                        `;
                        loadBooks(); // Refresh the books list
                    } else {
                        resultDiv.innerHTML = `
                            <div class="result error">
                                <h4>Error</h4>
                                <p>Failed to extract title from image.</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h4>Error</h4>
                            <p>Upload failed: ${error.message}</p>
                        </div>
                    `;
                });
            }
            
            function showToast(message) {
                const toast = document.getElementById('toast');
                toast.innerText = message;
                toast.style.display = 'block';
                setTimeout(() => { toast.style.display = 'none'; }, 2000);
            }

            function loadBooks() {
                fetch('/books')
                .then(response => response.json())
                .then(data => {
                    const booksListDiv = document.getElementById('booksList');
                    if (data.length === 0) {
                        booksListDiv.innerHTML = '<p>No books in database.</p>';
                        return;
                    }
                    let table = `
                        <table class="books-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Title</th>
                                    <th>ISBN</th>
                                    <th>Amazon.co.jp URL</th>
                                    <th>Amazon.com URL</th>
                                    <th>Purchase Price</th>
                                    <th>Used Price</th>
                                    <th>V</th>
                                    <th>R</th>
                                    <th>P</th>
                                    <th>F</th>
                                    <th>A</th>
                                    <th>S</th>
                                    <th>citation_R</th>
                                    <th>citation_P</th>
                                    <th>Decision</th>
                                    <th>Verified</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    data.forEach(book => {
                        const decisionClass = `decision-${book.decision.toLowerCase()}`;
                        table += `
                            <tr class="${decisionClass}">
                                <td>${book.id}</td>
                                <td>
                                    <input type="text" class="edit-title-input" value="${book.title || ''}" id="title-${book.id}" style="border: 1px solid #aaa; border-radius: 4px; padding: 4px 6px; width: 150px;">
                                </td>
                                <td>
                                    <input type="text" class="edit-title-input" value="${book.isbn || ''}" id="isbn-${book.id}" style="border: 1px solid #aaa; border-radius: 4px; padding: 4px 6px; width: 130px;">
                                </td>
                                <td>
                                    <input type="text" class="edit-title-input" value="${book.url || ''}" id="url-${book.id}" style="border: 1px solid #aaa; border-radius: 4px; padding: 4px 6px; width: 150px;">
                                </td>
                                <td>
                                    <input type="text" class="edit-title-input" value="${book.url_com || ''}" id="url_com-${book.id}" style="border: 1px solid #aaa; border-radius: 4px; padding: 4px 6px; width: 150px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input price-input" value="${book.purchase_price || 0}" min="0" id="purchase-${book.id}">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input price-input" value="${book.used_price || 0}" min="0" id="used-${book.id}">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.V || ''}" min="0" max="5" id="V-${book.id}" style="width: 40px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.R || ''}" min="1" max="5" id="R-${book.id}" style="width: 40px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.P || ''}" min="1" max="5" id="P-${book.id}" style="width: 40px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.F || ''}" min="1" max="5" id="F-${book.id}" style="width: 40px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.A || ''}" min="1" max="5" id="A-${book.id}" style="width: 40px;">
                                </td>
                                <td>
                                    <input type="number" class="edit-title-input" value="${book.S || ''}" min="1" max="5" id="S-${book.id}" style="width: 40px;">
                                </td>
                                <td>${book.citation_R || ''}</td>
                                <td>${book.citation_P || ''}</td>
                                <td>${book.decision}</td>
                                <td>${book.verified === 'yes' ? 'Yes' : 'No'}</td>
                                <td>
                                    <button class="edit-btn" onclick="saveBook('${book.id}')">Save</button>
                                </td>
                            </tr>
                        `;
                    });
                    
                    table += '</tbody></table>';
                    booksListDiv.innerHTML = table;
                })
                .catch(error => {
                    document.getElementById('booksList').innerHTML = '<p>Error loading books.</p>';
                });
            }
            
            function saveBook(bookId) {
                const title = document.getElementById(`title-${bookId}`).value;
                const isbn = document.getElementById(`isbn-${bookId}`).value;
                const url = document.getElementById(`url-${bookId}`).value;
                const url_com = document.getElementById(`url_com-${bookId}`).value;
                const purchase_price = parseFloat(document.getElementById(`purchase-${bookId}`).value);
                const used_price = parseFloat(document.getElementById(`used-${bookId}`).value);
                const V = document.getElementById(`V-${bookId}`).value;
                const R = document.getElementById(`R-${bookId}`).value;
                const P = document.getElementById(`P-${bookId}`).value;
                const F = document.getElementById(`F-${bookId}`).value;
                const A = document.getElementById(`A-${bookId}`).value;
                const S = document.getElementById(`S-${bookId}`).value;
                
                fetch('/rescan_title', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        id: bookId,
                        title: title,
                        isbn: isbn,
                        url: url,
                        url_com: url_com,
                        purchase_price: purchase_price,
                        used_price: used_price,
                        V: V || null,
                        R: R || null,
                        P: P || null,
                        F: F || null,
                        A: A || null,
                        S: S || null
                    })
                })
                .then(response => response.json())
                .then(data => {
                    loadBooks();
                    showToast('Book updated!');
                })
                .catch(error => {
                    showToast('Error updating book.');
                });
            }
            
            function submitManualTitle(event) {
                event.preventDefault();
                const input = document.getElementById('manualTitleInput');
                const isbnInput = document.getElementById('manualIsbnInput');
                const title = input.value.trim();
                const isbn = isbnInput.value.trim();
                if (!title || !isbn) return;
                input.disabled = true;
                isbnInput.disabled = true;
                const submitBtn = document.querySelector('#manualTitleForm button[type="submit"]');
                if (submitBtn) submitBtn.disabled = true;
                fetch('/add_manual_title', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, isbn })
                })
                .then(response => response.json())
                .then(data => {
                    input.value = '';
                    isbnInput.value = '';
                    input.disabled = false;
                    isbnInput.disabled = false;
                    if (submitBtn) submitBtn.disabled = false;
                    loadBooks();
                    showToast('Book added!');
                })
                .catch(() => {
                    input.disabled = false;
                    isbnInput.disabled = false;
                    if (submitBtn) submitBtn.disabled = false;
                    showToast('Failed to add book.');
                });
            }
            
            // Load books on page load
            loadBooks();
        </script>
    </body>
    </html>
    """


@app.post("/upload_photo")
async def upload_photo(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a photo and extract book title."""
    check_rate_limit(request.client.host if request.client else "unknown", "upload_photo", 60)
    
    if not book_triage or not vision_processor:
        raise HTTPException(status_code=500, detail="Application not initialized")
    
    try:
        # Read and validate file
        content = await file.read()
        validate_file_upload(content, max_size_mb=10)
        
        # Sanitize image
        sanitized_content = sanitize_image(content)
        
        # Save sanitized file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(sanitized_content)
            temp_file_path = temp_file.name
        
        # Extract title from image
        title = vision_processor.extract_title_from_image(temp_file_path)
        
        # Clean up temporary file
        Path(temp_file_path).unlink()
        
        if not title:
            raise HTTPException(status_code=400, detail="Could not extract title from image")
        
        # Create new book record
        record_id = vision_processor.generate_id()
        record = BookRecord(
            id=record_id,
            title=title,
            purchase_price=0.0,
            used_price=0.0,
            decision=Decision.UNKNOWN
        )
        
        # Add to book triage
        book_triage.add_record(record)
        
        return {
            "title": title,
            "id": record_id,
            "csv_row": record.to_dict()
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 400 for no title) as-is
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded photo: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.get("/books")
async def get_books(request: Request) -> list[Dict[str, Any]]:
    """Get all books from the database."""
    check_rate_limit(request.client.host if request.client else "unknown", "books", 30)
    
    if not book_triage:
        raise HTTPException(status_code=500, detail="Application not initialized")
    
    records = book_triage.get_records()
    return [record.to_dict() for record in records]


@app.post("/scan")
async def scan_books(request: Request, current_user: str = Depends(get_current_user)) -> Dict[str, str]:
    """Trigger scan and enrichment of all books."""
    check_rate_limit(request.client.host if request.client else "unknown", "scan", 60)
    
    if not book_triage:
        raise HTTPException(status_code=500, detail="Application not initialized")
    
    try:
        book_triage.scan_and_enrich()
        return {"message": "Scan and enrichment completed successfully"}
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.post("/rescan_title")
async def rescan_title(request: Request) -> dict:
    check_rate_limit(request.client.host if request.client else "unknown", "rescan_title", 60)
    
    data = await request.json()
    book_id = data.get("id")
    new_title = data.get("title")
    new_isbn = data.get("isbn", "")
    new_url = data.get("url", "")
    new_url_com = data.get("url_com", "")
    new_purchase = float(data.get("purchase_price", 0.0))
    new_used = float(data.get("used_price", 0.0))
    new_V = data.get("V")
    new_R = data.get("R") 
    new_P = data.get("P")
    new_F = data.get("F")
    new_A = data.get("A")
    new_S = data.get("S")
    if not book_triage:
        raise HTTPException(status_code=500, detail="Application not initialized")
    record = book_triage.get_record_by_id(book_id)
    if not record:
        raise HTTPException(status_code=404, detail="Book not found")
    record.title = new_title
    record.isbn = new_isbn
    record.url = new_url
    record.url_com = new_url_com
    record.purchase_price = new_purchase
    record.used_price = new_used
    record.V = int(new_V) if new_V is not None and new_V != "" else None
    record.R = int(new_R) if new_R is not None and new_R != "" else None
    record.P = int(new_P) if new_P is not None and new_P != "" else None
    record.F = int(new_F) if new_F is not None and new_F != "" else None
    record.A = int(new_A) if new_A is not None and new_A != "" else None
    record.S = int(new_S) if new_S is not None and new_S != "" else None
    # If V is not manually set and both prices are present, auto-calculate V
    if record.V is None and record.purchase_price > 0 and record.used_price > 0:
        ratio = record.used_price / record.purchase_price
        if ratio < 0.1:
            record.V = 0
        elif ratio < 0.25:
            record.V = 1
        elif ratio < 0.4:
            record.V = 2
        elif ratio < 0.6:
            record.V = 3
        elif ratio < 0.8:
            record.V = 4
        else:
            record.V = 5
    # Only re-enrich this record (calls GPT-4o) for URL if user did not provide a URL
    should_enrich_url = (
        (not record.url or record.url == 'unknown') or (not record.url_com or record.url_com == 'unknown')
    )
    if should_enrich_url and record.F is not None and record.A is not None and record.S is not None and record.purchase_price > 0:
        book_triage.enrich_with_gpt4o(record)
    # Recompute decision
    record.decision = book_triage.make_decision(record)
    # Save to CSV
    book_triage._save_csv()
    return {"row": record.to_dict()}


@app.post("/add_manual_title")
async def add_manual_title(request: Request) -> dict:
    check_rate_limit(request.client.host if request.client else "unknown", "add_manual_title", 60)
    
    data = await request.json()
    title = data.get("title", "").strip()
    isbn = data.get("isbn", "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    if not book_triage or not vision_processor:
        raise HTTPException(status_code=500, detail="Application not initialized")
    # Validate ISBN: must be exactly 13 digits, all numbers
    if not (isbn and isbn.isdigit() and len(isbn) == 13):
        raise HTTPException(status_code=400, detail="ISBN is 13 digits, only numbers. please retype it")
    # Generate new ID
    record_id = vision_processor.generate_id()
    record = BookRecord(
        id=record_id,
        title=title,
        isbn=isbn,
        purchase_price=0.0,
        used_price=0.0,
        decision=Decision.UNKNOWN
    )
    # First GPT-4o enrichment: use ISBN as primary key for Amazon URL and citation searches, fallback to title
    book_triage.enrich_with_gpt4o(record)
    # Save to CSV
    book_triage.add_record(record)
    return {"id": record_id, "title": title, "isbn": isbn, "csv_row": record.to_dict()}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 