import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.models.analysis_contract import AnalysisContract
from backend.data.dataset_resolver import DatasetResolver, DatasetResolverError
from backend.data.column_resolver import ColumnResolver, ColumnResolverError

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    is_valid: bool
    refusal_reason: Optional[str] = None
    errors: List[str] = []

class ContractValidator:
    """Pre-code-generation gate that strictly validates contract completeness and structural correctness."""

    VALID_RESULT_TYPES = {
        "scalar", "integer", "float", "percentage", "ranked_item",
        "grouped_table", "comparison", "string", "boolean", "refusal"
    }

    VALID_RETURN_DEFINITIONS = {
        "order_return_rate", "item_return_rate", "revenue_return_rate",
        "category_return_rate", "highest_return_rate_category"
    }

    VALID_UNITS = {
        "INR", "USD", "EUR", "percent", "%", "count", "unitless", "orders", "items", "customers"
    }

    @classmethod
    def _find_dataset_for_col(cls, requested_ds: Optional[str], col_name: str, datasets_required: List[str]) -> str:
        if requested_ds:
            try:
                ColumnResolver.resolve_column(requested_ds, col_name)
                return requested_ds
            except ColumnResolverError:
                pass
        for ds_id in datasets_required:
            try:
                ColumnResolver.resolve_column(ds_id, col_name)
                return ds_id
            except ColumnResolverError:
                pass
        return requested_ds or datasets_required[0]

    @classmethod
    def validate_contract(cls, contract: AnalysisContract) -> ValidationResult:
        errors = []

        # 1. Check if document retrieval query
        if contract.query_type == "document_retrieval":
            if not contract.documents_required:
                return ValidationResult(
                    is_valid=False,
                    refusal_reason="Document query has no documents_required specified",
                    errors=["Empty documents_required"]
                )
            return ValidationResult(is_valid=True)

        # 2. Check datasets required
        if not contract.datasets_required:
            return ValidationResult(
                is_valid=False,
                refusal_reason="Contract has no datasets_required specified",
                errors=["Empty datasets_required"]
            )

        # 2. Check each dataset exists via DatasetResolver
        for ds_id in contract.datasets_required:
            try:
                DatasetResolver.resolve_dataset(ds_id)
            except DatasetResolverError as e:
                return ValidationResult(
                    is_valid=False,
                    refusal_reason=f"Dataset resolution failed: {e}",
                    errors=[str(e)]
                )

        # 3. Check each required column exists via ColumnResolver
        for col_spec in contract.columns_required:
            if "." in col_spec:
                ds_id, col_name = col_spec.split(".", 1)
                try:
                    ColumnResolver.resolve_column(ds_id, col_name)
                except ColumnResolverError as e:
                    errors.append(f"Column resolution failed: {e}")
            else:
                found = False
                for ds_id in contract.datasets_required:
                    try:
                        ColumnResolver.resolve_column(ds_id, col_spec)
                        found = True
                        break
                    except ColumnResolverError:
                        pass
                if not found:
                    errors.append(f"Required column '{col_spec}' does not exist in any required dataset {contract.datasets_required}")

        if errors:
            return ValidationResult(
                is_valid=False,
                refusal_reason=f"Column validation failed: {'; '.join(errors)}",
                errors=errors
            )

        # 4. Check joins reference real datasets & keys
        for join in contract.joins:
            try:
                left_d = cls._find_dataset_for_col(join.left_dataset, join.left_column, contract.datasets_required)
                right_d = cls._find_dataset_for_col(join.right_dataset, join.right_column, contract.datasets_required)
                ColumnResolver.resolve_column(left_d, join.left_column)
                ColumnResolver.resolve_column(right_d, join.right_column)
            except (DatasetResolverError, ColumnResolverError) as e:
                errors.append(f"Invalid join specification: {e}")

        # 5. Check filters reference real columns
        for flt in contract.filters:
            try:
                target_d = cls._find_dataset_for_col(flt.dataset, flt.column, contract.datasets_required)
                ColumnResolver.resolve_column(target_d, flt.column)
            except (DatasetResolverError, ColumnResolverError) as e:
                errors.append(f"Invalid filter column: {e}")

        # 6. Check aggregations reference real columns
        for agg in contract.aggregations:
            try:
                target_d = cls._find_dataset_for_col(agg.dataset, agg.column, contract.datasets_required)
                ColumnResolver.resolve_column(target_d, agg.column)
            except (DatasetResolverError, ColumnResolverError) as e:
                errors.append(f"Invalid aggregation column: {e}")

        # 7. Check group_by columns exist
        for gb in contract.group_by:
            try:
                target_d = cls._find_dataset_for_col(gb.dataset, gb.column, contract.datasets_required)
                ColumnResolver.resolve_column(target_d, gb.column)
            except (DatasetResolverError, ColumnResolverError) as e:
                errors.append(f"Invalid group_by column: {e}")

        # 8. Check result type and unit validity
        if contract.expected_result_type not in cls.VALID_RESULT_TYPES:
            errors.append(f"Unsupported result_type '{contract.expected_result_type}'")

        if contract.expected_unit and contract.expected_unit not in cls.VALID_UNITS:
            errors.append(f"Unsupported or unverified unit '{contract.expected_unit}'")

        # 9. Completeness requirements for ranked / return-rate / numerical queries
        query_type = contract.query_type or "aggregation"
        
        if "ranked" in query_type or contract.expected_result_type == "ranked_item":
            if not contract.group_by or not contract.aggregations:
                errors.append("Ranked queries require group_by and aggregation")

        if ("return rate" in contract.question.lower() or "return_rate" in (contract.expected_metric or "").lower()):
            if not contract.return_definition:
                return ValidationResult(
                    is_valid=False,
                    refusal_reason="Ambiguous return-rate query lacks an explicit return_definition in contract",
                    errors=["Missing return_definition"]
                )
            if contract.return_definition not in cls.VALID_RETURN_DEFINITIONS:
                errors.append(f"Unsupported return_definition '{contract.return_definition}'")

        if errors:
            return ValidationResult(
                is_valid=False,
                refusal_reason=f"Contract validation failed: {'; '.join(errors)}",
                errors=errors
            )

        return ValidationResult(is_valid=True)
