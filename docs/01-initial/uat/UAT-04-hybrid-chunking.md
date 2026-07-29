# UAT-04: Hybrid Chunking Strategy

**Covers**: INGEST-3
**Type**: Service Layer Test
**Effort**: ~10 minutes

## Objective

Verify that the hybrid chunking service splits Markdown content into chunks using both heading-based sections and semantic (embedding-based) splits.

## Prerequisites

- UAT-03 passes (you have a generated Markdown file)
- Qdrant is running (for potential embedding-based splits)

## Steps

### Step 1: Prepare Markdown Input

```bash
# If UAT-03 didn't generate one, create a sample
cat > tests/test_data/sample_chunks.md << 'EOF'
# Section 1: Identity and Access Management

## 1.1 General Controls
The organization must establish access control procedures.
All users must be authenticated before access is granted.
Role-based access control must be enforced.

## 1.2 Authentication
Multi-factor authentication must be required for remote access.
Session timeout must be configured to 15 minutes of inactivity.

# Section 2: System Acquisition and Development

## 2.1 Development Lifecycle
Software development must follow a documented SDLC.
Security requirements must be defined during the design phase.

## 2.2 Testing
All system changes must undergo formal testing.
Penetration testing must be performed annually.
EOF
```

### Step 2: Run Hybrid Chunking

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.hybrid_chunking import hybrid_chunk

try:
    with open("tests/test_data/sample_chunks.md", "r") as f:
        markdown_content = f.read()

    chunks = hybrid_chunk(markdown_content)

    print(f"Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"  Method: {chunk.get('method', 'unknown')}")
        print(f"  Section: {chunk.get('section', 'N/A')}")
        print(f"  Text length: {len(chunk.get('text', ''))} chars")
        print(f"  Text preview: {chunk.get('text', '')[:100]}...")
        print(f"  Metadata: {chunk.get('metadata', {})}")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
```

### Step 3: Verify Chunk Output Structure

Each chunk must have:
- `id`: unique identifier
- `text`: the chunk text content
- `section`: parent section reference (e.g., "Section 1: Identity and Access Management")
- `method`: either "heading" or "semantic"
- `metadata`: JSONB with document_id, page, embedding_ref

### Step 4: Verify Chunk Statistics

```bash
python3 << 'PYEOF'
import sys
sys.path.insert(0, "backend")

from app.services.hybrid_chunking import hybrid_chunk

with open("tests/test_data/sample_chunks.md", "r") as f:
    markdown_content = f.read()

chunks = hybrid_chunk(markdown_content)

heading_chunks = [c for c in chunks if c.get("method") == "heading"]
semantic_chunks = [c for c in chunks if c.get("method") == "semantic"]

print(f"Total chunks: {len(chunks)}")
print(f"  Heading-based: {len(heading_chunks)}")
print(f"  Semantic-based: {len(semantic_chunks)}")

assert len(chunks) >= 2, "Should produce at least 2 chunks"
assert len(heading_chunks) >= 1, "Should have at least 1 heading-based chunk"
assert all("text" in c and "section" in c for c in chunks), "All chunks must have text and section fields"

print("\nAll assertions passed.")
PYEOF
```

## Expected Results Summary

| # | Step | Check | Expected |
|---|------|-------|----------|
| 1 | Input file | sample_chunks.md | Valid Markdown with headings and paragraphs |
| 2 | Chunking service | `hybrid_chunk()` returns list | List of chunk dicts with required fields |
| 3 | Chunk methods | Both chunk types present | At least 1 "heading" chunk, optionally "semantic" chunks |
| 4 | Chunk structure | All chunks have required fields | `id`, `text`, `section`, `method`, `metadata` |
| 5 | Assertions | Chunk count and structure | At least 2 chunks, all have required fields |

## Verification

- [ ] Hybrid chunking returns a list of chunk dictionaries
- [ ] Each chunk has all required fields (id, text, section, method, metadata)
- [ ] At least one chunk uses the "heading" method
- [ ] Section references are correctly extracted from Markdown headings
- [ ] Assertions in Step 4 pass without errors

## Pass/Fail Criteria

- **PASS**: Steps 2-5 all succeed — chunks are produced with correct structure and both heading-based and semantic splits
- **FAIL**: No chunks returned, missing required fields, or assertions fail

## Notes

- If no embedding service (Qdrant) is available, only heading-based chunks will be produced — this is acceptable
- The key requirement is that heading-based splitting works correctly with Markdown document structure
