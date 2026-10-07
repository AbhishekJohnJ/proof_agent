import pytest
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.models.dataset import DatasetArtifact, DatasetMetadata, DatasetProfile
from datetime import datetime

def test_unauthorized_dataset_access_fails_sandbox():
    sandbox = LocalIsolatedSandbox()

    # Code attempting to read dataset file not mounted in sandbox workspace
    unauthorized_code = """import pandas as pd
import json

df = pd.read_csv("data/ds_unauthorized_secret/data.csv")
print(json.dumps({"result": len(df)}))
"""

    meta = DatasetMetadata(
        dataset_id="ds_authorized",
        filename="data.csv",
        file_type="csv",
        rows=10,
        columns=2,
        file_size_bytes=100,
        created_at=datetime.now().isoformat()
    )
    prof = DatasetProfile(
        dataset_id="ds_authorized",
        filename="data.csv",
        rows=10,
        columns=2,
        column_names=["a", "b"],
        missing_values_total=0,
        duplicate_rows=0
    )

    art = DatasetArtifact(
        dataset_id="ds_authorized",
        filename="data.csv",
        file_path="data/ds_authorized/data.csv",
        workspace_path="data/ds_authorized/data.csv",
        file_type="csv",
        profile=prof,
        metadata=meta
    )

    res = sandbox.execute(unauthorized_code, datasets=[art])
    assert not res["success"]
    assert "FileNotFoundError" in res["stderr"] or "No such file" in res["stderr"] or res["returncode"] != 0
