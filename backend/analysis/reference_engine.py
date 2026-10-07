import math
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.models.analysis_contract import AnalysisContract

class ReferenceEngine:
    """
    Deterministic reference calculation engine providing an independent verification mechanism.
    Evaluates analysis contracts using separate, ground-truth pandas implementations.
    """

    @classmethod
    def compute_reference(
        cls,
        contract: AnalysisContract,
        dataset_files: Dict[str, Path]
    ) -> Dict[str, Any]:
        """
        Calculates reference result independently from dataset files on host.
        `dataset_files` maps table_name (or dataset_id) -> Path to CSV file.
        """
        q_lower = contract.question.lower()

        # Helper to load table by name
        def load_df(name_keyword: str) -> Optional[pd.DataFrame]:
            for key, fpath in dataset_files.items():
                if name_keyword in key.lower() or name_keyword in fpath.name.lower():
                    if fpath.exists():
                        return pd.read_csv(fpath)
            return None

        try:
            # 1. Total Revenue
            if ("total" in q_lower or "overall" in q_lower) and ("revenue" in q_lower or "sales" in q_lower) and "category" not in q_lower and "premium" not in q_lower and "returned" not in q_lower:
                df_orders = load_df("orders")
                if df_orders is not None and "final_amount" in df_orders.columns:
                    val = round(float(df_orders["final_amount"].sum()), 2)
                    return {
                        "success": True,
                        "result": val,
                        "metric": "total_revenue",
                        "label": None,
                        "unit": "INR",
                        "result_type": "scalar"
                    }

            # 2. Average Order Value
            if "average order value" in q_lower or "aov" in q_lower:
                if "segment" not in q_lower:
                    df_orders = load_df("orders")
                    if df_orders is not None and "final_amount" in df_orders.columns:
                        val = round(float(df_orders["final_amount"].mean()), 2)
                        return {
                            "success": True,
                            "result": val,
                            "metric": "average_order_value",
                            "label": None,
                            "unit": "INR",
                            "result_type": "scalar"
                        }

            # 3. Highest Revenue Category
            if "category" in q_lower and ("revenue" in q_lower or "sales" in q_lower or "highest" in q_lower) and "return" not in q_lower:
                df_items = load_df("order_items")
                df_prods = load_df("products")
                if df_items is not None and df_prods is not None:
                    merged = pd.merge(df_items, df_prods, on="product_id")
                    cat_sum = merged.groupby("category")["item_revenue"].sum().reset_index()
                    top = cat_sum.sort_values(by="item_revenue", ascending=False).iloc[0]
                    return {
                        "success": True,
                        "result": round(float(top["item_revenue"]), 2),
                        "metric": "highest_revenue_category",
                        "label": str(top["category"]),
                        "unit": "INR",
                        "result_type": "ranked_item"
                    }

            # 4. Premium Customer Revenue
            if "premium" in q_lower and ("revenue" in q_lower or "sales" in q_lower):
                df_cust = load_df("customers")
                df_ord = load_df("orders")
                if df_cust is not None and df_ord is not None:
                    merged = pd.merge(df_ord, df_cust, on="customer_id")
                    prem = merged[merged["customer_segment"].astype(str).str.lower() == "premium"]
                    val = round(float(prem["final_amount"].sum()), 2)
                    return {
                        "success": True,
                        "result": val,
                        "metric": "premium_customer_revenue",
                        "label": "Premium",
                        "unit": "INR",
                        "result_type": "scalar"
                    }

            # 5. Highest Sales State
            if ("state" in q_lower.split() or "states" in q_lower.split()) and ("revenue" in q_lower or "sales" in q_lower or "highest" in q_lower):
                df_cust = load_df("customers")
                df_ord = load_df("orders")
                if df_cust is not None and df_ord is not None:
                    merged = pd.merge(df_ord, df_cust, on="customer_id")
                    st_sum = merged.groupby("state")["final_amount"].sum().reset_index()
                    top = st_sum.sort_values(by="final_amount", ascending=False).iloc[0]
                    return {
                        "success": True,
                        "result": round(float(top["final_amount"]), 2),
                        "metric": "highest_sales_state",
                        "label": str(top["state"]),
                        "unit": "INR",
                        "result_type": "ranked_item"
                    }

            # 5. Returning Customers Revenue (Check before order return rate)
            if "returned" in q_lower and ("customer" in q_lower or "revenue" in q_lower) and "category" not in q_lower:
                df_ord = load_df("orders")
                df_ret = load_df("returns")
                if df_ord is not None and df_ret is not None:
                    ret_cust_ids = df_ret["customer_id"].unique()
                    ret_orders = df_ord[df_ord["customer_id"].isin(ret_cust_ids)]
                    val = round(float(ret_orders["final_amount"].sum()), 2)
                    return {
                        "success": True,
                        "result": val,
                        "metric": "returning_customers_revenue",
                        "label": None,
                        "unit": "INR",
                        "result_type": "scalar"
                    }

            # 6. Order Return Rate (Percentage of orders returned)
            if "percentage" in q_lower or ("return" in q_lower and "rate" in q_lower and "category" not in q_lower) or ("returned" in q_lower and "orders" in q_lower):
                df_ord = load_df("orders")
                df_ret = load_df("returns")
                if df_ord is not None and df_ret is not None:
                    tot_orders = len(df_ord)
                    ret_orders = df_ord["order_id"].isin(df_ret["order_id"]).sum()
                    rate = round((ret_orders / tot_orders) * 100.0, 2)
                    return {
                        "success": True,
                        "result": rate,
                        "metric": "order_return_rate",
                        "label": None,
                        "unit": "percent",
                        "result_type": "percentage"
                    }

            # 9. Highest Return Rate Category
            if "category" in q_lower and "return" in q_lower:
                df_ret = load_df("returns")
                df_prods = load_df("products")
                df_items = load_df("order_items")
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
                        "unit": "percent",
                        "result_type": "ranked_item"
                    }

            # Generic Contract-Based Fallback Engine
            if contract.operations:
                primary_ds = contract.datasets_required[0] if contract.datasets_required else "orders"
                df = load_df(primary_ds)
                if df is not None and contract.columns_required:
                    col = contract.columns_required[0]
                    if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                        val = round(float(df[col].dropna().sum()), 2)
                        return {
                            "success": True,
                            "result": val,
                            "metric": f"sum_{col}",
                            "label": None,
                            "unit": contract.expected_unit or "INR",
                            "result_type": "scalar"
                        }

            return {
                "success": False,
                "error": "Contract operation not supported by deterministic reference engine."
            }
        except Exception as ex:
            return {
                "success": False,
                "error": f"Reference engine execution error: {str(ex)}"
            }
