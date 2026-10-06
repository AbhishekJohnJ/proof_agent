from typing import Any, Optional
from pydantic import BaseModel, Field

class ContractOperation(BaseModel):
    type: str  # filter | aggregate | join | group_by | compare
    column: Optional[str] = None
    condition: Optional[str] = None
    operation: Optional[str] = None  # sum | mean | count | min | max

class AnalysisContract(BaseModel):
    question: str
    query_type: str = "data_aggregation"
    datasets_required: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    columns_required: list[str] = Field(default_factory=list)
    operations: list[ContractOperation] = Field(default_factory=list)
    expected_result_type: str = "number"  # number | integer | float | table | string | boolean | refusal
    expected_metric: str = "result"
    expected_unit: Optional[str] = None
    ambiguities: list[str] = Field(default_factory=list)
    quality_requirements: list[str] = Field(default_factory=list)
