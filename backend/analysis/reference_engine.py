import math
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from backend.models.analysis_contract import AnalysisContract

NON_NUMERIC_COLS = ["customer_id", "order_id", "product_id", "customer_segment", "category", "state", "city", "return_id", "tier", "region", "store", "payment_method", "name"]

class ReferenceEngine:
    """
    Independent deterministic reference engine evaluating AnalysisContract on host pandas DataFrames.
    Operates strictly on AnalysisContract specifications (joins, filters, group_by, aggregations, sorting, limit).
    DOES NOT parse or re-interpret English question string.
    Independent implementation from ContractExecutor and generated code.
    """

    @classmethod
    def compute_reference(
        cls,
        contract: AnalysisContract,
        dataset_files: Dict[str, Union[Path, str, pd.DataFrame]]
    ) -> Dict[str, Any]:
        """
        Calculates independent ground-truth reference result directly from dataset files on host.
        `dataset_files` maps table_name (or dataset_id) -> Path to CSV file or pd.DataFrame.
        """
        try:
            # 1. Helper to load DataFrames by contract dataset name or alias
            dfs: Dict[str, pd.DataFrame] = {}

            def load_df(name: str) -> Optional[pd.DataFrame]:
                if name in dfs:
                    return dfs[name]
                for k, item in dataset_files.items():
                    if k == name or name in k or k in name:
                        if isinstance(item, pd.DataFrame):
                            return item.copy()
                        fpath = Path(item)
                        if fpath.exists():
                            return pd.read_csv(fpath)
                return None

            for ds_id in contract.datasets_required:
                df = load_df(ds_id)
                if df is not None:
                    dfs[ds_id] = df

            if not dfs and dataset_files:
                for k, item in dataset_files.items():
                    if isinstance(item, pd.DataFrame):
                        dfs[k] = item.copy()
                    else:
                        fp = Path(item)
                        if fp.exists():
                            dfs[k] = pd.read_csv(fp)

            if not dfs:
                return {
                    "success": False,
                    "error": "Reference Engine: Required datasets not found."
                }

            # Handle Return Rate or Return Revenue calculations when explicitly contracted
            if contract.return_definition or (contract.expected_metric and "return" in contract.expected_metric.lower()):
                df_ord = load_df("orders")
                df_ret = load_df("returns")
                df_prods = load_df("products")
                df_items = load_df("order_items")

                if contract.expected_metric == "order_return_rate":
                    if df_ord is not None and df_ret is not None:
                        tot_orders = len(df_ord["order_id"].unique())
                        ret_orders = df_ord["order_id"].isin(df_ret["order_id"]).sum()
                        rate = round(float((ret_orders / tot_orders) * 100.0), 2)
                        return {
                            "success": True,
                            "result": rate,
                            "metric": "order_return_rate",
                            "label": None,
                            "unit": contract.expected_unit or "percent",
                            "result_type": "percentage"
                        }

                elif contract.expected_metric == "highest_return_rate_category":
                    if df_ret is not None and df_prods is not None and df_items is not None:
                        ret_m = pd.merge(df_ret, df_prods, on="product_id")
                        item_m = pd.merge(df_items, df_prods, on="product_id")
                        r_cnt = ret_m.groupby("category")["return_id"].count()
                        i_cnt = item_m.groupby("category")["order_item_id"].count()
                        rates = (r_cnt / i_cnt * 100.0).reset_index(name="rate")
                        top = rates.sort_values(by="rate", ascending=False).iloc[0]
                        return {
                            "success": True,
                            "result": round(float(top["rate"]), 2),
                            "metric": "highest_return_rate_category",
                            "label": str(top["category"]),
                            "unit": contract.expected_unit or "percent",
                            "result_type": "ranked_item"
                        }

                elif contract.expected_metric == "returning_customers_revenue":
                    if df_ord is not None and df_ret is not None:
                        ret_cust_ids = df_ret["customer_id"].unique()
                        ret_orders = df_ord[df_ord["customer_id"].isin(ret_cust_ids)]
                        val = round(float(ret_orders["final_amount"].sum()), 2)
                        return {
                            "success": True,
                            "result": val,
                            "metric": "returning_customers_revenue",
                            "label": None,
                            "unit": contract.expected_unit or "INR",
                            "result_type": "scalar"
                        }

            # 2. General Independent Pipeline Evaluation
            main_ds_id = contract.datasets_required[0] if contract.datasets_required and contract.datasets_required[0] in dfs else list(dfs.keys())[0]
            curr_df = dfs[main_ds_id].copy()

            # Apply Contract Joins
            for j in contract.joins:
                left_ds = j.left_dataset
                right_ds = j.right_dataset
                left_col = j.left_column
                right_col = j.right_column
                how_type = j.how or "inner"

                rdf = load_df(right_ds)
                if rdf is not None:
                    if left_col == right_col:
                        curr_df = pd.merge(curr_df, rdf, on=left_col, how=how_type)
                    else:
                        curr_df = pd.merge(curr_df, rdf, left_on=left_col, right_on=right_col, how=how_type)

            # Apply Contract Filters
            for f in contract.filters:
                c = f.column
                v = f.value
                op = f.operator
                if c not in curr_df.columns:
                    cands = [col for col in curr_df.columns if c.replace("customer_", "") in col.lower() or "tier" in col.lower() or "segment" in col.lower()]
                    if cands:
                        c = cands[0]
                if c in curr_df.columns:
                    if op == "==":
                        curr_df = curr_df[curr_df[c].astype(str).str.lower() == str(v).lower()]
                    elif op == "!=":
                        curr_df = curr_df[curr_df[c].astype(str).str.lower() != str(v).lower()]
                    elif op == ">":
                        curr_df = curr_df[curr_df[c] > v]
                    elif op == "<":
                        curr_df = curr_df[curr_df[c] < v]
                    elif op == ">=":
                        curr_df = curr_df[curr_df[c] >= v]
                    elif op == "<=":
                        curr_df = curr_df[curr_df[c] <= v]

            # Apply GroupBy & Aggregation
            g_cols = [g.column for g in contract.group_by if g.column in curr_df.columns]
            
            target_col = None
            target_op = "sum"
            if contract.aggregations and contract.aggregations[0].column:
                target_col = contract.aggregations[0].column
                target_op = contract.aggregations[0].operation or "sum"
            elif contract.columns_required:
                for col_candidate in contract.columns_required:
                    if col_candidate in curr_df.columns and col_candidate not in g_cols and col_candidate.lower() not in NON_NUMERIC_COLS and pd.api.types.is_numeric_dtype(curr_df[col_candidate]):
                        target_col = col_candidate
                        break

            if not target_col or target_col not in curr_df.columns or target_col.lower() in NON_NUMERIC_COLS:
                cands = [c for c in curr_df.columns if any(k in c.lower() for k in ["revenue", "amount", "sales", "price"]) and c.lower() not in NON_NUMERIC_COLS]
                if cands:
                    target_col = cands[0]
                else:
                    num_cols = [c for c in curr_df.select_dtypes(include=["number"]).columns if c.lower() not in NON_NUMERIC_COLS]
                    if num_cols:
                        target_col = num_cols[0]

            if g_cols and target_col and target_col in curr_df.columns:
                if target_op == "sum":
                    grp = curr_df.groupby(g_cols)[target_col].sum().reset_index()
                elif target_op == "mean":
                    grp = curr_df.groupby(g_cols)[target_col].mean().reset_index()
                elif target_op == "count":
                    grp = curr_df.groupby(g_cols)[target_col].count().reset_index()
                else:
                    grp = curr_df.groupby(g_cols)[target_col].sum().reset_index()

                asc = False
                if contract.sorting:
                    asc = (contract.sorting[0].order == "asc")
                grp = grp.sort_values(by=target_col, ascending=asc)

                top = grp.iloc[0]
                val = round(float(top[target_col]), 2)
                lbl = str(top[g_cols[0]])
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or f"highest_{target_col}",
                    "label": lbl,
                    "unit": contract.expected_unit or "INR",
                    "result_type": contract.expected_result_type or "ranked_item"
                }

            elif target_col and target_col in curr_df.columns:
                if target_op == "sum":
                    val = float(curr_df[target_col].sum())
                elif target_op == "mean":
                    val = float(curr_df[target_col].mean())
                elif target_op == "count":
                    val = float(len(curr_df))
                else:
                    val = float(curr_df[target_col].sum())

                val = round(val, 2)
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or f"{target_op}_{target_col}",
                    "label": None,
                    "unit": contract.expected_unit or "INR",
                    "result_type": contract.expected_result_type or "scalar"
                }

            else:
                # Row count
                val = float(len(curr_df))
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or "row_count",
                    "label": None,
                    "unit": contract.expected_unit or "count",
                    "result_type": contract.expected_result_type or "scalar"
                }

        except Exception as ex:
            return {
                "success": False,
                "error": f"Reference engine execution error: {str(ex)}"
            }
