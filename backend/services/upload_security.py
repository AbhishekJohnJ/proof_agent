import re
import uuid
import shutil
import hashlib
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.config import settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".pdf", ".txt", ".docx"}

class SafeUploadHandler:
    """Safe Upload Utility handling filename sanitization, SHA-256 content fingerprinting, size checks, and path traversal prevention."""

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        name = Path(filename).name
        clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
        return clean

    @classmethod
    def validate_and_save(cls, upload_file: UploadFile, target_dir: Path) -> tuple[str, str, str, str, Path]:
        """Validates upload file and returns (upload_id, dataset_id, raw_sha256, clean_name, save_path)."""
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Filename is missing.")

        clean_name = cls.sanitize_filename(upload_file.filename)
        ext = Path(clean_name).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported formats: {sorted(list(ALLOWED_EXTENSIONS))}"
            )

        # Generate unique upload event ID
        upload_id = f"up_{uuid.uuid4().hex[:12]}"

        # Prevent path traversal
        temp_saved_filename = f"{upload_id}_{clean_name}"
        save_path = target_dir / temp_saved_filename

        try:
            save_path.resolve().relative_to(target_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid path traversal detected.")

        # Read, compute SHA-256 hash, write file, enforce size limit
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        bytes_written = 0
        sha256_hash = hashlib.sha256()

        with open(save_path, "wb") as buffer:
            while chunk := upload_file.file.read(8192):
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    save_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                sha256_hash.update(chunk)
                buffer.write(chunk)

        if bytes_written == 0:
            save_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

        raw_sha256 = sha256_hash.hexdigest()
        dataset_id = f"ds_{raw_sha256[:12]}"

        return upload_id, dataset_id, raw_sha256, clean_name, save_path

