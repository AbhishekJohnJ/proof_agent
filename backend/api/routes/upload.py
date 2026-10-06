import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.config import settings
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker
from backend.documents.metadata import MetadataExtractor
from backend.services.storage import storage_service

router = APIRouter(tags=["Upload"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    
    # Tabular datasets
    if ext in [".csv", ".xlsx", ".xls", ".json"]:
        save_path = settings.DATA_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            df, metadata = FileManager.ingest_dataset(save_path)
            profile = DataProfiler.profile(metadata.dataset_id, metadata.filename, df)
            storage_service.save_dataset(metadata, df, profile)

            return {
                "type": "dataset",
                "id": metadata.dataset_id,
                "filename": metadata.filename,
                "metadata": metadata.model_dump(),
                "profile": profile.model_dump()
            }
        except Exception as e:
            if save_path.exists():
                save_path.unlink()
            raise HTTPException(status_code=400, detail=f"Failed to ingest tabular file: {str(e)}")

    # Unstructured Documents
    elif ext in [".pdf", ".txt", ".docx", ".doc"]:
        save_path = settings.DOCUMENT_DIR / file.filename
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            doc_id = f"doc_{Path(file.filename).stem}"
            pages = DocumentExtractor.extract_pages(save_path)
            chunks = DocumentChunker.create_chunks(doc_id, file.filename, pages)
            metadata = MetadataExtractor.extract_metadata(doc_id, save_path, len(pages), len(chunks))

            storage_service.save_document(metadata, chunks)

            return {
                "type": "document",
                "id": doc_id,
                "filename": file.filename,
                "metadata": metadata.model_dump()
            }
        except Exception as e:
            if save_path.exists():
                save_path.unlink()
            raise HTTPException(status_code=400, detail=f"Failed to ingest document file: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension '{ext}'.")
