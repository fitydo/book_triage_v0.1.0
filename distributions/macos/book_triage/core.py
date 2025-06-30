"""Core logic for book triage decision making."""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Decision(str, Enum):
    """Possible decisions for book triage."""
    
    SELL = "sell"
    DIGITAL = "digital"
    KEEP = "keep"
    UNKNOWN = "unknown"


@dataclass
class BookRecord:
    """Represents a book record with all metadata."""
    
    id: str
    title: str
    url: str = ""
    url_com: str = ""
    purchase_price: float = 0.0
    used_price: float = 0.0
    F: Optional[int] = None  # Frequency
    R: Optional[int] = None  # Rarity
    A: Optional[int] = None  # Annotation need
    V: Optional[int] = None  # Resale value
    S: Optional[int] = None  # Sentimental value
    P: Optional[int] = None  # Scannability
    decision: Decision = Decision.UNKNOWN
    verified: str = "no"
    citation_R: List[str] = field(default_factory=list)
    citation_P: List[str] = field(default_factory=list)
    isbn: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "url_com": self.url_com,
            "purchase_price": self.purchase_price,
            "used_price": self.used_price,
            "F": self.F,
            "R": self.R,
            "A": self.A,
            "V": self.V,
            "S": self.S,
            "P": self.P,
            "decision": self.decision.value,
            "verified": self.verified,
            "isbn": self.isbn,
            "citation_R": json.dumps(self.citation_R),
            "citation_P": json.dumps(self.citation_P),
        }


class BookTriage:
    """Main class for book triage operations."""
    
    def __init__(self, csv_path: Union[str, Path], scan_cost: int = 2):
        """Initialize BookTriage with CSV file path and scan cost."""
        self.csv_path = Path(csv_path)
        self.scan_cost = scan_cost
        self.client = OpenAI()
        self.records: List[BookRecord] = []
        self._load_csv()
    
    def _load_csv(self) -> None:
        """Load existing CSV data into memory."""
        if not self.csv_path.exists():
            logger.info(f"CSV file {self.csv_path} does not exist. Will create new file.")
            return
        
        try:
            df = pd.read_csv(self.csv_path)
            for _, row in df.iterrows():
                # Helper function to safely get integer values
                def get_int_value(col: str) -> Optional[int]:
                    value = row.get(col)
                    if value is None or (hasattr(value, '__bool__') and not value):
                        return None
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None
                
                def get_float_value(col: str) -> float:
                    value = row.get(col)
                    if value is None or (hasattr(value, '__bool__') and not value):
                        return 0.0
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return 0.0
                
                isbn = str(row.get("isbn", "")) if "isbn" in row else ""
                citation_R = json.loads(row.get("citation_R", "[]")) if "citation_R" in row and row.get("citation_R") else []
                citation_P = json.loads(row.get("citation_P", "[]")) if "citation_P" in row and row.get("citation_P") else []
                record = BookRecord(
                    id=str(row.get("id", "")),
                    title=str(row.get("title", "")),
                    url=str(row.get("url", "")),
                    url_com=str(row.get("url_com", "")) if "url_com" in row else "",
                    purchase_price=get_float_value("purchase_price") if "purchase_price" in row else 0.0,
                    used_price=get_float_value("used_price") if "used_price" in row else 0.0,
                    F=get_int_value("F"),
                    R=get_int_value("R"),
                    A=get_int_value("A"),
                    V=get_int_value("V"),
                    S=get_int_value("S"),
                    P=get_int_value("P"),
                    decision=Decision(row.get("decision", "unknown")),
                    verified=str(row.get("verified", "no")) if "verified" in row else "no",
                    isbn=isbn,
                    citation_R=citation_R,
                    citation_P=citation_P,
                )
                # If both prices are present, calculate V
                if record.purchase_price > 0 and record.used_price > 0:
                    ratio = record.used_price / record.purchase_price
                    # Map ratio to V score as in README
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
                self.records.append(record)
            logger.info(f"Loaded {len(self.records)} records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def _save_csv(self) -> None:
        """Save records to CSV file."""
        if not self.records:
            logger.warning("No records to save")
            return
        
        # Ensure directory exists
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert records to DataFrame
        data = [record.to_dict() for record in self.records]
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(self.csv_path, index=False)
        logger.info(f"Saved {len(self.records)} records to {self.csv_path}")
    
    def calculate_utilities(self, record: BookRecord) -> Dict[str, float]:
        """Calculate utility scores for each decision."""
        # Default values for missing data
        F = float(record.F or 0)
        R = float(record.R or 0)
        A = float(record.A or 0)
        V = float(record.V or 0)
        S = float(record.S or 0)
        P = float(record.P or 0)
        
        utilities = {
            "sell": V - (R + S),
            "digital": F + P - float(self.scan_cost),
            "keep": R + A + S,
        }
        
        return utilities
    
    def make_decision(self, record: BookRecord) -> Decision:
        """Make decision based on utility scores."""
        utilities = self.calculate_utilities(record)
        
        # Find the decision with highest utility
        max_utility = max(utilities.values())
        best_decision = max(utilities.items(), key=lambda x: x[1])[0]
        
        # If all utilities are equal or negative, mark as unknown
        if max_utility <= 0:
            return Decision.UNKNOWN
        
        # Update verified logic: yes only if at least one R citation, one P citation, and at least one valid Amazon URL
        has_r_citation = bool(record.citation_R)
        has_p_citation = bool(record.citation_P)
        has_amazon_url = (
            (record.url and record.url != 'unknown') or (record.url_com and record.url_com != 'unknown')
        )
        if has_r_citation and has_p_citation and has_amazon_url:
            record.verified = "yes"
        else:
            record.verified = "no"
        
        return Decision(best_decision)
    
    def enrich_with_gpt4o(self, record: BookRecord) -> None:
        """Enrich record with GPT-4o for URL and V (resale value)."""
        if not record.title and not (record.isbn and len(record.isbn) == 13 and record.isbn.isdigit()):
            logger.warning(f"No title or valid ISBN for record {record.id}, skipping GPT-4o enrichment")
            return
        try:
            logger.info(f"[GPT-4o] Starting enrichment for record {record.id} (title: {record.title}, isbn: {record.isbn})")
            print(f"[GPT-4o] Starting enrichment for record {record.id} (title: {record.title}, isbn: {record.isbn})")
            if record.isbn and len(record.isbn) == 13 and record.isbn.isdigit():
                search_key = f'ISBN: {record.isbn}'
            else:
                search_key = f'Title: {record.title}'
            prompt = f"""
            For the book with {search_key}, please:
            - Search Amazon.co.jp and Amazon.com for the best matching product page.
            - If you cannot find a real product, return the string \"unknown\" for the URL.

            Respond in JSON format:
            {{
              "amazon_co_jp_url": "...",
              "amazon_com_url": "..."
            }}
            """
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            content = response.choices[0].message.content
            if content:
                import json
                try:
                    data = json.loads(content)
                    record.url = data.get("amazon_co_jp_url", "")
                    record.url_com = data.get("amazon_com_url", "")
                except Exception as e:
                    logger.warning(f"Failed to parse GPT-4o response: {e}")
                    logger.warning(f"GPT-4o raw response: {content}")
            logger.info(f"[GPT-4o] Finished enrichment for record {record.id}")
            print(f"[GPT-4o] Finished enrichment for record {record.id}")
        except Exception as e:
            logger.error(f"Error in GPT-4o enrichment: {e}")
    
    def enrich_with_gpt35(self, record: BookRecord) -> None:
        # This function is now deprecated for R and P evidence; do nothing or remove
        pass
    
    def add_record(self, record: BookRecord) -> None:
        """Add a new record to the collection."""
        self.records.append(record)
        self._save_csv()
    
    def scan_and_enrich(self) -> None:
        """Scan all records and enrich missing data."""
        logger.info("Starting scan and enrichment process...")
        
        for record in tqdm(self.records, desc="Enriching records"):
            # Enrich URL and V with GPT-4o
            if not record.url or record.V is None:
                self.enrich_with_gpt4o(record)
            
            # Enrich R and P with GPT-3.5
            if record.R is None or record.P is None:
                self.enrich_with_gpt35(record)
            
            # Make decision
            record.decision = self.make_decision(record)
        
        self._save_csv()
        logger.info("Scan and enrichment completed")
    
    def get_records(self) -> List[BookRecord]:
        """Get all records."""
        return self.records.copy()
    
    def get_record_by_id(self, record_id: str) -> Optional[BookRecord]:
        """Get record by ID."""
        for record in self.records:
            if record.id == record_id:
                return record
        return None 