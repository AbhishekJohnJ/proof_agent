# ProofAI — Data Pipeline Guide (Phase 4 Specification)

This document describes file ingestion, profiling, quality check rules, relationship detection, dataset resolution, and multi-table join validation.

---

## Ingestion & Memory Caching Pipeline

1. `FileManager.ingest_dataset(file_path)` detects file extension.
2. In-memory DataFrame cache in `StorageService` prevents redundant disk reads and CSV parsing across test runs.
3. Profile metadata generated via `DataProfiler.profile()`.
4. Artifacts persisted to SQLite database.

---

## Dataset Resolution & Multi-Table Joins

- **Single Authoritative List (`resolved_dataset_ids`)**: Natural language queries resolve minimum required tables.
- **Join Key Validation (`JoinChecker`)**: Verifies key presence, null key counts, and detects suspicious join row count explosions (>2.5x expansion).
- **Return Rate Semantics**:
  - `order_return_rate`: `unique returned order IDs / total orders * 100.0`
  - `category_return_rate`: `returned items for category / total items for category * 100.0`

---

## Quality Engine & Traps

* **Missing values**: Aggregates total missing cells and calculates missing percentage.
* **Duplicate rows**: Full-row duplication check.
* **Mixed currencies**: Identifies inline symbols (`$`, `€`, `USD`, `JPY`) or multi-currency object columns.
* **Ambiguous dates**: Identifies date strings with unconfirmed day/month order (e.g., `01/02/2024`).
