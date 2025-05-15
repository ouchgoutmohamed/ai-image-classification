#!/bin/bash
# Setup script for running the image classifier in GitHub Codespaces

echo "Setting up Image Classifier API in GitHub Codespaces..."

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
  echo "Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Create needed directories if they don't exist
mkdir -p api/templates
mkdir -p api/static

# Run the FastAPI application
echo "Starting the FastAPI server..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
