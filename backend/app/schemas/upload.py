import uuid

from pydantic import BaseModel

from app.models.submission import SubmissionStatus


class UploadResponse(BaseModel):
    file_id: str
    submission_id: uuid.UUID
    pages: int
    status: SubmissionStatus
