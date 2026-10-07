import shutil
from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    docker_avail = shutil.which("docker") is not None
    return {
        "status": "healthy",
        "backend": "healthy",
        "provider": settings.LLM_PROVIDER,
        "code_generator": settings.CODE_GEN_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "model_providers": {
            "llm": settings.LLM_PROVIDER,
            "code_gen": settings.CODE_GEN_PROVIDER,
            "embedding": settings.EMBEDDING_PROVIDER,
        },
        "docker": "available" if docker_avail else "unavailable",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "mode": "demo_mock_frozen"
    }
