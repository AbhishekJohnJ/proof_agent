# ProofAI — Planned Model Architecture & Declaration

This document specifies the planned AI models to be integrated into ProofAI during Phase 6.

> [!IMPORTANT]
> The repository foundation is currently **model-independent**. The interfaces are designed so that the models below can be plugged in seamlessly without modifying core contracts.

---

## Model Declarations

### 1. Primary Reasoning & Orchestration Model
* **Model**: `Qwen3-4B-Instruct` (or `Qwen2.5-7B-Instruct`)
* **Provider / Source**: Qwen Team / Hugging Face
* **Role**:
  - High-level query planning (`AnalysisPlan` generation)
  - Decomposition of hybrid user questions (data vs document analysis)
  - Result synthesis & evidence presentation
  - Refusal reasoning on unanswerable/adversarial queries
* **License**: Apache 2.0 / Qwen License
* **Integration Interface**: [backend/providers/base.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/providers/base.py) -> `LLMProvider`
* **Status**: Planned (Mock implementation active for local mac development)

### 2. Code Generation Model
* **Model**: `DeepSeek-Coder-V2-Lite-Instruct`
* **Provider / Source**: DeepSeek AI / Hugging Face
* **Role**:
  - Deterministic Python analytical code generation
  - Multi-table Pandas filtering, joining, and aggregation code generation
  - Producing self-contained code blocks that print numerical answers to stdout
* **License**: DeepSeek License / Open Source
* **Integration Interface**: [backend/providers/base.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/providers/base.py) -> `CodeGenerationProvider`
* **Status**: Planned (Mock implementation active for local mac development)

### 3. Document Embedding Model
* **Model**: `Qwen3-Embedding-0.6B` (Alternative: `BAAI/bge-m3`)
* **Provider / Source**: Qwen Team / BAAI
* **Role**:
  - Vector embeddings for extracted document chunks (PDFs, text files, docx)
  - Dense retrieval for supporting document evidence
* **License**: Apache 2.0 / MIT
* **Integration Interface**: [backend/providers/base.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/providers/base.py) -> `EmbeddingProvider`
* **Status**: Planned (Mock implementation active for local mac development)

### 4. Order Return Risk Prediction Model (Implemented ML Capability)
* **Model**: `CatBoostClassifier`
* **Provider / Source**: CatBoost (Yandex)
* **Role**:
  - Predict probability of order return from pre-order / pre-return features
  - Identified high-risk return orders with probability ranking
  - Results strictly labeled as `MODEL PREDICTION` (probabilistic inference, distinct from verified historical facts)
* **Target Leakage Safeguards**:
  - Features defined in [backend/ml/features.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/ml/features.py)
  - Explicitly excludes `return_id`, `return_date`, `return_reason`, `return_status`, `refund_amount`, `actual_delivery_date`, `delivery_days`, `delivery_status`, `delayed_flag`
* **Artifact Locations**:
  - Model: `models/return_prediction_model.cbm`
  - Metadata: `models/return_prediction_metadata.json`
* **Retraining Command**:
  ```bash
  PYTHONPATH=. .venv/bin/python scripts/train_return_model.py
  ```
* **Status**: Implemented & Production-Ready

---

## Model Integration Guidelines for GPU Team

1. Implement concrete classes extending `LLMProvider`, `CodeGenerationProvider`, and `EmbeddingProvider` in `backend/providers/`.
2. Configure local model weights paths or Ollama/vLLM endpoints in `.env`.
3. Set `LLM_PROVIDER=qwen`, `CODE_GEN_PROVIDER=deepseek`, `EMBEDDING_PROVIDER=qwen_embed` in `.env`.
4. Ensure exact license verification before final hackathon submission.
