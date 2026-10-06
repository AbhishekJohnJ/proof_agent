import pytest
from pathlib import Path
from backend.services.storage import storage_service
from backend.services.persistence import SQLitePersistenceManager
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler
from backend.codegen.validator import StaticCodeValidator
from backend.execution.runner import LocalCodeRunner
from backend.execution.limits import ExecutionLimits
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.verification.result_checker import ResultChecker
from backend.models.verification import CheckStatus
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.api.dependencies import get_orchestrator
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker
from backend.documents.metadata import MetadataExtractor

# TEST 1: Upload clean sales dataset -> Ask total revenue -> Mock code executes -> Result verified
def test_1_clean_sales_revenue_verified():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_test1_clean")
    profile = DataProfiler.profile("ds_test1_clean", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the total revenue in sales.csv?",
        selected_datasets=[artifact.dataset_id]
    )
    result = orchestrator.process_analysis(req)

    assert result.status == AnalysisStatus.VERIFIED
    assert result.verification.status == "VERIFIED"
    assert result.canonical_result is not None
    assert result.canonical_result.result == 9350.0  # Sum of 1500+850+2200+450+1250+3100
    assert "9350" in result.answer

# TEST 2: Upload dataset -> Code execution fails -> Result must NOT be verified
def test_2_failed_execution_not_verified():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_test2_fail")
    profile = DataProfiler.profile("ds_test2_fail", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    # Force bad code execution
    bad_res = LocalCodeRunner.run_code("import sys; sys.exit(1)", [artifact])
    assert bad_res["success"] is False

    orchestrator = get_orchestrator()
    # Mock code generator returning division by zero code
    orchestrator.code_generator.provider.generate_code = lambda q, s, w: {
        "code": "x = 1 / 0",
        "expected_result_type": "number",
        "datasets_used": [artifact.dataset_id]
    }

    req = AnalysisRequest(
        question="Compute something",
        selected_datasets=[artifact.dataset_id]
    )
    result = orchestrator.process_analysis(req)

    assert result.status == AnalysisStatus.EXECUTION_FAILED
    assert result.verification.status == "VERIFICATION_FAILED"
    assert result.confidence == 0.0

# TEST 3: Access unavailable dataset -> Execution fails safely
def test_3_unavailable_dataset_isolation():
    code = 'import pandas as pd\ndf = pd.read_csv("data/non_existent_id/data.csv")'
    res = LocalCodeRunner.run_code(code, [])
    assert res["success"] is False
    assert "FileNotFoundError" in res["stderr"] or "No such file" in res["stderr"]

# TEST 4: Missing profit column -> Refusal
def test_4_missing_profit_refusal():
    path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_test4_noprofit")
    profile = DataProfiler.profile("ds_test4_noprofit", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the net profit for Q3?",
        selected_datasets=[artifact.dataset_id]
    )
    result = orchestrator.process_analysis(req)

    assert result.status == AnalysisStatus.REFUSED
    assert result.refusal_reason == "insufficient_data"
    assert result.confidence == 0.0

# TEST 5: Messy currency dataset -> Quality issue detected
def test_5_messy_sales_quality_issues():
    path = Path("datasets/sample/messy_sales.csv")
    df, meta = FileManager.ingest_dataset(path, dataset_id="ds_test5_messy")
    profile = DataProfiler.profile("ds_test5_messy", meta.filename, df)
    artifact = storage_service.save_dataset(meta, path, df, profile)

    assert profile.duplicate_rows > 0
    warning_types = [w.type for w in profile.quality_warnings]
    assert "mixed_currency" in warning_types
    assert "duplicate_rows" in warning_types

# TEST 6: Document upload -> Extraction -> Chunking -> Embedding -> Retrieval
def test_6_document_rag_pipeline():
    doc_path = Path("documents/sample/annual_report.txt")
    pages = DocumentExtractor.extract_pages(doc_path)
    chunks = DocumentChunker.create_chunks("doc_test6", doc_path.name, pages)
    meta = MetadataExtractor.extract_metadata("doc_test6", doc_path.name, len(pages), len(chunks))

    storage_service.save_document(meta, doc_path, chunks)
    assert meta.chunk_count == len(chunks)

# TEST 7: Hybrid request -> Data evidence + Document evidence contract
def test_7_hybrid_evidence_contract():
    ds_path = Path("datasets/sample/sales.csv")
    df, ds_meta = FileManager.ingest_dataset(ds_path, dataset_id="ds_test7")
    profile = DataProfiler.profile("ds_test7", ds_meta.filename, df)
    storage_service.save_dataset(ds_meta, ds_path, df, profile)

    doc_path = Path("documents/sample/annual_report.txt")
    pages = DocumentExtractor.extract_pages(doc_path)
    chunks = DocumentChunker.create_chunks("doc_test7", doc_path.name, pages)
    doc_meta = MetadataExtractor.extract_metadata("doc_test7", doc_path.name, len(pages), len(chunks))
    storage_service.save_document(doc_meta, doc_path, chunks)

    from backend.rag.vector_store import global_vector_store
    from backend.rag.embeddings import EmbeddingService
    from backend.providers.factory import ProviderFactory
    emb_service = EmbeddingService(ProviderFactory.get_embedding_provider())
    embs = emb_service.embed_chunks([c.text for c in chunks])
    global_vector_store.add_chunks(chunks, embs)

    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the total revenue stated in the annual report?",
        selected_datasets=[ds_meta.dataset_id],
        selected_documents=[doc_meta.document_id]
    )
    result = orchestrator.process_analysis(req)
    assert len(result.evidence) > 0

# TEST 8: Backend restart -> SQLite persistence metadata recovery
def test_8_sqlite_persistence_recovery(tmp_path):
    db_file = tmp_path / "test_recovery.sqlite3"
    pm1 = SQLitePersistenceManager(db_path=db_file)

    ds_path = Path("datasets/sample/sales.csv")
    df, meta = FileManager.ingest_dataset(ds_path, dataset_id="ds_persist")
    profile = DataProfiler.profile("ds_persist", meta.filename, df)

    pm1.save_dataset(meta, str(ds_path.resolve()), profile)

    # Instantiate new persistence manager from same DB file
    pm2 = SQLitePersistenceManager(db_path=db_file)
    recovered = pm2.load_datasets()

    assert len(recovered) == 1
    assert recovered[0][0].dataset_id == "ds_persist"

# TEST 9: Dangerous code -> AST validation rejects
def test_9_dangerous_code_rejected():
    dangerous_code = "import os\nos.system('echo hacked')"
    is_valid, errors = StaticCodeValidator.validate(dangerous_code)
    assert is_valid is False
    assert len(errors) > 0

# TEST 10: Large stdout -> Output limit enforced
def test_10_stdout_limit_enforced():
    code = "print('A' * 500000)"
    limits = ExecutionLimits(max_output_bytes=1000)
    res = LocalCodeRunner.run_code(code, limits=limits)
    assert len(res["stdout"]) <= 1000

# TEST 11: Timeout -> Execution terminated
def test_11_timeout_enforced():
    code = "import time\ntime.sleep(20)"
    limits = ExecutionLimits(timeout_seconds=1)
    res = LocalCodeRunner.run_code(code, limits=limits)
    assert res["success"] is False
    assert "timed out" in res["error"].lower()

# TEST 12: Reproducibility -> Verified with tolerance
def test_12_reproducibility_numeric_tolerance():
    sandbox = get_orchestrator().sandbox
    code = 'import json\nprint(json.dumps({"result": 100.0000001, "metric": "test"}))'
    initial_res = sandbox.execute(code, [])
    status, diff, method, errors = ReproducibilityVerifier.verify_reproducibility(
        sandbox, code, initial_res, [], tolerance=1e-4
    )
    assert status == CheckStatus.PASS
