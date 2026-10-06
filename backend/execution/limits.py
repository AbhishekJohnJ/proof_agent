from pydantic import BaseModel

class ExecutionLimits(BaseModel):
    timeout_seconds: int = 10
    max_memory_mb: int = 512
    max_output_bytes: int = 100000
    allowed_packages: list[str] = ["pandas", "numpy", "json", "math", "datetime", "re"]
