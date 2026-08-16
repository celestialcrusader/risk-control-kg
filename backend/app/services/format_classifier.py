"""
Upstream Document Format Classifier & Router Pipeline for Pure RCKG Engine (RCKG-201).

Inspects file magic bytes, font structures, image density, and table cell counts
to route incoming raw enterprise documents to specialized parser backends:
- NATIVE_PDF -> Marker / PyMuPDF
- SCANNED_PDF -> Surya / Tesseract OCR
- COMPLEX_MATRIX -> TableTransformer / pdfplumber
- DOCX -> python-docx
- HTML -> BeautifulSoup / HtmlParser
"""

import enum
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DocumentFormat(str, enum.Enum):
    NATIVE_PDF = "NATIVE_PDF"
    SCANNED_PDF = "SCANNED_PDF"
    COMPLEX_MATRIX = "COMPLEX_MATRIX"
    DOCX = "DOCX"
    HTML = "HTML"
    UNKNOWN = "UNKNOWN"


class ClassificationResult(BaseModel):
    format: DocumentFormat
    recommended_parser: str
    confidence: float = Field(ge=0.0, le=1.0)
    detected_mime: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpstreamFormatClassifier:
    """Upstream Document Format Classifier & Routing Engine."""

    MAGIC_BYTES_MAP = {
        b"%PDF": ("application/pdf", DocumentFormat.NATIVE_PDF, "MarkerParser"),
        b"PK\x03\x04": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", DocumentFormat.DOCX, "DocxParser"),
        b"<!DOC": ("text/html", DocumentFormat.HTML, "HtmlParser"),
        b"<html": ("text/html", DocumentFormat.HTML, "HtmlParser"),
    }

    def classify_pdf_features(
        self,
        text_char_count: int,
        page_count: int = 1,
        image_count: int = 0,
        table_cell_count: int = 0,
        font_count: int = 0,
        filename: str = "",
    ) -> ClassificationResult:
        """Classify PDF features based on text density, image ratio, and table cell count."""
        safe_pages = max(1, page_count)
        chars_per_page = text_char_count / safe_pages
        meta = {"filename": filename, "chars_per_page": chars_per_page}

        # Rule 1: High table cell density -> COMPLEX_MATRIX
        if table_cell_count >= 50:
            meta["table_cell_count"] = table_cell_count
            return ClassificationResult(
                format=DocumentFormat.COMPLEX_MATRIX,
                recommended_parser="TableTransformerParser",
                confidence=0.90,
                detected_mime="application/pdf",
                metadata=meta,
            )

        # Rule 2: Image-only or extremely low text density -> SCANNED_PDF
        if (chars_per_page < 50 and font_count == 0) or (image_count >= safe_pages and chars_per_page < 20):
            meta["image_count"] = image_count
            return ClassificationResult(
                format=DocumentFormat.SCANNED_PDF,
                recommended_parser="SuryaOcrParser",
                confidence=0.95,
                detected_mime="application/pdf",
                metadata=meta,
            )

        # Rule 3: Digital Native Vector PDF -> NATIVE_PDF
        meta["font_count"] = font_count
        return ClassificationResult(
            format=DocumentFormat.NATIVE_PDF,
            recommended_parser="MarkerParser",
            confidence=0.92,
            detected_mime="application/pdf",
            metadata=meta,
        )

    def classify(self, file_bytes: bytes, filename: str = "") -> ClassificationResult:
        """Classify raw file bytes by inspecting magic header bytes and file extensions."""
        prefix = file_bytes[:10]

        # Magic bytes inspection
        for magic, (mime, fmt, parser) in self.MAGIC_BYTES_MAP.items():
            if prefix.startswith(magic) or magic in prefix:
                if fmt == DocumentFormat.NATIVE_PDF:
                    text_sample = file_bytes.decode("latin1", errors="ignore")
                    font_count = text_sample.count("/Font")
                    image_count = text_sample.count("/Image") + text_sample.count("/XObject")
                    table_cell_count = text_sample.count("/Table") * 25
                    text_char_count = len(text_sample) // 5

                    return self.classify_pdf_features(
                        text_char_count=text_char_count,
                        page_count=1,
                        image_count=image_count,
                        table_cell_count=table_cell_count,
                        font_count=font_count,
                        filename=filename,
                    )
                return ClassificationResult(
                    format=fmt,
                    recommended_parser=parser,
                    confidence=0.95,
                    detected_mime=mime,
                    metadata={"filename": filename},
                )

        # Extension-based fallback
        fn_lower = filename.lower()
        if fn_lower.endswith(".docx"):
            return ClassificationResult(
                format=DocumentFormat.DOCX,
                recommended_parser="DocxParser",
                confidence=0.90,
                detected_mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                metadata={"filename": filename},
            )
        elif fn_lower.endswith(".html") or fn_lower.endswith(".htm"):
            return ClassificationResult(
                format=DocumentFormat.HTML,
                recommended_parser="HtmlParser",
                confidence=0.90,
                detected_mime="text/html",
                metadata={"filename": filename},
            )

        return ClassificationResult(
            format=DocumentFormat.UNKNOWN,
            recommended_parser="FallbackParser",
            confidence=0.50,
            detected_mime="application/octet-stream",
            metadata={"filename": filename},
        )
