#!/usr/bin/env python3
"""Additional tests to improve coverage for core module."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from book_triage.core import BookTriage, BookRecord, Decision


class TestBookTriageCoverage:
    """Test edge cases and error conditions to improve coverage."""

    def test_load_csv_with_invalid_float_values(self):
        """Test CSV loading with invalid float values."""
        # Create CSV with invalid float values
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,invalid,not_a_number,3,2,1,4,2,4,unknown,no,,[],[]
test2,Test Book 2,,,0.0,0.0,not_int,invalid,bad_value,5,1,3,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            # This should handle invalid values gracefully
            triage = BookTriage(csv_path)
            records = triage.get_records()
            
            # Should have loaded records despite invalid values
            assert len(records) == 2
            
            # First record should have 0.0 for invalid float values
            record1 = records[0]
            assert record1.purchase_price == 0.0
            assert record1.used_price == 0.0
            
            # Second record should have None for invalid int values
            record2 = records[1]
            assert record2.F is None
            assert record2.R is None
            assert record2.A is None
            
        finally:
            csv_path.unlink()

    def test_load_csv_with_nan_values(self):
        """Test CSV loading with NaN values."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,nan,nan,0.0,0.0,3,2,1,4,2,4,unknown,nan,nan,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            records = triage.get_records()
            
            assert len(records) == 1
            record = records[0]
            
            # NaN values should be converted to empty strings
            assert record.url == ""
            assert record.url_com == ""
            assert record.verified == "no"  # default value
            assert record.isbn == ""
            
        finally:
            csv_path.unlink()

    def test_enrich_with_gpt4o_no_title_no_isbn(self):
        """Test GPT-4o enrichment with no title and no ISBN."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            record = BookRecord(id="test", title="", isbn="")
            
            # Should skip enrichment for empty title and ISBN
            triage.enrich_with_gpt4o(record)
            
            # URLs should remain empty
            assert record.url == ""
            assert record.url_com == ""
            
        finally:
            csv_path.unlink()

    def test_enrich_with_gpt4o_invalid_isbn(self):
        """Test GPT-4o enrichment with invalid ISBN."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            record = BookRecord(id="test", title="", isbn="12345")  # Invalid ISBN
            
            # Should skip enrichment for invalid ISBN
            triage.enrich_with_gpt4o(record)
            
            # URLs should remain empty
            assert record.url == ""
            assert record.url_com == ""
            
        finally:
            csv_path.unlink()

    @patch('book_triage.core.OpenAI')
    def test_enrich_with_gpt4o_json_parsing_error(self, mock_openai):
        """Test GPT-4o enrichment with JSON parsing error."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            # Mock OpenAI client to return invalid JSON
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Invalid JSON response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            triage = BookTriage(csv_path)
            record = BookRecord(id="test", title="Test Book", isbn="1234567890123")
            
            # Should handle JSON parsing error gracefully
            triage.enrich_with_gpt4o(record)
            
            # URLs should be empty due to parsing error
            assert record.url == ""
            assert record.url_com == ""
            
        finally:
            csv_path.unlink()

    def test_calculate_utilities_with_none_values(self):
        """Test utility calculation with None values."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            record = BookRecord(
                id="test",
                title="Test Book",
                F=None, R=None, A=None, V=None, S=None, P=None
            )
            
            utilities = triage.calculate_utilities(record)
            
            # All utilities should be calculated with 0 values
            assert utilities['sell'] == 0.0  # V - (R + S) = 0 - (0 + 0) = 0
            assert utilities['digital'] == -2.0  # F + P - scan_cost = 0 + 0 - 2 = -2
            assert utilities['keep'] == 0.0  # R + A + S = 0 + 0 + 0 = 0
            
        finally:
            csv_path.unlink()

    def test_make_decision_with_verification_calculation(self):
        """Test decision making with verification calculation."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            
            # Test record with verification criteria
            record = BookRecord(
                id="test",
                title="Test Book",
                url="https://amazon.co.jp/test",
                citation_R=["R evidence"],
                citation_P=["P evidence"],
                F=3, R=2, A=1, V=4, S=2, P=4
            )
            
            decision = triage.make_decision(record)
            
            # Should calculate verification status
            assert record.verified == "yes"  # Has R, P citations and URL
            assert decision == Decision.DIGITAL  # Highest utility (F + P - scan_cost = 3 + 4 - 2 = 5)
            
        finally:
            csv_path.unlink()

    def test_save_csv_with_no_records(self):
        """Test saving CSV with no records."""
        csv_content = """id,title,url,url_com,purchase_price,used_price,F,R,A,V,S,P,decision,verified,isbn,citation_R,citation_P
test1,Test Book,,,0.0,0.0,3,2,1,4,2,4,unknown,no,,[],[]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            csv_path = Path(f.name)
        
        try:
            triage = BookTriage(csv_path)
            # Clear any existing records
            triage.records = []
            
            # Should handle empty records gracefully
            triage._save_csv()
            
            # File should still exist but be empty (except headers)
            assert csv_path.exists()
            
        finally:
            csv_path.unlink() 