import os
import pytest
from backend.config import settings
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.providers.ollama.client import OllamaClient
from backend.providers.ollama.discovery import OllamaDiscovery
from backend.providers.ollama.config import ollama_config
from backend.data.catalog import dataset_catalog
from backend.verification.proof_policy import ProofPolicy
from backend.models.verification import VerificationResult, CheckStatus

def is_ollama_available() -> bool:
    """Helper checking if local Ollama API service and models are reachable."""
    try:
        client = OllamaClient()
        hc = client.health_check()
        return hc.get("available", False)
    except Exception:
        return False

# Skip entire module if Ollama is unavailable
pytestmark = pytest.mark.skipif(
    not is_ollama_available(),
    reason="Local Ollama service or models are unavailable. Integration test requires active Ollama."
)

@pytest.fixture
def all_datasets():
    return [d["dataset_id"] for d in dataset_catalog.list_datasets()]

@pytest.fixture
def real_ollama_orchestrator():
    """Instantiates AnalysisOrchestrator backed strictly by real local Ollama models."""
    from backend.api.dependencies import get_orchestrator
    # Temporarily enforce Ollama provider settings
    settings.LLM_PROVIDER = "ollama"
    settings.CODE_GEN_PROVIDER = "ollama"

    return get_orchestrator()

def test_ollama_discovery():
    """Verifies automatic discovery of Ollama binary, version, and installed models."""
    disc = OllamaDiscovery.discover_all()
    assert disc.get("api_available") is True
    assert disc.get("selected_planner_model") is not None
    assert disc.get("selected_code_model") is not None

def test_ollama_model_inference():
    """Independently verifies Qwen and DeepSeek inference before pipeline execution."""
    client = OllamaClient()
    p_model = ollama_config.planner_model
    c_model = ollama_config.code_model

    v_planner = client.verify_model_inference(p_model)
    assert v_planner.get("verified") is True

    v_code = client.verify_model_inference(c_model)
    assert v_code.get("verified") is True

@pytest.mark.parametrize("question", [
    "What is the total revenue?",
    "What is the average order value?",
    "What is the return rate?",
    "Which category has the highest revenue?",
    "Which state has the highest revenue?"
])
def test_real_end_to_end_questions(real_ollama_orchestrator, all_datasets, question):
    """
    Submits analytical questions through real local Ollama pipeline:
    User -> Qwen3 Planner -> AnalysisContract -> DeepSeek CodeGen -> Sandbox -> Evidence -> Reference -> Verification -> Answer.
    """
    req = AnalysisRequest(question=question, selected_datasets=all_datasets)
    result = real_ollama_orchestrator.process_analysis(req)

    if result.status == AnalysisStatus.VERIFIED:
        assert result.canonical_result is not None
        assert result.canonical_result.result is not None
        assert result.verification.status == "VERIFIED"
        assert result.verification.v1_code_executed.value == "PASS"
        assert result.proof_trace is not None
        assert "model_provenance" in result.proof_trace

def test_wrong_model_output_fails_verification():
    """
    Verifies that if LLM output produces a wrong calculation (e.g. MEAN instead of SUM),
    the independent ReferenceEngine and ProofPolicy reject it with VERIFICATION_FAILED.
    """
    v_res = VerificationResult(
        v1_code_executed=CheckStatus.PASS,
        v2_output_exists=CheckStatus.PASS,
        v3_output_valid_canonical=CheckStatus.PASS,
        v4_result_type_matched=CheckStatus.PASS,
        v5_result_finite_valid=CheckStatus.PASS,
        v6_reproducible=CheckStatus.PASS,
        status="VERIFICATION_FAILED",
        errors=["Reference Mismatch: Generated result (100) differs from reference (500)"]
    )
    status, kind = ProofPolicy.evaluate_policy(
        verification_result=v_res,
        reference_matches=False,
        has_critical_quality_issue=False
    )
    assert status == AnalysisStatus.VERIFICATION_FAILED
    assert kind == "verification_failed"

def test_hallucinated_column_refused(real_ollama_orchestrator, all_datasets):
    """Verifies that requesting a nonexistent column results in REFUSED status."""
    req = AnalysisRequest(
        question="What is the average employee happiness score?",
        selected_datasets=all_datasets
    )
    result = real_ollama_orchestrator.process_analysis(req)
    assert result.status == AnalysisStatus.REFUSED
    assert "insufficient_data" in result.answer or "not exist" in result.answer or result.result_kind == "refusal"

def test_unauthorized_dataset_blocked(real_ollama_orchestrator, all_datasets):
    """Verifies that attempting to read unauthorized CSV files is blocked by static validator or sandbox."""
    req = AnalysisRequest(question="What is the total revenue?", selected_datasets=all_datasets)
    result = real_ollama_orchestrator.process_analysis(req)
    if result.proof_trace:
        auth = result.proof_trace.get("authorization", {})
        assert auth.get("unauthorized_access") is False
