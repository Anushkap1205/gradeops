import uuid
import logging
from .qwen_loader import extract_text_from_image

logger = logging.getLogger(__name__)


def run_ocr(image_path: str) -> dict:
    submission_id = str(uuid.uuid4())

    try:
        raw_text = extract_text_from_image(image_path)
        return {
            "submission_id": submission_id,
            "raw_text": raw_text,
        }
    except FileNotFoundError as e:
        logger.error("Image file not found: %s | %s", image_path, e)
        return {
            "submission_id": submission_id,
            "error": "file_not_found",
            "message": f"Image file not found: {image_path}",
        }
    except Exception as e:
        logger.exception("OCR failed for image: %s", image_path)
        return {
            "submission_id": submission_id,
            "error": "ocr_failed",
            "message": str(e),
        }
