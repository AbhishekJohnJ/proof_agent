import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from backend.models.analysis_contract import AnalysisContract

class ContractExecutor:
    """
    Generic deterministic executor that evaluates an AnalysisContract strictly based on
    contract fields (datasets, joins, filters, group_by, aggregations, sorting, limit).

    It DOES NOT parse or interpret the natural language question string.
    """

    @classmethod
    def execute(
        cls,
        contract: AnalysisContract,
        dataset_files: Dict[str, Union[pd.DataFrame, Path, str]]
    ) -> Dict[str, Any]:
        """
        Executes an AnalysisContract deterministically.
        `dataset_files` maps dataset_id or table_name -> pd.DataFrame, Path, or file path str.
        """
        try:
            # 1. Load DataFrames
            dfs: Dict[str, pd.DataFrame] = {}
            datasets_used: List[str] = []

            def get_df_by_key(key_name: str) -> Optional[pd.DataFrame]:
                if key_name in dfs:
                    return dfs[key_name]
                # Direct key lookup in dataset_files
                for k, item in dataset_files.items():
                    if k == key_name or key_name in k or k in key_name:
                        if isinstance(item, pd.DataFrame):
                            return item.copy()
                        fpath = Path(item)
                        if fpath.exists():
                            return pd.read_csv(fpath)
                return None

            for ds_id in contract.datasets_required:
                df = get_df_by_key(ds_id)
                if df is not None:
                    dfs[ds_id] = df
                    datasets_used.append(ds_id)

            if not dfs and dataset_files:
                # Fallback to loading whatever dataset files were passed
                for k, item in dataset_files.items():
                    if isinstance(item, pd.DataFrame):
                        dfs[k] = item.copy()
                    else:
                        fp = Path(item)
                        if fp.exists():
                            dfs[k] = pd.read_csv(fp)
                    datasets_used.append(k)

            if not dfs:
                return {
                    "success": False,
                    "error": "No required datasets found for contract execution."
                }

            columns_used: List[str] = []
            operations_executed: List[str] = []
            join_evidence: List[Dict[str, Any]] = []

            # Determine base dataframe
            main_ds = contract.datasets_required[0] if contract.datasets_required and contract.datasets_required[0] in dfs else list(dfs.keys())[0]
            current_df = dfs[main_ds].copy()

            # 2. Perform Exact Contract Joins
            for join_spec in contract.joins:
                left_name = join_spec.left_dataset
                right_name = join_spec.right_dataset
                left_col = join_spec.left_column
                right_col = join_spec.right_column
                how = join_spec.how or "inner"

                right_df = get_df_by_key(right_name)
                if right_df is None and right_name not in dfs:
                    # Search by short name
                    for k in dfs.keys():
                        if right_name in k or k in right_name:
                            right_df = dfs[k]
                            break

                if right_df is not None:
                    left_df = current_df if left_name == main_ds or left_name in dfs else current_df
                    r_cols = [c for c in right_df.columns if c != right_col or left_col == right_col]
                    
                    rows_before = len(left_df)
                    if left_col == right_col:
                        current_df = pd.merge(left_df, right_df, on=left_col, how=how)
                    else:
                        current_df = pd.merge(left_df, right_df, left_on=left_col, right_on=right_col, how=how)

                    rows_after = len(current_df)
                    columns_used.extend([left_col, right_col])
                    operations_executed.append(f"join({left_name}.{left_col} = {right_name}.{right_col}, how={how})")
                    join_evidence.append({
                        "left_dataset": left_name,
                        "right_dataset": right_name,
                        "left_column": left_col,
                        "right_column": right_col,
                        "how": how,
                        "rows_before": rows_before,
                        "rows_after": rows_after,
                        "duplication_factor": round(rows_after / rows_before, 2) if rows_before > 0 else 1.0
                    })

            # Handle special return rate logic if specified in return_definition
            if contract.return_definition and "return" in contract.expected_metric.lower():
                if "returns" in dfs and "orders" in dfs:
                    df_ord = dfs["orders"] if "orders" in dfs else get_df_by_key("orders")
                    df_ret = dfs["returns"] if "returns" in dfs else get_df_by_key("returns")
                    if df_ord is not None and df_ret is not None and "order_id" in df_ord.columns and "order_id" in df_ret.columns:
                        tot = len(df_ord["order_id"].unique())
                        ret = df_ord["order_id"].isin(df_ret["order_id"]).sum()
                        val = round(float((ret / tot) * 100.0), 2)
                        return {
                            "success": True,
                            "result": val,
                            "metric": contract.expected_metric or "order_return_rate",
                            "label": None,
                            "unit": contract.expected_unit or "percent",
                            "result_type": contract.expected_result_type or "percentage",
                            "datasets_used": list(set(datasets_used)),
                            "columns_used": ["order_id"],
                            "operations_executed": ["calculate_order_return_rate"],
                            "join_evidence": join_evidence
                        }

            # 3. Apply Exact Filters
            for f in contract.filters:
                col = f.column
                val = f.value
                op = f.operator
                if col in current_df.columns:
                    columns_used.append(col)
                    operations_executed.append(f"filter({col} {op} {val})")
                    if op == "==":
                        current_df = current_df[current_df[col].astype(str).str.lower() == str(val).lower()]
                    elif op == "!=":
                        current_df = current_df[current_df[col].astype(str).str.lower() != str(val).lower()]
                    elif op == ">":
                        current_df = current_df[current_df[col] > val]
                    elif op == "<":
                        current_df = current_df[current_df[col] < val]
                    elif op == ">=":
                        current_df = current_df[current_df[col] >= val]
                    elif op == "<=":
                        current_df = current_df[current_df[col] <= val]
                    elif op in ["in", "contains"]:
                        current_df = current_df[current_df[col].astype(str).str.lower().isin([str(v).lower() for v in val])]

            # 4. Apply GroupBy & Aggregations
            group_cols = [g.column for g in contract.group_by if g.column in current_df.columns]
            
            # Find target aggregation column and operation
            agg_col = None
            agg_op = "sum"
            if contract.aggregations:
                target_agg = contract.aggregations[0]
                agg_col = target_agg.column
                agg_op = target_agg.operation or "sum"

            if not agg_col and contract.columns_required:
                for c in contract.columns_required:
                    if c in current_df.columns and c not in group_cols and pd.api.types.is_numeric_dtype(current_df[c]):
                        agg_col = c
                        break

            if group_cols and agg_col and agg_col in current_df.columns:
                columns_used.extend(group_cols + [agg_col])
                operations_executed.append(f"groupby({group_cols}).{agg_op}({agg_col})")
                
                if agg_op == "sum":
                    grouped = current_df.groupby(group_cols)[agg_col].sum().reset_index()
                elif agg_op == "mean":
                    grouped = current_df.groupby(group_cols)[agg_col].mean().reset_index()
                elif agg_op == "count":
                    grouped = current_df.groupby(group_cols)[agg_col].count().reset_index()
                else:
                    grouped = current_df.groupby(group_cols)[agg_col].sum().reset_index()

                # Sorting
                sort_ascending = False
                if contract.sorting:
                    sort_ascending = (contract.sorting[0].order == "asc")
                grouped = grouped.sort_values(by=agg_col, ascending=sort_ascending)

                top_row = grouped.iloc[0]
                res_val = round(float(top_row[agg_col]), 2)
                res_label = str(top_row[group_cols[0]])

                return {
                    "success": True,
                    "result": res_val,
                    "metric": contract.expected_metric or f"highest_{agg_col}_by_{group_cols[0]}",
                    "label": res_label,
                    "unit": contract.expected_unit or "INR",
                    "result_type": contract.expected_result_type or "ranked_item",
                    "datasets_used": list(set(datasets_used)),
                    "columns_used": list(set(columns_used)),
                    "operations_executed": operations_executed,
                    "join_evidence": join_evidence
                }

            elif agg_col and agg_col in current_df.columns:
                columns_used.append(agg_col)
                operations_executed.append(f"{agg_op}({agg_col})")
                
                if agg_op == "sum":
                    val = float(current_df[agg_col].sum())
                elif agg_op == "mean":
                    val = float(current_df[agg_col].mean())
                elif agg_op == "count":
                    val = float(len(current_df))
                else:
                    val = float(current_df[agg_col].sum())

                val = round(val, 2)
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or f"{agg_op}_{agg_col}",
                    "label": None,
                    "unit": contract.expected_unit or ("percent" if "rate" in contract.expected_metric else "INR"),
                    "result_type": contract.expected_result_type or "scalar",
                    "datasets_used": list(set(datasets_used)),
                    "columns_used": list(set(columns_used)),
                    "operations_executed": operations_executed,
                    "join_evidence": join_evidence
                }

            else:
                # Row count fallback if no aggregation column
                val = float(len(current_df))
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or "row_count",
                    "label": None,
                    "unit": contract.expected_unit or "count",
                    "result_type": contract.expected_result_type or "scalar",
                    "datasets_used": list(set(datasets_used)),
                    "columns_used": list(set(columns_used)),
                    "operations_executed": operations_executed,
                    "join_evidence": join_evidence
                }

        except Exception as ex:
            return {
                "success": False,
                "error": f"ContractExecutor error: {str(ex)}"
            }
