from fastapi import APIRouter, HTTPException
from backend.services.storage import storage_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("")
def list_documents():
    return storage_service.list_documents()

@router.get("/{document_id}")
def get_document(document_id: str):
    meta = storage_service.get_document_metadata(document_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Document not found.")
    return meta
