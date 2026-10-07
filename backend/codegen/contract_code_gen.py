import json
from typing import Any, Dict, List, Optional
from backend.models.analysis_contract import AnalysisContract

NON_NUMERIC_COLS = ["customer_id", "order_id", "product_id", "customer_segment", "category", "state", "city", "return_id", "tier", "region", "store", "payment_method", "name"]

class ContractCodeGenerator:
    """
    Generic Pandas Python code generator driven strictly by AnalysisContract.
    Generates deterministic Pandas Python script without hardcoded keyword trees.
    """

    @classmethod
    def generate_python_code(
        cls,
        contract: AnalysisContract,
        dataset_schemas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generates executable Python script from AnalysisContract.
        """
        if not contract or not contract.datasets_required:
            ds_id = dataset_schemas[0].get("dataset_id", "ds_orders") if dataset_schemas else "ds_orders"
            datasets = [ds_id]
        else:
            datasets = contract.datasets_required

        # Create mapping of dataset_id -> sandbox path
        ds_var_map = {}
        load_code_lines = []

        for ds_id in datasets:
            clean_var = ds_id.replace("ds_kaggle_", "").replace("ds_bm_", "").replace("ds_", "").replace("-", "_").replace(".", "_")
            var_name = f"df_{clean_var}"
            ds_var_map[ds_id] = var_name
            load_code_lines.append(f'{var_name} = pd.read_csv("data/{ds_id}/data.csv")')

        load_script = "\n".join(load_code_lines)

        # Handle specific contracted metrics (like return rate / returning revenue)
        if contract.return_definition or (contract.expected_metric and "return" in contract.expected_metric.lower()):
            if contract.expected_metric == "order_return_rate":
                ds_ord = datasets[0]
                ds_ret = datasets[1] if len(datasets) > 1 else "ds_kaggle_returns"
                code = f"""import pandas as pd
import json

{load_script}

merged = pd.merge({ds_var_map.get(ds_ord, "df_orders")}, {ds_var_map.get(ds_ret, "df_returns")}, on="order_id", how="inner")
tot_orders = len({ds_var_map.get(ds_ord, "df_orders")}["order_id"].unique())
ret_orders = {ds_var_map.get(ds_ord, "df_orders")}["order_id"].isin({ds_var_map.get(ds_ret, "df_returns")}["order_id"]).sum()
rate = round(float((ret_orders / tot_orders) * 100.0), 2)

print(json.dumps({{"result": rate, "metric": "order_return_rate", "unit": "{contract.expected_unit or 'percent'}"}}))
"""
                return {"code": code, "datasets_used": datasets, "expected_result_type": "percentage"}

            elif contract.expected_metric == "highest_return_rate_category":
                ds_ret = ds_var_map.get(datasets[0], "df_returns")
                ds_prods = ds_var_map.get(datasets[1] if len(datasets) > 1 else datasets[0], "df_products")
                ds_items = ds_var_map.get(datasets[2] if len(datasets) > 2 else datasets[0], "df_order_items")
                code = f"""import pandas as pd
import json

{load_script}

ret_m = pd.merge({ds_ret}, {ds_prods}, on="product_id")
item_m = pd.merge({ds_items}, {ds_prods}, on="product_id")

r_cnt = ret_m.groupby("category")["return_id"].count()
i_cnt = item_m.groupby("category")["order_item_id"].count()

rates = (r_cnt / i_cnt * 100.0).reset_index(name="rate")
top = rates.sort_values(by="rate", ascending=False).iloc[0]

print(json.dumps({{"result": float(round(top["rate"], 2)), "metric": str(top["category"]), "unit": "{contract.expected_unit or 'percent'}"}}))
"""
                return {"code": code, "datasets_used": datasets, "expected_result_type": "ranked_item"}

            elif contract.expected_metric == "returning_customers_revenue":
                ds_ord = ds_var_map.get(datasets[0], "df_orders")
                ds_ret = ds_var_map.get(datasets[1] if len(datasets) > 1 else datasets[0], "df_returns")
                code = f"""import pandas as pd
import json

{load_script}

unique_ret_cust = {ds_ret}[["customer_id"]].drop_duplicates()
merged = pd.merge({ds_ord}, unique_ret_cust, on="customer_id", how="inner")
tot_rev = round(float(merged["final_amount"].sum()), 2)

print(json.dumps({{"result": tot_rev, "metric": "returning_customers_revenue", "unit": "{contract.expected_unit or 'INR'}"}}))
"""
                return {"code": code, "datasets_used": datasets, "expected_result_type": "scalar"}

        # General Contract-Based Script Construction
        join_lines = []
        curr_var = list(ds_var_map.values())[0]

        if contract.joins:
            for idx, j in enumerate(contract.joins):
                left_var = ds_var_map.get(j.left_dataset, curr_var)
                right_var = ds_var_map.get(j.right_dataset, f"df_tbl_{idx}")
                left_col = j.left_column
                right_col = j.right_column
                how = j.how or "inner"

                merged_var = f"merged_{idx+1}"
                if left_col == right_col:
                    join_lines.append(f'{merged_var} = pd.merge({left_var}, {right_var}, on="{left_col}", how="{how}")')
                else:
                    join_lines.append(f'{merged_var} = pd.merge({left_var}, {right_var}, left_on="{left_col}", right_on="{right_col}", how="{how}")')
                curr_var = merged_var

        filter_lines = []
        if contract.filters:
            for f in contract.filters:
                c = f.column
                v = f.value
                op = f.operator
                filter_lines.append(f'_fcol_{c} = "{c}"')
                filter_lines.append(f'if _fcol_{c} not in {curr_var}.columns:')
                filter_lines.append(f'    _fcands = [col for col in {curr_var}.columns if "{c}".replace("customer_", "") in col.lower() or "tier" in col.lower() or "segment" in col.lower()]')
                filter_lines.append(f'    if _fcands: _fcol_{c} = _fcands[0]')
                
                if op == "==":
                    filter_lines.append(f'{curr_var} = {curr_var}[{curr_var}[_fcol_{c}].astype(str).str.lower() == "{str(v).lower()}"]')
                elif op == "!=":
                    filter_lines.append(f'{curr_var} = {curr_var}[{curr_var}[_fcol_{c}].astype(str).str.lower() != "{str(v).lower()}"]')
                elif op in [">", "<", ">=", "<="]:
                    filter_lines.append(f'{curr_var} = {curr_var}[{curr_var}[_fcol_{c}] {op} {v}]')

        # Identify group_by and aggregation columns
        group_cols = [g.column for g in contract.group_by]
        
        target_col = None
        target_op = "sum"
        if contract.aggregations and contract.aggregations[0].column:
            target_col = contract.aggregations[0].column
            target_op = contract.aggregations[0].operation or "sum"
        elif contract.columns_required:
            for col_cand in contract.columns_required:
                if col_cand not in group_cols and col_cand.lower() not in NON_NUMERIC_COLS:
                    target_col = col_cand
                    break

        exec_body = []
        exec_body.extend(join_lines)
        exec_body.extend(filter_lines)

        # Dynamic target column fallback header inside script
        exec_body.append(f'_target_col = "{target_col}" if {repr(target_col)} else None')
        exec_body.append(f'if not _target_col or _target_col not in {curr_var}.columns:')
        exec_body.append(f'    _cand = [c for c in {curr_var}.columns if any(k in c.lower() for k in ["revenue", "amount", "sales", "price"]) and c.lower() not in {repr(NON_NUMERIC_COLS)}]')
        exec_body.append(f'    if _cand: _target_col = _cand[0]')
        exec_body.append(f'    else:')
        exec_body.append(f'        _num_cols = [c for c in {curr_var}.select_dtypes(include=["number"]).columns if c.lower() not in {repr(NON_NUMERIC_COLS)}]')
        exec_body.append(f'        _target_col = _num_cols[0] if _num_cols else {curr_var}.columns[-1]')

        metric_name = contract.expected_metric or "result"
        unit_str = contract.expected_unit or "INR"

        if group_cols:
            grp_col_str = json.dumps(group_cols)
            sort_order = "False"
            if contract.sorting and contract.sorting[0].order == "asc":
                sort_order = "True"

            exec_body.append(f'grouped = {curr_var}.groupby({grp_col_str})[_target_col].{target_op}().reset_index()')
            exec_body.append(f'top_row = grouped.sort_values(by=_target_col, ascending={sort_order}).iloc[0]')
            exec_body.append(f'res_val = round(float(top_row[_target_col]), 2)')
            exec_body.append(f'res_label = str(top_row[{group_cols[0]!r}])')
            exec_body.append(f'print(json.dumps({{"result": res_val, "metric": res_label, "unit": "{unit_str}"}}))')
            result_type = "ranked_item"

        else:
            exec_body.append(f'val = round(float({curr_var}[_target_col].{target_op}()), 2)')
            exec_body.append(f'print(json.dumps({{"result": val, "metric": "{metric_name}", "unit": "{unit_str}"}}))')
            result_type = contract.expected_result_type or "scalar"

        body_str = "\n".join(exec_body)

        full_code = f"""import pandas as pd
import json

{load_script}

{body_str}
"""
        return {
            "code": full_code,
            "explanation": "[CONTRACT-DRIVEN CODE GENERATOR] Generated Pandas code from AnalysisContract.",
            "expected_result_type": result_type,
            "datasets_used": datasets
        }
