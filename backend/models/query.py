from typing import Optional
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    question: str = Field(..., description="The user query or question to analyze")
    selected_datasets: list[str] = Field(default_factory=list, description="IDs of uploaded datasets to query")
    selected_documents: list[str] = Field(default_factory=list, description="IDs of uploaded documents to reference")
    allow_partial_match: bool = True
    config_overrides: dict[str, str] = Field(default_factory=dict)
