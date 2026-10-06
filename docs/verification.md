# ProofAI — Verification & Proof Engine Guide

This document details the verification process ensuring every answer is proof-backed and reproducible.

## Verification Pipeline Steps

1. **Static Validation**: Code must pass AST analysis (`StaticCodeValidator`).
2. **Sandbox Execution**: Code runs in isolated environment (`LocalIsolatedSandbox`).
3. **Output Format Check**: `ResultChecker` verifies JSON output format and non-null result value.
4. **Reproducibility Test**: `ReproducibilityVerifier` re-executes code to verify identical stdout output.
5. **Confidence Scoring**: `ConfidenceCalculator` computes deterministic score based on verification status and dataset quality warnings.
