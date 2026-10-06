from fastapi import APIRouter, Depends, HTTPException
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisResult
from backend.api.dependencies import get_orchestrator
from backend.agents.orchestrator import AnalysisOrchestrator
from backend.services.storage import storage_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/query", response_model=AnalysisResult)
def submit_query(
    request: AnalysisRequest,
    orchestrator: AnalysisOrchestrator = Depends(get_orchestrator)
):
    return orchestrator.process_analysis(request)

@router.get("/{analysis_id}")
def get_analysis_result(analysis_id: str):
    run = storage_service.get_analysis_run(analysis_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found.")
    return run

@router.get("/{analysis_id}/verification")
def get_analysis_verification(analysis_id: str):
    run = storage_service.get_analysis_run(analysis_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found.")
    return run.get("verification", {})

@router.get("/{analysis_id}/evidence")
def get_analysis_evidence(analysis_id: str):
    run = storage_service.get_analysis_run(analysis_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found.")
    return run.get("evidence", [])
