# ProofAI — Detailed Architecture Guide

This document details the software architecture, module interaction boundaries, and design patterns.

## Modular Component Design

* **Ingestion Layer** (`backend/ingestion/`): Decoupled file loaders (`CSVLoader`, `ExcelLoader`, `JSONLoader`) unified under `FileManager`.
* **Profiling Layer** (`backend/profiling/`): Deterministic `DataProfiler`, `QualityEngine`, `SchemaExtractor`, and `RelationshipDetector`.
* **Document Engine** (`backend/documents/`): Text extractor (`DocumentExtractor`), overlapping chunker (`DocumentChunker`), and metadata generator.
* **Provider Layer** (`backend/providers/`): Abstract interfaces (`LLMProvider`, `CodeGenerationProvider`, `EmbeddingProvider`) with development mocks (`MockLLMProvider`, `MockCodeGenerationProvider`, `MockEmbeddingProvider`).
* **Execution & Verification** (`backend/execution/`, `backend/verification/`): `StaticCodeValidator`, `LocalCodeRunner`, `ResultChecker`, `ReproducibilityVerifier`, `EvidenceAccumulator`, and `ConfidenceCalculator`.
