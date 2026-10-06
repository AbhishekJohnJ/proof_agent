# Changelog — ProofAI

All notable changes to the ProofAI project will be documented in this file.

## [0.1.0] - 2026-10-06

### Initial Release — Model-Independent Foundation

#### Added
- **Backend Architecture**: FastAPI backend structure with modular routing (`health`, `upload`, `datasets`, `documents`, `analysis`).
- **Ingestion Engine**: Unified file ingestion supporting CSV, XLSX, and JSON files with metadata extraction and error handling.
- **Data Profiling & Quality Engine**: Deterministic dataset profiler detecting row/col counts, data types, missing values, duplicates, mixed currencies/units, ambiguous dates, and schema anomalies.
- **Relationship Detector**: Heuristic candidate primary/foreign key relationship inference across datasets.
- **Document Engine**: Text extractor for PDF, TXT, and DOCX files with page-level metadata and chunking.
- **Provider Abstractions**: `LLMProvider`, `EmbeddingProvider`, `CodeGenerationProvider`, and `AgentProvider` interfaces with explicit development mocks (`MockLLMProvider`, `MockCodeGenerationProvider`, `MockEmbeddingProvider`).
- **Execution Sandbox Foundation**: Static code validator for blocking unsafe Python operations (`os.system`, `subprocess`, `eval`, network calls) and sandbox runner abstractions.
- **Verification Engine**: Verification contracts and logic for execution success, reproducibility, data quality compliance, and ground-truth matching.
- **Data Contracts**: Pydantic models for `DatasetProfile`, `DocumentChunk`, `AnalysisRequest`, `AnalysisPlan`, `AnalysisResult`, `VerificationResult`, `EvidenceItem`, and `RefusalResponse`.
- **Frontend Foundation**: Next.js / React / TypeScript / Tailwind CSS UI components (`FileUpload`, `DatasetProfile`, `QueryInput`, `AnalysisResult`, `CodeViewer`, `EvidenceViewer`, `VerificationBadge`, `DataQuality`).
- **Sample Datasets & Documents**: `customers.csv`, `orders.csv`, `sales.csv`, `messy_sales.csv`, `annual_report.txt`, `policy.txt`.
- **Test Suite**: Pytest test suite covering ingestion, profiling, quality checks, relationship detection, document extraction, provider mocks, code validation, and API routes.
