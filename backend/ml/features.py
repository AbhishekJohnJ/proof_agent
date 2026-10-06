import pandas as pd
from typing import Tuple, List, Dict, Any

FORBIDDEN_LEAKAGE_COLUMNS = [
    "return_id",
    "return_date",
    "return_reason",
    "return_status",
    "refund_amount",
    "is_returned",
    "actual_delivery_date",
    "delivery_days",
    "delivery_status",
    "delayed_flag"
]

FEATURE_COLUMNS = [
    "discount_percentage",
    "final_amount",
    "subtotal",
    "shipping_fee",
    "tax_amount",
    "customer_segment",
    "gender",
    "age",
    "state",
    "shipping_method",
    "marketing_channel",
    "category",
    "price",
    "rating_average",
    "stock_quantity",
    "product_type"
]

CATEGORICAL_FEATURES = [
    "customer_segment",
    "gender",
    "state",
    "shipping_method",
    "marketing_channel",
    "category",
    "product_type"
]

def prepare_prediction_dataset(
    orders_df: pd.DataFrame,
    returns_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    order_items_df: pd.DataFrame,
    products_df: pd.DataFrame
) -> pd.DataFrame:
    """Builds pre-return order-level analytical dataset with ground truth target label is_returned."""
    # 1. Base order dataset
    df = orders_df.copy()

    # 2. Target variable: is_returned (1 if order_id exists in returns_df, else 0)
    returned_order_ids = set(returns_df["order_id"].unique())
    df["is_returned"] = df["order_id"].apply(lambda oid: 1 if oid in returned_order_ids else 0)

    # 3. Join customer attributes
    df = pd.merge(df, customers_df[["customer_id", "customer_segment", "gender", "age", "state"]], on="customer_id", how="left")

    # 4. Join primary order item & product attributes
    first_items = order_items_df.drop_duplicates(subset=["order_id"]).copy()
    items_prods = pd.merge(first_items, products_df[["product_id", "category", "price", "rating_average", "stock_quantity", "product_type"]], on="product_id", how="left")
    df = pd.merge(df, items_prods[["order_id", "category", "price", "rating_average", "stock_quantity", "product_type"]], on="order_id", how="left")

    # Fill NaNs for categorical / numeric features
    df["customer_segment"] = df["customer_segment"].fillna("Regular").astype(str)
    df["gender"] = df["gender"].fillna("Unknown").astype(str)
    df["state"] = df["state"].fillna("Unknown").astype(str)
    df["shipping_method"] = df["shipping_method"].fillna("Standard").astype(str)
    df["marketing_channel"] = df["marketing_channel"].fillna("Direct").astype(str)
    df["category"] = df["category"].fillna("General").astype(str)
    df["product_type"] = df["product_type"].fillna("Standard").astype(str)

    df["age"] = df["age"].fillna(35.0).astype(float)
    df["price"] = df["price"].fillna(500.0).astype(float)
    df["rating_average"] = df["rating_average"].fillna(4.0).astype(float)
    df["stock_quantity"] = df["stock_quantity"].fillna(100.0).astype(float)
    df["discount_percentage"] = df["discount_percentage"].fillna(0.0).astype(float)
    df["final_amount"] = df["final_amount"].fillna(0.0).astype(float)
    df["subtotal"] = df["subtotal"].fillna(0.0).astype(float)
    df["shipping_fee"] = df["shipping_fee"].fillna(0.0).astype(float)
    df["tax_amount"] = df["tax_amount"].fillna(0.0).astype(float)

    return df

def extract_features_and_target(
    prepared_df: pd.DataFrame,
    is_training: bool = True
) -> Tuple[pd.DataFrame, pd.Series | None, List[str], List[str]]:
    """Extracts feature matrix X and target y, enforcing target leakage safeguards."""
    for forbidden in FORBIDDEN_LEAKAGE_COLUMNS:
        assert forbidden not in FEATURE_COLUMNS, f"TARGET LEAKAGE DETECTED: {forbidden} in feature columns list!"

    avail_features = [col for col in FEATURE_COLUMNS if col in prepared_df.columns]
    X = prepared_df[avail_features].copy()

    avail_cats = [col for col in CATEGORICAL_FEATURES if col in X.columns]
    for cat_col in avail_cats:
        X[cat_col] = X[cat_col].astype(str)

    y = prepared_df["is_returned"] if ("is_returned" in prepared_df.columns and is_training) else None
    return X, y, avail_features, avail_cats
