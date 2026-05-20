from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import evaluate, rubric, upload, auth, plagiarism
from app.core.config import settings
from app.utils.errors import json_exception_handler
from app.utils.files import page_image_path

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="GradeOps API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, json_exception_handler)

app.include_router(upload.router)
app.include_router(rubric.router)
app.include_router(evaluate.router)
app.include_router(auth.router)
app.include_router(plagiarism.router)

settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def review_ui():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse(content={"message": "GradeOps API"})


@app.get("/files/{file_id}/page_{page_number}.png")
def serve_page_image(file_id: str, page_number: int):
    try:
        path = page_image_path(file_id, page_number)
        if not path.is_file():
            return JSONResponse(
                status_code=404, content={"error": "Page image not found"}
            )
        return FileResponse(path, media_type="image/png")
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
