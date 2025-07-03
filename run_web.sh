#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p document_agent/static

# Start the FastAPI server
uvicorn document_agent.app.api.app:app --reload --host 0.0.0.0 --port 8000
