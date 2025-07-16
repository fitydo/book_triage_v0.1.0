"""Security module for Book Triage application."""

import os
import secrets
from functools import wraps
from typing import Callable, Any
import magic
from PIL import Image
import io

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic Auth credentials."""
    expected_username = os.getenv("BOOK_USER", "admin")
    expected_password = os.getenv("BOOK_PASS", "password")
    
    is_correct_username = secrets.compare_digest(credentials.username, expected_username)
    is_correct_password = secrets.compare_digest(credentials.password, expected_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def admin_required(func: Callable) -> Callable:
    """Decorator to require admin authentication for endpoints."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract dependencies from kwargs if present
        user = kwargs.get('current_user')
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Basic"},
            )
        return await func(*args, **kwargs)
    return wrapper


def validate_file_upload(file_content: bytes, max_size_mb: int = 10) -> None:
    """Validate uploaded file for security."""
    # Check file size
    if len(file_content) > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size_mb}MB"
        )
    
    # Check magic numbers using python-magic
    try:
        mime_type = magic.from_buffer(file_content, mime=True)
        if not mime_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
    except Exception:
        # If detecting MIME type fails (e.g., magic library error), report invalid format
        raise HTTPException(
            status_code=400,
            detail="Invalid file format"
        )


def sanitize_image(file_content: bytes) -> bytes:
    """Sanitize image by re-saving with Pillow to strip dangerous payloads."""
    try:
        # Load image with Pillow
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary (handles various formats)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Re-save as JPEG to strip metadata and potential payloads
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85)
        return output.getvalue()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        ) 