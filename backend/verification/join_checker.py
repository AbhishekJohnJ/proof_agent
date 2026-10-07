import pandas as pd
from typing import Dict, Any, List, Optional

class JoinChecker:
    """Validates multi-table joins, key integrity, uniqueness, and detects row explosion."""

    @classmethod
    def validate_join(
        cls,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_key: str,
        right_key: str,
        how: str = "inner",
        expected_cardinality: Optional[str] = None
    ) -> Dict[str, Any]:
        rows_left = len(left_df)
        rows_right = len(right_df)

        if left_key not in left_df.columns:
            return {
                "valid": False,
                "critical_issue": f"Left join key '{left_key}' missing from left dataframe.",
                "rows_before_left": rows_left,
                "rows_before_right": rows_right,
                "rows_after": 0,
                "is_explosion": False,
                "warning": None
            }

        if right_key not in right_df.columns:
            return {
                "valid": False,
                "critical_issue": f"Right join key '{right_key}' missing from right dataframe.",
                "rows_before_left": rows_left,
                "rows_before_right": rows_right,
                "rows_after": 0,
                "is_explosion": False,
                "warning": None
            }

        # Check domain key mismatch (e.g. order_id = customer_id)
        if left_key != right_key and ("id" in left_key.lower() and "id" in right_key.lower()):
            return {
                "valid": False,
                "critical_issue": f"Domain key mismatch: attempted to join '{left_key}' with '{right_key}'.",
                "rows_before_left": rows_left,
                "rows_before_right": rows_right,
                "rows_after": 0,
                "is_explosion": False,
                "warning": None
            }

        unique_left_keys = int(left_df[left_key].nunique())
        unique_right_keys = int(right_df[right_key].nunique())
        null_left = int(left_df[left_key].isnull().sum())
        null_right = int(right_df[right_key].isnull().sum())

        merged = pd.merge(left_df, right_df, left_on=left_key, right_on=right_key, how=how)
        rows_after = len(merged)

        is_explosion = False
        warning = None
        critical_issue = None

        max_expected = max(rows_left, rows_right)
        duplication_factor = round(rows_after / max_expected, 2) if max_expected > 0 else 1.0

        if expected_cardinality == "one_to_one":
            if rows_after > min(rows_left, rows_right):
                critical_issue = f"One-to-one join expectation violated: left={rows_left}, right={rows_right}, merged={rows_after}"
        elif expected_cardinality != "many_to_many":
            if rows_after > max_expected * 1.5 and rows_after > 50:
                is_explosion = True
                warning = f"Join cardinality expansion detected: {rows_left} left / {rows_right} right -> {rows_after} merged rows."
                if rows_after > max_expected * 2.5:
                    critical_issue = f"Critical join explosion detected ({duplication_factor}x expansion): merged rows ({rows_after}) exceeded expected limit ({max_expected})."

        return {
            "valid": critical_issue is None,
            "rows_before_left": rows_left,
            "rows_before_right": rows_right,
            "unique_left_keys": unique_left_keys,
            "unique_right_keys": unique_right_keys,
            "rows_after": rows_after,
            "null_keys_left": null_left,
            "null_keys_right": null_right,
            "duplication_factor": duplication_factor,
            "expected_cardinality": expected_cardinality,
            "is_explosion": is_explosion,
            "warning": warning,
            "critical_issue": critical_issue
        }
