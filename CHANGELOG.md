# Changelog — ProofAI

All notable changes to the ProofAI project will be documented in this file.

## [0.2.0] - 2026-10-06 — Phase 1.5 Functional Foundation Hardening

### Added
- **Dataset Artifact Abstraction**: Controlled workspace dataset paths (`data/<dataset_id>/data.csv`) preventing arbitrary filesystem access.
- **Strict Status Transitions**: `AnalysisStatus` enum (`RECEIVED`, `PLANNED`, `CODE_GENERATED`, `CODE_VALIDATED`, `EXECUTING`, `EXECUTION_FAILED`, `VERIFYING`, `VERIFIED`, `VERIFICATION_FAILED`, `REFUSED`, `MODEL_NOT_CONFIGURED`).
- **Explicit Verification States**: `CheckStatus` (`PASS`, `FAIL`, `NOT_CHECKED`, `NOT_APPLICABLE`) for all verification checks.
- **Data Quality Verification**: `quality_check_performed`, `quality_issues_found`, `critical_quality_issues` fields replacing primitive count check.
- **Provider Factory**: `ProviderFactory` supporting `mock` and unconfigured model stubs (`UnconfiguredLLMProvider`, `UnconfiguredCodeGenerationProvider`).
- **Hardened Upload Security**: `SafeUploadHandler` providing filename sanitization, server-side UUID IDs, path traversal prevention, size enforcement (50MB cap), and `.doc` rejection.
- **SQLite Persistence**: `SQLitePersistenceManager` storing dataset metadata, profiles, document metadata, chunks, and analysis runs across backend restarts.
- **RAG & Vector Store Integration**: Server-side document chunk vector indexing and retrieval via `SimpleVectorStore` and `DocumentRetriever`.
- **Hardened Docker Sandbox**: `DockerSandbox` support with network disabled, memory limits, and non-root execution.
- **AST Security Allowlist**: `StaticCodeValidator` enforcing import allowlisting (`pandas`, `numpy`, `json`, `math`, `datetime`, `re`, `statistics`).
- **Reproducibility Tolerance**: Numeric floating-point tolerance testing with diff calculation.
- **Frontend Multi-Selection & Verification Breakdown**: Multi-dataset/document selection, document metadata view, and detailed check status badge.
- **End-to-End Test Suite**: 36 unit and integration tests covering end-to-end hardened execution pipeline.

## [0.1.0] - 2026-10-06

### Initial Release — Model-Independent Foundation
- Initial architecture setup, ingestion loaders, data profiler, document extractor, and Next.js frontend UI foundation.
