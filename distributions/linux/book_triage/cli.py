"""CLI interface for book triage."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from dotenv import load_dotenv
import pandas as pd

from .api import app, initialize_app
from .core import BookTriage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

cli = typer.Typer(help="Book Triage - A tool for triaging books")


@cli.command()
def scan(
    csv: Path = typer.Argument(..., help="Path to CSV file"),
    scan_cost: int = typer.Option(2, "--scan-cost", "-s", help="Scan cost (0-5)", min=0, max=5),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Scan and enrich CSV data with AI-powered analysis."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Check if CSV file exists or can be created
        csv_path = Path(csv)
        if not csv_path.exists():
            logger.info(f"CSV file {csv_path} does not exist. Will create new file.")
            csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize book triage
        book_triage = BookTriage(csv_path, scan_cost)
        
        # Check if there are any records to process
        records = book_triage.get_records()
        if not records:
            logger.warning("No records found in CSV. Add some books first.")
            return
        
        logger.info(f"Starting scan and enrichment for {len(records)} records...")
        logger.info(f"Scan cost set to: {scan_cost}")
        
        # Perform scan and enrichment
        book_triage.scan_and_enrich()
        
        logger.info("Scan and enrichment completed successfully!")
        
        # Show summary
        decisions = {}
        for record in book_triage.get_records():
            decision = record.decision.value
            decisions[decision] = decisions.get(decision, 0) + 1
        
        logger.info("Decision summary:")
        for decision, count in decisions.items():
            logger.info(f"  {decision}: {count} books")
        
    except Exception as e:
        logger.error(f"Error during scan: {e}")
        sys.exit(1)


@cli.command()
def web(
    csv: Path = typer.Argument(..., help="Path to CSV file"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    scan_cost: int = typer.Option(2, "--scan-cost", "-s", help="Scan cost (0-5)", min=0, max=5),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """Launch FastAPI web interface."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Check if CSV file exists or can be created
        csv_path = Path(csv)
        if not csv_path.exists():
            logger.info(f"CSV file {csv_path} does not exist. Will create new file.")
            csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the FastAPI app
        initialize_app(csv_path, scan_cost)
        
        logger.info(f"Starting web interface at http://{host}:{port}")
        logger.info(f"CSV file: {csv_path}")
        logger.info(f"Scan cost: {scan_cost}")
        
        # Run the server
        uvicorn.run(
            "book_triage.api:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info" if verbose else "warning"
        )
        
    except Exception as e:
        logger.error(f"Error starting web interface: {e}")
        sys.exit(1)


@cli.command()
def create_csv(
    csv: Path = typer.Argument(..., help="Path to CSV file to create"),
    sample: bool = typer.Option(False, "--sample", help="Add sample data"),
) -> None:
    """Create a new CSV file with the correct headers."""
    try:
        csv_path = Path(csv)
        
        # Ensure directory exists
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create CSV with headers
        if sample:
            # Add sample data
            sample_data = [
                {
                    "id": "sample1",
                    "title": "Sample Book 1",
                    "url": "",
                    "F": 3,
                    "R": 2,
                    "A": 1,
                    "V": 4,
                    "S": 2,
                    "P": 4,
                    "decision": "unknown"
                },
                {
                    "id": "sample2", 
                    "title": "Sample Book 2",
                    "url": "",
                    "F": 1,
                    "R": 4,
                    "A": 3,
                    "V": 2,
                    "S": 5,
                    "P": 2,
                    "decision": "unknown"
                }
            ]
            df = pd.DataFrame(sample_data)
        else:
            # Create empty DataFrame with headers
            df = pd.DataFrame({
                "id": [],
                "title": [],
                "url": [],
                "F": [],
                "R": [],
                "A": [],
                "V": [],
                "S": [],
                "P": [],
                "decision": []
            })
        
        df.to_csv(csv_path, index=False)
        logger.info(f"Created CSV file: {csv_path}")
        
        if sample:
            logger.info("Added sample data to CSV")
        
    except Exception as e:
        logger.error(f"Error creating CSV: {e}")
        sys.exit(1)


@cli.command()
def info(
    csv: Path = typer.Argument(..., help="Path to CSV file"),
) -> None:
    """Show information about the CSV file."""
    try:
        csv_path = Path(csv)
        
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            sys.exit(1)
        
        # Load and analyze CSV
        book_triage = BookTriage(csv_path)
        records = book_triage.get_records()
        
        logger.info(f"CSV file: {csv_path}")
        logger.info(f"Total records: {len(records)}")
        
        if records:
            # Count decisions
            decisions = {}
            missing_fields = {
                "url": 0,
                "F": 0,
                "R": 0,
                "A": 0,
                "V": 0,
                "S": 0,
                "P": 0
            }
            
            for record in records:
                # Count decisions
                decision = record.decision.value
                decisions[decision] = decisions.get(decision, 0) + 1
                
                # Count missing fields
                if not record.url:
                    missing_fields["url"] += 1
                if record.F is None:
                    missing_fields["F"] += 1
                if record.R is None:
                    missing_fields["R"] += 1
                if record.A is None:
                    missing_fields["A"] += 1
                if record.V is None:
                    missing_fields["V"] += 1
                if record.S is None:
                    missing_fields["S"] += 1
                if record.P is None:
                    missing_fields["P"] += 1
            
            logger.info("Decision distribution:")
            for decision, count in decisions.items():
                logger.info(f"  {decision}: {count} books")
            
            logger.info("Missing fields:")
            for field, count in missing_fields.items():
                if count > 0:
                    logger.info(f"  {field}: {count} books")
        
    except Exception as e:
        logger.error(f"Error analyzing CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli() 