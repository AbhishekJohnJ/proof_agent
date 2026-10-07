import pytest

pytestmark = pytest.mark.redteam
import pandas as pd
from backend.verification.join_checker import JoinChecker

def test_join_explosion_detects_critical_issue():
    # Left table has 1,000 duplicate keys; Right table has 1,000 duplicate keys -> 1,000,000 rows output
    df1 = pd.DataFrame({"customer_id": ["C1"] * 1000, "val1": range(1000)})
    df2 = pd.DataFrame({"customer_id": ["C1"] * 1000, "val2": range(1000)})

    res = JoinChecker.validate_join(df1, df2, left_key="customer_id", right_key="customer_id", expected_cardinality="one_to_one")
    assert res["critical_issue"] is not None
    assert "expectation violated" in res["critical_issue"] or "Duplicate keys" in res["critical_issue"] or "multiplication" in res["critical_issue"]
