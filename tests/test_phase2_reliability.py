import pytest
from pathlib import Path
from backend.services.storage import storage_service
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker
from backend.documents.metadata import MetadataExtractor
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.models.verification import CheckStatus
from backend.api.dependencies import get_orchestrator
from backend.execution.sandbox import DockerSandbox, LocalIsolatedSandbox
from backend.config import settings

def test_A_clean_total_revenue():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_A")
    profile = DataProfiler.profile("ds_phase2_A", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(question="What is the total revenue in sales.csv?", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.VERIFIED
    assert res.verification.status == "VERIFIED"
    assert res.canonical_result.result == 9350.0

def test_B_wrong_generated_answer_v10_failure():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_B")
    profile = DataProfiler.profile("ds_phase2_B", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    # Force analyst to return a conflicting numerical answer (8950 instead of 9350)
    orchestrator.analyst.synthesize_answer = lambda q, e, ev: "The total revenue was $8,950."

    req = AnalysisRequest(question="What is the total revenue?", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.VERIFICATION_FAILED
    assert res.verification.v10_final_answer_consistent == CheckStatus.FAIL

def test_C_code_execution_failure():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_C")
    profile = DataProfiler.profile("ds_phase2_C", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    orchestrator.code_generator.provider.generate_code = lambda q, s, w: {
        "code": "import json\nx = 1 / 0\nprint(json.dumps({'result': x}))",
        "expected_result_type": "number",
        "datasets_used": [artifact.dataset_id]
    }

    req = AnalysisRequest(question="Compute total revenue", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.EXECUTION_FAILED
    assert res.verification.status == "VERIFICATION_FAILED"

def test_D_missing_column_refusal():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_D")
    profile = DataProfiler.profile("ds_phase2_D", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(question="What is the tax amount?", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.REFUSED
    assert res.refusal_reason == "insufficient_data"

def test_E_missing_profit_refusal():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_E")
    profile = DataProfiler.profile("ds_phase2_E", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(question="What is the net profit?", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.REFUSED
    assert res.refusal_reason == "insufficient_data"

def test_F_mixed_currency_refusal():
    path = Path("datasets/sample/messy_sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_F")
    profile = DataProfiler.profile("ds_phase2_F", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(question="Compare USD currency with EUR revenue.", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.REFUSED
    assert res.refusal_reason == "mixed_currency"

def test_G_ambiguous_dates_refusal():
    path = Path("datasets/sample/messy_sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_G")
    profile = DataProfiler.profile("ds_phase2_G", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(question="What was total revenue in Q4?", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.REFUSED
    assert res.refusal_reason == "ambiguous_date"

def test_K_document_isolation():
    orchestrator = get_orchestrator()

    # Create Doc A and Doc B
    docA_path = Path("documents/sample/annual_report.txt")
    pagesA = DocumentExtractor.extract_pages(docA_path)
    chunksA = DocumentChunker.create_chunks("doc_A_id", "annual_report_2026.pdf", pagesA)
    metaA = MetadataExtractor.extract_metadata("doc_A_id", docA_path, len(pagesA), len(chunksA))
    storage_service.save_document(metaA, docA_path, chunksA)

    docB_path = Path("documents/sample/policy.txt")
    pagesB = DocumentExtractor.extract_pages(docB_path)
    chunksB = DocumentChunker.create_chunks("doc_B_id", "annual_report_2025.pdf", pagesB)
    metaB = MetadataExtractor.extract_metadata("doc_B_id", docB_path, len(pagesB), len(chunksB))
    storage_service.save_document(metaB, docB_path, chunksB)

    # Search selecting ONLY Doc A
    retrieved = orchestrator.document_agent.retrieve_supporting_chunks(
        question="financial report",
        selected_document_ids=["doc_A_id"]
    )

    doc_ids_returned = [c[0].document_id for c in retrieved]
    assert "doc_B_id" not in doc_ids_returned

def test_O_docker_unavailable_no_host_fallback():
    # Instantiate DockerSandbox with dummy non-existent docker command
    sandbox = DockerSandbox()
    sandbox.docker_image = "non_existent_image_12345"
    res = sandbox.execute("print('hello')", [])

    assert res["execution_mode"] in ["docker_unavailable", "local_isolated"] or res["success"] is False

def test_R_final_answer_numerical_mismatch_fails_v10():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_phase2_R")
    profile = DataProfiler.profile("ds_phase2_R", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    orchestrator.analyst.synthesize_answer = lambda q, e, ev: "Total revenue was $8,950."

    req = AnalysisRequest(question="Calculate revenue", selected_datasets=[artifact.dataset_id])
    res = orchestrator.process_analysis(req)

    assert res.status == AnalysisStatus.VERIFICATION_FAILED
    assert res.verification.v10_final_answer_consistent == CheckStatus.FAIL

def test_V_model_unavailable_not_configured():
    old_llm_provider = settings.LLM_PROVIDER
    try:
        settings.LLM_PROVIDER = "qwen"
        orchestrator = get_orchestrator()
        req = AnalysisRequest(question="What is total revenue?", selected_datasets=["ds_dummy"])
        res = orchestrator.process_analysis(req)

        assert res.status == AnalysisStatus.MODEL_NOT_CONFIGURED
    finally:
        settings.LLM_PROVIDER = old_llm_provider
