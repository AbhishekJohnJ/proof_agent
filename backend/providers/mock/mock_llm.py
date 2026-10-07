from typing import Any, Dict, List
from backend.providers.base import LLMProvider

class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for local development & model-independent testing."""

    def __init__(self, model_name: str = "mock-qwen3-4b"):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        return f"[MOCK LLM GENERATION: {self.model_name}] Plan generated for prompt."

    def plan_query(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_lower = question.lower()

        # Build map from keyword -> dataset_id
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

        # Trap / Refusal checks
        if ("profit" in q_lower or "net_profit" in q_lower or "margin" in q_lower) and not any("profit" in str(s).lower() for s in dataset_schemas):
            return {
                "query_type": "unanswerable",
                "datasets_required": [],
                "documents_required": [],
                "columns_required": [],
                "operations": [],
                "needs_code": False,
                "needs_retrieval": False,
                "is_unanswerable": True,
                "ambiguity_flags": ["missing_profit_data"],
                "refusal_reason": "insufficient_data"
            }

        # 1. Total Revenue
        if ("total" in q_lower or "overall" in q_lower) and ("revenue" in q_lower or "sales" in q_lower) and "category" not in q_lower and "premium" not in q_lower and "returned" not in q_lower:
            ds_ord = ds_map.get("orders", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord],
                "documents_required": [],
                "columns_required": ["final_amount"],
                "operations": [{"type": "aggregate", "column": "final_amount", "operation": "sum"}],
                "aggregations": [{"operation": "sum", "column": "final_amount"}],
                "expected_metric": "total_revenue",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 2. Highest AOV Segment
        if "segment" in q_lower and ("aov" in q_lower or "average order value" in q_lower):
            ds_cust = ds_map.get("customers", ds_id_default)
            ds_ord = ds_map.get("orders", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord, ds_cust],
                "documents_required": [],
                "columns_required": ["customer_id", "customer_segment", "final_amount"],
                "joins": [{"left_dataset": ds_ord, "right_dataset": ds_cust, "left_column": "customer_id", "right_column": "customer_id"}],
                "group_by": ["customer_segment"],
                "operations": [
                    {"type": "join", "left_column": "customer_id", "right_column": "customer_id"},
                    {"type": "group_by", "column": "customer_segment"},
                    {"type": "aggregate", "column": "final_amount", "operation": "mean"}
                ],
                "expected_metric": "highest_aov_segment",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 3. Average Order Value
        if ("average order value" in q_lower or "aov" in q_lower):
            ds_ord = ds_map.get("orders", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord],
                "documents_required": [],
                "columns_required": ["final_amount"],
                "operations": [{"type": "aggregate", "column": "final_amount", "operation": "mean"}],
                "aggregations": [{"operation": "mean", "column": "final_amount"}],
                "expected_metric": "average_order_value",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 3. Product Category Revenue
        if "category" in q_lower and ("revenue" in q_lower or "sales" in q_lower or "highest" in q_lower) and "return" not in q_lower:
            ds_items = ds_map.get("order_items", ds_id_default)
            ds_prods = ds_map.get("products", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_items, ds_prods],
                "documents_required": [],
                "columns_required": ["product_id", "category", "item_revenue"],
                "joins": [{"left_dataset": ds_items, "right_dataset": ds_prods, "left_column": "product_id", "right_column": "product_id"}],
                "group_by": ["category"],
                "operations": [
                    {"type": "join", "left_column": "product_id", "right_column": "product_id"},
                    {"type": "group_by", "column": "category"},
                    {"type": "aggregate", "column": "item_revenue", "operation": "sum"}
                ],
                "expected_metric": "highest_revenue_category",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 4. Premium Customer Revenue
        if "premium" in q_lower and ("revenue" in q_lower or "sales" in q_lower or "order" in q_lower or "value" in q_lower or "spend" in q_lower):
            ds_cust = ds_map.get("customers", ds_id_default)
            ds_ord = ds_map.get("orders", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord, ds_cust],
                "documents_required": [],
                "columns_required": ["customer_id", "customer_segment", "final_amount"],
                "joins": [{"left_dataset": ds_ord, "right_dataset": ds_cust, "left_column": "customer_id", "right_column": "customer_id"}],
                "filters": [{"column": "customer_segment", "value": "Premium"}],
                "operations": [
                    {"type": "join", "left_column": "customer_id", "right_column": "customer_id"},
                    {"type": "filter", "column": "customer_segment", "value": "Premium"},
                    {"type": "aggregate", "column": "final_amount", "operation": "sum"}
                ],
                "expected_metric": "premium_customer_revenue",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 5. Highest Sales State
        if ("state" in q_lower.split() or "states" in q_lower.split()) and ("revenue" in q_lower or "sales" in q_lower or "highest" in q_lower):
            ds_cust = ds_map.get("customers", ds_id_default)
            ds_ord = ds_map.get("orders", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord, ds_cust],
                "documents_required": [],
                "columns_required": ["customer_id", "state", "final_amount"],
                "joins": [{"left_dataset": ds_ord, "right_dataset": ds_cust, "left_column": "customer_id", "right_column": "customer_id"}],
                "group_by": ["state"],
                "operations": [
                    {"type": "join", "left_column": "customer_id", "right_column": "customer_id"},
                    {"type": "group_by", "column": "state"},
                    {"type": "aggregate", "column": "final_amount", "operation": "sum"}
                ],
                "expected_metric": "highest_sales_state",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 5. Returning Customers Revenue (Check before return rate)
        if "returned" in q_lower and ("customer" in q_lower or "revenue" in q_lower) and "category" not in q_lower:
            ds_ord = ds_map.get("orders", ds_id_default)
            ds_ret = ds_map.get("returns", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord, ds_ret],
                "documents_required": [],
                "columns_required": ["customer_id", "final_amount"],
                "joins": [{"left_dataset": ds_ord, "right_dataset": ds_ret, "left_column": "customer_id", "right_column": "customer_id"}],
                "operations": [
                    {"type": "join", "left_column": "customer_id", "right_column": "customer_id"},
                    {"type": "aggregate", "column": "final_amount", "operation": "sum"}
                ],
                "expected_metric": "returning_customers_revenue",
                "expected_unit": "INR",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 6. Order Return Rate
        if "percentage" in q_lower or ("return" in q_lower and "rate" in q_lower and "category" not in q_lower) or ("returned" in q_lower and "orders" in q_lower):
            ds_ord = ds_map.get("orders", ds_id_default)
            ds_ret = ds_map.get("returns", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ord, ds_ret],
                "documents_required": [],
                "columns_required": ["order_id"],
                "return_definition": "unique returned order IDs / total orders * 100.0",
                "joins": [{"left_dataset": ds_ord, "right_dataset": ds_ret, "left_column": "order_id", "right_column": "order_id"}],
                "operations": [
                    {"type": "join", "left_column": "order_id", "right_column": "order_id"},
                    {"type": "aggregate", "operation": "count"}
                ],
                "expected_metric": "order_return_rate",
                "expected_unit": "percent",
                "needs_code": True,
                "needs_retrieval": False
            }

        # 9. Highest Return Rate Category
        if "category" in q_lower and "return" in q_lower:
            ds_ret = ds_map.get("returns", ds_id_default)
            ds_prods = ds_map.get("products", ds_id_default)
            ds_items = ds_map.get("order_items", ds_id_default)
            return {
                "query_type": "data_aggregation",
                "datasets_required": [ds_ret, ds_prods, ds_items],
                "documents_required": [],
                "columns_required": ["product_id", "category", "return_id", "order_item_id"],
                "joins": [
                    {"left_dataset": ds_ret, "right_dataset": ds_prods, "left_column": "product_id", "right_column": "product_id"},
                    {"left_dataset": ds_items, "right_dataset": ds_prods, "left_column": "product_id", "right_column": "product_id"}
                ],
                "group_by": ["category"],
                "operations": [
                    {"type": "join", "left_column": "product_id", "right_column": "product_id"},
                    {"type": "group_by", "column": "category"},
                    {"type": "aggregate", "operation": "count"}
                ],
                "expected_metric": "highest_return_rate_category",
                "expected_unit": "percent",
                "needs_code": True,
                "needs_retrieval": False
            }

        # Default plan
        req_ds = [s.get("dataset_id") for s in dataset_schemas if s.get("dataset_id")] or [ds_id_default]
        return {
            "query_type": "data_aggregation",
            "datasets_required": req_ds,
            "documents_required": [d.get("document_id") for d in document_summaries if d.get("document_id")],
            "columns_required": [],
            "operations": [{"type": "aggregate", "operation": "count"}],
            "needs_code": True,
            "needs_retrieval": len(document_summaries) > 0,
            "is_unanswerable": False,
            "ambiguity_flags": [],
            "refusal_reason": None
        }
