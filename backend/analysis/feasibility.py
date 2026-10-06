from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from backend.models.dataset import DatasetArtifact
from backend.models.document import DocumentMetadata

class RefusalReason(str, Enum):
    INSUFFICIENT_DATA = "insufficient_data"
    MISSING_COLUMN = "missing_column"
    AMBIGUOUS_DATE = "ambiguous_date"
    MIXED_CURRENCY = "mixed_currency"
    MIXED_UNITS = "mixed_units"
    CONFLICTING_SOURCES = "conflicting_sources"
    INVALID_QUESTION = "invalid_question"
    UNSUPPORTED_OPERATION = "unsupported_operation"
    NO_MATCHING_DATA = "no_matching_data"
    MODEL_NOT_CONFIGURED = "model_not_configured"
    SANDBOX_UNAVAILABLE = "sandbox_unavailable"
    VERIFICATION_FAILED = "verification_failed"

class FeasibilityEngine:
    """Preflight feasibility engine independently evaluating query feasibility prior to code generation."""

    @classmethod
    def evaluate_feasibility(
        cls,
        question: str,
        datasets: List[DatasetArtifact],
        documents: List[DocumentMetadata]
    ) -> Tuple[bool, Optional[RefusalReason], str, List[str]]:
        q_lower = question.lower()
        ambiguities: List[str] = []

        # 1. Dataset existence check for data queries
        if ("revenue" in q_lower or "sales" in q_lower or "amount" in q_lower or "count" in q_lower) and not datasets and not documents:
            return False, RefusalReason.INSUFFICIENT_DATA, "No dataset or document was selected.", ambiguities

        if datasets:
            all_cols = []
            has_critical_mixed_currency = False
            has_ambiguous_date = False

            for art in datasets:
                prof = art.profile
                if prof.rows == 0:
                    return False, RefusalReason.NO_MATCHING_DATA, f"Selected dataset '{art.filename}' is empty.", ambiguities

                for col_prof in prof.column_profiles:
                    all_cols.append(col_prof.name.lower())

                for w in prof.quality_warnings:
                    if w.type == "mixed_currency":
                        has_critical_mixed_currency = True
                    elif w.type == "ambiguous_date":
                        has_ambiguous_date = True

            # 2. Missing profit / cost / margin check
            if "profit" in q_lower or "margin" in q_lower:
                if not any(c in all_cols for c in ["profit", "net_profit", "margin", "cost"]):
                    return False, RefusalReason.INSUFFICIENT_DATA, "Requested metric (profit) is absent from dataset schema.", ambiguities

            # 3. Missing tax / deduction check
            if "tax" in q_lower or "deduction" in q_lower:
                if not any(c in all_cols for c in ["tax", "vat", "deduction"]):
                    return False, RefusalReason.INSUFFICIENT_DATA, "Requested column (tax) is absent from dataset schema.", ambiguities

            # 4. Ambiguous date check when filtering by date/quarter
            if ("q1" in q_lower or "q2" in q_lower or "q3" in q_lower or "q4" in q_lower or "month" in q_lower or "date" in q_lower or "quarter" in q_lower) and has_ambiguous_date:
                ambiguities.append("ambiguous_date_format")
                return False, RefusalReason.AMBIGUOUS_DATE, "Date column contains ambiguous date formats (day/month order unconfirmed).", ambiguities

            # 5. Mixed Currency check when comparing or calculating amounts on mixed currency dataset
            if ("compare" in q_lower or "total" in q_lower or "sum" in q_lower or "revenue" in q_lower or "usd" in q_lower or "eur" in q_lower) and has_critical_mixed_currency:
                return False, RefusalReason.MIXED_CURRENCY, "Cannot compare or aggregate revenue due to unhedged mixed currency values.", ambiguities

        return True, None, "", ambiguities
