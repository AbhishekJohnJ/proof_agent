import pytest
from pathlib import Path
from backend.services.storage import storage_service
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler

pytestmark = pytest.mark.redteam

@pytest.fixture(scope="module", autouse=True)
def setup_redteam_datasets():
    fixtures_dir = Path("tests/fixtures")
    if (fixtures_dir / "clean_sales.csv").exists():
        df, meta = FileManager.ingest_dataset(fixtures_dir / "clean_sales.csv", dataset_id="ds_redteam_sales")
        profile = DataProfiler.profile("ds_redteam_sales", "clean_sales.csv", df)
        storage_service.save_dataset(meta, fixtures_dir / "clean_sales.csv", df, profile)

    if (fixtures_dir / "messy_sales.csv").exists():
        df2, meta2 = FileManager.ingest_dataset(fixtures_dir / "messy_sales.csv", dataset_id="ds_redteam_messy")
        profile2 = DataProfiler.profile("ds_redteam_messy", "messy_sales.csv", df2)
        storage_service.save_dataset(meta2, fixtures_dir / "messy_sales.csv", df2, profile2)
