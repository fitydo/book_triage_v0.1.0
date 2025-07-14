# ADR-001: Data Storage Using CSV Files

## Status
Accepted

## Context
The Book Triage application needs to store and manage book collection data. We need to choose a data storage solution that balances simplicity, portability, and functionality for a personal book collection management tool.

**Requirements:**
- Simple setup with no external dependencies
- Human-readable data format
- Easy backup and version control
- Cross-platform compatibility
- Support for tabular data with structured fields
- Ability to handle moderate data volumes (thousands of books)

**Alternatives Considered:**
1. **SQLite Database**: Local database with SQL support
2. **JSON Files**: Structured data in JSON format
3. **CSV Files**: Comma-separated values in plain text
4. **Cloud Database**: External database service (PostgreSQL, MongoDB)

## Decision
We will use **CSV files** as the primary data storage mechanism for Book Triage.

**Rationale:**
- **Simplicity**: No database setup or configuration required
- **Portability**: CSV files can be easily moved between systems
- **Human-readable**: Users can view and edit data in Excel, Google Sheets, or text editors
- **Version Control Friendly**: Text-based format works well with Git
- **Pandas Integration**: Excellent support via pandas DataFrame operations
- **Cross-platform**: Universal support across all operating systems
- **Zero Dependencies**: No additional database software required
- **Backup Simplicity**: Just copy the CSV file

## Consequences

### Positive
- **Quick Setup**: Application works immediately without database configuration
- **User Control**: Users can directly manipulate their data in familiar tools
- **Backup Strategy**: Simple file copy for complete data backup
- **Debugging**: Easy to inspect data directly in text editors
- **Distribution**: Data travels with the application
- **Performance**: Adequate for expected data volumes (< 10,000 books)
- **Memory Efficiency**: pandas handles CSV loading/saving efficiently

### Negative
- **Concurrency**: No built-in support for concurrent access
- **ACID Properties**: No transactional guarantees
- **Query Complexity**: Limited complex querying capabilities
- **Data Integrity**: No foreign key constraints or data validation at storage level
- **Scalability**: May become slow with very large datasets (> 50,000 books)
- **Memory Usage**: Entire dataset loaded into memory

### Mitigation Strategies
- **File Locking**: Implement application-level file locking for write operations
- **Data Validation**: Perform validation in application layer before CSV writes
- **Backup**: Automatic backup creation before modifications
- **Performance**: Monitor and optimize pandas operations for large datasets
- **Migration Path**: Design data layer to allow future migration to database if needed

## Implementation Details
- Use pandas DataFrame for in-memory data manipulation
- Implement BookTriage class to encapsulate CSV operations
- UTF-8 encoding for international character support
- Consistent column naming and data types
- Atomic write operations (write to temp file, then rename)

## Related Decisions
- [ADR-010: Modular Project Structure](010-project-structure-modular.md) - Enables clean data layer abstraction
- Future ADR for database migration strategy if scaling requirements change 