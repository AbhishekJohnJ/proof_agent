import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.models.dataset import DatasetMetadata, DatasetProfile
from backend.models.document import DocumentMetadata, DocumentChunk

class StorageService:
    """Local storage service managing dataset files, DataFrames, profiles, documents, and runs."""

    def __init__(self):
        self.data_dir: Path = settings.DATA_DIR
        self.doc_dir: Path = settings.DOCUMENT_DIR
        self.storage_dir: Path = settings.STORAGE_DIR

        self.datasets_meta: Dict[str, DatasetMetadata] = {}
        self.dataset_profiles: Dict[str, DatasetProfile] = {}
        self.dataframes: Dict[str, pd.DataFrame] = {}

        self.documents_meta: Dict[str, DocumentMetadata] = {}
        self.document_chunks: Dict[str, List[DocumentChunk]] = {}

        self.analysis_runs: Dict[str, Dict[str, Any]] = {}

    def save_dataset(self, metadata: DatasetMetadata, df: pd.DataFrame, profile: DatasetProfile):
        self.datasets_meta[metadata.dataset_id] = metadata
        self.dataframes[metadata.dataset_id] = df
        self.dataset_profiles[metadata.dataset_id] = profile

    def get_dataset_metadata(self, dataset_id: str) -> Optional[DatasetMetadata]:
        return self.datasets_meta.get(dataset_id)

    def get_dataset_profile(self, dataset_id: str) -> Optional[DatasetProfile]:
        return self.dataset_profiles.get(dataset_id)

    def get_dataframe(self, dataset_id: str) -> Optional[pd.DataFrame]:
        return self.dataframes.get(dataset_id)

    def list_datasets(self) -> List[DatasetMetadata]:
        return list(self.datasets_meta.values())

    def save_document(self, metadata: DocumentMetadata, chunks: List[DocumentChunk]):
        self.documents_meta[metadata.document_id] = metadata
        self.document_chunks[metadata.document_id] = chunks

    def get_document_metadata(self, document_id: str) -> Optional[DocumentMetadata]:
        return self.documents_meta.get(document_id)

    def list_documents(self) -> List[DocumentMetadata]:
        return list(self.documents_meta.values())

    def save_analysis_run(self, analysis_id: str, data: Dict[str, Any]):
        self.analysis_runs[analysis_id] = data

    def get_analysis_run(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return self.analysis_runs.get(analysis_id)

# Singleton global instance
storage_service = StorageService()
