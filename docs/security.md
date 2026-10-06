# ProofAI — Security Architecture

This document describes the security controls protecting execution environments from untrusted AI-generated code.

## Defense in Depth

1. **Static Validation Layer**: `StaticCodeValidator` inspects Python AST to reject dangerous imports (`os`, `subprocess`, `sys`, `socket`, `requests`, `shutil`) and dangerous calls (`eval`, `exec`, `__import__`, `open`).
2. **Process Isolation**: Execution runs in separate process/container with non-root permissions and execution timeout (10 seconds default).
3. **Container Sandbox**: Production deployment runs code inside isolated Docker container with `network_mode: none` and memory limits (512MB).
