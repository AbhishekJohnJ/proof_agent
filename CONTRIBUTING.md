# Contributing to ProofAI

Thank you for contributing to **ProofAI**! This guide outlines the development workflow, coding standards, and testing procedures.

---

## Model-Independent Development Rule

> [!IMPORTANT]
> The initial foundation must run without GPU requirements, LLM downloads, or external API keys. All new features MUST work with mock providers (`MockLLMProvider`, `MockCodeGenerationProvider`, `MockEmbeddingProvider`).

---

## Development Workflow

1. **Environment Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

3. **Running Backend**:
   ```bash
   source .venv/bin/activate
   uvicorn backend.main:app --reload --port 8000
   ```

4. **Running Tests**:
   ```bash
   pytest tests/
   ```

---

## Code Quality Standards

* **Type Annotations**: All backend Python functions must include standard Python type hints.
* **Pydantic Validation**: API requests, dataset schemas, and result objects must use explicit Pydantic models.
* **No Fake AI Claims**: Do not write code that returns fake AI answers without explicitly marking them as `mock` or `not_configured`.
* **Security & Validation**: Ensure generated code undergoes static validation before execution.

---

## Folder Structure Guidelines

* `backend/api/routes/` for FastAPI endpoints.
* `backend/models/` for Pydantic data contracts.
* `backend/providers/` for model interfaces and mock implementations.
* `backend/verification/` for verification engine logic.
* `frontend/src/components/` for React components.
