import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.models.analysis_contract import AnalysisContract

logger = logging.getLogger(__name__)

class OperationVerificationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

class OperationVerifier:
    """
    Deterministic comparator evaluating runtime operation traces against AnalysisContract specifications.
    Validates JOIN, FILTER, GROUP_BY, AGGREGATE, SORT, and LIMIT events.
    """

    @classmethod
    def verify_operations(
        cls,
        contract: AnalysisContract,
        runtime_operations: List[Dict[str, Any]]
    ) -> OperationVerificationResult:
        if not contract:
            return OperationVerificationResult(is_valid=True)

        # Skip operation check for non-code document retrieval queries
        if contract.query_type == "document_retrieval":
            return OperationVerificationResult(is_valid=True)

        errors = []
        details = {
            "contract_aggregations": [a.model_dump() for a in contract.aggregations],
            "contract_filters": [f.model_dump() for f in contract.filters],
            "contract_group_by": [g.column for g in contract.group_by],
            "contract_joins": [j.model_dump() for j in contract.joins],
            "runtime_operations_count": len(runtime_operations or [])
        }

        ops = runtime_operations or []

        # 1. Verify Aggregations
        for contract_agg in contract.aggregations:
            expected_fn = (contract_agg.operation or "").lower()
            expected_col = contract_agg.column

            # Special case for return rate semantic calculations
            if contract.return_definition and expected_fn in ("count", "sum"):
                pass
            elif expected_fn:
                matching_agg = None
                mismatch_fn = None
                mismatch_col = None

                for op in ops:
                    if op.get("operation") == "aggregate":
                        actual_fn = (op.get("function") or "").lower()
                        actual_col = op.get("column")

                        if actual_fn == expected_fn:
                            if not expected_col or actual_col == expected_col:
                                matching_agg = op
                                break
                            else:
                                mismatch_col = actual_col
                        else:
                            mismatch_fn = actual_fn

                if not matching_agg:
                    if mismatch_fn:
                        errors.append(f"Aggregation mismatch: contract specified '{expected_fn}' for '{expected_col}', but runtime executed '{mismatch_fn}'.")
                    elif mismatch_col:
                        errors.append(f"Aggregation column mismatch: contract specified '{expected_fn}' on '{expected_col}', but runtime aggregated on '{mismatch_col}'.")
                    else:
                        errors.append(f"Missing required aggregation: contract specified '{expected_fn}' on column '{expected_col}', but operation was not found in runtime trace.")

        # 2. Verify Filters
        for contract_filter in contract.filters:
            target_col = contract_filter.column
            target_val = str(contract_filter.value).lower() if contract_filter.value is not None else None
            target_op = contract_filter.operator or "=="

            matching_filter = None
            mismatch_val = None
            mismatch_col = None

            for op in ops:
                if op.get("operation") == "filter":
                    actual_col = op.get("column")
                    actual_val = str(op.get("value")).lower() if op.get("value") is not None else None
                    actual_op = op.get("operator", "==")

                    if actual_col and target_col and actual_col == target_col:
                        if actual_val == target_val or target_val is None:
                            matching_filter = op
                            break
                        else:
                            mismatch_val = op.get("value")
                    elif actual_val == target_val and actual_col:
                        mismatch_col = actual_col

            if not matching_filter:
                if mismatch_val is not None:
                    errors.append(f"Filter value mismatch: contract specified filter on '{target_col}' == '{contract_filter.value}', but runtime filtered on '{mismatch_val}'.")
                elif mismatch_col is not None:
                    errors.append(f"Filter column mismatch: contract specified filter on '{target_col}', but runtime filtered on '{mismatch_col}'.")
                else:
                    errors.append(f"Missing required filter: contract specified filter '{target_col} {target_op} {contract_filter.value}', but filter was not executed.")

        # 3. Verify GroupBy
        for contract_gb in contract.group_by:
            target_col = contract_gb.column
            matching_gb = None
            mismatch_col = None

            for op in ops:
                if op.get("operation") == "group_by" or op.get("operation") == "groupby":
                    actual_col = op.get("column")
                    actual_cols = op.get("columns", [])
                    if actual_col and actual_col == target_col:
                        matching_gb = op
                        break
                    elif actual_cols and target_col in actual_cols:
                        matching_gb = op
                        break
                    elif actual_col:
                        mismatch_col = actual_col
                    elif actual_cols:
                        mismatch_col = actual_cols[0]

            if not matching_gb:
                if mismatch_col:
                    errors.append(f"GroupBy column mismatch: contract specified GROUP BY '{target_col}', but runtime executed GROUP BY '{mismatch_col}'.")
                else:
                    errors.append(f"Missing required GroupBy: contract specified GROUP BY '{target_col}', but no groupby operation was recorded in runtime trace.")

        # 4. Verify Joins
        for contract_join in contract.joins:
            left_col = contract_join.left_column
            right_col = contract_join.right_column

            matching_join = None
            mismatch_key = None

            for op in ops:
                if op.get("operation") == "join":
                    act_left = op.get("left_column") or op.get("on")
                    act_right = op.get("right_column") or op.get("on")

                    left_match = (act_left and left_col and act_left == left_col)
                    right_match = (act_right and right_col and act_right == right_col)

                    if left_match and right_match:
                        matching_join = op
                        break
                    elif act_left or act_right:
                        mismatch_key = f"left={act_left}, right={act_right}"

            if not matching_join:
                if mismatch_key:
                    errors.append(f"Join key mismatch: contract specified join on '{left_col}'='{right_col}', but runtime joined on '{mismatch_key}'.")
                else:
                    errors.append(f"Missing required Join: contract specified join on '{left_col}'='{right_col}', but join was not executed in runtime trace.")

        # 5. Verify Sort
        for contract_sort in (contract.sorting or []):
            target_col = contract_sort.column
            matching_sort = None
            for op in ops:
                if op.get("operation") == "sort":
                    actual_col = op.get("column")
                    if actual_col and actual_col == target_col:
                        matching_sort = op
                        break
            if not matching_sort:
                errors.append(f"Missing required Sort: contract specified SORT BY '{target_col}', but sort was not executed in runtime trace.")

        # 6. Verify Limit
        if contract.limit is not None:
            matching_limit = None
            for op in ops:
                if op.get("operation") == "limit":
                    if op.get("value") == contract.limit:
                        matching_limit = op
                        break
            if not matching_limit:
                errors.append(f"Missing required Limit: contract specified LIMIT {contract.limit}, but limit was not recorded in runtime trace.")

        is_valid = len(errors) == 0
        return OperationVerificationResult(is_valid=is_valid, errors=errors, details=details)
