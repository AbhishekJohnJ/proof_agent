# ProofAI — API Endpoints Specification

FastAPI automatic interactive OpenAPI documentation is available at `/docs` when running the backend.

## Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Service health status and provider configuration |
| POST | `/api/upload` | Upload CSV, XLSX, JSON, PDF, TXT, DOCX |
| GET | `/api/datasets` | List uploaded datasets |
| GET | `/api/datasets/{dataset_id}` | Get dataset metadata |
| GET | `/api/datasets/{dataset_id}/profile` | Get dataset profile & quality report |
| GET | `/api/datasets/relationships` | Get candidate foreign key relationships |
| GET | `/api/documents` | List uploaded documents |
| GET | `/api/documents/{document_id}` | Get document metadata |
| POST | `/api/analysis/query` | Submit analytical question |
| GET | `/api/analysis/{analysis_id}` | Retrieve analysis result |
| GET | `/api/analysis/{analysis_id}/verification` | Retrieve verification proof |
| GET | `/api/analysis/{analysis_id}/evidence` | Retrieve evidence collection |
