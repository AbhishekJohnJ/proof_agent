from typing import Any, Dict, List
from backend.providers.base import CodeGenerationProvider

class MockCodeGenerationProvider(CodeGenerationProvider):
    """Mock Code Generation Provider producing verified Pandas code for multi-table Kaggle datasets and synthetic benchmark tests."""

    def generate_code(
        self,
        question: str,
        dataset_schemas: List[Dict[str, Any]],
        quality_warnings: List[Dict[str, Any]],
        analysis_contract: Any = None
    ) -> Dict[str, Any]:
        q_lower = question.lower()
        
        # Build lookup from table name -> dataset_id
        ds_map = {}
        for s in dataset_schemas:
            fname = s.get("filename", "").lower()
            ds_id = s.get("dataset_id", "")
            if "customer_reviews" in fname or "review" in ds_id:
                ds_map["reviews"] = ds_id
            elif "customer" in fname or "cust" in ds_id:
                ds_map["customers"] = ds_id
            elif "order_item" in fname or "item" in ds_id:
                ds_map["order_items"] = ds_id
            elif "order" in fname or "ord" in ds_id:
                ds_map["orders"] = ds_id
            elif "product" in fname or "prod" in ds_id:
                ds_map["products"] = ds_id
            elif "return" in fname or "ret" in ds_id:
                ds_map["returns"] = ds_id

        ds_id_default = dataset_schemas[0].get("dataset_id", "ds_default") if dataset_schemas else "ds_default"

        # 1. Premium Customer Revenue
        if "premium" in q_lower and ("revenue" in q_lower or "sales" in q_lower or "order" in q_lower or "spend" in q_lower) and "customers" in ds_map and "orders" in ds_map:
            ds_cust = ds_map["customers"]
            ds_ord = ds_map["orders"]
            
            code = f"""import pandas as pd
import json

df_cust = pd.read_csv("data/{ds_cust}/data.csv")
df_ord = pd.read_csv("data/{ds_ord}/data.csv")

merged = pd.merge(df_ord, df_cust, on="customer_id")
seg_col = "customer_segment" if "customer_segment" in merged.columns else ("tier" if "tier" in merged.columns else merged.columns[0])
premium_df = merged[merged[seg_col].astype(str).str.lower() == "premium"]
rev_col = "final_amount" if "final_amount" in premium_df.columns else ("amount" if "amount" in premium_df.columns else "item_revenue")
total_rev = round(float(premium_df[rev_col].sum()), 2)

print(json.dumps({{"result": total_rev, "metric": "premium_customer_revenue", "unit": "INR"}}))
"""
            used = [ds_cust, ds_ord]

        # 2. Highest Sales / Revenue State
        elif ("state" in q_lower.split() or "states" in q_lower.split()) and ("revenue" in q_lower or "sales" in q_lower or "highest" in q_lower) and "customers" in ds_map and "orders" in ds_map:
            ds_cust = ds_map["customers"]
            ds_ord = ds_map["orders"]

            code = f"""import pandas as pd
import json

df_cust = pd.read_csv("data/{ds_cust}/data.csv")
df_ord = pd.read_csv("data/{ds_ord}/data.csv")

merged = pd.merge(df_ord, df_cust, on="customer_id")
state_sales = merged.groupby("state")["final_amount"].sum().reset_index()
top_state = state_sales.sort_values(by="final_amount", ascending=False).iloc[0]

print(json.dumps({{"result": float(round(top_state["final_amount"], 2)), "metric": str(top_state["state"]), "unit": "INR"}}))
"""
            used = [ds_cust, ds_ord]

        # 3. Product Category Revenue
        elif "category" in q_lower and ("revenue" in q_lower or "highest" in q_lower or "sales" in q_lower) and "return" not in q_lower:
            ds_items = ds_map.get("order_items", ds_id_default)
            ds_prods = ds_map.get("products", ds_id_default)

            code = f"""import pandas as pd
import json

df_items = pd.read_csv("data/{ds_items}/data.csv")
df_prods = pd.read_csv("data/{ds_prods}/data.csv")

merged = pd.merge(df_items, df_prods, on="product_id")
cat_rev = merged.groupby("category")["item_revenue"].sum().reset_index()
top_cat = cat_rev.sort_values(by="item_revenue", ascending=False).iloc[0]

print(json.dumps({{"result": float(round(top_cat["item_revenue"], 2)), "metric": str(top_cat["category"]), "unit": "INR"}}))
"""
            used = [ds_items, ds_prods]

        # 4. Product Category Return Rate
        elif "category" in q_lower and "return" in q_lower:
            ds_ret = ds_map.get("returns", ds_id_default)
            ds_prods = ds_map.get("products", ds_id_default)
            ds_items = ds_map.get("order_items", ds_id_default)

            code = f"""import pandas as pd
import json

df_ret = pd.read_csv("data/{ds_ret}/data.csv")
df_prods = pd.read_csv("data/{ds_prods}/data.csv")
df_items = pd.read_csv("data/{ds_items}/data.csv")

ret_merged = pd.merge(df_ret, df_prods, on="product_id")
item_merged = pd.merge(df_items, df_prods, on="product_id")

ret_cnt = ret_merged.groupby("category")["return_id"].count()
item_cnt = item_merged.groupby("category")["order_item_id"].count()

rates = (ret_cnt / item_cnt * 100.0).reset_index(name="rate")
top_row = rates.sort_values(by="rate", ascending=False).iloc[0]

print(json.dumps({{"result": float(round(top_row["rate"], 2)), "metric": str(top_row["category"]), "unit": "percent"}}))
"""
            used = [ds_ret, ds_prods, ds_items]

        # 5. Revenue from Customers who Returned Products
        elif "returned" in q_lower and ("customer" in q_lower or "revenue" in q_lower) and "category" not in q_lower:
            ds_ord = ds_map.get("orders", ds_id_default)
            ds_ret = ds_map.get("returns", ds_id_default)

            code = f"""import pandas as pd
import json

df_ord = pd.read_csv("data/{ds_ord}/data.csv")
df_ret = pd.read_csv("data/{ds_ret}/data.csv")

unique_ret_cust = df_ret[["customer_id"]].drop_duplicates()
merged = pd.merge(df_ord, unique_ret_cust, on="customer_id", how="inner")
total_rev = round(float(merged["final_amount"].sum()), 2)

print(json.dumps({{"result": total_rev, "metric": "returning_customers_revenue", "unit": "INR"}}))
"""
            used = [ds_ord, ds_ret]

        # 6. Percentage of Orders Returned (Return Rate)
        elif "percentage" in q_lower or ("return" in q_lower and "rate" in q_lower) or ("returned" in q_lower and "orders" in q_lower):
            ds_ord = ds_map.get("orders", ds_id_default)
            ds_ret = ds_map.get("returns", ds_id_default)

            code = f"""import pandas as pd
import json

df_ord = pd.read_csv("data/{ds_ord}/data.csv")
df_ret = pd.read_csv("data/{ds_ret}/data.csv")

merged = pd.merge(df_ord, df_ret, on="order_id", how="inner")
total_orders = len(df_ord)
ret_orders = merged["order_id"].nunique()
rate = round((ret_orders / total_orders) * 100.0, 2)
cnt = merged["order_id"].count()

print(json.dumps({{"result": float(rate), "metric": "order_return_rate", "unit": "percent"}}))
"""
            used = [ds_ord, ds_ret]

        # 7. Customer Segment Highest AOV
        elif "segment" in q_lower and ("aov" in q_lower or "average order value" in q_lower):
            ds_cust = ds_map.get("customers", ds_id_default)
            ds_ord = ds_map.get("orders", ds_id_default)

            code = f"""import pandas as pd
import json

df_cust = pd.read_csv("data/{ds_cust}/data.csv")
df_ord = pd.read_csv("data/{ds_ord}/data.csv")

merged = pd.merge(df_ord, df_cust, on="customer_id")
seg_aov = merged.groupby("customer_segment")["final_amount"].mean().reset_index()
top_seg = seg_aov.sort_values(by="final_amount", ascending=False).iloc[0]

print(json.dumps({{"result": float(round(top_seg["final_amount"], 2)), "metric": str(top_seg["customer_segment"]), "unit": "INR"}}))
"""
            used = [ds_cust, ds_ord]

        # 8. Average Order Value
        elif "average order value" in q_lower or "aov" in q_lower:
            ds_ord = ds_map.get("orders", ds_id_default)
            code = f"""import pandas as pd
import json

df_ord = pd.read_csv("data/{ds_ord}/data.csv")
aov = round(float(df_ord["final_amount"].mean()), 2)

print(json.dumps({{"result": aov, "metric": "average_order_value", "unit": "INR"}}))
"""
            used = [ds_ord]

        # 9. Total Revenue
        elif "revenue" in q_lower or "sales" in q_lower or "total" in q_lower:
            ds_ord = ds_map.get("orders", ds_id_default)
            code = f"""import pandas as pd
import json

df = pd.read_csv("data/{ds_ord}/data.csv")
df = df.drop_duplicates()
rev_col = "final_amount" if "final_amount" in df.columns else [c for c in df.columns if "revenue" in c.lower() or "amount" in c.lower()][0]
total_rev = round(float(df[rev_col].dropna().sum()), 2)

print(json.dumps({{"result": total_rev, "metric": "total_revenue", "unit": "INR"}}))
"""
            used = [ds_ord]

        # 10. Default / Row Count
        else:
            code = f"""import pandas as pd
import json

df = pd.read_csv("data/{ds_id_default}/data.csv")
cnt = int(len(df))

print(json.dumps({{"result": float(cnt), "metric": "record_count", "unit": "count"}}))
"""
            used = [ds_id_default]

        return {
            "code": code,
            "explanation": "[MOCK CODE GENERATOR] Generated Pandas code operating on Kaggle dataset workspace paths.",
            "expected_result_type": "number",
            "datasets_used": used
        }
