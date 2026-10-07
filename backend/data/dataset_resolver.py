import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from backend.services.storage import storage_service

logger = logging.getLogger(__name__)

class ResolvedDatasetArtifact(BaseModel):
    dataset_id: str
    workspace_path: str
    filename: str
    dataset_schema: Dict[str, Any] = Field(..., description="Dataset schema and column details")
    provenance: Dict[str, Any]
    unit_metadata: Dict[str, Any]
    columns: List[str]

class DatasetResolverError(Exception):
    pass

class DatasetResolver:
    """Authoritative exact dataset resolver. Enforces zero fuzzy/implicit guessing."""

    @staticmethod
    def resolve_dataset(dataset_id: str) -> ResolvedDatasetArtifact:
        if not dataset_id:
            raise DatasetResolverError("Empty dataset_id provided")

        clean_id = dataset_id.strip()
        
        # 1. Primary lookup via storage service
        artifact = storage_service.get_dataset_artifact(clean_id)
        
        # 2. If storage_service returns artifact, validate existence
        if artifact:
            workspace_path = str(artifact.workspace_path)
            file_path = Path(workspace_path)
            if not file_path.exists():
                raise DatasetResolverError(f"Dataset artifact '{clean_id}' path '{workspace_path}' does not exist on disk")

            # Extract columns reliably from profile, dataframe, or CSV header directly
            columns: List[str] = []
            df = storage_service.get_dataframe(clean_id)
            if df is not None:
                columns = [str(c) for c in df.columns]
            else:
                profile = getattr(artifact, "profile", None)
                if profile and hasattr(profile, "column_names") and profile.column_names:
                    columns = [str(c) for c in profile.column_names]
                elif profile and hasattr(profile, "column_profiles") and profile.column_profiles:
                    columns = [str(cp.name) for cp in profile.column_profiles if hasattr(cp, "name")]

            if not columns and file_path.exists():
                try:
                    df_head = pd.read_csv(file_path, nrows=0)
                    columns = [str(c) for c in df_head.columns]
                except Exception:
                    pass

            row_cnt = 0
            profile = getattr(artifact, "profile", None)
            if profile and hasattr(profile, "rows"):
                row_cnt = profile.rows
            elif artifact.metadata and hasattr(artifact.metadata, "row_count"):
                row_cnt = artifact.metadata.row_count

            d_schema = {
                "dataset_id": clean_id,
                "columns": columns,
                "row_count": row_cnt
            }

            provenance = {
                "dataset_id": clean_id,
                "filename": artifact.metadata.filename if artifact.metadata else "data.csv",
                "source": (artifact.metadata.description if artifact.metadata else None) or "registered_dataset"
            }

            unit_metadata = getattr(artifact.metadata, "unit_metadata", {}) or {
                "currency": None,
                "source": "dataset_manifest"
            }

            return ResolvedDatasetArtifact(
                dataset_id=clean_id,
                workspace_path=workspace_path,
                filename=artifact.metadata.filename if artifact.metadata else "data.csv",
                dataset_schema=d_schema,
                provenance=provenance,
                unit_metadata=unit_metadata,
                columns=columns
            )

        raise DatasetResolverError(f"Dataset '{clean_id}' could not be resolved. Strict dataset resolution failed.")
