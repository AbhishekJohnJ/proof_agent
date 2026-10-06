from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class EvidenceType(str, Enum):
    DATA = "data"
    DOCUMENT = "document"
    CODE = "code"
    EXECUTION = "execution"
    VERIFICATION = "verification"

class EvidenceItem(BaseModel):
    type: EvidenceType
    source: str
    description: str
    details: dict[str, Any] = Field(default_factory=dict)
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    dataset_id: Optional[str] = None
    columns_used: list[str] = Field(default_factory=list)

class EvidenceCollection(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
