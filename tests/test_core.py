"""Tests for core module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import json
import os

import pytest
import pandas as pd

from book_triage.core import BookTriage, BookRecord, Decision


class TestBookRecord:
    """Test BookRecord class."""
    
    def test_book_record_creation(self):
        """Test creating a BookRecord."""
        record = BookRecord(
            id="test1",
            title="Test Book",
            url="https://amazon.co.jp/test",
            F=3,
            R=2,
            A=1,
            V=4,
            S=2,
            P=4
        )
        
        assert record.id == "test1"
        assert record.title == "Test Book"
        assert record.url == "https://amazon.co.jp/test"
        assert record.F == 3
        assert record.R == 2
        assert record.A == 1
        assert record.V == 4
        assert record.S == 2
        assert record.P == 4
        assert record.decision == Decision.UNKNOWN
    
    def test_book_record_to_dict(self):
        """Test converting BookRecord to dictionary."""
        record = BookRecord(
            id="test1",
            title="Test Book",
            F=3,
            R=2
        )
        
        data = record.to_dict()
        expected = {
            "id": "test1",
            "title": "Test Book",
            "url": "",
            "url_com": "",
            "purchase_price": 0.0,
            "used_price": 0.0,
            "F": 3,
            "R": 2,
            "A": None,
            "V": None,
            "S": None,
            "P": None,
            "decision": "unknown",
            "verified": "no",
            "isbn": "",
            "citation_R": "[]",
            "citation_P": "[]"
        }
        
        assert data == expected

    def test_book_record_with_all_fields(self):
        """Test BookRecord with all fields populated."""
        record = BookRecord(
            id="test2",
            title="Complete Book",
            url="https://amazon.co.jp/complete",
            url_com="https://amazon.com/complete",
            purchase_price=1500.0,
            used_price=800.0,
            F=4,
            R=3,
            A=2,
            V=3,
            S=4,
            P=5,
            decision=Decision.DIGITAL,
            verified="yes",
            citation_R=["Source 1", "Source 2"],
            citation_P=["Scan source"],
            isbn="9781234567890"
        )
        
        data = record.to_dict()
        assert data["purchase_price"] == 1500.0
        assert data["used_price"] == 800.0
        assert data["decision"] == "digital"
        assert data["verified"] == "yes"
        assert data["isbn"] == "9781234567890"
        assert json.loads(data["citation_R"]) == ["Source 1", "Source 2"]
        assert json.loads(data["citation_P"]) == ["Scan source"]


class TestBookTriage:
    """Test BookTriage class."""
    
    def test_book_triage_initialization_nonexistent_file(self):
        """Test BookTriage initialization with non-existent file."""
        # Create a path that doesn't exist
        temp_dir = tempfile.mkdtemp()
        csv_path = Path(temp_dir) / "nonexistent.csv"
        
        try:
            triage = BookTriage(csv_path, scan_cost=3)
            
            assert triage.csv_path == csv_path
            assert triage.scan_cost == 3
            assert len(triage.get_records()) == 0
        finally:
            # Clean up directory
            if csv_path.exists():
                csv_path.unlink()
            os.rmdir(temp_dir)
    
    def test_book_triage_initialization_with_data(self):
        """Test BookTriage initialization with existing CSV data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False) as tmp:
            csv_path = Path(tmp.name)
            # Write sample CSV data
            tmp.write("id,title,url,F,R,A,V,S,P,decision\n")
            tmp.write("test1,Test Book,https://example.com,3,2,1,4,2,4,unknown\n")
        
        try:
            triage = BookTriage(csv_path, scan_cost=2)
            records = triage.get_records()
            assert len(records) == 1
            assert records[0].id == "test1"
            assert records[0].title == "Test Book"
            assert records[0].F == 3
            assert records[0].R == 2
        finally:
            csv_path.unlink()
    
    def test_calculate_utilities(self):
        """Test utility calculation."""
        import tempfile
        import os
        
        temp_dir = tempfile.mkdtemp()
        csv_path = Path(temp_dir) / "test.csv"
        
        try:
            triage = BookTriage(csv_path)
            
            record = BookRecord(
                id="test1",
                title="Test Book",
                F=3,
                R=2,
                A=1,
                V=4,
                S=1,
                P=3
            )
            
            utilities = triage.calculate_utilities(record)
            
            assert utilities["sell"] == 1.0  # V - (R + S) = 4 - (2 + 1) = 1
            assert utilities["digital"] == 4.0  # F + P - scan_cost = 3 + 3 - 2 = 4
            assert utilities["keep"] == 4.0  # R + A + S = 2 + 1 + 1 = 4
        finally:
            if csv_path.exists():
                csv_path.unlink()
            os.rmdir(temp_dir)

    def test_calculate_utilities_with_none_values(self):
        """Test utility calculation with None values."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=True) as tmp:
            csv_path = Path(tmp.name)
        
        triage = BookTriage(csv_path)
        record = BookRecord(
            id="test1",
            title="Test Book",
            F=None,
            R=None,
            A=None,
            V=None,
            S=None,
            P=None
        )
        
        utilities = triage.calculate_utilities(record)
        
        # All values should default to 0
        assert utilities["sell"] == 0.0  # 0 - (0 + 0)
        assert utilities["digital"] == -2.0  # 0 + 0 - 2
        assert utilities["keep"] == 0.0  # 0 + 0 + 0
    
    def test_make_decision(self):
        """Test decision making logic."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            triage = BookTriage(csv_path)
            
            # Test case where digital has highest utility
            record = BookRecord(
                id="test1",
                title="Test Book 1",
                F=4,  # High frequency
                R=2,  # Medium rarity
                A=1,  # Low annotation need
                V=2,  # Medium resale value
                S=1,  # Low sentimental value
                P=4   # High scannability
            )
            
            decision = triage.make_decision(record)
            # U_digital = 4 + 4 - 2 = 6 (highest)
            assert decision == Decision.DIGITAL
            
            # Test case where keep has highest utility
            record = BookRecord(
                id="test2",
                title="Test Book 2",
                F=1,  # Low frequency
                R=5,  # High rarity
                A=4,  # High annotation need
                V=1,  # Low resale value
                S=5,  # High sentimental value
                P=1   # Low scannability
            )
            
            decision = triage.make_decision(record)
            # U_keep = 5 + 4 + 5 = 14 (highest)
            assert decision == Decision.KEEP

            # Test case where sell has highest utility
            record = BookRecord(
                id="test3",
                title="Test Book 3",
                F=1,  # Low frequency
                R=1,  # Low rarity
                A=1,  # Low annotation need
                V=5,  # High resale value
                S=1,  # Low sentimental value
                P=1   # Low scannability
            )
            
            decision = triage.make_decision(record)
            # U_sell = 5 - (1 + 1) = 3 (highest)
            assert decision == Decision.SELL
            
            # Test case where all utilities are negative or zero
            record = BookRecord(
                id="test4",
                title="Test Book 4",
                F=0,
                R=1,
                A=0,
                V=0,
                S=1,
                P=0
            )
            
            decision = triage.make_decision(record)
            # U_sell = 0 - (1 + 1) = -2
            # U_digital = 0 + 0 - 2 = -2  
            # U_keep = 1 + 0 + 1 = 2 (highest but positive, so not UNKNOWN)
            # Max utility is 2, so should be KEEP, not UNKNOWN
            assert decision == Decision.KEEP
        finally:
            if csv_path.exists():
                csv_path.unlink()
    
    def test_add_record(self):
        """Test adding records."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            # File doesn't exist, so BookTriage will handle it gracefully
            triage = BookTriage(csv_path)
            
            record = BookRecord(
                id="test1",
                title="Test Book"
            )
            
            triage.add_record(record)
            
            records = triage.get_records()
            assert len(records) == 1
            assert records[0].id == "test1"
            assert records[0].title == "Test Book"
            
            # Check that file was created and contains data
            assert csv_path.exists()
            df = pd.read_csv(csv_path)
            assert len(df) == 1
            assert df.iloc[0]['id'] == "test1"
        finally:
            # Clean up
            if csv_path.exists():
                csv_path.unlink()
    
    def test_get_record_by_id(self):
        """Test getting record by ID."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            # File doesn't exist, so BookTriage will handle it gracefully
            triage = BookTriage(csv_path)
            
            record1 = BookRecord(id="test1", title="Test Book 1")
            record2 = BookRecord(id="test2", title="Test Book 2")
            
            triage.add_record(record1)
            triage.add_record(record2)
            
            found = triage.get_record_by_id("test1")
            assert found is not None
            assert found.title == "Test Book 1"
            
            not_found = triage.get_record_by_id("nonexistent")
            assert not_found is None
        finally:
            # Clean up
            if csv_path.exists():
                csv_path.unlink()

    def test_price_to_v_calculation(self):
        """Test automatic V calculation from purchase and used prices."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".csv", delete=False) as tmp:
            csv_path = Path(tmp.name)
            # Write CSV with price data
            tmp.write("id,title,purchase_price,used_price,F,R,A,S,P,decision\n")
            tmp.write("test1,Test Book,1000,50,3,2,1,2,4,unknown\n")  # 0.05 ratio -> V=0
            tmp.write("test2,Test Book 2,1000,200,3,2,1,2,4,unknown\n")  # 0.2 ratio -> V=1
            tmp.write("test3,Test Book 3,1000,350,3,2,1,2,4,unknown\n")  # 0.35 ratio -> V=2
            tmp.write("test4,Test Book 4,1000,500,3,2,1,2,4,unknown\n")  # 0.5 ratio -> V=3
            tmp.write("test5,Test Book 5,1000,700,3,2,1,2,4,unknown\n")  # 0.7 ratio -> V=4
            tmp.write("test6,Test Book 6,1000,900,3,2,1,2,4,unknown\n")  # 0.9 ratio -> V=5
        
        try:
            triage = BookTriage(csv_path)
            records = triage.get_records()
            
            assert len(records) == 6
            assert records[0].V == 0  # 0.05 ratio
            assert records[1].V == 1  # 0.2 ratio
            assert records[2].V == 2  # 0.35 ratio
            assert records[3].V == 3  # 0.5 ratio
            assert records[4].V == 4  # 0.7 ratio
            assert records[5].V == 5  # 0.9 ratio
        finally:
            if csv_path.exists():
                csv_path.unlink()

    @patch('book_triage.core.OpenAI')
    def test_enrich_with_gpt4o_mock(self, mock_openai):
        """Test GPT-4o enrichment with mocked OpenAI client."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            # Mock the OpenAI response for URL enrichment (not R and P)
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"amazon_co_jp_url": "https://amazon.co.jp/test", "amazon_com_url": "https://amazon.com/test"}'
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            triage = BookTriage(csv_path)
            triage.client = mock_client  # Set the client directly
            record = BookRecord(id="test1", title="Test Book")
            
            triage.enrich_with_gpt4o(record)
            
            # GPT-4o enriches URLs, not R and P
            assert record.url == "https://amazon.co.jp/test"
            assert record.url_com == "https://amazon.com/test"
            
            # Verify OpenAI was called
            mock_client.chat.completions.create.assert_called_once()
        finally:
            if csv_path.exists():
                csv_path.unlink()

    def test_scan_cost_parameter(self):
        """Test that scan cost parameter affects utility calculations."""
        # Use a non-existent path that BookTriage can handle
        csv_path = Path(tempfile.mktemp(suffix=".csv"))
        
        try:
            # Test with different scan costs
            triage_low_cost = BookTriage(csv_path, scan_cost=1)
            triage_high_cost = BookTriage(csv_path, scan_cost=4)
            
            record = BookRecord(
                id="test1",
                title="Test Book",
                F=3,
                P=3
            )
            
            utilities_low = triage_low_cost.calculate_utilities(record)
            utilities_high = triage_high_cost.calculate_utilities(record)
            
            # Digital utility should be higher with lower scan cost
            assert utilities_low["digital"] > utilities_high["digital"]
            assert utilities_low["digital"] == 5.0  # 3 + 3 - 1
            assert utilities_high["digital"] == 2.0  # 3 + 3 - 4
        finally:
            if csv_path.exists():
                csv_path.unlink()


class TestDecisionEnum:
    """Test Decision enum."""
    
    def test_decision_values(self):
        """Test Decision enum values."""
        assert Decision.SELL.value == "sell"
        assert Decision.DIGITAL.value == "digital"
        assert Decision.KEEP.value == "keep"
        assert Decision.UNKNOWN.value == "unknown"
    
    def test_decision_comparison(self):
        """Test Decision enum comparison."""
        assert Decision.SELL == "sell"
        assert Decision.DIGITAL == "digital"
        assert Decision.KEEP == "keep"
        assert Decision.UNKNOWN == "unknown" 