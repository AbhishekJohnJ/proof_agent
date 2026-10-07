# ProofAI Phase 10 — Local Model Setup & Verification Guide

This document provides complete operational guidelines for running **ProofAI (HNX26PSI08)** with **Real Local Model Inference** powered by **Ollama**, **Qwen3**, and **DeepSeek-Coder**.

---

## 1. Architecture Overview

ProofAI uses a strict proof-carrying architecture where local LLMs assist with natural-language reasoning, query planning, and Python pandas script generation, while the deterministic proof engine retains 100% authoritative control over data authorization, execution, evidence collection, and verification.

```
USER QUESTION
      ↓
Qwen3 (Local Ollama Planner)
      ↓
AnalysisContract (Validated Schema)
      ↓
DeepSeek (Local Ollama Code Generator)
      ↓
Generated Python Analysis Script
      ↓
Sandbox Execution Environment
      ↓
Runtime Evidence & Operation Verification
      ↓
Reference Engine (Independent Deterministic Verification)
      ↓
ProofPolicy (VERIFIED / REFUSED / VERIFICATION_FAILED)
      ↓
CanonicalResult & AnswerRenderer
```

---

## 2. Automatic Ollama Discovery

ProofAI automatically discovers local Ollama installations across Windows, macOS, and Linux without hardcoding filesystem paths.

Discovery checks:
1. `ollama` executable via `PATH` environment variable.
2. System installation paths:
   - **Windows:** `%LOCALAPPDATA%\Programs\Ollama\ollama.exe`, `C:\Program Files\Ollama\ollama.exe`
   - **macOS:** `/usr/local/bin/ollama`, `/opt/homebrew/bin/ollama`, `/Applications/Ollama.app/Contents/Resources/ollama`
   - **Linux:** `/usr/local/bin/ollama`, `/usr/bin/ollama`, `/bin/ollama`, `/snap/bin/ollama`
3. Ollama service version via `ollama --version`.
4. Ollama HTTP REST API connectivity (Default: `http://localhost:11434`).
5. Installed models via `/api/tags` or `ollama list`.

---

## 3. Environment Variables

Configure local model settings in `.env` or system environment:

```ini
# Default production providers
LLM_PROVIDER=ollama
CODE_GEN_PROVIDER=ollama

# Local Ollama endpoint
OLLAMA_BASE_URL=http://localhost:11434

# Optional explicit model overrides (leave blank for automatic discovery)
OLLAMA_PLANNER_MODEL=qwen3:8b
OLLAMA_CODE_MODEL=deepseek-coder-v2:16b-lite-instruct-q4_K_M

# Inference settings
OLLAMA_TIMEOUT=60
OLLAMA_TEMPERATURE=0.0
MAX_LLM_RETRIES=2
PROOFAI_DEBUG=false
```

---

## 4. Verification Commands

### A. Verify Ollama CLI & Models
```bash
# Check version
ollama --version

# List installed local models
ollama list
```

### B. Verify API Endpoint
```bash
# Check available tags
curl http://localhost:11434/api/tags
```

### C. Verify Model Inference via Python API
```python
from backend.providers.ollama.client import OllamaClient

client = OllamaClient()
print("Health:", client.health_check())
print("Qwen Inference:", client.verify_model_inference("qwen3:8b"))
print("DeepSeek Inference:", client.verify_model_inference("deepseek-coder-v2:16b-lite-instruct-q4_K_M"))
```

---

## 5. Running ProofAI

### Start Backend API Server
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Check System Health Endpoint
```bash
curl http://localhost:8000/api/health
```

Output:
```json
{
  "status": "healthy",
  "provider": "ollama",
  "code_generator": "ollama",
  "ollama_status": {
    "available": true,
    "base_url": "http://localhost:11434",
    "version": "0.40.0"
  },
  "planner_status": {
    "provider": "ollama",
    "model": "qwen3:8b",
    "available": true
  },
  "code_generator_status": {
    "provider": "ollama",
    "model": "deepseek-coder-v2:16b-lite-instruct-q4_K_M",
    "available": true
  },
  "mode": "production_ollama"
}
```

---

## 6. Testing Strategy

- **Production Mode:** Default uses real local Ollama models (`LLM_PROVIDER=ollama`).
- **Testing Mode:** Deterministic unit and CI tests use mock providers (`LLM_PROVIDER=mock`).
- **Integration Test:** Run real Ollama pipeline integration tests:
  ```bash
  python -m pytest tests/integration/test_real_ollama_pipeline.py -v
  ```

---

## 7. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Ollama service unreachable` | Ollama service is not running | Start Ollama (`ollama serve` or run background app). |
| `Model not found` | Selected tag not pulled | Run `ollama pull qwen3:8b` or update `OLLAMA_PLANNER_MODEL`. |
| `Timeout error` | CPU inference exceeded 60s | Increase `OLLAMA_TIMEOUT=120` in `.env`. |
| `Validation refusal` | Question asks for unavailable column | Expected behavior. Deterministic engine returns structured refusal. |
