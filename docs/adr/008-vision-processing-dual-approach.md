# ADR-008: Vision Processing - Dual OCR Approach

## Status
Accepted

## Context
Book Triage requires optical character recognition (OCR) capabilities to extract book titles and ISBN numbers from uploaded images. Users need to be able to photograph book covers and automatically extract metadata. The system must handle various image qualities, lighting conditions, and book cover designs while providing fallback mechanisms for reliability.

**Requirements:**
- Extract book titles from images with high accuracy
- Extract ISBN numbers when visible
- Handle various image formats (JPEG, PNG, etc.)
- Work with different lighting conditions and image qualities
- Provide graceful fallback mechanisms
- Support both AI-powered and traditional OCR approaches
- Maintain reasonable processing speeds

**Constraints:**
- OpenAI API costs for vision processing
- Tesseract OCR reliability varies with image quality
- Network dependency for AI services
- Processing time considerations for user experience

## Decision
We will implement a **dual OCR approach** combining:

1. **Primary**: OpenAI GPT-4 Vision API for high-accuracy text extraction
2. **Fallback**: Tesseract OCR for offline/cost-effective processing
3. **Smart Routing**: Automatic fallback when primary method fails
4. **Image Preprocessing**: Optimize images for better OCR results

## Consequences

### Positive
- **High Accuracy**: AI-powered vision provides superior text recognition
- **Reliability**: Fallback ensures functionality even when AI service unavailable
- **Cost Control**: Users can operate without OpenAI API if needed
- **Flexibility**: Different approaches for different use cases
- **Image Handling**: Robust image preprocessing and format support
- **Offline Capability**: Tesseract works without internet connection

### Negative
- **Complexity**: Two different OCR systems to maintain
- **API Costs**: OpenAI Vision API charges per image processed
- **Network Dependency**: Primary method requires internet connectivity
- **Variable Quality**: Tesseract results depend heavily on image quality
- **Processing Time**: AI processing can be slower than local OCR

### Mitigation Strategies
- **Smart Fallback**: Automatic detection and switching between methods
- **Cost Monitoring**: Usage tracking and limits for API calls
- **Image Optimization**: Preprocessing to improve OCR success rates
- **Caching**: Store results to avoid reprocessing same images
- **User Control**: Allow users to choose preferred OCR method

## Implementation Details

### Vision Processor Architecture

#### Core VisionProcessor Class
```python
# book_triage/vision.py
class VisionProcessor:
    def __init__(self, use_openai=True):
        self.use_openai = use_openai
        self.openai_client = None
        
        if use_openai:
            try:
                import openai
                self.openai_client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )
            except Exception:
                self.use_openai = False
                logger.warning("OpenAI not available, using Tesseract only")
    
    def extract_title_from_image(self, image_path):
        """Extract title using dual approach with fallback"""
        
        if self.use_openai and self.openai_client:
            try:
                return self.extract_with_openai_vision(image_path)
            except Exception as e:
                logger.warning(f"OpenAI Vision failed: {e}, falling back to Tesseract")
        
        # Fallback to Tesseract
        return self.extract_with_tesseract(image_path)
```

#### OpenAI Vision Integration
```python
def extract_with_openai_vision(self, image_path):
    """Extract text using OpenAI GPT-4 Vision"""
    
    # Convert image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    response = self.openai_client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the main title from this book cover image. Return only the title text, nothing else."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip()
```

#### Tesseract OCR Fallback
```python
def extract_with_tesseract(self, image_path):
    """Extract text using Tesseract OCR"""
    
    try:
        # Load and preprocess image
        image = Image.open(image_path)
        
        # Image optimization for better OCR
        image = self.preprocess_image_for_ocr(image)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image, config='--psm 6')
        
        # Post-process text to extract likely title
        title = self.extract_title_from_text(text)
        
        return title if title else ""
        
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        return ""
```

### Image Preprocessing Pipeline

#### Image Optimization
```python
def preprocess_image_for_ocr(self, image):
    """Optimize image for better OCR results"""
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize for optimal OCR (larger images often work better)
    width, height = image.size
    if width < 800 or height < 600:
        scale_factor = max(800/width, 600/height)
        new_size = (int(width * scale_factor), int(height * scale_factor))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Enhance contrast and sharpness
    from PIL import ImageEnhance
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.1)
    
    return image
```

#### Text Post-Processing
```python
def extract_title_from_text(self, raw_text):
    """Extract likely book title from raw OCR text"""
    
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    if not lines:
        return ""
    
    # Heuristics for title extraction
    # 1. Look for longest line (often the title)
    # 2. Skip very short lines (likely not titles)
    # 3. Skip lines with only numbers or symbols
    
    candidates = []
    for line in lines:
        if len(line) > 3 and not line.isdigit():
            # Remove common OCR artifacts
            cleaned = re.sub(r'[^\w\s\-\'\"]', ' ', line)
            cleaned = ' '.join(cleaned.split())  # Normalize whitespace
            if len(cleaned) > 3:
                candidates.append(cleaned)
    
    # Return the longest reasonable candidate
    if candidates:
        return max(candidates, key=len)
    
    return ""
```

### ISBN Extraction Enhancement

#### Dual ISBN Detection
```python
def extract_title_and_isbn_from_image(self, image_path):
    """Extract both title and ISBN using dual approach"""
    
    title = ""
    isbn = ""
    
    # Try OpenAI Vision first for both title and ISBN
    if self.use_openai and self.openai_client:
        try:
            result = self.extract_structured_data_openai(image_path)
            title = result.get('title', '')
            isbn = result.get('isbn', '')
        except Exception as e:
            logger.warning(f"OpenAI structured extraction failed: {e}")
    
    # Fallback to Tesseract if OpenAI failed or not available
    if not title:
        title = self.extract_with_tesseract(image_path)
    
    if not isbn:
        isbn = self.extract_isbn_with_tesseract(image_path)
    
    return title, isbn

def extract_structured_data_openai(self, image_path):
    """Extract structured data (title + ISBN) using OpenAI"""
    
    # Enhanced prompt for structured extraction
    prompt = """
    Analyze this book cover image and extract:
    1. The main title of the book
    2. The ISBN number if visible (13 digits, may have dashes)
    
    Return the information in this exact format:
    TITLE: [book title]
    ISBN: [isbn number or "Not found"]
    """
    
    # ... OpenAI API call implementation ...
    
    # Parse structured response
    response_text = response.choices[0].message.content
    result = {}
    
    for line in response_text.split('\n'):
        if line.startswith('TITLE:'):
            result['title'] = line.replace('TITLE:', '').strip()
        elif line.startswith('ISBN:'):
            isbn_text = line.replace('ISBN:', '').strip()
            if isbn_text != "Not found":
                result['isbn'] = isbn_text
    
    return result
```

### Error Handling and Resilience

#### Graceful Degradation
```python
def extract_title_from_image_safe(self, image_path):
    """Safe extraction with comprehensive error handling"""
    
    try:
        # Validate image file
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Check file size and format
        image = Image.open(image_path)
        if image.size[0] < 50 or image.size[1] < 50:
            raise ValueError("Image too small for text extraction")
        
        # Attempt extraction
        title = self.extract_title_from_image(image_path)
        
        if not title:
            logger.warning("No title extracted from image")
            return ""
        
        # Validate title (basic sanity checks)
        if len(title) < 2 or len(title) > 200:
            logger.warning(f"Extracted title seems invalid: {title}")
            return ""
        
        return title
        
    except Exception as e:
        logger.error(f"Error extracting title from {image_path}: {e}")
        return ""
```

## Performance Optimization

### Caching Strategy
```python
import hashlib
from functools import lru_cache

class VisionProcessor:
    def __init__(self):
        self.result_cache = {}
    
    def get_image_hash(self, image_path):
        """Generate hash for image caching"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def extract_title_from_image_cached(self, image_path):
        """Extract title with caching"""
        
        image_hash = self.get_image_hash(image_path)
        
        if image_hash in self.result_cache:
            return self.result_cache[image_hash]
        
        result = self.extract_title_from_image(image_path)
        self.result_cache[image_hash] = result
        
        return result
```

### Batch Processing
```python
def process_multiple_images(self, image_paths):
    """Process multiple images efficiently"""
    
    results = []
    
    # Group by processing method for efficiency
    openai_batch = []
    tesseract_batch = []
    
    for path in image_paths:
        if self.should_use_openai(path):
            openai_batch.append(path)
        else:
            tesseract_batch.append(path)
    
    # Process batches
    for path in openai_batch:
        results.append(self.extract_with_openai_vision(path))
    
    for path in tesseract_batch:
        results.append(self.extract_with_tesseract(path))
    
    return results
```

## Configuration and Control

### User Configuration
```python
# Configuration options
VISION_CONFIG = {
    "prefer_openai": True,
    "openai_timeout": 30,
    "tesseract_config": "--psm 6",
    "image_resize_threshold": 800,
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "cache_results": True,
    "cache_duration": 3600,  # 1 hour
}
```

### Cost Management
```python
class CostTracker:
    def __init__(self):
        self.daily_openai_calls = 0
        self.daily_limit = 100  # Configurable limit
    
    def can_use_openai(self):
        return self.daily_openai_calls < self.daily_limit
    
    def record_openai_call(self):
        self.daily_openai_calls += 1
```

## Testing Strategy

### Comprehensive Testing
```python
# tests/test_vision.py
class TestVisionProcessor:
    def test_openai_vision_success(self):
        """Test successful OpenAI vision processing"""
        
    def test_tesseract_fallback(self):
        """Test fallback to Tesseract when OpenAI fails"""
        
    def test_image_preprocessing(self):
        """Test image optimization pipeline"""
        
    def test_structured_extraction(self):
        """Test title and ISBN extraction"""
        
    def test_error_handling(self):
        """Test various error conditions"""
        
    def test_caching_mechanism(self):
        """Test result caching functionality"""
```

### Mock Testing
```python
@patch('book_triage.vision.openai.OpenAI')
def test_vision_processor_with_mock(self, mock_openai):
    """Test vision processing with mocked OpenAI responses"""
    
    # Mock successful response
    mock_response = Mock()
    mock_response.choices[0].message.content = "Test Book Title"
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    processor = VisionProcessor()
    result = processor.extract_title_from_image("test_image.jpg")
    
    assert result == "Test Book Title"
```

## Monitoring and Analytics

### Performance Metrics
- **Success Rate**: Percentage of successful extractions
- **Accuracy**: Manual validation of extracted titles
- **Processing Time**: Average time per image
- **Cost Tracking**: OpenAI API usage and costs
- **Fallback Rate**: How often Tesseract is used

### Quality Metrics
- **Title Length Distribution**: Analyze extracted title lengths
- **Common Failures**: Track common failure patterns
- **Image Quality Impact**: Correlation between image quality and success
- **User Feedback**: Manual correction frequency

## Related Decisions
- [ADR-002: FastAPI Framework](002-web-framework-fastapi.md) - File upload handling integration
- [ADR-004: Security Hardening](004-security-hardening-approach.md) - File validation and security
- [ADR-005: Testing Strategy](005-testing-strategy-comprehensive.md) - Vision processing testing
- [ADR-010: Project Structure](010-project-structure-modular.md) - Vision module organization 