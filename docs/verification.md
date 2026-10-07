# ProofAI — Contract-Driven Proof Engine Guide (Phase 5 Specification)

ProofAI does **NOT** trust AI-generated code merely because it executes, outputs JSON, or is reproducible. It enforces a strict proof-carrying protocol against an authoritative `AnalysisContract`.

---

## The Core Phase 5 Invariant

AN ANSWER MAY BE MARKED **VERIFIED** ONLY IF:

1. The question is answerable.
2. The resolved datasets are correct and authorized.
3. The `AnalysisContract` explicitly describes the computation.
4. Generated code follows that contract.
5. Only authorized datasets are accessible (least privilege).
6. Required columns are actually accessed at runtime.
7. Required joins are exactly the contracted joins.
8. Required filters are actually applied.
9. Required group-bys are actually applied.
10. Required aggregations are actually applied.
11. Result type matches the contract.
12. Result unit matches the contract and has provenance (`UnitSource`).
13. Generated result matches an independent deterministic reference calculation (`ReferenceEngine`).
14. A second execution reproduces the exact same result (`ReproducibilityVerifier`).
15. Data quality requirements pass without critical join explosions or invalid values.
16. Final natural-language answer is deterministically rendered from the canonical result.
17. Proof trace contains real execution evidence with measured timings (`execution_ms`, `reference_ms`, `verification_ms`, `total_ms`).
18. No fabricated verification metadata exists.

If any required condition fails:
- **NEVER** return `VERIFIED`.
- Return `VERIFICATION_FAILED` or `REFUSED` as appropriate.

---

## The Contract-Driven Flow

```
  LLM proposes
       ↓
  AnalysisContract (structured joins, filters, aggregations, group_by, sorting, limit)
       ↓
  ContractCodeGenerator (generates Pandas Python script strictly from contract)
       ↓
  LocalIsolatedSandbox (mounts ONLY authorized datasets - least privilege)
       ↓
  Runtime Audit + AST Verification (checks accessed columns & operations)
       ↓
  ReferenceEngine (evaluates contract independently on host without question parsing)
       ↓
  Reproducibility & Join Cardinality Check
       ↓
  ProofPolicy Evaluation
       ↓
  VERIFIED / REFUSED / VERIFICATION_FAILED / MODEL_PREDICTION / DOCUMENT_SUPPORTED
```

---

## Semantic Statuses

- `VERIFIED`: Deterministic analytical answer passed all V1–V13 checks, matched host reference calculation, and maintained dataset authorization.
- `VERIFICATION_FAILED`: Generated code or execution violated the contract, accessed unauthorized data, expanded join cardinality suspiciously, or produced mismatching numbers.
- `REFUSED`: Question is unanswerable (e.g. missing columns, unhedged mixed currency conversion, ambiguous dates) or sandbox is unavailable.
- `MODEL_PREDICTION`: Predictive ML output from CatBoost classifier (explicitly separated from historical facts).
- `DOCUMENT_SUPPORTED`: Pure document retrieval claim supported by document chunks when executable code reconstruction is not applicable.
