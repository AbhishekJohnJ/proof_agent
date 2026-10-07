import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from backend.data.dataset_resolver import DatasetResolver, DatasetResolverError

logger = logging.getLogger(__name__)

class ColumnResolution(BaseModel):
    dataset_id: str
    requested_column: str
    resolved_column: str
    data_type: Optional[str] = None
    is_exact_match: bool

class ColumnResolverError(Exception):
    pass

class ColumnResolver:
    """Authoritative exact column resolver. Prevents silent column guessing or fuzzy mapping."""

    @staticmethod
    def resolve_column(dataset_id: str, column_name: str, explicit_schema_mapping: Optional[Dict[str, str]] = None) -> ColumnResolution:
        if not dataset_id or not column_name:
            raise ColumnResolverError("Dataset ID and column name must both be specified")

        resolved_ds = DatasetResolver.resolve_dataset(dataset_id)
        cols = resolved_ds.columns

        # Check explicit schema mapping first if provided
        if explicit_schema_mapping and column_name in explicit_schema_mapping:
            mapped_col = explicit_schema_mapping[column_name]
            if mapped_col in cols:
                return ColumnResolution(
                    dataset_id=resolved_ds.dataset_id,
                    requested_column=column_name,
                    resolved_column=mapped_col,
                    is_exact_match=False
                )

        # Exact match check
        if column_name in cols:
            return ColumnResolution(
                dataset_id=resolved_ds.dataset_id,
                requested_column=column_name,
                resolved_column=column_name,
                is_exact_match=True
            )

        raise ColumnResolverError(
            f"Column '{column_name}' does not exist in dataset '{dataset_id}'. "
            f"Available columns: {cols}. Silent fuzzy column mapping is strictly prohibited."
        )

    @staticmethod
    def validate_columns_exist(dataset_id: str, column_names: List[str]) -> List[ColumnResolution]:
        results = []
        for col in column_names:
            res = ColumnResolver.resolve_column(dataset_id, col)
            results.append(res)
        return results
