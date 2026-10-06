import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.models.dataset import DatasetMetadata, DatasetProfile
from backend.models.document import DocumentMetadata, DocumentChunk

class SQLitePersistenceManager:
    """Lightweight SQLite persistence manager for ProofAI metadata and analysis runs."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or (settings.STORAGE_DIR / "proofai_metadata.sqlite3")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Datasets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Document Chunks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    section TEXT,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id)
                )
            """)

            # Analysis Runs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    analysis_id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    def save_dataset(self, metadata: DatasetMetadata, file_path: str, profile: DatasetProfile):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO datasets (dataset_id, filename, file_path, file_type, metadata_json, profile_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.dataset_id,
                metadata.filename,
                file_path,
                metadata.file_type,
                metadata.model_dump_json(),
                profile.model_dump_json(),
                metadata.created_at
            ))
            conn.commit()

    def load_datasets(self) -> List[tuple[DatasetMetadata, str, DatasetProfile]]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT metadata_json, file_path, profile_json FROM datasets")
            rows = cursor.fetchall()
            for r in rows:
                meta = DatasetMetadata.model_validate_json(r["metadata_json"])
                profile = DatasetProfile.model_validate_json(r["profile_json"])
                results.append((meta, r["file_path"], profile))
        return results

    def save_document(self, metadata: DocumentMetadata, file_path: str, chunks: List[DocumentChunk]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO documents (document_id, filename, file_path, file_type, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metadata.document_id,
                metadata.filename,
                file_path,
                metadata.file_type,
                metadata.model_dump_json(),
                metadata.created_at
            ))

            for chunk in chunks:
                cursor.execute("""
                    INSERT OR REPLACE INTO document_chunks (chunk_id, document_id, document_name, page_number, section, text, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.document_name,
                    chunk.page_number,
                    chunk.section,
                    chunk.text,
                    json.dumps(chunk.metadata)
                ))

            conn.commit()

    def load_documents(self) -> List[tuple[DocumentMetadata, str, List[DocumentChunk]]]:
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT document_id, metadata_json, file_path FROM documents")
            doc_rows = cursor.fetchall()
            for r in doc_rows:
                doc_id = r["document_id"]
                meta = DocumentMetadata.model_validate_json(r["metadata_json"])
                file_path = r["file_path"]

                cursor.execute("SELECT chunk_id, document_id, document_name, page_number, section, text, metadata_json FROM document_chunks WHERE document_id = ?", (doc_id,))
                chunk_rows = cursor.fetchall()

                chunks = []
                for cr in chunk_rows:
                    chunks.append(DocumentChunk(
                        chunk_id=cr["chunk_id"],
                        document_id=cr["document_id"],
                        document_name=cr["document_name"],
                        page_number=cr["page_number"],
                        section=cr["section"],
                        text=cr["text"],
                        metadata=json.loads(cr["metadata_json"])
                    ))

                results.append((meta, file_path, chunks))
        return results

    def save_analysis_run(self, analysis_id: str, question: str, status: str, result_dict: Dict[str, Any], created_at: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_runs (analysis_id, question, status, result_json, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (analysis_id, question, status, json.dumps(result_dict), created_at))
            conn.commit()

    def load_analysis_runs(self) -> Dict[str, Dict[str, Any]]:
        runs = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT analysis_id, result_json FROM analysis_runs")
            rows = cursor.fetchall()
            for r in rows:
                runs[r["analysis_id"]] = json.loads(r["result_json"])
        return runs
