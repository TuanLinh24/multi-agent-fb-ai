#!/usr/bin/env python
"""Test script for data ingestion pipeline"""

import os
import sys

# Set PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rag.ingest import DataIngestionPipeline

if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    pipeline.run_all()
