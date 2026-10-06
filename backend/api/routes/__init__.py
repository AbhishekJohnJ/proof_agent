from backend.api.routes.health import router as health_router
from backend.api.routes.upload import router as upload_router
from backend.api.routes.datasets import router as datasets_router
from backend.api.routes.documents import router as documents_router
from backend.api.routes.analysis import router as analysis_router

__all__ = [
    "health_router",
    "upload_router",
    "datasets_router",
    "documents_router",
    "analysis_router",
]
