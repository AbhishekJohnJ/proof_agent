# ProofAI — Data Pipeline Guide

This document describes file ingestion, profiling, quality check rules, and relationship detection.

## Ingestion Pipeline
1. `FileManager.ingest_dataset(file_path)` detects file extension.
2. Calls `CSVLoader`, `ExcelLoader`, or `JSONLoader`.
3. Validates non-empty file content.
4. Returns Pandas DataFrame & `DatasetMetadata`.

## Quality Engine Rules
* **Missing values**: Aggregates total missing cells and calculates missing percentage.
* **Duplicate rows**: Full-row duplication check.
* **Mixed currencies**: Identifies inline symbols (`$`, `€`, `USD`, `JPY`) or multi-currency object columns.
* **Ambiguous dates**: Identifies date strings with unconfirmed day/month order (e.g., `01/02/2024`).
