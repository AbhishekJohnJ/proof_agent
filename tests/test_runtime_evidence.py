import pytest
import pandas as pd
from pathlib import Path
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.models.dataset import DatasetArtifact, DatasetMetadata

pytestmark = pytest.mark.unit

def test_runtime_evidence_tracing():
    sandbox = LocalIsolatedSandbox()

    code = """import pandas as pd
import json

df_orders = pd.read_csv("data/ds_orders/data.csv")
df_cust = pd.read_csv("data/ds_customers/data.csv")

# Filter
df_prem = df_cust[df_cust["region"] == "North"]

# Join
m = pd.merge(df_orders, df_prem, on="category", how="inner")

# GroupBy & Aggregate
g = m.groupby("category")["revenue_x"].sum().reset_index()

# Sort & Limit
s = g.sort_values(by="revenue_x", ascending=False).head(1)

res_val = float(s["revenue_x"].iloc[0])
print(json.dumps({"result": res_val, "metric": "total_revenue"}))
"""

    from backend.ingestion.file_manager import FileManager
    from backend.profiling.profiler import DataProfiler
    from backend.services.storage import storage_service

    path = Path("datasets/sample/sales.csv")
    df1, meta1 = FileManager.ingest_dataset(path, dataset_id="ds_orders")
    prof1 = DataProfiler.profile("ds_orders", "orders.csv", df1)
    art1 = storage_service.save_dataset(meta1, path, df1, prof1)

    df2, meta2 = FileManager.ingest_dataset(path, dataset_id="ds_customers")
    prof2 = DataProfiler.profile("ds_customers", "customers.csv", df2)
    art2 = storage_service.save_dataset(meta2, path, df2, prof2)

    res = sandbox.execute(code, [art1, art2])
    assert res["success"] is True

    # Check dataset access recorded
    accessed_ds = res.get("accessed_dataset_ids", [])
    assert "ds_orders" in accessed_ds or "ds_customers" in accessed_ds

    # Check column access recorded
    accessed_cols = [c.get("column") for c in res.get("accessed_columns", [])]
    assert "region" in accessed_cols or "amount" in accessed_cols or "customer_id" in accessed_cols

    # Check runtime operations recorded
    ops = res.get("runtime_operations", [])
    op_types = [o.get("operation") for o in ops]

    assert "join" in op_types
    assert "group_by" in op_types or "groupby" in op_types
    assert "filter" in op_types or "read" in [c.get("operation") for c in res.get("accessed_columns", [])]
    assert "aggregate" in op_types or "sort" in op_types or "limit" in op_types
