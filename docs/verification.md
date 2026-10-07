# ProofAI — Verification & Proof Engine Guide (Phase 4 Specification)

ProofAI does **NOT** trust AI-generated code merely because it executes, outputs JSON, or is reproducible. It enforces a strict proof-carrying protocol against an authoritative `AnalysisContract`.

---

## The Proof-Carrying Core Cycle

```
  LLM proposes
       ↓
 Analysis Contract
       ↓
  Code computes
       ↓
 Sandbox executes
       ↓
 Verifier independently checks
       ↓
  Evidence explains
       ↓
  Answer is released
```

---

## Verification Pipeline Checks (V1 – V13)

| Check | Name | Description | Engine / Checker |
|-------|------|-------------|-------------------|
| **V1** | `v1_code_executed` | Code compiled and ran without process errors or AST security violations. | Sandbox / CodeValidator |
| **V2** | `v2_output_exists` | Code generated valid non-empty stdout output. | ResultChecker |
| **V3** | `v3_output_valid_canonical` | Output contains valid JSON with a non-null primary result field. | ResultChecker |
| **V4** | `v4_result_type_matched` | Output type matches contract expected result type (number, string, table, etc.). | ResultChecker |
| **V5** | `v5_result_finite_valid` | Numerical values are finite (not NaN, null, or Infinity). | ResultChecker |
| **V6** | `v6_reproducible` | Independent re-execution in isolated sandbox produces bitwise / numerical exact match. | ReproducibilityVerifier |
| **V7** | `v7_required_datasets_used` | All resolved dataset IDs are statically referenced in AST AND no unselected datasets were accessed at runtime. | StaticContractChecker + Sandbox Tracer |
| **V8** | `v8_required_columns_used` | All columns specified in contract are present in AST. | StaticContractChecker |
| **V9** | `v9_expected_operation_reflected` | Required joins (`pd.merge`), aggregations (`sum`, `mean`), group_by (`groupby`), and filters exist in code AST. | StaticContractChecker |
| **V10** | `v10_final_answer_consistent` | Synthesized answer text numerical claims match canonical verified result. | AnswerValidator |
| **V11** | `v11_unit_matched` | Currency/unit in canonical result matches dataset schema metadata unit (`INR`, `percent`, `count`). | Contract / ResultChecker |
| **V12** | `v12_quality_requirements_satisfied` | No critical data quality issues or join cardinality explosions (>2.5x expansion). | JoinChecker / QualityEngine |
| **V13** | `v13_evidence_sources_matched` | Line-level evidence items trace back to executed code & loaded dataset tables. | EvidenceAccumulator |

---

## Independent Reference Engine

ProofAI uses a separate deterministic calculation path (`ReferenceEngine`) that executes independently from the generated code:
1. Loads host tables directly.
2. Validates contract parameters.
3. Computes reference result using standard deterministic pandas primitives.
4. Compares generated result vs reference result. If mismatch occurs, status becomes `VERIFICATION_FAILED`.

---

## Semantic Statuses

- `VERIFIED`: Deterministic analysis passed all V1–V13 checks and matched reference calculation.
- `MODEL_PREDICTION`: Output produced by CatBoost ML return prediction model (clearly labeled as prediction, not fact).
- `REFUSED`: Query requested unavailable metrics (e.g. net profit from orders table) or violated dataset constraints.
- `VERIFICATION_FAILED`: Code executed but violated AnalysisContract, used unselected dataset, or produced mismatching results.
