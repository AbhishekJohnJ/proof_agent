# ProofAI — Core System Architecture

```text
                    USER / UI
                        │
                        ▼
            POST /dataset/upload
                        │
                        ▼
            SHA-256 CONTENT FINGERPRINT
                        │
            ┌───────────┴───────────┐
            │                       │
     [New Content]          [Duplicate Content]
            │                       │
            ▼                       ▼
    DATASET REGISTRY       REUSE PROFILE & ARTIFACT
            │                       │
            └───────────┬───────────┘
                        │
                        ▼
                POST /analysis
                        │
                        ▼
             QWEN3 ANALYSIS PLANNER
           (Produces AnalysisContract)
                        │
                        ▼
          DETERMINISTIC VALIDATION GATE
           (Columns, Datasets, Types)
                        │
                 valid? │
                 ┌──────┴──────┐
                 │             │
                NO            YES
                 │             │
                 ▼             ▼
              REFUSED     DEEPSEEK CODE GENERATOR
                           (Sandboxed Pandas Python)
                               │
                               ▼
                       SECURE SANDBOX EXECUTION
                     (No Network, No Subprocess)
                               │
                               ▼
                        RUNTIME EVIDENCE
                 (Exact Column Access Log)
                               │
                               ├──────────────┐
                               │              │
                               ▼              ▼
                        SANDBOX RESULT  REFERENCE ENGINE
                               │              │
                               └──────┬───────┘
                                      ▼
                               RESULT COMPARATOR
                          (Exact Numerical Tolerance)
                                      │
                                      ▼
                                PROOF POLICY
                         (VERIFIED / REFUSED / FAILED)
```

## System Guarantees
1. **Deterministic Verification Invariant**: Models propose analysis scripts and query plans, but ProofPolicy, ReferenceEngine, Sandbox, and OperationVerifier remain 100% authoritative over truth status.
2. **Arbitrary CSV Generalization**: Operates on any user-uploaded CSV without dataset or column hardcoding.
3. **No Mocks in Production**: Production explicitly communicates with local Ollama (`qwen3:8b` and `deepseek-coder-v2:16b-lite-instruct-q4_K_M`) and throws clean errors when unreachable.
