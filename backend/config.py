import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "ProofAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Model Providers (mock | qwen | deepseek | custom)
    LLM_PROVIDER: str = "mock"
    CODE_GEN_PROVIDER: str = "mock"
    EMBEDDING_PROVIDER: str = "mock"
    
    LLM_MODEL: str = "qwen3-4b-instruct"
    CODE_MODEL: str = "deepseek-coder-v2-lite"
    EMBEDDING_MODEL: str = "qwen3-embedding-0.6b"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "datasets"
    DOCUMENT_DIR: Path = BASE_DIR / "documents"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    
    EXECUTION_TIMEOUT: int = 10
    SANDBOX_ENABLED: bool = False
    MAX_UPLOAD_SIZE_MB: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.DOCUMENT_DIR, exist_ok=True)
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
