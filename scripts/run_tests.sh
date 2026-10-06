#!/bin/bash
set -e

echo "=== Running ProofAI Backend Tests ==="
source .venv/bin/activate
PYTHONPATH=. pytest tests/

echo "=== Running Frontend Build Check ==="
cd frontend
npm run build
cd ..

echo "=== All Checks Passed Successfully! ==="
