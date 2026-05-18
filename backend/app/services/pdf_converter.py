import shutil
from pathlib import Path

import fitz


def convert_pdf_to_images(pdf_path: Path, output_dir: Path) -> int:
    """Render each PDF page to PNG at 150 DPI. Returns page count."""
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(150 / 72, 150 / 72)
    doc = fitz.open(pdf_path)
    try:
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix)
            pix.save(output_dir / f"page_{i}.png")
        return len(doc)
    finally:
        doc.close()


def save_image_as_page(source_path: Path, output_dir: Path) -> int:
    """Copy a JPG/PNG upload to outputs as a single page_1.png."""
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, output_dir / "page_1.png")
    return 1
