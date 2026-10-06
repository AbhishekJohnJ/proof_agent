#!/bin/bash
set -e

echo "=== ProofAI Dev Environment Setup ==="

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "Installing Python requirements..."
source .venv/bin/activate
pip install -r requirements.txt

echo "Installing Frontend dependencies..."
cd frontend
npm install
cd ..

echo "=== Setup Complete! ==="
echo "Run backend: source .venv/bin/activate && uvicorn backend.main:app --reload --port 8000"
echo "Run frontend: cd frontend && npm run dev"
