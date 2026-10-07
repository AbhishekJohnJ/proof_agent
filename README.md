# ProofAI — Contract-Driven Proof Engine & PSI08 Real Benchmark

> **Tagline**: *"An AI Data Analyst That Proves Its Answers."*  
> **HackNex 2026 Problem Statement**: `HNX26PSI08 — Agentic GenAI · Data Analytics · Code Generation · Proof Verification`

---

## 1. Core Architecture & Philosophy

> **LLM proposes → AnalysisContract defines → Code computes → Independent Verifier checks → Proof Trace proves**

ProofAI is **NOT** a standard chatbot or text-generator. The LLM is **NEVER** the source of truth for numerical calculations.

- **LLM Proposes**: Proposes an analytical query plan.
- **AnalysisContract**: Explicitly defines datasets, required columns, exact joins, filters, group-bys, aggregations, sorting, limit, result types, and monetary/percentage units (`INR`, `percent`, `count`).
- **ContractCodeGenerator**: Generates Pandas Python script strictly driven by the `AnalysisContract`.
- **Sandbox Execution**: Executes code under least-privilege isolation mounting ONLY contract-authorized datasets.
- **Independent ReferenceEngine**: Evaluates `AnalysisContract` on host pandas DataFrames without parsing natural language text.
- **Proof Trace**: Provides real, un-fabricated execution evidence and timing metrics (`execution_ms`, `reference_ms`, `verification_ms`, `total_ms`).

---

## 2. Production Real Local Model Integration (Phase 10)

- **Production Default (Real LLM Inference)**: Uses local **Ollama** serving **Qwen3** (Planning) and **DeepSeek-Coder** (Code Generation).
  - Configured via environment: `LLM_PROVIDER=ollama`, `CODE_GEN_PROVIDER=ollama`
  - Automatic platform-aware discovery detects Ollama binary, service endpoint (`http://localhost:11434`), and installed model tags without hardcoded paths.
  - Setup guide available at [docs/local-model-setup.md](file:///c:/Users/Viviyanpeter/proof_agent/docs/local-model-setup.md).
- **Deterministic Testing Mode**: Uses mock providers (`LLM_PROVIDER=mock`, `CODE_GEN_PROVIDER=mock`) for CI, unit testing, and fast regression checks without GPU requirements.
- **Sandbox Security Boundary**: Process-isolated sandbox enforcing read-only least-privilege dataset mounting and static code validation.

---

## 2. Strong Phase 5 Verification Invariant

AN ANSWER MAY BE MARKED **VERIFIED** ONLY IF:

1. The question is answerable.
2. The resolved datasets are correct and authorized.
3. The `AnalysisContract` explicitly describes the computation.
4. Generated code follows that contract.
5. Only authorized datasets are accessible.
6. Required columns are actually accessed at runtime.
7. Required joins match contracted joins.
8. Required filters are actually applied.
9. Required group-bys are actually applied.
10. Required aggregations are actually applied.
11. Result type matches the contract.
12. Result unit matches the contract with provenance (`UnitSource`).
13. Generated result matches independent deterministic reference calculation (`ReferenceEngine`).
14. A second execution reproduces the exact same result (`ReproducibilityVerifier`).
15. Data quality requirements pass without critical join explosions or invalid values.
16. Final answer is deterministically rendered from canonical result.
17. Proof trace contains real execution evidence with measured timings.
18. No fabricated verification metadata exists.

---

## 3. Supported Result Statuses

- `VERIFIED`: Deterministic analytical answer passed all V1–V13 checks and matched host reference calculation.
- `VERIFICATION_FAILED`: Code or execution violated contract, accessed unauthorized data, or produced mismatching numbers.
- `REFUSED`: Question is unanswerable (e.g., missing columns, unhedged mixed currency conversion, ambiguous dates).
- `MODEL_PREDICTION`: Predictive ML output from CatBoost classifier (clearly separated from historical facts).
- `DOCUMENT_SUPPORTED`: Pure document claim supported by document chunks when code reconstruction is inapplicable.

---

## 4. Commands to Run & Demonstrate

### Run Full Test Suite (81 Tests)
```bash
pytest -q
```

### Run Module-Specific Test Suites
```bash
# 1. Adversarial Verifier (A through T)
pytest -q tests/test_adversarial_verifier.py

# 2. End-to-End Hardening Pipeline
pytest -q tests/test_end_to_end_hardening.py

# 3. Kaggle Indian E-Commerce Benchmark
pytest -q tests/test_kaggle_integration.py

# 4. PSI08 Benchmark Manifest Suite
pytest -q tests/benchmark/test_psi08_benchmark.py
```

### Run Python Queries to Demonstrate Statuses

**Demonstrate VERIFIED Query**:
```bash
python -c '
from backend.models.query import AnalysisRequest
from backend.api.dependencies import get_orchestrator
from backend.data.catalog import dataset_catalog

ds = [d["dataset_id"] for d in dataset_catalog.list_datasets()]
orchestrator = get_orchestrator()
req = AnalysisRequest(question="What is the total revenue?", selected_datasets=ds)
res = orchestrator.process_analysis(req)
print("STATUS:", res.status)
print("CANONICAL RESULT:", res.canonical_result)
'
```

**Demonstrate REFUSED Query**:
```bash
python -c '
from backend.models.query import AnalysisRequest
from backend.api.dependencies import get_orchestrator
orchestrator = get_orchestrator()
req = AnalysisRequest(question="What is the net profit for Q3?", selected_datasets=["ds_kaggle_orders"])
res = orchestrator.process_analysis(req)
print("STATUS:", res.status)
print("REFUSAL REASON:", res.refusal_reason)
'
```

**Demonstrate VERIFICATION_FAILED Query**:
```bash
python -c '
from backend.models.query import AnalysisRequest
from backend.api.dependencies import get_orchestrator
orchestrator = get_orchestrator()

# Attempting to access unauthorized dataset or invalid code
req = AnalysisRequest(question="Calculate revenue using payments dataset without selecting it", selected_datasets=["ds_kaggle_orders"])
res = orchestrator.process_analysis(req)
print("STATUS:", res.status)
print("ERRORS:", res.verification.errors if res.verification else [])
'
```

**Demonstrate MODEL_PREDICTION Query**:
```bash
python -c '
from backend.models.query import AnalysisRequest
from backend.api.dependencies import get_orchestrator
orchestrator = get_orchestrator()
req = AnalysisRequest(question="Which orders are most likely to be returned?")
res = orchestrator.process_analysis(req)
print("STATUS:", res.status)
print("ANSWER:", res.answer)
'
```

---

## 5. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Pandas, NumPy, CatBoost ML, Pytest
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS
- **Sandbox**: Process-isolated sandbox enforcing least-privilege dataset mounting
- **Data Catalog**: 9 Indian E-Commerce Sales & Customer Analytics tables (1.2M rows)