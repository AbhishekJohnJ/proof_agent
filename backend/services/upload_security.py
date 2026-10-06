import re
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from backend.config import settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".pdf", ".txt", ".docx"}

class SafeUploadHandler:
    """Safe Upload Utility handling filename sanitization, size checks, and path traversal prevention."""

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        # Strip path directory parts (prevent traversal)
        name = Path(filename).name
        # Keep alphanumeric, underscores, hyphens, and dots
        clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
        return clean

    @classmethod
    def validate_and_save(cls, upload_file: UploadFile, target_dir: Path) -> tuple[str, str, Path]:
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Filename is missing.")

        clean_name = cls.sanitize_filename(upload_file.filename)
        ext = Path(clean_name).suffix.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported formats: {sorted(list(ALLOWED_EXTENSIONS))}"
            )

        # Generate server-side ID to avoid collisions
        unique_id = f"up_{uuid.uuid4().hex[:12]}"
        saved_filename = f"{unique_id}_{clean_name}"
        save_path = target_dir / saved_filename

        # Prevent path traversal
        try:
            save_path.resolve().relative_to(target_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid path traversal detected.")

        # Copy file and enforce size limit
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        bytes_written = 0

        with open(save_path, "wb") as buffer:
            while chunk := upload_file.file.read(8192):
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    save_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                buffer.write(chunk)

        return unique_id, clean_name, save_path
