# ProofAI — Testing Guide

This document outlines backend testing strategy and commands.

## Running Tests

All unit and integration tests run without requiring AI models or GPU downloads.

```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/
```

## Test Coverage
* `test_ingestion.py`: CSV, XLSX, JSON ingestion & error cases
* `test_profiling.py`: Row/column counting, data type inference
* `test_quality.py`: Detection of duplicates, missing values, mixed currencies, constant columns
* `test_relationships.py`: Candidate primary/foreign key join detection
* `test_documents.py`: Document extraction & chunking
* `test_providers.py`: Mock provider behavior
* `test_validation.py`: AST security validator
* `test_execution.py`: Subprocess code execution
* `test_verification.py`: Output checking & reproducibility testing
* `test_api.py`: FastAPI endpoint integration tests
