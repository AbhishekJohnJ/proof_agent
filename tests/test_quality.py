import pandas as pd
from backend.profiling.quality import QualityEngine

def test_quality_engine_detects_traps():
    df = pd.read_csv("datasets/sample/messy_sales.csv")
    warnings = QualityEngine.analyze(df)

    warning_types = [w.type for w in warnings]
    assert "duplicate_rows" in warning_types
    assert "missing_values" in warning_types
    assert "mixed_currency" in warning_types
    assert "constant_column" in warning_types
