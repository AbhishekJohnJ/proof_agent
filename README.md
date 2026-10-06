# ProofAI — Proof-Carrying Data Analyst

> **Tagline**: *"An AI Data Analyst That Proves Its Answers."*  
> **HackNex 2026 Problem Statement**: `HNX26PSI08 — Agentic GenAI · Data Analytics · Code Generation · Verification`

---

## 1. Core Philosophy

> **LLM proposes → Code computes → Verifier proves**

ProofAI is **NOT** a standard chatbot. The LLM is **NEVER** the source of truth for numerical calculations.

- **The LLM** plans analytical queries and proposes Python code.
- **Deterministic Python Execution** computes the actual numerical result in an isolated sandbox.
- **The Verification Layer** proves that the code executed cleanly, used correct datasets, handled data quality traps, and produced a reproducible output.

Every numerical answer returned by ProofAI is backed by **re-runnable, executable code**. If code fails to execute or produces a different result on re-run, the answer is rejected.

---

## 2. Model-Independent Development Status

> [!NOTE]
> This repository houses the **model-independent foundation** of ProofAI. It runs locally without requiring GPUs, external API keys, or heavy LLM weight downloads.
> 
> Provider abstractions (`LLMProvider`, `CodeGenerationProvider`, `EmbeddingProvider`) allow our GPU team members to seamlessly plug in **Qwen3** and **DeepSeek-Coder-V2-Lite** without refactoring the application.

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic, Pandas, NumPy, PyMuPDF, Uvicorn, Pytest
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS
- **Container Infrastructure**: Docker, Docker Compose, Isolated Process Sandbox
- **Model Interfaces**: Pluggable interfaces for Qwen3, DeepSeek-Coder, and Qwen-Embedding

---

## 4. Key Features

1. **Deterministic Data Profiling**: Automatic row/column counting, data type inference, unique value counts, and missing ratio detection without LLM calls.
2. **Data Quality Engine**: Automated detection of duplicate rows, duplicate candidate keys, mixed currencies (`$`, `€`, `USD`, `JPY`), ambiguous dates (`01/02/2024`), constant columns, and schema anomalies.
3. **Multi-Table Relational Inference**: Heuristic detection of primary/foreign key relationships across datasets (`customers.csv` ↔ `orders.csv`).
4. **Document Analysis**: Text extraction and overlapping chunking for PDFs, TXT, and DOCX files with page number tracking.
5. **Static Code Security Validation**: AST inspection blocking dangerous operations (`os.system`, `subprocess`, `eval`, `exec`, network calls, destructive file operations).
6. **Verification Engine**: Result validation, re-execution reproducibility testing, evidence accumulation, and confidence scoring.
7. **Justified Refusal Engine**: Returns structured refusals on missing data, ambiguous queries, or contradictory sources rather than hallucinating wrong answers.

---

## 5. Repository Structure

```
proof-ai/
├── backend/
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Application configuration & Pydantic settings
│   ├── logging_config.py      # Structured logging setup
│   ├── api/                   # REST API routes (health, upload, datasets, documents, analysis)
│   ├── models/                # Pydantic data contracts (dataset, query, analysis, verification, evidence)
│   ├── ingestion/             # File loaders for CSV, XLSX, JSON & unified FileManager
│   ├── profiling/             # Profiler, SchemaExtractor, QualityEngine, RelationshipDetector
│   ├── documents/             # Extractor (PDF/TXT/DOCX), DocumentChunker, MetadataExtractor
│   ├── agents/                # QueryPlanner, DataAnalystAgent, DocumentAgent, AnalysisOrchestrator
│   ├── providers/             # Pluggable LLM, Embedding, CodeGen interfaces & Mocks
│   ├── rag/                   # SimpleVectorStore, EmbeddingService, DocumentRetriever
│   ├── codegen/               # CodeGeneratorService, StaticCodeValidator, Prompt templates
│   ├── execution/             # SandboxExecutionEnvironment, LocalCodeRunner, Limits
│   ├── verification/          # ResultChecker, ReproducibilityVerifier, EvidenceAccumulator, ConfidenceCalculator
│   └── services/              # StorageService abstraction
├── frontend/                  # Next.js / TypeScript / Tailwind CSS UI Foundation
│   └── src/
│       ├── components/        # FileUpload, DatasetProfile, QueryInput, AnalysisResult, CodeViewer, EvidenceViewer, VerificationBadge, DataQuality
│       ├── services/          # API client calling FastAPI endpoints
│       └── types/             # TypeScript data contract definitions
├── datasets/sample/           # Synthetic sample datasets (customers.csv, orders.csv, sales.csv, messy_sales.csv)
├── documents/sample/          # Sample documents (annual_report.txt, policy.txt)
├── tests/                     # Pytest suite covering all modules & API endpoints
├── docs/                      # Architectural, security, API, and testing documentation
├── docker/                    # Dockerfiles for backend and execution sandbox
├── scripts/                   # Dev setup and test runner scripts
├── .github/workflows/ci.yml   # CI pipeline configuration
├── docker-compose.yml         # Container orchestration manifest
├── requirements.txt           # Python dependency specifications
└── README.md
```

---

## 6. Quick Start & Execution

### Prerequisites
- Python 3.11+
- Node.js 20+

### Option A: Running Locally

1. **Set Up Python Virtual Environment & Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Backend API Server**:
   ```bash
   source .venv/bin/activate
   PYTHONPATH=. uvicorn backend.main:app --reload --port 8000
   ```
   * Interactive API documentation will be available at: `http://127.0.0.1:8000/docs`

3. **Run Frontend Application**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   * Open UI in browser at: `http://localhost:3000`

### Option B: Running Tests

To run the complete test suite (24 tests):
```bash
source .venv/bin/activate
PYTHONPATH=. pytest tests/
```

Or execute the test runner script:
```bash
./scripts/run_tests.sh
```

---

## 7. Sample Data & Demonstration

ProofAI includes synthetic messy datasets designed to test data quality checks:

- `datasets/sample/messy_sales.csv`: Contains duplicate transaction rows, missing revenue cells, ambiguous date formats (`01/02/2024`), mixed currency notations (`$1500`, `€850`, `2200 USD`, `JPY 15000`), and constant columns (`company_name`).
- Upload `messy_sales.csv` via the UI to view the **Data Quality Engine** warnings.

---

## 8. Planned AI Model Declarations (Phase 6)

| Role | Model | Provider / Source | Integration Point |
|---|---|---|---|
| Reasoning & Orchestration | `Qwen3-4B-Instruct` | Qwen / HuggingFace | `LLMProvider` |
| Code Generation | `DeepSeek-Coder-V2-Lite` | DeepSeek AI | `CodeGenerationProvider` |
| Document Embeddings | `Qwen3-Embedding-0.6B` | Qwen / HuggingFace | `EmbeddingProvider` |

See [MODELS.md](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/MODELS.md) for complete details.

---

## 9. Security Controls

AI-generated code is treated as **untrusted input**. ProofAI enforces:
- AST-level static validation blocking dangerous calls (`os.system`, `subprocess`, `eval`, `exec`, `requests`, network/socket calls).
- Subprocess execution with strict 10-second timeout and resource limits.
- Container isolation with network disabling in production.

See [docs/security.md](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/docs/security.md) for full security specs.