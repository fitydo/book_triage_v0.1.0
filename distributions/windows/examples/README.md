# Examples

This directory contains sample data and usage examples for the Book Triage application.

## Sample Data

### `sample_books.csv`
Example CSV file with book data showing the FRAVSP scoring system:

| Column | Description | Example Values |
|--------|-------------|----------------|
| `id` | Unique identifier | "book_001", "programming_pearls" |
| `title` | Book title | "Clean Code", "Design Patterns" |
| `url` | Reference URL | Amazon or other book URLs |
| `F` | Frequency (0-5) | 5 = weekly use, 0 = never |
| `R` | Rarity (0-5) | 5 = out of print, 0 = always available |
| `A` | Annotation need (0-5) | 5 = extensive notes, 0 = no notes |
| `V` | Value/resale (0-5) | 5 = retains 80%+ value, 0 = <10% value |
| `S` | Sentimental (0-5) | 5 = high emotional value, 0 = none |
| `P` | Scannability (0-5) | 5 = easy to digitize, 0 = complex layout |
| `decision` | Result | "keep", "sell", "digital", "unknown" |

## Usage Examples

### Process Sample Data
```bash
# Using the CLI
python -m book_triage.cli process examples/sample_books.csv --output results.csv

# Using the web interface
python -m uvicorn book_triage.api:app --reload
# Then upload the CSV file via the web UI
```

### Create Your Own CSV
Use `sample_books.csv` as a template:

1. Copy the file: `cp examples/sample_books.csv my_books.csv`
2. Edit with your book data
3. Process: `python -m book_triage.cli process my_books.csv`

### FRAVSP Scoring Guide

**Frequency (F)** - How often you'll use the book:
- 0: Never again
- 1: Once every few years
- 2: Yearly reference
- 3: Few times per year
- 4: Monthly reference
- 5: Weekly or more

**Rarity (R)** - How hard to replace:
- 0: Always in print, widely available
- 1: Usually available new
- 2: Sometimes out of stock
- 3: Often out of print periods
- 4: Rare, expensive to replace
- 5: Out of print, very scarce

**Annotation (A)** - Need for handwritten notes:
- 0: No notes needed
- 1: Occasional highlights
- 2: Light markup
- 3: Moderate notes in margins
- 4: Heavy annotation throughout
- 5: Extensive notes, references

**Value (V)** - Resale value retention:
- 0: <10% of original price
- 1: 10-25% retention
- 2: 25-40% retention
- 3: 40-60% retention
- 4: 60-80% retention
- 5: 80%+ retention

**Sentimental (S)** - Emotional attachment:
- 0: No special meaning
- 1: Slight attachment
- 2: Moderate meaning
- 3: Good memories
- 4: Strong emotional value
- 5: Irreplaceable sentimental value

**Scannability (P)** - Ease of digitization:
- 0: Complex layout, photos, binding issues
- 1: Difficult to scan well
- 2: Moderate scanning effort
- 3: Standard book, some effort
- 4: Easy to scan, mostly text
- 5: Perfect for digitization

The algorithm will recommend:
- **Keep**: High rarity, annotation need, or sentimental value
- **Sell**: High resale value, low other factors
- **Digital**: High frequency/scannability, moderate other factors 