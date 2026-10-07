from typing import Any, Optional, List, Dict, Union
from pydantic import BaseModel, Field, field_validator

class ContractJoin(BaseModel):
    left_dataset: str
    left_column: str
    right_dataset: str
    right_column: str
    how: str = "inner"
    expected_cardinality: Optional[str] = None  # one_to_one, one_to_many, many_to_one, many_to_many

class ContractFilter(BaseModel):
    dataset: Optional[str] = None
    column: str
    operator: str = "=="  # ==, !=, >, <, >=, <=, in, contains
    value: Any

class ContractAggregation(BaseModel):
    dataset: Optional[str] = None
    column: Optional[str] = None
    operation: str  # sum, mean, count, min, max, nunique

class ContractGroupBy(BaseModel):
    dataset: Optional[str] = None
    column: str

class ContractSort(BaseModel):
    dataset: Optional[str] = None
    column: str
    order: str = "desc"  # asc, desc

class UnitSource(BaseModel):
    dataset: str
    column: str
    source: str = "dataset_manifest/data_dictionary"

class ContractOperation(BaseModel):
    type: str  # join | aggregate | filter | group_by | sort | select
    dataset: Optional[str] = None
    column: Optional[str] = None
    operation: Optional[str] = None  # sum | mean | count | min | max | nunique
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
    joins: List[ContractJoin] = Field(default_factory=list)
    filters: List[ContractFilter] = Field(default_factory=list)
    aggregations: List[ContractAggregation] = Field(default_factory=list)
    group_by: List[ContractGroupBy] = Field(default_factory=list)
    sorting: List[ContractSort] = Field(default_factory=list)
    limit: Optional[int] = None
    operations: List[ContractOperation] = Field(default_factory=list)
    expected_result_type: str = "scalar"  # scalar | integer | float | percentage | ranked_item | grouped_table | comparison | string | boolean | refusal
    expected_metric: str = "result"
    expected_unit: Optional[str] = None  # INR | USD | EUR | percent | count | unitless
    unit_source: Optional[UnitSource] = None
    return_definition: Optional[str] = None  # order_return_rate | item_return_rate | revenue_return_rate
    quality_requirements: List[str] = Field(default_factory=list)
    ambiguity_requirements: List[str] = Field(default_factory=list)

    @field_validator("group_by", mode="before")
    @classmethod
    def _coerce_group_by(cls, v: Any) -> List[Any]:
        if not v:
            return []
        res = []
        for item in v:
            if isinstance(item, str):
                res.append({"column": item})
            else:
                res.append(item)
        return res
