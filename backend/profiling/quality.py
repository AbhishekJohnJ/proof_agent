import re
import pandas as pd
from typing import List
from backend.models.dataset import QualityWarning

CURRENCY_SYMBOLS = [r"\$", r"€", r"£", r"¥", r"₹", r"USD", r"EUR", r"GBP", r"JPY", r"INR"]
CURRENCY_REGEX = re.compile(r"(\$|€|£|¥|₹|USD|EUR|GBP|JPY|INR)", re.IGNORECASE)

class QualityEngine:
    """Deterministic Data Quality Engine checking for traps, anomalies, mixed currencies, ambiguous dates."""

    @classmethod
    def analyze(cls, df: pd.DataFrame) -> List[QualityWarning]:
        warnings: List[QualityWarning] = []

        # A. Missing values
        total_missing = int(df.isnull().sum().sum())
        if total_missing > 0:
            cols_with_missing = [str(c) for c in df.columns if df[c].isnull().any()]
            missing_pct = round((total_missing / (len(df) * len(df.columns))) * 100, 2)
            warnings.append(QualityWarning(
                severity="warning" if missing_pct < 20 else "critical",
                type="missing_values",
                message=f"Dataset contains {total_missing} missing values ({missing_pct}% total cells missing).",
                affected_columns=cols_with_missing
            ))

        # B. Duplicate rows
        dup_rows = int(df.duplicated().sum())
        if dup_rows > 0:
            warnings.append(QualityWarning(
                severity="critical" if dup_rows > len(df) * 0.05 else "warning",
                type="duplicate_rows",
                message=f"Detected {dup_rows} exact duplicate rows.",
                affected_columns=list(map(str, df.columns))
            ))

        # C. Constant columns, duplicate IDs, mixed currency
        for col in df.columns:
            col_str = str(col)
            non_null = df[col].dropna()
            
            # Constant column check
            if len(non_null.unique()) == 1 and len(df) > 1:
                warnings.append(QualityWarning(
                    severity="warning",
                    type="constant_column",
                    message=f"Column '{col_str}' contains a constant value ('{non_null.iloc[0]}') across all non-null rows.",
                    affected_columns=[col_str]
                ))

            # Potential ID duplication check
            if "id" in col_str.lower() or "key" in col_str.lower() or "code" in col_str.lower():
                if non_null.duplicated().any():
                    warnings.append(QualityWarning(
                        severity="critical",
                        type="duplicate_candidate_id",
                        message=f"Candidate identifier column '{col_str}' contains duplicate non-null keys.",
                        affected_columns=[col_str]
                    ))

            # G & H. Mixed currency / units check
            if "currency" in col_str.lower() or "unit" in col_str.lower() or "amount" in col_str.lower() or "price" in col_str.lower() or df[col].dtype == "object":
                str_vals = non_null.astype(str)
                found_currencies = set()
                for v in str_vals:
                    matches = CURRENCY_REGEX.findall(v)
                    for m in matches:
                        found_currencies.add(m.upper())

                if len(found_currencies) > 1 or ("currency" in col_str.lower() and len(non_null.unique()) > 1):
                    warnings.append(QualityWarning(
                        severity="critical",
                        type="mixed_currency",
                        message=f"Column '{col_str}' contains multiple distinct currency formats/units.",
                        affected_columns=[col_str]
                    ))

            # E & F. Ambiguous dates check
            if df[col].dtype == "object" or "date" in col_str.lower() or "time" in col_str.lower():
                cls._check_date_ambiguity(df[col], col_str, warnings)

        return warnings

    @classmethod
    def _check_date_ambiguity(cls, series: pd.Series, col_name: str, warnings: List[QualityWarning]):
        non_null = series.dropna().astype(str)
        ambiguous_pattern_count = 0
        for val in non_null.head(50):
            parts = re.split(r"[-/\.]", val.strip())
            if len(parts) == 3:
                try:
                    p1, p2 = int(parts[0]), int(parts[1])
                    if 1 <= p1 <= 12 and 1 <= p2 <= 12 and p1 != p2:
                        ambiguous_pattern_count += 1
                except ValueError:
                    pass
        
        if ambiguous_pattern_count > 0:
            warnings.append(QualityWarning(
                severity="warning",
                type="ambiguous_date",
                message=f"Column '{col_name}' contains ambiguous date strings (day/month order unconfirmed, e.g. '01/02/2024').",
                affected_columns=[col_name]
            ))
