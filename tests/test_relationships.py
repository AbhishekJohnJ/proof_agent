import pandas as pd
from backend.profiling.relationships import RelationshipDetector

def test_relationship_detection():
    customers_df = pd.read_csv("datasets/sample/customers.csv")
    orders_df = pd.read_csv("datasets/sample/orders.csv")

    candidates = RelationshipDetector.detect_relationships({
        "customers.csv": customers_df,
        "orders.csv": orders_df
    })

    assert len(candidates) > 0
    top_cand = candidates[0]
    assert "customer_id" in top_cand.left_column.lower()
    assert "customer_id" in top_cand.right_column.lower()
    assert top_cand.confidence > 0.5
