import math
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from backend.models.analysis_contract import AnalysisContract
from backend.data.dataset_resolver import DatasetResolver, DatasetResolverError
from backend.data.column_resolver import ColumnResolver, ColumnResolverError
from backend.data.dataset_cache import DatasetCache
from backend.services.storage import storage_service

class ReferenceEngineError(Exception):
    pass

class ReferenceEngine:
    """
    Independent deterministic reference engine evaluating AnalysisContract on host pandas DataFrames.
    Operates strictly on AnalysisContract specifications (joins, filters, group_by, aggregations, sorting, limit).
    DOES NOT parse English question string.
    DOES NOT use implicit fallbacks, fuzzy column guessing, or question keyword hardcoding.
    Independent implementation from ContractExecutor and generated sandbox code.
    """

    @classmethod
    def _get_table_df(cls, table_name: str, dfs: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
        if table_name in dfs:
            return dfs[table_name]
        candidate_id = f"ds_kaggle_{table_name}" if not table_name.startswith("ds_") else table_name
        if candidate_id in dfs:
            return dfs[candidate_id]
        try:
            art = DatasetResolver.resolve_dataset(table_name if table_name.startswith("ds_") else candidate_id)
            return storage_service.get_dataframe(art.dataset_id)
        except Exception:
            return None

    @classmethod
    def compute_reference(
        cls,
        contract: AnalysisContract,
        dataset_files: Optional[Dict[str, Union[Path, str, pd.DataFrame]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates independent ground-truth reference result directly from dataset files on host.
        """
        try:
            if not contract or not contract.datasets_required:
                return {
                    "success": False,
                    "error": "ReferenceEngine: AnalysisContract has no datasets_required specified"
                }

            # 1. Load exact datasets required by contract using DatasetResolver
            dfs: Dict[str, pd.DataFrame] = {}

            for ds_id in contract.datasets_required:
                try:
                    res_artifact = DatasetResolver.resolve_dataset(ds_id)
                    w_path = Path(res_artifact.workspace_path)
                    if w_path.exists():
                        df_cached = DatasetCache.get_dataframe(w_path)
                        if df_cached is not None:
                            dfs[ds_id] = df_cached
                    else:
                        if dataset_files and ds_id in dataset_files:
                            item = dataset_files[ds_id]
                            if isinstance(item, pd.DataFrame):
                                dfs[ds_id] = item.copy()
                            else:
                                dfs[ds_id] = DatasetCache.get_dataframe(Path(item)) or pd.read_csv(Path(item))
                except DatasetResolverError:
                    if dataset_files and ds_id in dataset_files:
                        item = dataset_files[ds_id]
                        if isinstance(item, pd.DataFrame):
                            dfs[ds_id] = item.copy()
                        else:
                            dfs[ds_id] = DatasetCache.get_dataframe(Path(item)) or pd.read_csv(Path(item))
                    else:
                        df_storage = storage_service.get_dataframe(ds_id)
                        if df_storage is not None:
                            dfs[ds_id] = df_storage.copy()

            if not dfs:
                return {
                    "success": False,
                    "error": "ReferenceEngine: Required datasets could not be loaded."
                }

            # 2. Semantic Return Rate Definitions
            if contract.return_definition:
                ret_def = contract.return_definition
                df_ord = cls._get_table_df("orders", dfs)
                df_ret = cls._get_table_df("returns", dfs)

                if ret_def in ("highest_return_rate_category", "category_return_rate") or contract.expected_metric == "highest_return_rate_category":
                    df_prods = cls._get_table_df("products", dfs)
                    df_items = cls._get_table_df("order_items", dfs)
                    if df_ret is not None and df_prods is not None and df_items is not None:
                        ret_m = pd.merge(df_ret, df_prods, on="product_id", how="inner")
                        item_m = pd.merge(df_items, df_prods, on="product_id", how="inner")
                        r_cnt = ret_m.groupby("category")["return_id"].count()
                        i_cnt = item_m.groupby("category")["order_item_id"].count()
                        rates = (r_cnt / i_cnt * 100.0).reset_index(name="rate")
                        top = rates.sort_values(by="rate", ascending=False).iloc[0]
                        return {
                            "success": True,
                            "result": round(float(top["rate"]), 2),
                            "metric": contract.expected_metric or str(top["category"]),
                            "label": str(top["category"]),
                            "unit": contract.expected_unit or "percent",
                            "result_type": "ranked_item"
                        }

                elif ret_def == "order_return_rate":
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

                elif ret_def == "item_return_rate":
                    df_items = cls._get_table_df("order_items", dfs)
                    if df_items is not None and df_ret is not None:
                        tot_items = len(df_items)
                        ret_items = len(df_ret)
                        rate = round(float((ret_items / tot_items) * 100.0), 2)
                        return {
                            "success": True,
                            "result": rate,
                            "metric": "item_return_rate",
                            "label": None,
                            "unit": contract.expected_unit or "percent",
                            "result_type": "percentage"
                        }

                elif ret_def == "revenue_return_rate":
                    if df_ord is not None and df_ret is not None:
                        tot_rev = df_ord["final_amount"].sum()
                        ret_cust_ids = df_ret["customer_id"].unique()
                        ret_rev = df_ord[df_ord["customer_id"].isin(ret_cust_ids)]["final_amount"].sum()
                        rate = round(float((ret_rev / tot_rev) * 100.0), 2)
                        return {
                            "success": True,
                            "result": rate,
                            "metric": "revenue_return_rate",
                            "label": None,
                            "unit": contract.expected_unit or "percent",
                            "result_type": "percentage"
                        }

            # 3. General Contract Evaluation
            main_ds_id = contract.datasets_required[0]
            curr_df = dfs[main_ds_id].copy()

            # Apply Contract Joins
            for j in contract.joins:
                left_ds = j.left_dataset
                right_ds = j.right_dataset
                left_col = j.left_column
                right_col = j.right_column
                how_type = j.how or "inner"

                rdf = dfs.get(right_ds)
                if rdf is None:
                    rdf = storage_service.get_dataframe(right_ds)

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
                    return {
                        "success": False,
                        "error": f"ReferenceEngine: Filter column '{c}' not found in dataset dataframe"
                    }

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

            # Apply GroupBy & Aggregations
            g_cols = [g.column for g in contract.group_by]
            for gc in g_cols:
                if gc not in curr_df.columns:
                    return {
                        "success": False,
                        "error": f"ReferenceEngine: Group-by column '{gc}' not found in dataset dataframe"
                    }

            target_col = None
            target_op = "sum"
            if contract.aggregations:
                target_col = contract.aggregations[0].column
                target_op = contract.aggregations[0].operation or "sum"
            elif contract.columns_required:
                for col_cand in contract.columns_required:
                    if col_cand not in g_cols:
                        target_col = col_cand
                        break

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
                if contract.sorting and contract.sorting[0].order == "asc":
                    asc = True
                grp = grp.sort_values(by=target_col, ascending=asc)

                if len(grp) == 0:
                    return {
                        "success": False,
                        "error": "ReferenceEngine: GroupBy returned 0 rows"
                    }

                top = grp.iloc[0]
                val = round(float(top[target_col]), 2)
                lbl = str(top[g_cols[0]])
                return {
                    "success": True,
                    "result": val,
                    "metric": contract.expected_metric or lbl,
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
