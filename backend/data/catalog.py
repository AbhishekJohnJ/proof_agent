import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from backend.config import settings
from backend.services.storage import storage_service
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler

logger = logging.getLogger(__name__)

class DatasetCatalog:
    """Catalog service managing built-in Kaggle datasets, schema discovery, relationship graph, and semantic query resolution."""

    def __init__(self, manifest_path: Optional[Path] = None):
        self.manifest_path = manifest_path or Path("data/dataset_manifest.json")
        self.manifest: Dict[str, Any] = {}
        self.relationships: List[Dict[str, Any]] = []
        self.table_to_id: Dict[str, str] = {}
        self.id_to_table: Dict[str, str] = {}
        
        self._load_manifest_and_register()

    def _load_manifest_and_register(self):
        if not self.manifest_path.exists():
            logger.warning(f"Dataset manifest at {self.manifest_path} not found.")
            return

        try:
            with open(self.manifest_path, "r") as f:
                self.manifest = json.load(f)
            self.relationships = self.manifest.get("relationships", [])
        except Exception as e:
            logger.error(f"Error reading dataset manifest: {e}")
            return

        # Register Kaggle tables into storage_service as built-in datasets
        data_dir = Path("data")
        datasets_dict = self.manifest.get("datasets", {})
        
        for table_name, table_info in datasets_dict.items():
            fname = table_info.get("file", f"{table_name}.csv")
            fpath = data_dir / fname
            if not fpath.exists():
                continue

            ds_id = f"ds_kaggle_{table_name}"
            self.table_to_id[table_name] = ds_id
            self.id_to_table[ds_id] = table_name

            # Ingest & profile built-in dataset if not already in storage
            if not storage_service.get_dataset_artifact(ds_id):
                try:
                    df, metadata = FileManager.ingest_dataset(fpath, dataset_id=ds_id)
                    metadata.filename = fname
                    metadata.description = f"Built-in Kaggle table: {table_name}"
                    profile = DataProfiler.profile(ds_id, fname, df)
                    storage_service.save_dataset(metadata, fpath, df, profile)
                except Exception as ex:
                    logger.error(f"Failed auto-registering Kaggle table {table_name}: {ex}")

    def list_datasets(self) -> List[Dict[str, Any]]:
        result = []
        datasets_dict = self.manifest.get("datasets", {})
        for name, info in datasets_dict.items():
            ds_id = self.table_to_id.get(name, f"ds_kaggle_{name}")
            artifact = storage_service.get_dataset_artifact(ds_id)
            result.append({
                "dataset_id": ds_id,
                "table_name": name,
                "file": info.get("file"),
                "primary_key": info.get("primary_key"),
                "row_count": info.get("row_count"),
                "columns": info.get("columns"),
                "source": "Kaggle",
                "is_built_in": True,
                "artifact": artifact.model_dump() if artifact else None
            })
        return result

    def get_schema(self, table_or_id: str) -> Optional[Dict[str, Any]]:
        table_name = self.id_to_table.get(table_or_id, table_or_id)
        return self.manifest.get("datasets", {}).get(table_name)

    def get_relationships(self) -> List[Dict[str, Any]]:
        return self.relationships

    def resolve_dataset_by_name(self, name: str) -> Optional[str]:
        if not name:
            return None
        if name in self.id_to_table or (hasattr(storage_service, "get_dataset_artifact") and storage_service.get_dataset_artifact(name)):
            return name
        n_lower = name.lower().strip()
        if n_lower in self.table_to_id:
            return self.table_to_id[n_lower]
        for table_name, ds_id in self.table_to_id.items():
            if table_name.lower() == n_lower:
                return ds_id
        return None

    def resolve_column_by_semantic_meaning(self, intent: str) -> Optional[Tuple[str, str]]:
        """Maps natural language concepts to exact (table_name, column_name)."""
        intent_lower = intent.lower()
        if "revenue" in intent_lower or "sales" in intent_lower:
            return ("orders", "final_amount")
        elif "aov" in intent_lower or "average order value" in intent_lower:
            return ("orders", "final_amount")
        elif "customer" in intent_lower and "segment" in intent_lower:
            return ("customers", "customer_segment")
        elif "return" in intent_lower and "rate" in intent_lower:
            return ("returns", "return_id")
        elif "state" in intent_lower:
            return ("customers", "state")
        elif "category" in intent_lower:
            return ("products", "category")
        return None

    def get_join_path(self, source_table: str, target_table: str) -> Optional[Dict[str, Any]]:
        for rel in self.relationships:
            if (rel["source_table"] == source_table and rel["target_table"] == target_table) or \
               (rel["source_table"] == target_table and rel["target_table"] == source_table):
                return rel
        return None

# Global Singleton DatasetCatalog
dataset_catalog = DatasetCatalog()
