# ProofAI — CSV Data & Upload Contract Specification

## 1. Dataset Identity & Fingerprinting

ProofAI enforces strict, content-derived dataset identity:

- **Upload ID (`upload_id`)**: A unique string (`up_<uuid12>`) generated for every physical upload event.
- **Content SHA-256 (`raw_sha256`)**: SHA-256 cryptographic hash computed over the exact raw uploaded file bytes.
- **Dataset ID (`dataset_id`)**: A stable content-hash derived string (`ds_<sha256_12>`).

### Duplicate Handling Rules
1. **Identical Content Uploads**:
   - `upload_1 != upload_2`
   - `dataset_1 == dataset_2`
   - `raw_sha256_1 == raw_sha256_2`
   - API response flags `is_duplicate_content: true` and reuses existing dataset profile without creating duplicate logical registry records.
2. **Different Content, Same Filename**:
   - Filename does **NOT** determine dataset identity.
   - `sales.csv` (hash A) and `sales.csv` (hash B) receive `dataset_id A != dataset_id B`.

---

## 2. Ingestion & Schema Profiling Capabilities

- **Encodings**: Automated multi-encoding fallback (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`, `iso-8859-1`).
- **Delimiter Auto-Detection**: Supports `,`, `;`, `\t`, `|`.
- **Missing Value Handling**: Preserves original data while detecting standard missing representations (`NaN`, `NA`, `N/A`, `NULL`, `null`, `empty`, `#N/A`, `n/a`).
- **Column Normalization**: Preserves original column names (`Customer Name`, `Revenue ($)`) in dataset profiles and maps them to internal safe representations for execution.

---

## 3. UI API Integration Endpoints

### 1. Upload CSV Dataset
`POST /dataset/upload` or `POST /api/upload`
**Response**:
```json
{
  "type": "dataset",
  "upload_id": "up_a1b2c3d4e5f6",
  "dataset_id": "ds_9f8e7d6c5b4a",
  "filename": "custom_sales.csv",
  "is_duplicate_content": false,
  "raw_sha256": "9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e",
  "profile": {
    "rows": 1000,
    "columns": 5,
    "column_names": ["order_id", "product", "category", "revenue", "state"]
  }
}
```

### 2. Submit Analytical Query
`POST /analysis` or `POST /api/analysis/query`
**Request**:
```json
{
  "question": "What is the total revenue?",
  "selected_datasets": ["ds_9f8e7d6c5b4a"]
}
```
**Response**:
```json
{
  "analysis_id": "ans_123456789abc",
  "question": "What is the total revenue?",
  "status": "VERIFIED",
  "answer": "Total revenue is 1542000.5",
  "canonical_result": {
    "result": 1542000.5,
    "result_type": "scalar",
    "unit": null
  },
  "proof_trace": {
    "authorization": {
      "datasets_authorized": ["ds_9f8e7d6c5b4a"],
      "datasets_accessed": ["ds_9f8e7d6c5b4a"]
    },
    "model_provenance": {
      "planner": {"provider": "ollama", "model": "qwen3:8b"},
      "code_generator": {"provider": "ollama", "model": "deepseek-coder-v2:16b-lite-instruct-q4_K_M"}
    }
  }
}
```
