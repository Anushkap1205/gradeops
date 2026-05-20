from pydantic import BaseModel

from app.models.submission import SubmissionStatus


class UploadItemResponse(BaseModel):
    file_id: str
    submission_id: int
    pages: int
    status: SubmissionStatus

class BulkUploadResponse(BaseModel):
    uploads: list[UploadItemResponse]
