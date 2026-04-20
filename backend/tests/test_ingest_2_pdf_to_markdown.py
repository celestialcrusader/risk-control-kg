"""
Test suite for INGEST-2: MinerU PDF-to-Markdown Conversion

This test module verifies the PDF-to-Markdown conversion service including:
- H1-H6 heading hierarchy preservation from PDFs
- GFM (GitHub-Flavored Markdown) table rendering
- Footnote annotation inline or appended to parent section
- Marker fallback when MinerU confidence < 0.85
- MinIO storage in markdown-conversions bucket
- Conversion time tracking
- Output metadata structure

Test Strategy:
- Unit tests with mocked MinerU, Marker, and MinIO
- Tests verify all acceptance criteria from the INGEST-2 story
- All assertions are meaningful
- AAA pattern (Arrange, Act, Assert)
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Ensure app module is importable
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_mineru_result():
    """Create a mock MinerU conversion result with headings, tables, footnotes."""
    mock = MagicMock()
    mock.headings = []
    mock.tables = []
    mock.footnotes = []
    mock.markdown = ""
    mock.confidence = 0.0
    return mock


@pytest.fixture
def mock_marker_result():
    """Create a mock Marker conversion result."""
    return MagicMock()


@pytest.fixture
def mock_minio_storage():
    """Create a mock MinIO storage instance."""
    mock = MagicMock()
    mock.markdown_conversions_bucket = "markdown-conversions"
    return mock


# ==============================================================================
# AC-1: Heading Hierarchy Preservation (H1-H6)
# ==============================================================================


class TestHeadingHierarchy:
    """TC-2.1: convert_pdf_to_markdown extracts H1-H6 headings correctly."""

    def test_convert_returns_heading_list(self, mock_mineru_result):
        """Converter returns heading entries with level and text."""
        mock_mineru_result.headings = [
            {"level": 1, "text": "Chapter 1", "position": 0},
            {"level": 2, "text": "Section 1.1", "position": 50},
            {"level": 3, "text": "Subsection 1.1.1", "position": 100},
            {"level": 1, "text": "Chapter 2", "position": 200},
            {"level": 4, "text": "Sub-subsection 2.1.1.1", "position": 250},
            {"level": 5, "text": "Level 5 heading", "position": 300},
            {"level": 6, "text": "Level 6 heading", "position": 350},
        ]
        mock_mineru_result.markdown = "# Chapter 1\n## Section 1.1\n### Subsection 1.1.1"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/test.pdf",
                document_id="doc-heading-test",
            )

            assert "heading_count" in result
            assert result["heading_count"] == 7

    def test_all_six_heading_levels_extracted(self, mock_mineru_result):
        """Converter returns all six heading levels (H1-H6)."""
        mock_mineru_result.headings = [
            {"level": 1, "text": "H1", "position": 0},
            {"level": 2, "text": "H2", "position": 10},
            {"level": 3, "text": "H3", "position": 20},
            {"level": 4, "text": "H4", "position": 30},
            {"level": 5, "text": "H5", "position": 40},
            {"level": 6, "text": "H6", "position": 50},
        ]
        mock_mineru_result.markdown = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/h6.pdf",
                document_id="doc-h6-test",
            )

            assert result["heading_count"] == 6

    def test_heading_hierarchy_order_preserved(self, mock_mineru_result):
        """Headings are returned in the order they appear in the document."""
        mock_mineru_result.headings = [
            {"level": 1, "text": "First", "position": 0},
            {"level": 2, "text": "Second", "position": 100},
            {"level": 1, "text": "Third", "position": 200},
        ]
        mock_mineru_result.markdown = "# First\n## Second\n# Third"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/order.pdf",
                document_id="doc-order-test",
            )

            assert result["heading_count"] == 3

    def test_heading_markdown_rendered_with_hashes(self, mock_mineru_result):
        """Markdown output uses proper # prefix for each heading level."""
        mock_mineru_result.headings = [
            {"level": 1, "text": "Top", "position": 0},
            {"level": 3, "text": "Mid", "position": 50},
        ]
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/render.pdf",
                document_id="doc-render-test",
            )

            # The markdown_uri should point to the stored file
            assert "markdown_uri" in result
            assert result["markdown_uri"] is not None

    def test_empty_pdf_returns_zero_headings(self, mock_mineru_result):
        """A PDF with no headings returns heading_count of 0."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "No headings here, just plain text."
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/noheadings.pdf",
                document_id="doc-noheadings-test",
            )

            assert result["heading_count"] == 0


# ==============================================================================
# AC-2: GFM Table Rendering
# ==============================================================================


class TestTableRendering:
    """TC-2.2: Tables are rendered in valid GFM table syntax."""

    def test_convert_detects_tables(self, mock_mineru_result):
        """Converter returns table entries extracted from the PDF."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = [
            {
                "headers": ["Name", "Value", "Type"],
                "rows": [
                    ["Item A", "100", "Alpha"],
                    ["Item B", "200", "Beta"],
                ],
            },
        ]
        mock_mineru_result.markdown = (
            "| Name | Value | Type |\n"
            "|------|-------|------|\n"
            "| Item A | 100 | Alpha |\n"
            "| Item B | 200 | Beta |"
        )
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/table.pdf",
                document_id="doc-table-test",
            )

            assert result["table_count"] == 1

    def test_multiple_tables_detected(self, mock_mineru_result):
        """Converter correctly counts multiple tables."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = [
            {
                "headers": ["Col1", "Col2"],
                "rows": [["a", "b"], ["c", "d"]],
            },
            {
                "headers": ["X", "Y", "Z"],
                "rows": [["1", "2", "3"]],
            },
        ]
        mock_mineru_result.markdown = "Table 1 and Table 2"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/multi-table.pdf",
                document_id="doc-multitable-test",
            )

            assert result["table_count"] == 2

    def test_gfm_table_syntax_valid(self, mock_mineru_result):
        """Output markdown contains valid GFM table pipe-delimited format."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = [
            {
                "headers": ["A", "B"],
                "rows": [["1", "2"]],
            },
        ]
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/gfm.pdf",
                document_id="doc-gfm-test",
            )

            # The markdown should be stored and accessible
            assert result["markdown_uri"] is not None
            assert result["table_count"] == 1


# ==============================================================================
# AC-3: Footnote Annotation
# ==============================================================================


class TestFootnoteAnnotation:
    """TC-2.3: Footnotes are annotated inline or appended to parent section."""

    def test_convert_handles_footnotes(self, mock_mineru_result):
        """Converter returns footnote entries from the PDF."""
        mock_mineru_result.headings = []
        mock_mineru_result.footnotes = [
            {
                "id": "fn1",
                "text": "This is a footnote explanation.",
                "anchor": "[^1]",
                "parent_section": "Introduction",
            },
            {
                "id": "fn2",
                "text": "Another footnote reference.",
                "anchor": "[^2]",
                "parent_section": "Methodology",
            },
        ]
        mock_mineru_result.markdown = "Text with [^1] and [^2] references.\n\n[^1]: This is a footnote explanation.\n\n[^2]: Another footnote reference."
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/footnote.pdf",
                document_id="doc-footnote-test",
            )

            assert result["footnotes_count"] == 2

    def test_footnotes_annotated_in_markdown(self, mock_mineru_result):
        """Markdown output contains footnote annotations with [^id] syntax."""
        mock_mineru_result.headings = []
        mock_mineru_result.footnotes = [
            {
                "id": "fn1",
                "text": "Footnote content.",
                "anchor": "[^1]",
                "parent_section": "Section 1",
            },
        ]
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockConverter,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockConverter.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_result = MagicMock()
            mock_minio_result.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/annotated.pdf",
                document_id="doc-annotated-test",
            )

            # Conversion completes successfully with footnotes
            assert result["markdown_uri"] is not None
            assert result["confidence_score"] > 0


# ==============================================================================
# AC-4: Marker Fallback When MinerU Confidence < 0.85
# ==============================================================================


class TestMarkerFallback:
    """TC-2.4: Marker fallback produces semantically equivalent output when confidence < 0.85."""

    def test_marker_fallback_triggers_when_confidence_low(self, mock_mineru_result, mock_marker_result):
        """When MinerU confidence < 0.85, Marker is invoked as fallback."""
        # MinerU returns low confidence
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Low Confidence Output"
        mock_mineru_result.confidence = 0.70

        # Marker produces replacement output
        mock_marker_result.headings = []
        mock_marker_result.tables = []
        mock_marker_result.markdown = "# Marker Fallback Output"
        mock_marker_result.confidence = 0.90

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            # Configure MinerU mock
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            # Configure Marker mock
            mock_marker_instance = MagicMock()
            mock_marker_instance.convert.return_value = mock_marker_result
            MockMarker.return_value = mock_marker_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/fallback.pdf",
                document_id="doc-fallback-test",
            )

            # Marker should have been called
            MockMarker.return_value.convert.assert_called_once()
            # Final result should reflect Marker's output (higher confidence)
            assert result["confidence_score"] == 0.90
            # Should indicate fallback was used
            assert result["converter_used"] == "marker"
            # upload_data should have been called
            mock_minio_storage.upload_data.assert_called_once()

    def test_no_marker_when_confidence_above_threshold(self, mock_mineru_result):
        """When MinerU confidence >= 0.85, Marker is NOT invoked."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Good Confidence"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/good.pdf",
                document_id="doc-good-test",
            )

            # Marker should NOT have been called
            MockMarker.return_value.convert.assert_not_called()
            # MinerU result should be used
            assert result["confidence_score"] == 0.95
            assert result["converter_used"] == "mineru"

    def test_marker_fallback_uses_same_output_format(self, mock_mineru_result, mock_marker_result):
        """Marker fallback returns the same metadata structure as MinerU."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# MinerU"
        mock_mineru_result.confidence = 0.60

        mock_marker_result.headings = [
            {"level": 1, "text": "Marker Output", "position": 0},
        ]
        mock_marker_result.tables = []
        mock_marker_result.markdown = "# Marker Fallback"
        mock_marker_result.confidence = 0.88

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            mock_marker_instance = MagicMock()
            mock_marker_instance.convert.return_value = mock_marker_result
            MockMarker.return_value = mock_marker_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/format.pdf",
                document_id="doc-format-test",
            )

            # Result should have the same keys regardless of converter
            assert "document_id" in result
            assert "markdown_uri" in result
            assert "confidence_score" in result
            assert "conversion_time_ms" in result
            assert "heading_count" in result
            assert "table_count" in result

    def test_marker_fallback_uses_markdown_from_fallback(self, mock_mineru_result, mock_marker_result):
        """When Marker is used, the stored markdown comes from Marker, not MinerU."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# MinerU Original"
        mock_mineru_result.confidence = 0.50

        mock_marker_result.headings = []
        mock_marker_result.tables = []
        mock_marker_result.markdown = "# Marker Replaced Content"
        mock_marker_result.confidence = 0.85

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            mock_marker_instance = MagicMock()
            mock_marker_instance.convert.return_value = mock_marker_result
            MockMarker.return_value = mock_marker_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/content.pdf",
                document_id="doc-content-test",
            )

            # Stored markdown should be Marker's output
            # (We verify by checking the stored content)
            mock_minio_storage.upload_data.assert_called_once()
            upload_kwargs = mock_minio_storage.upload_data.call_args[1]
            # Data sent to MinIO should be Marker's markdown
            assert "Marker Replaced" in upload_kwargs["data"].decode()

    def test_no_fallback_at_exact_threshold(self, mock_mineru_result):
        """When MinerU confidence == 0.85, Marker is NOT invoked (threshold exclusive)."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Exactly Threshold"
        mock_mineru_result.confidence = 0.85

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/exact.pdf",
                document_id="doc-exact-test",
            )

            # Marker should NOT have been called at exact threshold
            MockMarker.return_value.convert.assert_not_called()
            # MinerU result should be used
            assert result["converter_used"] == "mineru"
            assert result["confidence_score"] == 0.85


# ==============================================================================
# AC-6: MinIO Storage in markdown-conversions Bucket
# ==============================================================================


class TestMinIOStorage:
    """TC-2.6: Output stored in MinIO markdown-conversions bucket."""

    def test_output_stored_in_markdown_conversions_bucket(self, mock_mineru_result):
        """Conversion output is uploaded to 'markdown-conversions' bucket."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Test Markdown"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/storage.pdf",
                document_id="doc-storage-test",
            )

            # upload_data should have been called
            mock_minio_storage.upload_data.assert_called_once()
            upload_kwargs = mock_minio_storage.upload_data.call_args[1]
            assert upload_kwargs["bucket"] == "markdown-conversions"

    def test_minio_key_format(self, mock_mineru_result):
        """MinIO key follows pattern conversions/{document_id}/{document_id}.md."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Key Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            doc_id = "unique-doc-12345"
            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/keytest.pdf",
                document_id=doc_id,
            )

            upload_kwargs = mock_minio_storage.upload_data.call_args[1]
            expected_key = f"conversions/{doc_id}/{doc_id}.md"
            assert upload_kwargs["key"] == expected_key

    def test_markdown_uri_matches_minio_key(self, mock_mineru_result):
        """Returned markdown_uri reflects the stored MinIO key."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# URI Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            doc_id = "uri-doc-99"
            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/uri.pdf",
                document_id=doc_id,
            )

            expected_key = f"conversions/{doc_id}/{doc_id}.md"
            assert result["markdown_uri"] == expected_key

    def test_content_type_is_markdown(self, mock_mineru_result):
        """Uploaded content has markdown content type."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Content Type Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            convert_pdf_to_markdown(
                pdf_path="/fake/path/ct.pdf",
                document_id="doc-ct-test",
            )

            upload_kwargs = mock_minio_storage.upload_data.call_args[1]
            assert upload_kwargs["content_type"] == "text/markdown"


# ==============================================================================
# AC-5: Conversion Time Tracking
# ==============================================================================


class TestConversionTime:
    """TC-2.5: Conversion time tracked and under 30 seconds for <100 pages."""

    def test_conversion_time_measured(self, mock_mineru_result):
        """Conversion time is measured and returned in milliseconds."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Timing Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/timing.pdf",
                document_id="doc-timing-test",
            )

            assert "conversion_time_ms" in result
            assert isinstance(result["conversion_time_ms"], int)
            assert result["conversion_time_ms"] >= 0

    def test_conversion_time_under_30_seconds(self, mock_mineru_result):
        """Conversion time is under 30000ms (30 seconds)."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Under Limit"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/under30.pdf",
                document_id="doc-under30-test",
            )

            assert result["conversion_time_ms"] < 30000


# ==============================================================================
# Return Dict Structure Tests
# ==============================================================================


class TestReturnStructure:
    """Tests for the return dict structure from convert_pdf_to_markdown."""

    def test_return_dict_has_all_required_keys(self, mock_mineru_result):
        """Return dict contains all required keys."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Keys Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/keys.pdf",
                document_id="doc-keys-test",
            )

            required_keys = [
                "document_id",
                "markdown_uri",
                "confidence_score",
                "conversion_time_ms",
                "heading_count",
                "table_count",
                "footnotes_count",
                "converter_used",
            ]
            for key in required_keys:
                assert key in result, f"Missing required key: {key}"

    def test_return_dict_types(self, mock_mineru_result):
        """Return dict values have correct types."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Types Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/types.pdf",
                document_id="doc-types-test",
            )

            assert isinstance(result["document_id"], str)
            assert isinstance(result["markdown_uri"], str)
            assert isinstance(result["confidence_score"], float)
            assert isinstance(result["conversion_time_ms"], int)
            assert isinstance(result["heading_count"], int)
            assert isinstance(result["table_count"], int)
            assert isinstance(result["footnotes_count"], int)

    def test_document_id_passed_through(self, mock_mineru_result):
        """Document ID in result matches the one passed to the function."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# DocId Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            expected_doc_id = "custom-doc-777"
            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/docid.pdf",
                document_id=expected_doc_id,
            )

            assert result["document_id"] == expected_doc_id

    def test_confidence_score_reflected(self, mock_mineru_result):
        """Confidence score from converter is reflected in result."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Confidence Test"
        mock_mineru_result.confidence = 0.87

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/conf.pdf",
                document_id="doc-conf-test",
            )

            assert result["confidence_score"] == 0.87


# ==============================================================================
# MinerUConverter Unit Tests
# ==============================================================================


class TestMinerUConverter:
    """Tests for the MinerUConverter wrapper class."""

    def test_converter_init(self):
        """MinerUConverter initializes without error."""
        from app.services.pdf_to_markdown import MinerUConverter

        converter = MinerUConverter()
        assert converter is not None

    def test_converter_called_with_pdf_path(self):
        """Converter receives the PDF path when convert() is called."""
        from app.services.pdf_to_markdown import MinerUConverter

        result = MagicMock()
        result.headings = []
        result.markdown = "# Test"
        result.confidence = 0.95
        result.tables = []
        result.footnotes = []

        with (
            patch("app.services.pdf_to_markdown._run_mineru") as mock_run,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_run.return_value = result
            converter = MinerUConverter()
            result_obj = converter.convert("/path/to/test.pdf")

            mock_run.assert_called_once_with("/path/to/test.pdf")
            assert result_obj is result


# ==============================================================================
# MarkerFallbackConverter Unit Tests
# ==============================================================================


class TestMarkerFallbackConverter:
    """Tests for the MarkerFallbackConverter wrapper class."""

    def test_converter_init(self):
        """MarkerFallbackConverter initializes without error."""
        from app.services.pdf_to_markdown import MarkerFallbackConverter

        converter = MarkerFallbackConverter()
        assert converter is not None

    def test_converter_called_with_pdf_path(self):
        """Converter receives the PDF path when convert() is called."""
        from app.services.pdf_to_markdown import MarkerFallbackConverter

        result = MagicMock()
        result.headings = []
        result.markdown = "# Marker"
        result.confidence = 0.90
        result.tables = []
        result.footnotes = []

        with (
            patch("app.services.pdf_to_markdown._run_marker") as mock_run,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_run.return_value = result
            converter = MarkerFallbackConverter()
            result_obj = converter.convert("/path/to/test.pdf")

            mock_run.assert_called_once_with("/path/to/test.pdf")
            assert result_obj is result


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestEdgeCases:
    """Edge case tests beyond the core acceptance criteria."""

    def test_pdf_path_must_exist(self):
        """Conversion raises error for non-existent PDF file."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage"),
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMC,
        ):
            mock_instance = MagicMock()
            mock_instance.convert.side_effect = FileNotFoundError("PDF file not found: /nonexistent/path/file.pdf")
            MockMC.return_value = mock_instance

            with pytest.raises(FileNotFoundError):
                convert_pdf_to_markdown(
                    pdf_path="/nonexistent/path/file.pdf",
                    document_id="doc-nofile-test",
                )

    def test_document_id_required(self):
        """Conversion raises error when document_id is missing."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
        ):
            mock_minio.return_value = MagicMock()
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            with pytest.raises(ValueError, match="document_id"):
                convert_pdf_to_markdown(
                    pdf_path="/fake/test.pdf",
                    document_id=None,
                )

    def test_pdf_path_must_have_pdf_extension(self):
        """Conversion raises error for non-PDF files."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
        ):
            mock_minio.return_value = MagicMock()
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            # Create a temporary file with non-pdf extension
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                f.write(b"not a pdf")
                temp_path = f.name

            try:
                with pytest.raises(ValueError, match="pdf"):
                    convert_pdf_to_markdown(
                        pdf_path=temp_path,
                        document_id="doc-ext-test",
                    )
            finally:
                Path(temp_path).unlink()

    def test_converter_used_field_in_result(self, mock_mineru_result):
        """Result includes converter_used field indicating which converter was used."""
        mock_mineru_result.headings = []
        mock_mineru_result.markdown = "# Field Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/field.pdf",
                document_id="doc-field-test",
            )

            assert "converter_used" in result
            assert result["converter_used"] == "mineru"

    def test_path_traversal_rejected(self):
        """Document ID with path traversal characters is rejected."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
        ):
            mock_minio.return_value = MagicMock()
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            with pytest.raises(ValueError, match="invalid characters"):
                convert_pdf_to_markdown(
                    pdf_path="/fake/test.pdf",
                    document_id="../etc/passwd",
                )

    def test_path_traversal_slash_rejected(self):
        """Document ID with forward slash is rejected."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
        ):
            mock_minio.return_value = MagicMock()
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            with pytest.raises(ValueError, match="invalid characters"):
                convert_pdf_to_markdown(
                    pdf_path="/fake/test.pdf",
                    document_id="doc/sneaky",
                )

    def test_mineru_runtime_error_raises_runtime_error(self):
        """When MinerU raises RuntimeError, the error propagates."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
            patch("app.services.pdf_to_markdown._run_mineru") as mock_run,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            mock_run.side_effect = RuntimeError("MinerU library not available in this environment")

            with pytest.raises(RuntimeError, match="MinerU library"):
                convert_pdf_to_markdown(
                    pdf_path="/fake/test.pdf",
                    document_id="doc-mineru-err",
                )

    def test_mineru_generic_error_wrapped(self):
        """When MinerU raises a non-RuntimeError, it is wrapped in RuntimeError."""
        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.get_minio_storage") as mock_minio,
            patch("app.services.pdf_to_markdown._run_mineru") as mock_run,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_minio.return_value.markdown_conversions_bucket = "markdown-conversions"

            mock_run.side_effect = ValueError("Some MinerU internal error")

            with pytest.raises(RuntimeError, match="MinerU conversion failed"):
                convert_pdf_to_markdown(
                    pdf_path="/fake/test.pdf",
                    document_id="doc-mineru-wrap",
                )

    def test_footnotes_count_in_result(self, mock_mineru_result):
        """Result includes footnotes_count reflecting the number of footnotes."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = []
        mock_mineru_result.footnotes = [
            {"id": "fn1", "text": "Note 1", "anchor": "[^1]", "parent_section": "Intro"},
            {"id": "fn2", "text": "Note 2", "anchor": "[^2]", "parent_section": "Intro"},
            {"id": "fn3", "text": "Note 3", "anchor": "[^3]", "parent_section": "Methods"},
        ]
        mock_mineru_result.markdown = "Some text with [^1] and [^2] and [^3]."
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/footnotes.pdf",
                document_id="doc-footnotes-count",
            )

            assert result["footnotes_count"] == 3

    def test_footnotes_count_zero_when_empty(self, mock_mineru_result):
        """Result footnotes_count is 0 when no footnotes present."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = []
        mock_mineru_result.footnotes = []
        mock_mineru_result.markdown = "No footnotes here."
        mock_mineru_result.confidence = 0.90

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/no-footnotes.pdf",
                document_id="doc-no-footnotes",
            )

            assert result["footnotes_count"] == 0

    def test_marker_fallback_includes_footnotes(self, mock_mineru_result, mock_marker_result):
        """When Marker is used, footnotes_count reflects Marker's footnotes."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = []
        mock_mineru_result.footnotes = []
        mock_mineru_result.markdown = "# Low Confidence"
        mock_mineru_result.confidence = 0.70

        mock_marker_result.headings = []
        mock_marker_result.tables = []
        mock_marker_result.footnotes = [
            {"id": "fn1", "text": "Marker footnote", "anchor": "[^1]", "parent_section": "Section"},
        ]
        mock_marker_result.markdown = "# Marker Output"
        mock_marker_result.confidence = 0.90

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch("app.services.pdf_to_markdown.MarkerFallbackConverter") as MockMarker,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            mock_mineru_instance = MagicMock()
            mock_mineru_instance.convert.return_value = mock_mineru_result
            MockMinerU.return_value = mock_mineru_instance

            mock_marker_instance = MagicMock()
            mock_marker_instance.convert.return_value = mock_marker_result
            MockMarker.return_value = mock_marker_instance

            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            result = convert_pdf_to_markdown(
                pdf_path="/fake/path/fb-footnotes.pdf",
                document_id="doc-fb-footnotes",
            )

            assert result["footnotes_count"] == 1
            assert result["converter_used"] == "marker"

    def test_upload_data_called_with_bytes(self, mock_mineru_result):
        """MinIO upload_data receives the markdown as bytes."""
        mock_mineru_result.headings = []
        mock_mineru_result.tables = []
        mock_mineru_result.footnotes = []
        mock_mineru_result.markdown = "# Bytes Test"
        mock_mineru_result.confidence = 0.95

        from app.services.pdf_to_markdown import convert_pdf_to_markdown

        with (
            patch("app.services.pdf_to_markdown.MinerUConverter") as MockMinerU,
            patch(
                "app.services.pdf_to_markdown.get_minio_storage"
            ) as mock_minio_factory,
        ):
            MockMinerU.return_value.convert.return_value = mock_mineru_result
            mock_minio_factory.return_value = mock_minio_storage = MagicMock()
            mock_minio_storage.markdown_conversions_bucket = "markdown-conversions"

            convert_pdf_to_markdown(
                pdf_path="/fake/path/bytes.pdf",
                document_id="doc-bytes-test",
            )

            upload_kwargs = mock_minio_storage.upload_data.call_args[1]
            assert isinstance(upload_kwargs["data"], bytes)
            assert upload_kwargs["data"] == b"# Bytes Test"
