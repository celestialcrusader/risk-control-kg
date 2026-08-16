"""
Parser Dispatcher Factory routing DocumentFormat to specialized parser implementations.
"""

from app.services.format_classifier import DocumentFormat
from app.services.parsers.base_parser import BaseParser
from app.services.parsers.native_pdf_parser import NativePdfParser
from app.services.parsers.ocr_parser import ScannedOcrParser
from app.services.parsers.matrix_parser import MatrixTableParser


class ParserDispatcher:
    """Factory routing classified document format to optimal parser engine."""

    def __init__(self):
        self._parsers = {
            DocumentFormat.NATIVE_PDF: NativePdfParser(),
            DocumentFormat.SCANNED_PDF: ScannedOcrParser(),
            DocumentFormat.COMPLEX_MATRIX: MatrixTableParser(),
            DocumentFormat.DOCX: NativePdfParser(),
            DocumentFormat.HTML: NativePdfParser(),
            DocumentFormat.UNKNOWN: NativePdfParser(),
        }

    def get_parser(self, doc_format: DocumentFormat) -> BaseParser:
        """Return specialized parser instance for document format."""
        return self._parsers.get(doc_format, NativePdfParser())
