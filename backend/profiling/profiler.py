import pandas as pd
from typing import List
from backend.models.dataset import DatasetProfile, ColumnProfile
from backend.profiling.quality import QualityEngine

class DataProfiler:
    """Deterministic dataset profiler producing DatasetProfile objects."""

    @classmethod
    def profile(cls, dataset_id: str, filename: str, df: pd.DataFrame) -> DatasetProfile:
        rows = len(df)
        columns = len(df.columns)
        total_missing = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        col_profiles: List[ColumnProfile] = []

        for col in df.columns:
            col_str = str(col)
            series = df[col]
            missing_cnt = int(series.isnull().sum())
            missing_pct = round((missing_cnt / rows) * 100, 2) if rows > 0 else 0.0
            unique_cnt = int(series.nunique(dropna=True))

            # Sample values (up to 3 non-null)
            sample_vals = series.dropna().head(3).tolist()
            # Convert non-serializable sample values to str if needed
            sample_vals = [str(v) if not isinstance(v, (int, float, bool, str)) else v for v in sample_vals]

            inferred_type = cls._infer_column_type(series, col_str, unique_cnt, rows)
            is_const = (unique_cnt == 1 and rows > 1)

            col_profiles.append(ColumnProfile(
                name=col_str,
                inferred_type=inferred_type,
                missing_count=missing_cnt,
                missing_percentage=missing_pct,
                unique_count=unique_cnt,
                sample_values=sample_vals,
                has_mixed_units=False,
                is_constant=is_const
            ))

        # Run Quality Engine
        quality_warnings = QualityEngine.analyze(df)

        # Determine overall quality status
        critical_count = sum(1 for w in quality_warnings if w.severity == "critical")
        warning_count = sum(1 for w in quality_warnings if w.severity == "warning")

        if critical_count > 0:
            quality_status = "poor"
        elif warning_count > 0:
            quality_status = "medium"
        else:
            quality_status = "good"

        return DatasetProfile(
            dataset_id=dataset_id,
            filename=filename,
            rows=rows,
            columns=columns,
            column_names=[str(c) for c in df.columns],
            missing_values_total=total_missing,
            duplicate_rows=duplicate_rows,
            column_profiles=col_profiles,
            quality_status=quality_status,
            quality_warnings=quality_warnings
        )

    @classmethod
    def _infer_column_type(cls, series: pd.Series, col_name: str, unique_cnt: int, total_rows: int) -> str:
        col_lower = col_name.lower()
        if "id" in col_lower or "key" in col_lower or "code" in col_lower:
            return "identifier"

        if pd.api.types.is_numeric_dtype(series):
            return "numeric"

        if pd.api.types.is_datetime64_any_dtype(series) or "date" in col_lower or "time" in col_lower:
            return "date"

        if unique_cnt < min(20, max(2, total_rows * 0.1)):
            return "categorical"

        return "text"
