import json
import pytest
from pathlib import Path

pytestmark = pytest.mark.benchmark
from backend.services.storage import storage_service
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker
from backend.documents.metadata import MetadataExtractor
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.api.dependencies import get_orchestrator
from backend.rag.vector_store import global_vector_store
from backend.rag.embeddings import EmbeddingService
from backend.providers.factory import ProviderFactory

embedding_provider = ProviderFactory.get_embedding_provider()
embedding_service = EmbeddingService(embedding_provider)

def load_benchmark_manifest():
    manifest_path = Path("tests/benchmark/benchmark_manifest.json")
    with open(manifest_path, "r") as f:
        return json.load(f)

@pytest.fixture(scope="module", autouse=True)
def prepare_benchmark_data():
    search_dirs = [Path("tests/fixtures"), Path("datasets/sample")]
    for csv_file in ["sales.csv", "clean_sales.csv", "messy_sales.csv", "customers.csv", "orders.csv"]:
        fpath = None
        for d in search_dirs:
            candidate = d / csv_file
            if candidate.exists():
                fpath = candidate
                break
        if fpath:
            df, meta = FileManager.ingest_dataset(fpath, dataset_id=f"ds_bm_{csv_file}")
            meta.filename = csv_file
            profile = DataProfiler.profile(meta.dataset_id, csv_file, df)
            storage_service.save_dataset(meta, fpath, df, profile)

    doc_dirs = [Path("tests/fixtures"), Path("documents/sample")]
    for txt_file in ["annual_report.txt", "policy.txt"]:
        fpath = None
        for d in doc_dirs:
            candidate = d / txt_file
            if candidate.exists():
                fpath = candidate
                break
        if fpath:
            doc_id = f"doc_bm_{txt_file}"
            pages = DocumentExtractor.extract_pages(fpath)
            chunks = DocumentChunker.create_chunks(doc_id, txt_file, pages)
            meta = MetadataExtractor.extract_metadata(doc_id, fpath, len(pages), len(chunks))
            meta.filename = txt_file
            storage_service.save_document(meta, fpath, chunks)
            if chunks:
                embs = embedding_service.embed_chunks([c.text for c in chunks])
                global_vector_store.add_chunks(chunks, embs)

def test_run_psi08_benchmark_cases():
    cases = load_benchmark_manifest()
    orchestrator = get_orchestrator()

    for case in cases:
        dataset_ids = [f"ds_bm_{fname}" for fname in case["selected_datasets"]]
        document_ids = [f"doc_bm_{fname}" for fname in case["selected_documents"]]

        req = AnalysisRequest(
            question=case["question"],
            selected_datasets=dataset_ids,
            selected_documents=document_ids
        )
        res = orchestrator.process_analysis(req)

        expected_outcome = case["expected_outcome"]
        if expected_outcome == "VERIFIED":
            assert res.status == AnalysisStatus.VERIFIED, f"Case {case['id']} ({case['name']}) failed to verify (got {res.status})."
            if case["expected_result"] is not None and res.canonical_result:
                assert abs(float(res.canonical_result.result) - float(case["expected_result"])) < 1e-2
        elif expected_outcome == "DOCUMENT_SUPPORTED":
            assert res.status == AnalysisStatus.DOCUMENT_SUPPORTED, f"Case {case['id']} ({case['name']}) expected DOCUMENT_SUPPORTED but got {res.status}."
        elif expected_outcome == "REFUSED":
            assert res.status == AnalysisStatus.REFUSED, f"Case {case['id']} ({case['name']}) expected REFUSED but got {res.status}."
            if case["expected_refusal_reason"]:
                assert res.refusal_reason == case["expected_refusal_reason"]
