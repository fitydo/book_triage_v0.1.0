"""
Simple tests for Book Triage core functionality.
"""
import pytest
from pathlib import Path
import tempfile
from book_triage.core import BookRecord, BookTriage, Decision


class TestBookRecord:
    """Test BookRecord class."""
    
    def test_book_record_creation(self):
        """Test basic BookRecord creation."""
        record = BookRecord(id="test1", title="Test Book")
        assert record.id == "test1"
        assert record.title == "Test Book"
        assert record.F is None
        assert record.R is None
        assert record.A is None
        assert record.V is None
        assert record.S is None
        assert record.P is None
        assert record.decision == Decision.UNKNOWN

    def test_book_record_with_values(self):
        """Test BookRecord with all values."""
        record = BookRecord(
            id="test1",
            title="Test Book",
            F=5, R=4, A=3, V=2, S=1, P=5
        )
        assert record.F == 5
        assert record.R == 4
        assert record.A == 3
        assert record.V == 2
        assert record.S == 1
        assert record.P == 5


class TestBookTriage:
    """Test BookTriage class."""
    
    def test_book_triage_initialization(self):
        """Test BookTriage initialization."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            triage = BookTriage(csv_path)
            assert triage.csv_path == csv_path
        finally:
            if csv_path.exists():
                csv_path.unlink()

    def test_calculate_utilities_simple(self):
        """Test simple utility calculation."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            triage = BookTriage(csv_path)
            
            record = BookRecord(
                id="test1",
                title="Test Book",
                F=3, R=2, A=1, V=4, S=1, P=3
            )
            
            utilities = triage.calculate_utilities(record)
            
            # Check that utilities are calculated
            assert "sell" in utilities
            assert "digital" in utilities
            assert "keep" in utilities
            assert isinstance(utilities["sell"], (int, float))
            assert isinstance(utilities["digital"], (int, float))
            assert isinstance(utilities["keep"], (int, float))
        finally:
            if csv_path.exists():
                csv_path.unlink()

    def test_make_decision_simple(self):
        """Test simple decision making."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            triage = BookTriage(csv_path)
            
            record = BookRecord(
                id="test1",
                title="Test Book",
                F=4, R=2, A=1, V=2, S=1, P=4
            )
            
            decision = triage.make_decision(record)
            assert isinstance(decision, Decision)
            assert decision in [Decision.SELL, Decision.DIGITAL, Decision.KEEP, Decision.UNKNOWN]
        finally:
            if csv_path.exists():
                csv_path.unlink()


class TestDecision:
    """Test Decision enum."""
    
    def test_decision_values(self):
        """Test Decision enum values."""
        assert Decision.SELL == "sell"
        assert Decision.DIGITAL == "digital"
        assert Decision.KEEP == "keep"
        assert Decision.UNKNOWN == "unknown" 