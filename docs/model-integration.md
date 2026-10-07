# ProofAI — Production Model Integration Guide (Qwen3 + DeepSeek)

This document provides step-by-step instructions for plugging real LLM reasoning models (**Qwen3**) and code generation models (**DeepSeek-Coder**) into ProofAI when the production GPU environment is available.

---

## Architecture Principle

> **Models Propose — Deterministic Verification Decides**

```
+---------------------------------------------------------------------------------+
|                               MODEL LAYER (Proposes)                           |
|                                                                                 |
|   Qwen3 (Planner)                            DeepSeek-Coder (Code Generator)    |
|   - Inputs: Question, Catalog Schemas        - Inputs: AnalysisContract         |
|   - Outputs: AnalysisPlan + AnalysisContract - Outputs: Python Analytical Code  |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                        DETERMINISTIC PROOF LAYER (Decides)                      |
|                                                                                 |
|   1. ContractValidator  -> Strict pre-code-generation gate                      |
|   2. Sandbox            -> Local / Docker sandbox execution                    |
|   3. Runtime Audit      -> Dataset, Column, and Operation evidence recording    |
|   4. ReferenceEngine    -> Independent host-side pandas contract calculation   |
|   5. Reproducibility    -> Re-execution & exact canonical comparison            |
|   6. ProofPolicy        -> Authoritative status decision (VERIFIED / REFUSED /   |
|                            VERIFICATION_FAILED / MODEL_PREDICTION)              |
+---------------------------------------------------------------------------------+
```

---

## 1. Integrating Qwen3 (PlannerProvider)

### Step 1.1: Start Qwen3 Inference Server
Deploy Qwen3 using vLLM or Ollama:

```bash
# vLLM example
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3-14B-Instruct \
    --port 8000
```

### Step 1.2: Implement `Qwen3Adapter`
Create `backend/providers/qwen3.py`:

```python
import json
import requests
from typing import Dict, Any, List
from backend.providers.base import LLMProvider

class Qwen3Adapter(LLMProvider):
    def __init__(self, api_url: str = "http://localhost:8000/v1"):
        self.api_url = api_url

    def plan_query(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = f"""You are ProofAI Planner. Analyze question and return JSON format matching AnalysisContract.
Question: {question}
Dataset Schemas: {json.dumps(dataset_schemas)}
Document Summaries: {json.dumps(document_summaries)}
"""
        response = requests.post(
            f"{self.api_url}/chat/completions",
            json={
                "model": "Qwen/Qwen3-14B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

---

## 2. Integrating DeepSeek-Coder (CodeGenerationProvider)

### Step 2.1: Start DeepSeek Inference Server

```bash
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct \
    --port 8001
```

### Step 2.2: Implement `DeepSeekAdapter`
Create `backend/providers/deepseek.py`:

```python
import requests
from typing import Dict, Any, List
from backend.providers.base import CodeGenerationProvider

class DeepSeekAdapter(CodeGenerationProvider):
    def __init__(self, api_url: str = "http://localhost:8001/v1"):
        self.api_url = api_url

    def generate_code(self, question: str, dataset_schemas: List[Dict[str, Any]], quality_warnings: List[Dict[str, Any]], analysis_contract: Any = None) -> Dict[str, Any]:
        prompt = f"""Generate executable Python code using pandas for this AnalysisContract:
Contract: {analysis_contract.model_dump_json()}
Required: Print JSON matching {{ "result": <numeric/value>, "metric": "<name>", "unit": "<unit>" }}
"""
        response = requests.post(
            f"{self.api_url}/chat/completions",
            json={
                "model": "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0
            }
        )
        code = response.json()["choices"][0]["message"]["content"]
        return {"code": code, "language": "python"}
```

---

## 3. Registering Adapters in Factory

Update `backend/providers/factory.py`:

```python
if provider_name == "qwen3":
    return Qwen3Adapter()

if provider_name == "deepseek":
    return DeepSeekAdapter()
```

Update environment variables in `.env`:

```env
LLM_PROVIDER=qwen3
CODE_GEN_PROVIDER=deepseek
```

---

## 4. Verification & Testing

Run existing proof test suites to ensure zero regression:

```bash
# Fast unit & red-team tests
pytest -q -m "not slow"

# HNX26PSI08 Benchmark suite
pytest -q -m benchmark

# Full test suite
pytest -q
```

No changes are required in `ContractValidator`, `Sandbox`, `ReferenceEngine`, `ReproducibilityVerifier`, or `ProofPolicy` when real models are connected!
