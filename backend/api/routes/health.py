import shutil
from fastapi import APIRouter
from backend.config import settings
from backend.providers.factory import ProviderFactory

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    docker_avail = shutil.which("docker") is not None
    provider_status = ProviderFactory.get_health_status()
    
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
        "ollama_status": provider_status.get("ollama", {}),
        "planner_status": provider_status.get("planner", {}),
        "code_generator_status": provider_status.get("code_generator", {}),
        "docker": "available" if docker_avail else "unavailable",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "mode": "production_ollama" if settings.LLM_PROVIDER.lower() == "ollama" else "testing_mock"
    }

