# ProofAI — Testing Guide (Phase 4 Specification)

This document outlines backend testing strategy, benchmark regression tests, and adversarial verifier test cases.

---

## Running Tests

All unit, benchmark, and adversarial verifier tests run locally without GPU or model downloads:

```bash
PYTHONPATH=. .venv/bin/pytest -q
```

---

## Test Coverage

* `tests/test_adversarial_verifier.py`: 11 adversarial cases (A–K) testing code execution failure, wrong numbers, unselected dataset access, missing columns, wrong aggregations, missing joins, join key errors, join explosions, wrong units, non-reproducible code, and answer mismatches.
* `tests/test_kaggle_integration.py`: 13 end-to-end integration tests on the Kaggle Indian E-Commerce dataset using exact benchmark ground truth.
* `tests/benchmark/test_psi08_benchmark.py`: Benchmark suite evaluating `benchmark_manifest.json` synthetic cases.
* `tests/test_validation.py`: AST security validator.
* `tests/test_execution.py`: Subprocess isolated sandbox.
* `tests/test_verification.py`: Output checking & reproducibility testing.
* `tests/test_end_to_end_hardening.py`: Hardening and edge case coverage.
* `tests/test_phase2_reliability.py`: Reliability tests.
