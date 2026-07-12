import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, status

from config import settings
from src.presentation.schemas.ocr_schemas import OCRResponse

router = APIRouter(prefix="/api/v1/ocr", tags=["ocr"])

# Allowed image types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}


@router.post("", response_model=OCRResponse, status_code=status.HTTP_200_OK)
async def ocr_upload(file: UploadFile = File(...)) -> OCRResponse:
    """Upload a receipt image and extract text using OCR."""
    if file.content_type not in ALLOWED_TYPES:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_TYPES}",
        )

    # Save file
    ext = Path(file.filename or "receipt.png").suffix or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    filepath = upload_path / filename

    content = await file.read()
    filepath.write_bytes(content)

    # Run OCR
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(filepath)
        raw_text = pytesseract.image_to_string(img, lang="por")
    except Exception as e:
        raw_text = f"OCR failed: {str(e)}"

    # Parse lines
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    items = [{"text": line, "confidence": 0.0} for line in lines]

    return OCRResponse(
        filename=filename,
        raw_text=raw_text,
        items=items,
    )
