from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExecutionManifest(BaseModel):
    selected_dataset_ids: List[str] = Field(default_factory=list)
    filenames: List[str] = Field(default_factory=list)
    controlled_paths: List[str] = Field(default_factory=list)
    allowed_columns: List[str] = Field(default_factory=list)
    accessed_dataset_ids: List[str] = Field(default_factory=list)

    @classmethod
    def create_manifest(cls, datasets: List[Any]) -> "ExecutionManifest":
        ids = [art.dataset_id for art in datasets]
        fnames = [art.filename for art in datasets]
        cpaths = [art.workspace_path for art in datasets]
        cols = []
        for art in datasets:
            cols.extend(art.profile.column_names)

        return ExecutionManifest(
            selected_dataset_ids=ids,
            filenames=fnames,
            controlled_paths=cpaths,
            allowed_columns=cols,
            accessed_dataset_ids=ids  # Populated based on workspace mounts
        )
