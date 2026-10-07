import ast
from typing import Any, Dict, List, Set, Tuple
from backend.models.analysis_contract import AnalysisContract
from backend.models.verification import CheckStatus

class StaticContractChecker:
    """Inspects generated Python code AST against AnalysisContract requirements."""

    @classmethod
    def check_contract(
        cls,
        code: str,
        contract: AnalysisContract,
        resolved_dataset_ids: List[str]
    ) -> Tuple[CheckStatus, CheckStatus, CheckStatus, List[str]]:
        """
        statically inspects AST of generated code.
        Returns:
            v7_required_datasets_used: CheckStatus
            v8_required_columns_used: CheckStatus
            v9_expected_operation_reflected: CheckStatus
            errors: list of error strings
        """
        if not code or not code.strip():
            return CheckStatus.FAIL, CheckStatus.FAIL, CheckStatus.FAIL, ["No code generated to check."]

        try:
            tree = ast.parse(code)
        except Exception as e:
            return CheckStatus.FAIL, CheckStatus.FAIL, CheckStatus.FAIL, [f"AST Syntax error in generated code: {e}"]

        errors: List[str] = []

        # Collect strings, variable names, call attribute names from AST
        strings_in_ast: Set[str] = set()
        names_in_ast: Set[str] = set()
        calls_in_ast: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                strings_in_ast.add(node.value)
            elif isinstance(node, ast.Name):
                names_in_ast.add(node.id)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    calls_in_ast.add(node.func.attr)
                elif isinstance(node.func, ast.Name):
                    calls_in_ast.add(node.func.id)

        # 1. V7 Check: Required datasets referenced statically
        v7_status = CheckStatus.PASS
        for ds_id in resolved_dataset_ids:
            table_name = ds_id.replace("ds_kaggle_", "").replace("ds_bm_", "").replace("ds_", "")
            # Verify dataset ID or dataset file or table variable name appears in AST
            matched = any(ds_id in s or table_name in s for s in strings_in_ast) or \
                      any(table_name in n for n in names_in_ast)
            if not matched:
                v7_status = CheckStatus.FAIL
                errors.append(f"V7 Static Failure: Code does not reference required dataset '{ds_id}'.")

        # 2. V8 Check: Required columns referenced statically
        v8_status = CheckStatus.PASS
        if contract.columns_required:
            missing_cols = []
            for col in contract.columns_required:
                if col not in strings_in_ast and col not in names_in_ast:
                    missing_cols.append(col)
            if missing_cols:
                v8_status = CheckStatus.FAIL
                errors.append(f"V8 Static Failure: Code does not reference required columns: {missing_cols}.")
        else:
            v8_status = CheckStatus.NOT_APPLICABLE

        # 3. V9 Check: Required operations (joins, group_by, aggregations, filters) reflected in AST
        v9_status = CheckStatus.PASS

        # Check Join
        if contract.joins or any(op.type == "join" for op in contract.operations):
            if "merge" not in calls_in_ast and "join" not in calls_in_ast:
                v9_status = CheckStatus.FAIL
                errors.append("V9 Static Failure: Contract requires table join but code contains no 'merge' or 'join' operation.")

        # Check GroupBy
        if contract.group_by or any(op.type == "group_by" for op in contract.operations):
            if "groupby" not in calls_in_ast:
                v9_status = CheckStatus.FAIL
                errors.append("V9 Static Failure: Contract requires group-by but code contains no 'groupby' method call.")

        # Check Aggregations
        agg_ops = []
        for op in contract.operations:
            if op.operation:
                agg_ops.append(op.operation.lower())
        for agg in contract.aggregations:
            if isinstance(agg, dict) and "operation" in agg:
                agg_ops.append(agg["operation"].lower())

        for op_name in set(agg_ops):
            if op_name in ["sum", "mean", "count", "min", "max"]:
                if op_name not in calls_in_ast and not any(op_name in c.lower() for c in calls_in_ast):
                    v9_status = CheckStatus.FAIL
                    errors.append(f"V9 Static Failure: Contract requires '{op_name}' aggregation, but '{op_name}' function call missing from AST.")

        return v7_status, v8_status, v9_status, errors
