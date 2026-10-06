import pandas as pd
from backend.profiling.profiler import DataProfiler

def test_profiling_sales_csv():
    df = pd.read_csv("datasets/sample/sales.csv")
    profile = DataProfiler.profile("ds_test", "sales.csv", df)

    assert profile.rows == len(df)
    assert profile.columns == len(df.columns)
    assert profile.missing_values_total == 0
    assert profile.duplicate_rows == 0
    assert profile.quality_status == "good"

def test_profiling_messy_sales():
    df = pd.read_csv("datasets/sample/messy_sales.csv")
    profile = DataProfiler.profile("ds_messy", "messy_sales.csv", df)

    assert profile.duplicate_rows > 0
    assert profile.quality_status in ["medium", "poor"]
    assert len(profile.quality_warnings) > 0
