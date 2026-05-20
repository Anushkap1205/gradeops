import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.exam import Exam
from app.models.submission import Submission, SubmissionStatus
from app.models.user import User, UserRole
from app.core.security import get_current_user
from app.schemas.upload import BulkUploadResponse, UploadItemResponse
from app.services import pdf_converter
from app.utils.files import validate_upload_filename

router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=BulkUploadResponse)
async def upload_submission(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    exam_id: int = Form(...),
    student_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.professor:
        return JSONResponse(status_code=403, content={"error": "Only professors can upload"})
    try:
        if not files:
            return JSONResponse(
                status_code=400, content={"error": "No files provided"}
            )

        if not db.get(Exam, exam_id):
            return JSONResponse(status_code=400, content={"error": "Exam not found"})
        if not db.get(User, student_id):
            return JSONResponse(status_code=400, content={"error": "Student not found"})

        responses = []
        for file in files:
            if not file.filename:
                continue

            ext = validate_upload_filename(file.filename)
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
                student_id=student_id,
                exam_id=exam_id,
                file_path=relative_path,
                status=SubmissionStatus.uploaded,
            )
            db.add(submission)
            db.flush()

            responses.append(UploadItemResponse(
                file_id=file_id,
                submission_id=submission.id,
                pages=page_count,
                status=submission.status,
            ))

        db.commit()
        return BulkUploadResponse(uploads=responses)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
