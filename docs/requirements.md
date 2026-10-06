# ProofAI — Formal Requirements Specification

"An AI Data Analyst That Proves Its Answers."

---

## 1. Problem Statement & Mission

Modern AI analytics applications suffer from dangerous hallucination when performing numerical operations across messy, multi-table enterprise data. A confident wrong answer is worse than a justified refusal.

ProofAI addresses this challenge under HackNex 2026 Problem Statement **HNX26PSI08 — Proof-Carrying Data Analyst**.

### Mandatory Requirement
> **EVERY NUMERICAL ANSWER MUST HAVE RE-RUNNABLE EXECUTABLE CODE.**

Another party must be able to run the generated code independently and obtain the exact same numerical result. If generated code does not run or produces a different answer, the answer must NOT be considered valid.

---

## 2. Core Functional Requirements

1. **Deterministic Execution**: LLMs plan queries and propose code; Python execution computes results. The LLM is NEVER the ground truth for math.
2. **Data Profiling & Quality Engine**: Automatic detection of duplicate rows, missing values, ambiguous dates, constant columns, and mixed currencies.
3. **Multi-Table Relational Inference**: Foreign key heuristics to infer candidate joins across separate datasets.
4. **Supporting Document Integration**: PDF/TXT extraction with page-level metadata for evidence retrieval.
5. **Verification & Proof Engine**: Static code validation, execution status checking, output parsing, reproducibility testing, and confidence scoring.
6. **Refusal Engine**: Justified refusal on incomplete data, ambiguous dates, mixed currencies, or unanswerable queries.
