import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from backend.services.upload_security import SafeUploadHandler
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker
from backend.documents.metadata import MetadataExtractor
from backend.services.storage import storage_service
from backend.rag.vector_store import SimpleVectorStore
from backend.rag.embeddings import EmbeddingService
from backend.providers.factory import ProviderFactory

router = APIRouter(tags=["Upload"])

# Shared global vector store & embedding service
embedding_provider = ProviderFactory.get_embedding_provider()
embedding_service = EmbeddingService(embedding_provider)
vector_store = SimpleVectorStore()

# Rebuild vector store from persisted document chunks if any
def rebuild_vector_index():
    for doc in storage_service.list_documents():
        chunks = storage_service.get_document_chunks(doc.document_id)
        if chunks:
            embeddings = embedding_service.embed_chunks([c.text for c in chunks])
            vector_store.add_chunks(chunks, embeddings)

rebuild_vector_index()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()

    # 1. Tabular Data Upload
    if ext in [".csv", ".xlsx", ".xls", ".json"]:
        unique_id, clean_filename, save_path = SafeUploadHandler.validate_and_save(file, settings.DATA_DIR)
        try:
            dataset_id = f"ds_{unique_id}"
            df, metadata = FileManager.ingest_dataset(save_path, dataset_id=dataset_id)
            metadata.filename = clean_filename
            profile = DataProfiler.profile(dataset_id, clean_filename, df)
            
            artifact = storage_service.save_dataset(metadata, save_path, df, profile)

            return {
                "type": "dataset",
                "id": dataset_id,
                "filename": clean_filename,
                "metadata": metadata.model_dump(),
                "profile": profile.model_dump(),
                "artifact": artifact.model_dump()
            }
        except Exception as e:
            save_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=f"Failed to ingest tabular file: {str(e)}")

    # 2. Unstructured Document Upload
    elif ext in [".pdf", ".txt", ".docx"]:
        unique_id, clean_filename, save_path = SafeUploadHandler.validate_and_save(file, settings.DOCUMENT_DIR)
        try:
            document_id = f"doc_{unique_id}"
            pages = DocumentExtractor.extract_pages(save_path)
            chunks = DocumentChunker.create_chunks(document_id, clean_filename, pages)
            metadata = MetadataExtractor.extract_metadata(document_id, save_path, len(pages), len(chunks))
            metadata.filename = clean_filename

            storage_service.save_document(metadata, save_path, chunks)

            # Embed and index document chunks into RAG Vector Store
            if chunks:
                embeddings = embedding_service.embed_chunks([c.text for c in chunks])
                vector_store.add_chunks(chunks, embeddings)

            return {
                "type": "document",
                "id": document_id,
                "filename": clean_filename,
                "metadata": metadata.model_dump()
            }
        except Exception as e:
            save_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=f"Failed to ingest document file: {str(e)}")

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Supported formats: .csv, .xlsx, .xls, .json, .pdf, .txt, .docx"
        )
