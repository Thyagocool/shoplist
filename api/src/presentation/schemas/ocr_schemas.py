from pydantic import BaseModel


class OCRResultItem(BaseModel):
    text: str
    confidence: float = 0.0


class OCRResponse(BaseModel):
    filename: str
    raw_text: str
    items: list[OCRResultItem] = []
