from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "model_providers": {
            "llm": settings.LLM_PROVIDER,
            "code_gen": settings.CODE_GEN_PROVIDER,
            "embedding": settings.EMBEDDING_PROVIDER,
        },
        "mode": "model_independent_foundation"
    }
