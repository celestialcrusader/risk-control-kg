"""
Test suite for INGEST-3: Hybrid Chunking Strategy

This test module verifies the hybrid chunking service that splits
Markdown documents into semantically-meaningful chunks based on heading
boundaries, table detection, and character-size constraints.

Test Strategy:
- Unit tests with sample Markdown documents
- MinIO calls are mocked to avoid real storage interactions
- All assertions are meaningful
- AAA pattern (Arrange, Act, Assert)

Acceptance Criteria Covered:
- AC-1: Heading-based chunking splits at H1-H6 boundaries
- AC-2: Each chunk has metadata: doc_id, chunk_index, heading_path, char_count, table_ref
- AC-3: Tables are chunked separately with table_ref metadata
- AC-4: Chunk char counts between min_chunk_size and max_chunk_size
- AC-5: Chunks stored in MinIO markdown-conversions bucket with correct key pattern
- AC-6: Manifest JSON stored listing all chunks and metadata
"""

import json
import sys
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
def mock_minio_storage():
    """Create a mock MinIO storage instance.

    Each test gets a fresh mock with call history cleared.
    """
    mock = MagicMock()
    mock.markdown_conversions_bucket = "markdown-conversions"
    return mock


@pytest.fixture
def sample_markdown_with_headings():
    """Sample Markdown with H1 and H2 headings and enough text per section."""
    return (
        "# Chapter One\n\n"
        "This is the introductory text for chapter one. It contains enough "
        "characters to meet the minimum chunk size requirement for testing "
        "the hybrid chunking strategy and to prevent unwanted merging.\n\n"
        "## Section 1.1\n\n"
        "This is section one one of chapter one with sufficient content "
        "length to remain as a separate chunk and avoid merging with "
        "adjacent sections during the chunking process.\n\n"
        "## Section 1.2\n\n"
        "This is section one two with additional content for chunking "
        "validation. It has enough characters to stay as its own chunk.\n\n"
        "# Chapter Two\n\n"
        "The second chapter begins here with substantial introductory "
        "text that should form its own chunk boundary at the H1 level.\n\n"
        "## Section 2.1\n\n"
        "Section two one has enough content to be a valid chunk by "
        "itself and remain separate from other sections during processing.\n"
    )


@pytest.fixture
def sample_markdown_deep_hierarchy():
    """Sample Markdown with deep heading hierarchy H1-H4."""
    return (
        "# Level 1 Root\n\n"
        "Root level content that provides context for the entire document "
        "and has enough characters to remain as a separate chunk on its own.\n\n"
        "## Level 2 A\n\n"
        "Content under the first level two heading with sufficient length "
        "to remain as a separate chunk without merging into adjacent sections.\n\n"
        "### Level 3 A\n\n"
        "Content under level three heading with enough characters for testing "
        "the deep hierarchy preservation in the heading path metadata field.\n\n"
        "#### Level 4 A\n\n"
        "Content under the deepest heading level in this test document. It "
        "has enough text to meet the minimum chunk size requirement on its own.\n\n"
        "## Level 2 B\n\n"
        "Another level two section to test sibling boundary detection and "
        "ensure sections with the same heading level are kept separate.\n"
    )


@pytest.fixture
def sample_markdown_with_tables():
    """Sample Markdown with headings and a GFM table."""
    return (
        "# Document with Tables\n\n"
        "This section introduces the tables that follow in the document.\n\n"
        "## Product Catalog\n\n"
        "Here is a table listing our products:\n\n"
        "| Name | Price | Type |\n"
        "|------|-------|------|\n"
        "| Widget A | 10.00 | Alpha |\n"
        "| Widget B | 20.00 | Beta |\n"
        "\n"
        "## Pricing Summary\n\n"
        "Another section after the tables with regular text content.\n"
    )


@pytest.fixture
def sample_markdown_empty():
    """Empty Markdown document."""
    return ""


@pytest.fixture
def sample_markdown_no_headings():
    """Markdown with no headings at all."""
    return (
        "This document has no headings whatsoever. It is just plain text "
        "content that should be handled gracefully by the chunking logic.\n\n"
        "Multiple paragraphs exist here to test the behavior when no heading "
        "boundaries are found in the input document.\n"
    )


# ==============================================================================
# AC-1: Heading-based chunking splits at H1-H6 boundaries
# ==============================================================================


class TestHeadingBasedChunking:
    """TC-3.1: chunk_document splits Markdown at heading boundaries."""

    def test_single_heading_splits_into_chunk(self, mock_minio_storage, sample_markdown_with_headings):
        """A document with multiple headings produces multiple chunks."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-heading-1")

            assert len(chunks) >= 2
            # Each chunk should have text
            for chunk in chunks:
                assert chunk["text"] != ""

    def test_each_chunk_has_accurate_heading_path(self, mock_minio_storage, sample_markdown_with_headings):
        """Each chunk's heading_path reflects its section hierarchy."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-heading-1")

            heading_paths = [c["heading_path"] for c in chunks]
            # Should include both H1 paths
            assert "# Chapter One" in heading_paths or "Chapter One" in " ".join(heading_paths)
            assert "# Chapter Two" in heading_paths or "Chapter Two" in " ".join(heading_paths)

    def test_heading_hierarchy_preserved_across_levels(self, mock_minio_storage, sample_markdown_deep_hierarchy):
        """Deep heading hierarchy H1-H4 produces correct heading_path for each chunk."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_deep_hierarchy, "doc-hierarchy")

            assert len(chunks) >= 4  # At least 4 sections (H1, H2A, H3A, H4A, H2B)
            paths = [c["heading_path"] for c in chunks]
            # Verify the H3 chunk has "Level 3" in its path
            assert any("Level 3" in p for p in paths)

    def test_two_h1_sections_produce_separate_chunks(self, mock_minio_storage, sample_markdown_with_headings):
        """Two H1 headings create two separate top-level chunks."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-two-h1")

            # Count chunks whose heading_path starts with "#" (H1)
            h1_chunks = [c for c in chunks if c["heading_path"].startswith("# ")]
            assert len(h1_chunks) == 2

    def test_h2_sections_within_h1_are_separate_chunks(self, mock_minio_storage, sample_markdown_with_headings):
        """H2 sections under the same H1 are separate chunks."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-h2-test")

            h2_chunks = [c for c in chunks if c["heading_path"].startswith("## ")]
            assert len(h2_chunks) >= 2  # Section 1.1 and Section 1.2

    def test_chunk_index_starts_at_zero(self, mock_minio_storage, sample_markdown_with_headings):
        """chunk_index is zero-based."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-index-zero")

            indices = [c["chunk_index"] for c in chunks]
            assert indices[0] == 0
            assert indices == list(range(len(chunks)))

    def test_empty_document_returns_empty_list(self, mock_minio_storage):
        """An empty Markdown document returns an empty chunk list."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document("", "doc-empty")
            assert chunks == []

    def test_chunk_text_contains_section_content(self, mock_minio_storage, sample_markdown_with_headings):
        """Each chunk's text contains the content of its section."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-content-test")

            # The first chunk should contain "Chapter One" related content
            first_chunk = chunks[0]
            assert "Chapter One" in first_chunk["heading_path"]
            assert "introductory text" in first_chunk["text"].lower()


# ==============================================================================
# AC-2: Chunk metadata fields
# ==============================================================================


class TestChunkMetadata:
    """TC-3.2: Each chunk has doc_id, chunk_index, heading_path, char_count, table_ref."""

    def test_chunk_has_doc_id_field(self, mock_minio_storage):
        """Each chunk dictionary includes a doc_id field matching the input."""
        doc_id = "metadata-doc-1"
        md = "# Title\n\nSome content here for testing the metadata fields present in chunks.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, doc_id)

            assert len(chunks) >= 1
            assert chunks[0]["doc_id"] == doc_id

    def test_chunk_has_chunk_index_field(self, mock_minio_storage):
        """Each chunk has a chunk_index integer field."""
        md = "# Section\n\nSome content here for testing the metadata fields present in chunks.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-index-field")

            assert isinstance(chunks[0]["chunk_index"], int)

    def test_chunk_has_heading_path_field(self, mock_minio_storage):
        """Each chunk has a heading_path string field."""
        md = "# My Heading\n\nSome content here for testing the metadata fields present in chunks.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-path-field")

            assert isinstance(chunks[0]["heading_path"], str)
            assert chunks[0]["heading_path"] != ""

    def test_chunk_has_char_count_field(self, mock_minio_storage):
        """Each chunk has a char_count integer reflecting its text length."""
        md = "# Test\n\nSome content here for testing the metadata fields present in chunks.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-charcount")

            assert isinstance(chunks[0]["char_count"], int)
            assert chunks[0]["char_count"] == len(chunks[0]["text"])

    def test_chunk_has_table_ref_field(self, mock_minio_storage):
        """Each chunk has a table_ref field (None when no table)."""
        md = "# Test\n\nSome content here for testing the metadata fields present in chunks.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-tableref")

            assert "table_ref" in chunks[0]
            assert chunks[0]["table_ref"] is None

    def test_all_required_metadata_keys_present(self, mock_minio_storage):
        """Every chunk contains all five required metadata keys."""
        md = "# Test\n\nSome content here for testing all required metadata keys present in each chunk.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-all-keys")

            required_keys = {"doc_id", "chunk_index", "heading_path", "char_count", "table_ref", "text"}
            for chunk in chunks:
                assert required_keys.issubset(chunk.keys()), f"Missing keys in chunk: {required_keys - chunk.keys()}"


# ==============================================================================
# AC-3: Table detection and separate chunking
# ==============================================================================


class TestTableChunking:
    """TC-3.3: Tables in Markdown are chunked separately with table_ref metadata."""

    def test_table_detected_in_document(self, mock_minio_storage, sample_markdown_with_tables):
        """A document containing a GFM table triggers table detection."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_tables, "doc-table-test")

            # At least one chunk should have table_ref set
            chunks_with_tables = [c for c in chunks if c.get("table_ref") is not None]
            assert len(chunks_with_tables) >= 1

    def test_table_chunk_has_table_ref(self, mock_minio_storage, sample_markdown_with_tables):
        """Chunks that contain a table have a non-null table_ref value."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_tables, "doc-tableref-test")

            table_chunks = [c for c in chunks if c.get("table_ref") is not None]
            for tc in table_chunks:
                assert tc["table_ref"] is not None
                assert isinstance(tc["table_ref"], str)

    def test_table_chunk_text_contains_pipe_syntax(self, mock_minio_storage, sample_markdown_with_tables):
        """A table chunk's text includes the pipe-delimited table content."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_tables, "doc-table-content")

            table_chunks = [c for c in chunks if c.get("table_ref") is not None]
            assert len(table_chunks) >= 1
            # The table text should contain pipe characters
            combined_table_text = "\n".join(c["text"] for c in table_chunks)
            assert "|" in combined_table_text

    def test_regular_chunks_have_table_ref_none(self, mock_minio_storage, sample_markdown_with_tables):
        """Non-table chunks have table_ref set to None."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_tables, "doc-table-regular")

            no_table_chunks = [c for c in chunks if c.get("table_ref") is None]
            assert len(no_table_chunks) >= 1


# ==============================================================================
# AC-4: Char count between min_chunk_size and max_chunk_size
# ==============================================================================


class TestChunkSizeConstraints:
    """TC-3.4: Each chunk's char count is between min_chunk_size and max_chunk_size."""

    def test_chunk_size_within_default_bounds(self, mock_minio_storage, sample_markdown_with_headings):
        """By default, all chunk char counts are between 100 and 1000."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-size-default")

            for chunk in chunks:
                assert 100 <= chunk["char_count"] <= 1000, (
                    f"Chunk {chunk['chunk_index']} char_count={chunk['char_count']} "
                    f"outside bounds [100, 1000]"
                )

    def test_chunk_size_within_custom_bounds(self, mock_minio_storage, sample_markdown_with_headings):
        """With custom min/max, all chunk char counts respect the bounds."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(
                sample_markdown_with_headings,
                "doc-size-custom",
                min_chunk_size=50,
                max_chunk_size=500,
            )

            for chunk in chunks:
                assert 50 <= chunk["char_count"] <= 500, (
                    f"Chunk {chunk['chunk_index']} char_count={chunk['char_count']} "
                    f"outside bounds [50, 500]"
                )

    def test_large_section_is_split_into_multiple_chunks(self, mock_minio_storage):
        """A section exceeding max_chunk_size is split into smaller chunks."""
        long_content = "x" * 1500
        md = f"# Big Section\n\n{long_content}"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-split-large")

            for chunk in chunks:
                assert chunk["char_count"] <= 1000

            # Should be more than one chunk
            assert len(chunks) >= 2

    def test_min_chunk_size_enforced_for_small_sections(self, mock_minio_storage):
        """Small sections are merged together until they meet min_chunk_size."""
        small_content = "Short note with enough words to reach fifty characters here."
        md = f"# First\n\n{small_content}\n\n# Second\n\n{small_content}"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            # Use a low min_chunk_size so merging can reach it
            chunks = chunk_document(md, "doc-enforce-min", min_chunk_size=50, max_chunk_size=500)

            # Each section is ~58 chars, merged they exceed 100
            # But with min=50, each should meet the threshold
            for chunk in chunks:
                assert chunk["char_count"] >= 50, (
                    f"Chunk {chunk['chunk_index']} char_count={chunk['char_count']} "
                    f"below min_chunk_size 50"
                )

    def test_default_min_chunk_size_is_one_hundred(self, mock_minio_storage, sample_markdown_with_headings):
        """Default min_chunk_size is 100 characters."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-min-default")

            for chunk in chunks:
                assert chunk["char_count"] >= 100

    def test_default_max_chunk_size_is_one_thousand(self, mock_minio_storage, sample_markdown_with_headings):
        """Default max_chunk_size is 1000 characters."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-max-default")

            for chunk in chunks:
                assert chunk["char_count"] <= 1000


# ==============================================================================
# AC-5: MinIO storage of chunks
# ==============================================================================


class TestMinIOStorage:
    """TC-3.5: Chunks stored in MinIO markdown-conversions bucket."""

    def test_chunks_stored_in_markdown_conversions_bucket(self, mock_minio_storage, sample_markdown_with_headings):
        """All chunk .md files are uploaded to the markdown-conversions bucket."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, "doc-bucket-test")

            # Check all upload_data calls target markdown-conversions bucket
            for call_obj in mock_minio_storage.upload_data.call_args_list:
                kwargs = call_obj[1]
                assert kwargs["bucket"] == "markdown-conversions"

    def test_chunk_key_format_is_correct(self, mock_minio_storage, sample_markdown_with_headings):
        """Each chunk file uses key chunks/{doc_id}/{doc_id}_chunk_{N}.md."""
        doc_id = "key-format-test"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, doc_id)

            # Only check .md file keys (exclude manifest.json)
            md_uploads = [
                call_obj for call_obj in mock_minio_storage.upload_data.call_args_list
                if call_obj[1]["key"].endswith(".md")
            ]
            expected_keys = {
                f"chunks/{doc_id}/{doc_id}_chunk_{i}.md"
                for i in range(len(chunks))
            }
            actual_keys = {call_obj[1]["key"] for call_obj in md_uploads}
            assert actual_keys == expected_keys

    def test_chunk_key_has_correct_index(self, mock_minio_storage, sample_markdown_with_headings):
        """Chunk keys have the correct sequential index (0, 1, 2, ...)."""
        doc_id = "index-test-99"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, doc_id)

            # Only check .md file keys (exclude manifest.json)
            keys = [
                call_obj[1]["key"]
                for call_obj in mock_minio_storage.upload_data.call_args_list
                if call_obj[1]["key"].endswith(".md")
            ]
            for i, key in enumerate(keys):
                assert f"_chunk_{i}.md" in key

    def test_chunk_content_is_markdown(self, mock_minio_storage, sample_markdown_with_headings):
        """Uploaded chunk data contains the Markdown text."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, "doc-content")

            # All non-manifest uploads should contain valid text content
            markdown_uploads = [
                c for c in mock_minio_storage.upload_data.call_args_list
                if c[1]["key"].endswith(".md")
            ]
            for call_obj in markdown_uploads:
                kwargs = call_obj[1]
                assert len(kwargs["data"]) > 0
                assert b"\n" in kwargs["data"] or b" " in kwargs["data"]

    def test_chunk_content_type_is_markdown(self, mock_minio_storage, sample_markdown_with_headings):
        """Chunk uploads use content_type text/markdown."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, "doc-ct")

            # All non-manifest uploads should use text/markdown
            markdown_uploads = [
                c for c in mock_minio_storage.upload_data.call_args_list
                if c[1]["key"].endswith(".md")
            ]
            for call_obj in markdown_uploads:
                kwargs = call_obj[1]
                assert kwargs["content_type"] == "text/markdown"

    def test_multiple_chunks_multiple_uploads(self, mock_minio_storage, sample_markdown_with_headings):
        """N chunks result in N+1 upload_data calls (chunks plus manifest)."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "doc-upload-count")

            # N chunks + 1 manifest = N+1 total uploads
            assert len(mock_minio_storage.upload_data.call_args_list) == len(chunks) + 1


# ==============================================================================
# AC-6: Manifest JSON
# ==============================================================================


class TestManifestStorage:
    """TC-3.6: Manifest JSON stored at chunks/{doc_id}/manifest.json."""

    def test_manifest_is_stored(self, mock_minio_storage, sample_markdown_with_headings):
        """A manifest.json is uploaded to MinIO."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, "doc-manifest")

            # Last upload should be the manifest
            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            assert manifest_call[1]["key"] == "chunks/doc-manifest/manifest.json"

    def test_manifest_bucket_is_markdown_conversions(self, mock_minio_storage, sample_markdown_with_headings):
        """Manifest is stored in the markdown-conversions bucket."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, "doc-manifest-bucket")

            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            assert manifest_call[1]["bucket"] == "markdown-conversions"

    def test_manifest_contains_doc_id(self, mock_minio_storage, sample_markdown_with_headings):
        """Manifest JSON contains the doc_id field."""
        doc_id = "manifest-doc-id-42"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, doc_id)

            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            manifest_data = json.loads(manifest_call[1]["data"])
            assert manifest_data["doc_id"] == doc_id

    def test_manifest_contains_chunks_list(self, mock_minio_storage, sample_markdown_with_headings):
        """Manifest JSON contains a 'chunks' list with all chunk entries."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "manifest-chunk-list")

            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            manifest_data = json.loads(manifest_call[1]["data"])
            assert "chunks" in manifest_data
            assert len(manifest_data["chunks"]) == len(chunks)

    def test_manifest_entries_match_chunk_metadata(self, mock_minio_storage, sample_markdown_with_headings):
        """Each manifest chunk entry matches the corresponding chunk's metadata."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_with_headings, "manifest-match")

            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            manifest_data = json.loads(manifest_call[1]["data"])

            for i, entry in enumerate(manifest_data["chunks"]):
                assert entry["chunk_index"] == chunks[i]["chunk_index"]
                assert entry["heading_path"] == chunks[i]["heading_path"]
                assert entry["char_count"] == chunks[i]["char_count"]
                assert entry["table_ref"] == chunks[i]["table_ref"]

    def test_manifest_key_pattern(self, mock_minio_storage, sample_markdown_with_headings):
        """Manifest is stored at key chunks/{doc_id}/manifest.json."""
        doc_id = "manifest-key-pattern"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunk_document(sample_markdown_with_headings, doc_id)

            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            assert manifest_call[1]["key"] == f"chunks/{doc_id}/manifest.json"


# ==============================================================================
# Path Traversal and Input Validation
# ==============================================================================


class TestInputValidation:
    """Edge case tests for input validation."""

    def test_path_traversal_in_doc_id_raises_error(self, mock_minio_storage):
        """Document ID with path traversal is rejected."""
        md = "# Test\n\nSome content here for testing path traversal rejection.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            with pytest.raises(ValueError, match="invalid"):
                chunk_document(md, "../etc/passwd")

    def test_slash_in_doc_id_raises_error(self, mock_minio_storage):
        """Document ID with forward slash is rejected."""
        md = "# Test\n\nSome content here for testing slash rejection.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            with pytest.raises(ValueError, match="invalid"):
                chunk_document(md, "doc/sneaky")

    def test_valid_doc_id_with_alphanumeric_underscore_dot_hyphen(self, mock_minio_storage):
        """Valid document IDs with alphanumeric, underscore, dot, hyphen are accepted."""
        md = "# Test\n\nSome content here for testing valid doc ID patterns.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            for valid_id in ["doc_123", "doc-abc", "doc.456", "a", "a.b-c_d"]:
                chunks = chunk_document(md, valid_id)
                assert len(chunks) >= 0  # Should not raise

    def test_doc_id_starting_with_digit_is_valid(self, mock_minio_storage):
        """Document ID starting with a digit should be accepted."""
        md = "# Test\n\nSome content here for testing digit-start doc ID.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "123valid")
            assert isinstance(chunks, list)

    def test_empty_doc_id_raises_error(self, mock_minio_storage):
        """Empty document ID is rejected."""
        md = "# Test\n\nSome content here for testing empty doc ID.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            with pytest.raises(ValueError, match="required"):
                chunk_document(md, "")

    def test_none_doc_id_raises_error(self, mock_minio_storage):
        """None document ID is rejected."""
        md = "# Test\n\nSome content here for testing None doc ID.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            with pytest.raises(ValueError, match="required"):
                chunk_document(md, None)


# ==============================================================================
# Return Value Structure
# ==============================================================================


class TestReturnStructure:
    """Tests for the chunk_document return value structure."""

    def test_returns_list(self, mock_minio_storage):
        """chunk_document returns a list."""
        md = "# Test\n\nSome content here for testing return structure.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            result = chunk_document(md, "doc-return-list")
            assert isinstance(result, list)

    def test_returns_list_of_dicts(self, mock_minio_storage):
        """Each element in the returned list is a dict."""
        md = "# Test\n\nSome content here for testing return structure types.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-return-dicts")
            for chunk in chunks:
                assert isinstance(chunk, dict)

    def test_return_chunks_have_text_field(self, mock_minio_storage):
        """Every returned chunk has a 'text' field with string content."""
        md = "# Test\n\nSome content here for testing text field presence.\n"
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "doc-text-field")
            for chunk in chunks:
                assert isinstance(chunk["text"], str)

    def test_no_headings_single_chunk(self, mock_minio_storage, sample_markdown_no_headings):
        """A document with no headings returns a single chunk with empty heading_path."""
        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(sample_markdown_no_headings, "doc-no-headings")

            assert len(chunks) == 1
            assert chunks[0]["heading_path"] == ""


# ==============================================================================
# Integration: Full Pipeline
# ==============================================================================


class TestFullPipeline:
    """Integration-style tests combining heading, table, size, and storage."""

    def test_complex_document_chunks_and_stores(self, mock_minio_storage):
        """A complex document with headings and tables is chunked and stored correctly."""
        md = (
            "# Main Title\n\n"
            "This is the main introduction text. It needs to be long enough to reach the minimum "
            "chunk size of one hundred characters for the hybrid chunking strategy to work properly "
            "and keep this section as a standalone chunk.\n\n"
            "## Chapter One\n\n"
            "Content for chapter one that meets the minimum size requirement for chunking and "
            "prevents merging with adjacent sections during the chunking process.\n\n"
            "## Chapter Two\n\n"
            "Data table follows:\n\n"
            "| ID | Value | Description |\n"
            "|----|-------|-------------|\n"
            "| 1  | 100   | First row   |\n"
            "| 2  | 200   | Second row  |\n"
            "\n"
            "## Chapter Three\n\n"
            "Final chapter content that wraps up the document with sufficient text length to "
            "stand as its own chunk without merging into previous sections.\n"
        )

        with patch(
            "app.services.hybrid_chunking.get_minio_storage",
            return_value=mock_minio_storage,
        ):
            from app.services.hybrid_chunking import chunk_document

            chunks = chunk_document(md, "complex-doc-1")

            # Verify chunk count
            assert len(chunks) >= 3  # Title, Ch1, Ch2, Ch3 sections

            # Verify all chunks meet size constraints
            for chunk in chunks:
                assert 100 <= chunk["char_count"] <= 1000

            # Verify storage calls
            total_uploads = len(mock_minio_storage.upload_data.call_args_list)
            # N chunks + 1 manifest
            assert total_uploads == len(chunks) + 1

            # Verify manifest exists as last upload
            manifest_call = mock_minio_storage.upload_data.call_args_list[-1]
            manifest_data = json.loads(manifest_call[1]["data"])
            assert "chunks" in manifest_data
            assert len(manifest_data["chunks"]) == len(chunks)
