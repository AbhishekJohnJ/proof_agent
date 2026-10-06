from fastapi import APIRouter, HTTPException
from backend.services.storage import storage_service
from backend.profiling.relationships import RelationshipDetector

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("")
def list_datasets():
    return storage_service.list_datasets()

@router.get("/relationships")
def get_candidate_relationships():
    dfs = {ds.dataset_id: storage_service.get_dataframe(ds.dataset_id) for ds in storage_service.list_datasets()}
    valid_dfs = {k: v for k, v in dfs.items() if v is not None}
    relationships = RelationshipDetector.detect_relationships(valid_dfs)
    return [r.model_dump() for r in relationships]

@router.get("/{dataset_id}")
def get_dataset(dataset_id: str):
    meta = storage_service.get_dataset_metadata(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return meta

@router.get("/{dataset_id}/profile")
def get_dataset_profile(dataset_id: str):
    profile = storage_service.get_dataset_profile(dataset_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Dataset profile not found.")
    return profile

@router.get("/{dataset_id}/artifact")
def get_dataset_artifact(dataset_id: str):
    artifact = storage_service.get_dataset_artifact(dataset_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Dataset artifact not found.")
    return artifact.model_dump()
