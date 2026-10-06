import shutil
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.models.dataset import DatasetMetadata, DatasetProfile, DatasetArtifact
from backend.models.document import DocumentMetadata, DocumentChunk
from backend.services.persistence import SQLitePersistenceManager
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler

class StorageService:
    """Local storage service managing dataset artifacts, DataFrames, profiles, documents, vector indexes, and persistent SQLite metadata."""

    def __init__(self, persistence_manager: SQLitePersistenceManager | None = None):
        self.data_dir: Path = settings.DATA_DIR
        self.doc_dir: Path = settings.DOCUMENT_DIR
        self.storage_dir: Path = settings.STORAGE_DIR
        self.workspace_dir: Path = settings.STORAGE_DIR / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.persistence = persistence_manager or SQLitePersistenceManager()

        self.datasets_meta: Dict[str, DatasetMetadata] = {}
        self.dataset_profiles: Dict[str, DatasetProfile] = {}
        self.dataset_artifacts: Dict[str, DatasetArtifact] = {}
        self.dataframes: Dict[str, pd.DataFrame] = {}

        self.documents_meta: Dict[str, DocumentMetadata] = {}
        self.document_chunks: Dict[str, List[DocumentChunk]] = {}

        self.analysis_runs: Dict[str, Dict[str, Any]] = {}

        # Recover persisted state on initialization
        self._recover_from_persistence()

    def _recover_from_persistence(self):
        # 1. Recover Datasets
        dataset_records = self.persistence.load_datasets()
        for meta, file_path_str, profile in dataset_records:
            fpath = Path(file_path_str)
            if fpath.exists():
                try:
                    df, _ = FileManager.ingest_dataset(fpath, dataset_id=meta.dataset_id)
                    ws_path = self._prepare_workspace_dataset(meta.dataset_id, fpath)
                    artifact = DatasetArtifact(
                        dataset_id=meta.dataset_id,
                        filename=meta.filename,
                        file_path=str(fpath.resolve()),
                        workspace_path=str(ws_path.resolve()),
                        file_type=meta.file_type,
                        profile=profile,
                        metadata=meta
                    )
                    self.datasets_meta[meta.dataset_id] = meta
                    self.dataset_profiles[meta.dataset_id] = profile
                    self.dataset_artifacts[meta.dataset_id] = artifact
                    self.dataframes[meta.dataset_id] = df
                except Exception:
                    pass

        # 2. Recover Documents
        doc_records = self.persistence.load_documents()
        for meta, file_path_str, chunks in doc_records:
            self.documents_meta[meta.document_id] = meta
            self.document_chunks[meta.document_id] = chunks

        # 3. Recover Runs
        self.analysis_runs = self.persistence.load_analysis_runs()

    def _prepare_workspace_dataset(self, dataset_id: str, original_path: Path) -> Path:
        ds_ws_dir = self.workspace_dir / dataset_id
        ds_ws_dir.mkdir(parents=True, exist_ok=True)
        target_file = ds_ws_dir / f"data{original_path.suffix.lower()}"
        if not target_file.exists() or original_path.stat().st_mtime > target_file.stat().st_mtime:
            shutil.copy2(original_path, target_file)
        return target_file

    def save_dataset(self, metadata: DatasetMetadata, original_path: Path, df: pd.DataFrame, profile: DatasetProfile) -> DatasetArtifact:
        ws_path = self._prepare_workspace_dataset(metadata.dataset_id, original_path)
        
        artifact = DatasetArtifact(
            dataset_id=metadata.dataset_id,
            filename=metadata.filename,
            file_path=str(original_path.resolve()),
            workspace_path=str(ws_path.resolve()),
            file_type=metadata.file_type,
            profile=profile,
            metadata=metadata
        )

        self.datasets_meta[metadata.dataset_id] = metadata
        self.dataset_profiles[metadata.dataset_id] = profile
        self.dataset_artifacts[metadata.dataset_id] = artifact
        self.dataframes[metadata.dataset_id] = df

        self.persistence.save_dataset(metadata, str(original_path.resolve()), profile)
        return artifact

    def get_dataset_artifact(self, dataset_id: str) -> Optional[DatasetArtifact]:
        return self.dataset_artifacts.get(dataset_id)

    def get_dataset_metadata(self, dataset_id: str) -> Optional[DatasetMetadata]:
        return self.datasets_meta.get(dataset_id)

    def get_dataset_profile(self, dataset_id: str) -> Optional[DatasetProfile]:
        return self.dataset_profiles.get(dataset_id)

    def get_dataframe(self, dataset_id: str) -> Optional[pd.DataFrame]:
        return self.dataframes.get(dataset_id)

    def list_datasets(self) -> List[DatasetMetadata]:
        return list(self.datasets_meta.values())

    def save_document(self, metadata: DocumentMetadata, original_path: Path, chunks: List[DocumentChunk]):
        self.documents_meta[metadata.document_id] = metadata
        self.document_chunks[metadata.document_id] = chunks

        self.persistence.save_document(metadata, str(original_path.resolve()), chunks)

    def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        return self.documents_meta.get(document_id)

    def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        return self.document_chunks.get(document_id, [])

    def list_documents(self) -> List[DocumentMetadata]:
        return list(self.documents_meta.values())

    def save_analysis_run(self, analysis_id: str, question: str, status: str, result_dict: Dict[str, Any]):
        self.analysis_runs[analysis_id] = result_dict
        created_at = pd.Timestamp.now().isoformat()
        self.persistence.save_analysis_run(analysis_id, question, status, result_dict, created_at)

    def get_analysis_run(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return self.analysis_runs.get(analysis_id)

# Singleton global storage instance
storage_service = StorageService()
