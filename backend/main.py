from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.logging_config import logger
from backend.api.routes import (
    health_router,
    upload_router,
    datasets_router,
    documents_router,
    analysis_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="ProofAI — Model-Independent Foundation for Proof-Carrying Data Analysis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers (Both /api prefix and root level for UI compatibility)
app.include_router(health_router)
app.include_router(health_router, prefix="/api")

app.include_router(upload_router)
app.include_router(upload_router, prefix="/api")
app.include_router(upload_router, prefix="/dataset")

app.include_router(datasets_router)
app.include_router(datasets_router, prefix="/api")
app.include_router(datasets_router, prefix="/dataset")

app.include_router(documents_router)
app.include_router(documents_router, prefix="/api")

app.include_router(analysis_router)
app.include_router(analysis_router, prefix="/api")


@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.APP_NAME} Backend (Env: {settings.APP_ENV})")
    logger.info(f"Active LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Active CodeGen Provider: {settings.CODE_GEN_PROVIDER}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
