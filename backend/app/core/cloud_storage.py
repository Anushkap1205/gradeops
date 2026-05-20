import shutil
from pathlib import Path
from app.core.config import settings

class CloudStorageMock:
    """
    Mock implementation of an S3-like Cloud Storage interface.
    Uses the local file system but exposes a generic API that can 
    be easily swapped out for boto3/S3 later.
    """
    def __init__(self):
        self.base_dir = settings.uploads_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, local_path: Path | str, bucket: str, object_name: str) -> str:
        """Upload a file to the mock cloud storage."""
        dest = self.base_dir / bucket / object_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(local_path, Path):
            shutil.copy2(local_path, dest)
        else:
            with open(dest, "wb") as f_out, open(local_path, "rb") as f_in:
                shutil.copyfileobj(f_in, f_out)
        return f"{bucket}/{object_name}"

    def upload_fileobj(self, file_obj, bucket: str, object_name: str) -> str:
        """Upload a file-like object to the mock cloud storage."""
        dest = self.base_dir / bucket / object_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f_out:
            shutil.copyfileobj(file_obj, f_out)
        return f"{bucket}/{object_name}"

    def download_file(self, bucket: str, object_name: str, local_path: Path | str) -> None:
        """Download a file from the mock cloud storage."""
        src = self.base_dir / bucket / object_name
        if not src.exists():
            raise FileNotFoundError(f"Object {object_name} not found in bucket {bucket}")
        shutil.copy2(src, local_path)

cloud_storage = CloudStorageMock()
