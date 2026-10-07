import logging
from typing import Dict, Any, Optional
from backend.models.analysis import CanonicalResult

logger = logging.getLogger(__name__)

class AnswerRenderer:
    """Deterministic answer renderer driven strictly by CanonicalResult."""

    @staticmethod
    def render_answer(canonical_result: CanonicalResult) -> str:
        if not canonical_result or canonical_result.result is None:
            return "No analytical result could be rendered."

        metric_name = canonical_result.metric or "The value"
        val = canonical_result.result
        unit = canonical_result.unit or ""
        result_type = canonical_result.result_type or "scalar"

        # Format metric label cleanly
        clean_metric = metric_name.replace("_", " ").title()

        # Handle Ranked Item
        if result_type == "ranked_item":
            label = canonical_result.label or "Top category"
            if isinstance(val, (int, float)):
                if unit == "INR":
                    formatted_val = f"₹{val:,.2f}"
                elif unit == "USD":
                    formatted_val = f"${val:,.2f}"
                elif unit == "EUR":
                    formatted_val = f"€{val:,.2f}"
                elif unit in ["percent", "%"]:
                    formatted_val = f"{val:.2f}%"
                else:
                    formatted_val = f"{val:,.2f} {unit}".strip()
                return f"The highest {clean_metric.lower()} was {label} with {formatted_val}."
            return f"The highest {clean_metric.lower()} was {label}."

        # Handle Percentage
        if result_type == "percentage" or unit in ["percent", "%"]:
            if isinstance(val, (int, float)):
                return f"{clean_metric} was {val:.2f}%."
            return f"{clean_metric} was {val}%."

        # Handle Numerical / Scalar
        if isinstance(val, (int, float)):
            if unit == "INR":
                formatted_val = f"₹{val:,.2f}"
            elif unit == "USD":
                formatted_val = f"${val:,.2f}"
            elif unit == "EUR":
                formatted_val = f"€{val:,.2f}"
            else:
                formatted_val = f"{val:,.2f} {unit}".strip()
            return f"{clean_metric} was {formatted_val}."

        return f"{clean_metric} was {val}."
