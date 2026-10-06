import pandas as pd
from typing import Dict, Any, List, Optional, Union

class DeterministicAnalyticsEngine:
    """Deterministic data analytics engine performing verified pandas calculations."""

    @staticmethod
    def filter_dataframe(df: pd.DataFrame, column: str, operator: str, value: Any) -> pd.DataFrame:
        if column not in df.columns:
            return df
        
        if operator in ["==", "eq"]:
            if isinstance(value, str):
                return df[df[column].astype(str).str.lower() == value.lower()]
            return df[df[column] == value]
        elif operator in ["!=", "ne"]:
            if isinstance(value, str):
                return df[df[column].astype(str).str.lower() != value.lower()]
            return df[df[column] != value]
        elif operator in [">", "gt"]:
            return df[df[column] > value]
        elif operator in [">=", "gte"]:
            return df[df[column] >= value]
        elif operator in ["<", "lt"]:
            return df[df[column] < value]
        elif operator in ["<=", "lte"]:
            return df[df[column] <= value]
        elif operator == "in":
            val_list = [v.lower() if isinstance(v, str) else v for v in value] if isinstance(value, list) else [value]
            return df[df[column].astype(str).str.lower().isin(val_list)]
        elif operator == "not_null":
            return df[df[column].notna()]
        return df

    @staticmethod
    def join_dataframes(
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        left_on: str,
        right_on: str,
        how: str = "inner"
    ) -> pd.DataFrame:
        return pd.merge(left_df, right_df, left_on=left_on, right_on=right_on, how=how)

    @staticmethod
    def aggregate(
        df: pd.DataFrame,
        operation: str,
        target_column: Optional[str] = None,
        group_by: Optional[List[str]] = None
    ) -> Union[float, int, Dict[str, Any], pd.DataFrame]:
        if group_by:
            grouped = df.groupby(group_by)
            if operation == "sum":
                res_df = grouped[target_column].sum().reset_index()
            elif operation == "mean":
                res_df = grouped[target_column].mean().reset_index()
            elif operation == "median":
                res_df = grouped[target_column].median().reset_index()
            elif operation == "count":
                res_df = grouped[target_column].count().reset_index() if target_column else grouped.size().reset_index(name="count")
            elif operation == "count_distinct":
                res_df = grouped[target_column].nunique().reset_index()
            elif operation == "min":
                res_df = grouped[target_column].min().reset_index()
            elif operation == "max":
                res_df = grouped[target_column].max().reset_index()
            else:
                res_df = grouped.size().reset_index(name="count")
            return res_df

        if operation == "sum":
            return float(df[target_column].sum())
        elif operation == "mean":
            return float(df[target_column].mean())
        elif operation == "median":
            return float(df[target_column].median())
        elif operation == "count":
            return int(len(df))
        elif operation == "count_distinct":
            return int(df[target_column].nunique())
        elif operation == "min":
            return float(df[target_column].min())
        elif operation == "max":
            return float(df[target_column].max())
        elif operation == "percentage":
            total = len(df)
            matching = df[target_column].sum() if target_column else len(df)
            return float((matching / total) * 100.0) if total > 0 else 0.0
        return float(len(df))

    @staticmethod
    def calculate_return_rate(orders_df: pd.DataFrame, returns_df: pd.DataFrame) -> float:
        total_orders = len(orders_df)
        if total_orders == 0:
            return 0.0
        returned_orders_count = len(returns_df["order_id"].unique())
        return round(float((returned_orders_count / total_orders) * 100.0), 2)
