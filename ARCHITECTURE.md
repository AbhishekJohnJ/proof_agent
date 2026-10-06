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
Proves answer correctness through:
- Execution output validation
- Reproducibility checks (re-running code to ensure identical numeric output)
- Quality check verification (checking if filters correctly handled flagged data quality issues)
- Ground-truth matching between generated answer and code output

### 5. Refusal Engine ([backend/agents/planner.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/agents/planner.py))
Handles trap questions, missing data, mixed currencies, or unanswerable queries by issuing explicit, structured refusal responses rather than hallucinating an answer.
