# ProofAI — Model Integration Guide for Teammates (GPU Team)

This guide instructs teammates on how to plug in Qwen3, DeepSeek-Coder, and embedding models.

## Integration Steps

1. Install PyTorch / HuggingFace Transformers / vLLM / Ollama on GPU machine.
2. Implement concrete classes in `backend/providers/`:
   - `Qwen3LLMProvider(LLMProvider)`
   - `DeepSeekCodeProvider(CodeGenerationProvider)`
   - `QwenEmbeddingProvider(EmbeddingProvider)`
3. Update `.env` settings:
   ```env
   LLM_PROVIDER=qwen
   CODE_GEN_PROVIDER=deepseek
   EMBEDDING_PROVIDER=qwen_embed
   ```
4. Verify exact licenses and model versions before final hackathon submission.
