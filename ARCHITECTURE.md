# ProofAI — Architecture Specification

"An AI Data Analyst That Proves Its Answers."

---

## Core Philosophy

> **LLM proposes → Code computes → Verifier proves**

ProofAI is **NOT** a standard chatbot. The LLM is **NEVER** the source of truth for numerical calculations. Instead:
1. The **LLM** plans the query and generates deterministic Python code.
2. The **Python Execution Engine** computes the actual numerical result in a isolated environment.
3. The **Verification Engine** independently verifies that code executed cleanly, used correct datasets, handled data quality traps, and produced a reproducible output.

---

## System Architecture Diagram

```
User Query + Files (CSV, XLSX, JSON, PDF, TXT)
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                 ProofAI API / Frontend                  │
└──────────────────────────┬──────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│     Data Ingestion        │ │    Document Extractor     │
│   CSV / XLSX / JSON       │ │     PDF / TXT / DOCX      │
└────────────┬──────────────┘ └─────────────┬─────────────┘
             │                              │
             ▼                              ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│  Profiling & Quality      │ │     Document Chunker      │
│  - Duplicates / Missing   │ │  - Metadata & Page Refs   │
│  - Mixed Currency / Dates │ │  - Vector Index           │
│  - Foreign Key Inference  │ │                           │
└────────────┬──────────────┘ └─────────────┬─────────────┘
             │                              │
             └──────────────┬───────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Query Planner                        │
│ - Evaluates query feasibility                           │
│ - Detects unanswerable / ambiguous / trap questions     │
│ - Generates AnalysisPlan & Evidence Requirements        │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│             Code Generator (DeepSeek-Coder)             │
│ Generates self-contained Pandas/NumPy execution script  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│               Static Security Validator                 │
│ Rejects dangerous calls (os.system, network, eval, etc) │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│            Execution Sandbox (Docker / Isolated)        │
│ Executes Python script & captures stdout / result JSON  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Verification Engine                   │
│ - Verifies code execution & reproducibility             │
│ - Checks schema adherence & filter integrity            │
│ - Matches final answer to stdout execution result       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 Proof-Carrying Result                   │
│  Answer + Re-runnable Code + Verification + Evidence     │
└─────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Ingestion & Profiling Engine ([backend/ingestion/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/ingestion/), [backend/profiling/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/profiling/))
Deterministic loading and profiling of structured tabular datasets and unstructured documents. Detects missing values, duplicate rows, currency mismatches, ambiguous date formats, and candidate primary/foreign key relationships.

### 2. Provider Abstraction Layer ([backend/providers/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/providers/))
Loose coupling between agent logic and AI models. Allows development and testing to run seamlessly using `MockLLMProvider`, `MockCodeGenerationProvider`, and `MockEmbeddingProvider` on local machines (e.g. Mac), while enabling plug-and-play integration for Qwen3 and DeepSeek on GPU nodes.

### 3. Execution Sandbox ([backend/execution/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/execution/))
Isolated Python execution runner enforcing static code validation, strict CPU/memory limits, execution timeouts, and network isolation.

### 4. Verification Engine ([backend/verification/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/verification/))
Proves answer correctness through Phase 4 multi-stage verification (V1–V13):
- **AST Contract Checking (`StaticContractChecker`)**: Statically inspects generated Python AST against the authoritative `AnalysisContract` to ensure required datasets, columns, join operations (`pd.merge`), aggregations (`sum`, `mean`), group-bys (`groupby`), and filters are explicitly present.
- **Runtime Dataset Access Tracking**: Monitored file access hooks in execution sandboxes record `accessed_dataset_ids`. Unselected table access triggers `VERIFICATION_FAILED`.
- **Independent Reference Engine (`ReferenceEngine`)**: Non-circular, host-side pandas calculation layer that calculates independent reference answers from raw table files to validate generated code outputs.
- **Multi-Table Join & Explosion Validation (`JoinChecker`)**: Validates join key presence and detects dangerous join cardinality explosions (>2.5x row count expansion).
- **Canonical Answer Consistency**: Ensures primary numerical claims in synthesized text match canonical verified results.
- **Reproducibility Testing (`ReproducibilityVerifier`)**: Re-runs code in isolated sandbox to verify identical numeric output.

### 5. ML Return Model Status Separation ([backend/ml/](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/ml/))
CatBoost ML return-risk predictions are strictly separated from deterministic historical analyses. Prediction queries output status `MODEL_PREDICTION` with model specifications, ROC-AUC metrics, and clear disclaimers, avoiding false claims of verified historical fact.

### 6. Refusal Engine ([backend/analysis/feasibility.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/analysis/feasibility.py))
Preflight feasibility engine detects missing required metrics (e.g., net profit on sales tables lacking profit data), ambiguous columns, or contradictory sources, returning structured refusals rather than hallucinating answers.
