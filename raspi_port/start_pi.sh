#!/bin/bash
echo "Starting Raksha Pi Backend API..."

# Activate virtual environment
source venv/bin/activate

# Run the FastAPI server on port 8000, accessible on all interfaces
python3 raspi_api.py
