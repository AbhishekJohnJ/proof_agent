import pandas as pd
from typing import Dict, Any, List, Optional

class JoinChecker:
    """Validates multi-table joins, key integrity, and detects row explosion."""

    @classmethod
    def validate_join(
        cls,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_key: str,
        right_key: str,
        how: str = "inner",
        expected_cardinality: Optional[str] = "many_to_one"
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

        null_left = left_df[left_key].isnull().sum()
        null_right = right_df[right_key].isnull().sum()

        merged = pd.merge(left_df, right_df, left_on=left_key, right_on=right_key, how=how)
        rows_after = len(merged)

        is_explosion = False
        warning = None
        critical_issue = None

        max_expected = max(rows_left, rows_right)
        if rows_after > max_expected * 1.2 and rows_after > 50:
            is_explosion = True
            warning = f"Join cardinality expansion detected: {rows_left} left / {rows_right} right -> {rows_after} merged rows."
            if rows_after > max_expected * 2.5:
                critical_issue = f"Critical join explosion detected: merged rows ({rows_after}) exceeded expected limit ({max_expected})."

        return {
            "valid": critical_issue is None,
            "rows_before_left": rows_left,
            "rows_before_right": rows_right,
            "rows_after": rows_after,
            "null_keys_left": int(null_left),
            "null_keys_right": int(null_right),
            "is_explosion": is_explosion,
            "warning": warning,
            "critical_issue": critical_issue
        }
