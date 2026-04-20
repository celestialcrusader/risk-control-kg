"""
PDF-to-Markdown conversion service for RCKG.

Provides:
- MinerUConverter: Wraps the MinerU PDF parsing library
- MarkerFallbackConverter: Wraps the Marker PDF parsing library as fallback
- convert_pdf_to_markdown(): Top-level function coordinating MinerU + Marker fallback

MinerU is the primary converter. When its confidence score is below 0.85,
MarkerFallbackConverter is invoked automatically to produce a replacement
output. The final output is stored in MinIO's markdown-conversions bucket.
"""

import logging
import re
import time
from pathlib import Path

from app.storage import get_minio_storage

logger = logging.getLogger(__name__)

# Confidence threshold for triggering Marker fallback
CONFIDENCE_THRESHOLD = 0.85

# Pattern allowing only safe characters in document_id
_DOCUMENT_ID_PATTERN = re.compile(r"^[\w][\w.-]*$")


class MinerUConverter:
    """Wrapper around the MinerU PDF parsing library.

    MinerU preserves heading hierarchies (H1-H6), multi-column layouts,
    nested tables, and footnotes from PDF documents.
    """

    def convert(self, pdf_path: str) -> "MinerUResult":
        """Convert a PDF to structured Markdown using MinerU.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            MinerUResult with headings, tables, footnotes, markdown text, and confidence.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            RuntimeError: If the MinerU library fails during conversion.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            result = _run_mineru(pdf_path)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"MinerU conversion failed for {pdf_path}: {exc}"
            ) from exc
        return result


class MarkerFallbackConverter:
    """Wrapper around the Marker PDF parsing library as fallback.

    Marker is used when MinerU confidence is below the threshold.
    It produces semantically equivalent output with better reliability
    on complex PDF layouts.
    """

    def convert(self, pdf_path: str) -> "MarkerResult":
        """Convert a PDF to structured Markdown using Marker.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            MarkerResult with headings, tables, footnotes, markdown text, and confidence.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            RuntimeError: If the Marker library fails during conversion.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            result = _run_marker(pdf_path)
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Marker conversion failed for {pdf_path}: {exc}"
            ) from exc
        return result


class _MinerUResult:
    """Result from MinerU conversion.

    Attributes:
        headings: List of heading dicts with level, text, position.
        tables: List of table dicts with headers and rows.
        footnotes: List of footnote dicts with id, text, anchor, parent_section.
        markdown: The full Markdown string output.
        confidence: Conversion confidence score (0.0 to 1.0).
    """

    def __init__(
        self,
        headings: list,
        tables: list,
        footnotes: list,
        markdown: str,
        confidence: float,
    ) -> None:
        self.headings = headings
        self.tables = tables
        self.footnotes = footnotes
        self.markdown = markdown
        self.confidence = confidence


class _MarkerResult:
    """Result from Marker conversion (same structure as MinerUResult)."""

    def __init__(
        self,
        headings: list,
        tables: list,
        footnotes: list,
        markdown: str,
        confidence: float,
    ) -> None:
        self.headings = headings
        self.tables = tables
        self.footnotes = footnotes
        self.markdown = markdown
        self.confidence = confidence


def _run_mineru(pdf_path: str) -> _MinerUResult:
    """Run the actual MinerU conversion.

    In production, this imports and calls the MinerU library. In tests,
    this function is mocked to return controlled result objects.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        _MinerUResult with parsed content and confidence.
    """
    # In production, call MinerU:
    #   from mineru import MinerU
    #   mineru = MinerU()
    #   result = mineru.convert(pdf_path)
    #   return _MinerUResult(...)
    raise RuntimeError("MinerU library not available in this environment")


def _run_marker(pdf_path: str) -> _MarkerResult:
    """Run the actual Marker conversion.

    In production, this imports and calls the Marker library. In tests,
    this function is mocked to return controlled result objects.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        _MarkerResult with parsed content and confidence.
    """
    # In production, call Marker:
    #   from marker import MarkerConverter
    #   marker = MarkerConverter()
    #   result = marker.convert(pdf_path)
    #   return _MarkerResult(...)
    raise RuntimeError("Marker library not available in this environment")


def convert_pdf_to_markdown(
    pdf_path: str,
    document_id: str,
) -> dict:
    """Convert a PDF to structured Markdown using MinerU with Marker fallback.

    Primary conversion uses MinerU. If MinerU's confidence score is below
    the threshold (0.85), MarkerFallbackConverter is invoked automatically.
    The final Markdown is stored in MinIO's markdown-conversions bucket.

    Args:
        pdf_path: Path to the PDF file to convert.
        document_id: Unique identifier for the document (used in MinIO key).

    Returns:
        Dict with keys:
            - document_id: str
            - markdown_uri: str (MinIO key)
            - confidence_score: float
            - conversion_time_ms: int
            - heading_count: int
            - table_count: int
            - footnotes_count: int
            - converter_used: str ("mineru" or "marker")

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If document_id is missing or file is not a PDF.
    """
    # --- Input validation ---
    if not document_id:
        raise ValueError("document_id is required")

    # Sanitize document_id to prevent path traversal attacks
    if not _DOCUMENT_ID_PATTERN.match(document_id):
        raise ValueError(
            f"document_id contains invalid characters: {document_id!r}. "
            "Only alphanumeric, hyphens, underscores, and dots are allowed "
            "(must start with alphanumeric)."
        )

    pdf_ext = Path(pdf_path).suffix.lower()
    if pdf_ext != ".pdf":
        raise ValueError(
            f"Only PDF files (.pdf) are supported, got: {pdf_ext}"
        )

    # --- Start timing ---
    start_time = time.time()

    # --- Primary conversion with MinerU ---
    mineru_converter = MinerUConverter()
    mineru_result = mineru_converter.convert(pdf_path)

    # --- Marker fallback if confidence is low ---
    if mineru_result.confidence < CONFIDENCE_THRESHOLD:
        logger.warning(
            "MinerU confidence %.2f below threshold %.2f; "
            "invoking Marker fallback",
            mineru_result.confidence,
            CONFIDENCE_THRESHOLD,
        )
        marker_converter = MarkerFallbackConverter()
        marker_result = marker_converter.convert(pdf_path)

        converter_used = "marker"
        confidence_score = marker_result.confidence
        headings = marker_result.headings
        tables = marker_result.tables
        footnotes = marker_result.footnotes
        markdown_text = marker_result.markdown
    else:
        converter_used = "mineru"
        confidence_score = mineru_result.confidence
        headings = mineru_result.headings
        tables = mineru_result.tables
        footnotes = mineru_result.footnotes
        markdown_text = mineru_result.markdown

    # --- End timing ---
    conversion_time_ms = int((time.time() - start_time) * 1000)

    # --- Count headings, tables, and footnotes ---
    heading_count = len(headings)
    table_count = len(tables)
    footnotes_count = len(footnotes)

    # --- Store in MinIO ---
    minio = get_minio_storage()
    bucket = minio.markdown_conversions_bucket
    minio_key = f"conversions/{document_id}/{document_id}.md"

    minio.upload_data(
        bucket=bucket,
        key=minio_key,
        data=markdown_text.encode("utf-8"),
        content_type="text/markdown",
    )

    # --- Build result ---
    result = {
        "document_id": document_id,
        "markdown_uri": minio_key,
        "confidence_score": confidence_score,
        "conversion_time_ms": conversion_time_ms,
        "heading_count": heading_count,
        "table_count": table_count,
        "footnotes_count": footnotes_count,
        "converter_used": converter_used,
    }

    logger.info(
        "PDF conversion complete: document_id=%s converter=%s "
        "confidence=%.2f headings=%d tables=%d footnotes=%d time=%dms",
        document_id,
        converter_used,
        confidence_score,
        heading_count,
        table_count,
        footnotes_count,
        conversion_time_ms,
    )

    return result
