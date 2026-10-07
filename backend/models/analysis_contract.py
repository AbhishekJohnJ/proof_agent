from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class ContractOperation(BaseModel):
    type: str  # join | aggregate | filter | group_by | sort | select
    dataset: Optional[str] = None
    column: Optional[str] = None
    operation: Optional[str] = None  # sum | mean | count | min | max
    left_dataset: Optional[str] = None
    left_column: Optional[str] = None
    right_dataset: Optional[str] = None
    right_column: Optional[str] = None
    how: Optional[str] = "inner"
    condition: Optional[str] = None
    value: Optional[Any] = None
    group_column: Optional[str] = None
    order: Optional[str] = "desc"
    limit: Optional[int] = None

class AnalysisContract(BaseModel):
    question: str
    query_type: str = "data_aggregation"
    datasets_required: List[str] = Field(default_factory=list)
    documents_required: List[str] = Field(default_factory=list)
    columns_required: List[str] = Field(default_factory=list)
    joins: List[Dict[str, Any]] = Field(default_factory=list)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    aggregations: List[Dict[str, Any]] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    sorting: List[Dict[str, Any]] = Field(default_factory=list)
    operations: List[ContractOperation] = Field(default_factory=list)
    expected_result_type: str = "number"  # number | integer | float | table | string | boolean | refusal | ranked_item
    expected_metric: str = "result"
    expected_unit: Optional[str] = None  # INR, percent, count, None
    quality_requirements: List[str] = Field(default_factory=list)
    ambiguity_requirements: List[str] = Field(default_factory=list)
    return_definition: Optional[str] = None

