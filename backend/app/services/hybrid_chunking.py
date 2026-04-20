"""
Hybrid Chunking Service for RCKG.

Provides document chunking that respects Markdown heading boundaries,
detects tables, and enforces character-size constraints. Chunks are stored
in MinIO's markdown-conversions bucket with a manifest JSON for fast lookup.

Usage:
    from app.services.hybrid_chunking import chunk_document

    chunks = chunk_document(
        markdown="# Title\n\nContent here...",
        doc_id="my-document-1",
        min_chunk_size=100,
        max_chunk_size=1000,
    )
"""

import json
import logging
import re
from typing import List, Optional

from app.storage import get_minio_storage

logger = logging.getLogger(__name__)

# Document ID sanitization pattern (same as INGEST-2)
_DOCUMENT_ID_PATTERN = re.compile(r"^[\w][\w.-]*$")

# Heading pattern: H1-H6
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

# Table line pattern: lines containing pipe-delimited columns
_TABLE_LINE_PATTERN = re.compile(r"^\|(.+)\|(\s*)$")

# Default chunk size constraints
DEFAULT_MIN_CHUNK_SIZE = 100
DEFAULT_MAX_CHUNK_SIZE = 1000


def _sanitize_doc_id(doc_id: str) -> str:
    """Validate and sanitize document ID.

    Args:
        doc_id: Document identifier to validate.

    Returns:
        The validated doc_id.

    Raises:
        ValueError: If doc_id is invalid.
    """
    if not doc_id:
        raise ValueError("document_id is required")

    if not _DOCUMENT_ID_PATTERN.match(doc_id):
        raise ValueError(
            f"document_id contains invalid characters: {doc_id!r}. "
            "Only alphanumeric, hyphens, underscores, and dots are allowed "
            "(must start with alphanumeric)."
        )

    return doc_id


def _split_by_headings(markdown: str) -> List[dict]:
    """Split Markdown text into sections at heading boundaries.

    Each section contains the heading line and its body text.

    Args:
        markdown: The full Markdown document text.

    Returns:
        List of dicts with keys: heading (str or None), body (str).
    """
    if not markdown or not markdown.strip():
        return []

    lines = markdown.split("\n")
    sections = []
    current_heading = None
    current_body_lines = []

    for line in lines:
        match = _HEADING_PATTERN.match(line)
        if match:
            # Save previous section if exists
            if current_heading is not None or current_body_lines:
                sections.append({
                    "heading": current_heading,
                    "body": "\n".join(current_body_lines).strip(),
                })
            current_heading = line
            current_body_lines = []
        else:
            current_body_lines.append(line)

    # Save the last section
    if current_heading is not None or current_body_lines:
        sections.append({
            "heading": current_heading or "",
            "body": "\n".join(current_body_lines).strip(),
        })

    return sections


def _detect_tables(text: str) -> List[dict]:
    """Detect GFM tables within a text block.

    A table is defined as consecutive lines starting with |, including
    the separator line (|---|---|).

    Args:
        text: Text block to scan for tables.

    Returns:
        List of dicts with keys: table_text (str), start_line (int), end_line (int).
    """
    lines = text.split("\n")
    tables = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if _TABLE_LINE_PATTERN.match(line):
            # Found start of a table, collect consecutive table lines
            table_lines = [line]
            j = i + 1
            while j < len(lines) and _TABLE_LINE_PATTERN.match(lines[j]):
                table_lines.append(lines[j])
                j += 1

            if len(table_lines) >= 2:  # Need at least header + separator
                tables.append({
                    "table_text": "\n".join(table_lines),
                    "start_line": i,
                    "end_line": j,
                })
            i = j
        else:
            i += 1

    return tables


def _extract_table_and_text(text: str) -> tuple:
    """Separate table content from regular text in a section body.

    Args:
        text: The body text that may contain tables.

    Returns:
        Tuple of (regular_text, tables_list) where tables_list contains
        dicts with 'table_text' and 'table_ref'.
    """
    tables = _detect_tables(text)
    if not tables:
        return text, []

    # Build regular text by removing table lines
    table_lines = set()
    for t in tables:
        for i in range(t["start_line"], t["end_line"]):
            table_lines.add(i)

    lines = text.split("\n")
    regular_lines = [line for i, line in enumerate(lines) if i not in table_lines]
    regular_text = "\n".join(regular_lines).strip()

    # Build table entries with refs
    table_refs = []
    for idx, t in enumerate(tables):
        table_refs.append({
            "table_text": t["table_text"],
            "table_ref": f"table-{idx + 1}",
        })

    return regular_text, table_refs


def _split_text_into_chunks(text: str, min_size: int, max_size: int) -> List[str]:
    """Split text into chunks respecting min/max size constraints.

    If text is shorter than min_size, it is returned as a single chunk.
    If longer than max_size, it is split at paragraph or sentence boundaries.

    Args:
        text: Text to split.
        min_size: Minimum chunk size in characters.
        max_size: Maximum chunk size in characters.

    Returns:
        List of chunk strings.
    """
    if not text or not text.strip():
        return []

    text = text.strip()

    # If text is within bounds, return as single chunk
    if min_size <= len(text) <= max_size:
        return [text]

    # Too small: return as-is (can't split further)
    if len(text) < min_size:
        return [text]

    # Too large: split at paragraph boundaries first
    paragraphs = re.split(r"\n{2,}", text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) <= max_size:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If a single paragraph exceeds max_size, split by sentences
            if len(para) > max_size:
                sentence_chunks = _split_by_sentences(para, max_size)
                chunks.extend(sentence_chunks)
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_by_sentences(text: str, max_size: int) -> List[str]:
    """Split text by sentence boundaries, falling back to character splits.

    Args:
        text: Text to split.
        max_size: Maximum chunk size in characters.

    Returns:
        List of chunk strings.
    """
    sentences = re.split(r"([.!?]\s+)", text)
    sentence_chunks = []
    current = ""

    for part in sentences:
        if len(current) + len(part) <= max_size:
            current += part
        else:
            if current:
                sentence_chunks.append(current.strip())
            current = part

    if current:
        sentence_chunks.append(current.strip())

    # If any chunk still exceeds max_size, split by fixed-size slices
    result = []
    for chunk in sentence_chunks:
        if len(chunk) > max_size:
            result.extend(_split_by_fixed_size(chunk, max_size))
        else:
            result.append(chunk)

    return result


def _split_by_fixed_size(text: str, max_size: int) -> List[str]:
    """Split text into fixed-size chunks (character-level fallback).

    Args:
        text: Text to split.
        max_size: Maximum chunk size in characters.

    Returns:
        List of chunk strings.
    """
    result = []
    for i in range(0, len(text), max_size):
        result.append(text[i : i + max_size])
    return result


def chunk_document(
    markdown: str,
    doc_id: str,
    min_chunk_size: int = DEFAULT_MIN_CHUNK_SIZE,
    max_chunk_size: int = DEFAULT_MAX_CHUNK_SIZE,
) -> List[dict]:
    """Chunk a Markdown document into semantically-meaningful pieces.

    The hybrid strategy:
    1. Splits the document at heading boundaries (H1-H6)
    2. Within each section, detects and separates GFM tables
    3. Enforces min/max character size constraints on each chunk
    4. Stores chunks in MinIO with a manifest JSON

    Args:
        markdown: The full Markdown document text.
        doc_id: Unique document identifier (sanitized against path traversal).
        min_chunk_size: Minimum chunk size in characters (default: 100).
        max_chunk_size: Maximum chunk size in characters (default: 1000).

    Returns:
        List of chunk dicts, each containing:
            - doc_id: str
            - chunk_index: int
            - heading_path: str (e.g., "# Chapter One" or "")
            - char_count: int
            - table_ref: str or None
            - text: str

    Raises:
        ValueError: If doc_id is invalid.
    """
    _sanitize_doc_id(doc_id)

    # Split by headings
    sections = _split_by_headings(markdown)

    all_chunks = []
    chunk_index = 0

    for section in sections:
        heading = section["heading"]
        body = section["body"]

        # Build heading path
        heading_path = heading if heading else ""

        # Extract tables from body
        regular_text, table_entries = _extract_table_and_text(body)

        # Process regular text into size-constrained chunks
        if regular_text.strip():
            text_chunks = _split_text_into_chunks(regular_text, min_chunk_size, max_chunk_size)
            for text_chunk in text_chunks:
                all_chunks.append({
                    "doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "heading_path": heading_path,
                    "char_count": len(text_chunk),
                    "table_ref": None,
                    "text": text_chunk,
                })
                chunk_index += 1

        # Process table chunks
        for table_entry in table_entries:
            all_chunks.append({
                "doc_id": doc_id,
                "chunk_index": chunk_index,
                "heading_path": heading_path,
                "char_count": len(table_entry["table_text"]),
                "table_ref": table_entry["table_ref"],
                "text": table_entry["table_text"],
            })
            chunk_index += 1

    # If we got no chunks (empty document with no headings), return empty
    if not all_chunks:
        return []

    # Merge adjacent small chunks to meet min_chunk_size
    all_chunks = _merge_small_chunks(all_chunks, min_chunk_size)

    # Renumber indices after merging
    for i, chunk in enumerate(all_chunks):
        chunk["chunk_index"] = i

    # Store in MinIO
    _store_chunks_in_minio(all_chunks, doc_id)

    logger.info(
        "Document chunked: doc_id=%s chunks=%d min_size=%d max_size=%d",
        doc_id,
        len(all_chunks),
        min_chunk_size,
        max_chunk_size,
    )

    return all_chunks


def _merge_small_chunks(chunks: List[dict], min_size: int) -> List[dict]:
    """Merge adjacent chunks that fall below min_size.

    Small chunks are merged with their preceding sibling. If the first
    chunk is small, it is merged with the second chunk.

    Args:
        chunks: List of chunk dicts.
        min_size: Minimum acceptable char_count.

    Returns:
        Merged list of chunk dicts.
    """
    if len(chunks) <= 1:
        return chunks

    merged = []
    for chunk in chunks:
        if chunk["char_count"] < min_size and merged:
            # Merge with previous chunk
            prev = merged[-1]
            prev["text"] = f"{prev['text']}\n\n{chunk['text']}"
            prev["char_count"] = len(prev["text"])
            # Prefer non-None table_ref
            if prev["table_ref"] is None and chunk["table_ref"] is not None:
                prev["table_ref"] = chunk["table_ref"]
        else:
            merged.append(chunk)

    return merged


def _store_chunks_in_minio(chunks: List[dict], doc_id: str) -> None:
    """Store chunk .md files and manifest in MinIO.

    Args:
        chunks: List of chunk dicts to store.
        doc_id: Document identifier for key construction.
    """
    minio = get_minio_storage()
    bucket = minio.markdown_conversions_bucket

    # Upload each chunk
    for chunk in chunks:
        key = f"chunks/{doc_id}/{doc_id}_chunk_{chunk['chunk_index']}.md"
        minio.upload_data(
            bucket=bucket,
            key=key,
            data=chunk["text"].encode("utf-8"),
            content_type="text/markdown",
        )

    # Build and upload manifest
    manifest = {
        "doc_id": doc_id,
        "chunks": [
            {
                "chunk_index": c["chunk_index"],
                "heading_path": c["heading_path"],
                "char_count": c["char_count"],
                "table_ref": c["table_ref"],
                "doc_id": c["doc_id"],
                "key": f"chunks/{doc_id}/{doc_id}_chunk_{c['chunk_index']}.md",
            }
            for c in chunks
        ],
    }

    manifest_key = f"chunks/{doc_id}/manifest.json"
    minio.upload_data(
        bucket=bucket,
        key=manifest_key,
        data=json.dumps(manifest, indent=2).encode("utf-8"),
        content_type="application/json",
    )
