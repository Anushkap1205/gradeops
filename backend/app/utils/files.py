import re
from pathlib import Path

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
FILE_ID_PATTERN = re.compile(r"uploads/([0-9a-f-]{36})/")


def validate_upload_filename(filename: str) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Invalid file type. Allowed types: PDF, JPG, PNG"
        )
    return ext


def file_id_from_submission_path(file_path: str) -> str | None:
    match = FILE_ID_PATTERN.search(file_path.replace("\\", "/"))
    return match.group(1) if match else None


def page_image_path(file_id: str, page_number: int) -> Path:
    return settings.outputs_dir / file_id / f"page_{page_number}.png"
