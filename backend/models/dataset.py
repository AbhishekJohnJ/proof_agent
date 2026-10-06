from typing import Any, Optional
from pydantic import BaseModel, Field

class QualityWarning(BaseModel):
    severity: str = Field(..., description="warning | critical | info")
    type: str = Field(..., description="mixed_currency | missing_values | duplicate_rows | ambiguous_date | schema_anomaly")
    message: str
    affected_columns: list[str] = Field(default_factory=list)

class ColumnProfile(BaseModel):
    name: str
    inferred_type: str  # numeric | categorical | date | identifier | text | unknown
    missing_count: int
    missing_percentage: float
    unique_count: int
    sample_values: list[Any] = Field(default_factory=list)
    has_mixed_units: bool = False
    is_constant: bool = False

class DatasetProfile(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    column_names: list[str]
    missing_values_total: int
    duplicate_rows: int
    column_profiles: list[ColumnProfile] = Field(default_factory=list)
    quality_status: str = "good"  # good | medium | poor | unprocessable
    quality_warnings: list[QualityWarning] = Field(default_factory=list)

class CandidateRelationship(BaseModel):
    left_dataset: str
    left_column: str
    right_dataset: str
    right_column: str
    confidence: float
    reason: str
    is_left_unique: bool = False
    is_right_unique: bool = False

class DatasetMetadata(BaseModel):
    dataset_id: str
    filename: str
    file_type: str
    rows: int
    columns: int
    file_size_bytes: int
    created_at: str
    status: str = "success"  # success | error
    error_message: Optional[str] = None
