import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.exam import Exam
from app.models.submission import Submission, SubmissionStatus
from app.models.user import User
from app.schemas.upload import UploadResponse
from app.services import pdf_converter
from app.utils.files import validate_upload_filename

router = APIRouter(tags=["upload"])


@router.post("/upload")
async def upload_submission(
    file: UploadFile = File(...),
    exam_id: str = Form(...),
    student_id: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        if not file.filename:
            return JSONResponse(
                status_code=400, content={"error": "No file provided"}
            )

        ext = validate_upload_filename(file.filename)

        try:
            exam_uuid = uuid.UUID(exam_id)
            student_uuid = uuid.UUID(student_id)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "exam_id and student_id must be valid UUIDs"},
            )

        if not db.get(Exam, exam_uuid):
            return JSONResponse(status_code=400, content={"error": "Exam not found"})
        if not db.get(User, student_uuid):
            return JSONResponse(status_code=400, content={"error": "Student not found"})

        file_id = str(uuid.uuid4())
        upload_dir = settings.uploads_dir / file_id
        output_dir = settings.outputs_dir / file_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        stored_name = "original.pdf" if ext == ".pdf" else f"original{ext}"
        dest_path = upload_dir / stored_name

        with dest_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)

        if ext == ".pdf":
            page_count = pdf_converter.convert_pdf_to_images(dest_path, output_dir)
        else:
            page_count = pdf_converter.save_image_as_page(dest_path, output_dir)

        relative_path = f"uploads/{file_id}/{stored_name}"
        submission = Submission(
            student_id=student_uuid,
            exam_id=exam_uuid,
            file_path=relative_path,
            status=SubmissionStatus.uploaded,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return UploadResponse(
            file_id=file_id,
            submission_id=submission.id,
            pages=page_count,
            status=submission.status,
        )
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
