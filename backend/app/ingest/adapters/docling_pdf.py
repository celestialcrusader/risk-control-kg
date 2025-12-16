from datetime import datetime
import uuid
from typing import List, Dict

# Conditional imports to avoid ImportErrors before install completes
try:
    from docling.document_converter import DocumentConverter
    from langchain_text_splitters import MarkdownHeaderTextSplitter
except ImportError:
    DocumentConverter = None
    MarkdownHeaderTextSplitter = None

from app.ingest.adapters.base import BaseAdapter
from app.core.oscal import Catalog, Group, Control, Metadata, Property

class DoclingPDFAdapter(BaseAdapter):
    def to_oscal(self, file_path: str) -> Catalog:
        if not DocumentConverter:
            raise ImportError("Docling not installed. Please install 'docling' and 'langchain-text-splitters'.")

        # 1. Convert PDF to Markdown using Docling
        converter = DocumentConverter()
        result = converter.convert(file_path)
        markdown_text = result.document.export_to_markdown()

        # 2. Split Markdown by Headers using LangChain
        # We assume structure: # Title -> ## Group -> ### Control/Section
        headers_to_split_on = [
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]
        
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        splits = splitter.split_text(markdown_text)
        
        # 3. Convert Splits to OSCAL
        # This is a loose mapping. We'll treat every split as a "Control" (Requirement)
        # and try to group them if possible, or just flat list them.
        
        controls = []
        for i, split in enumerate(splits):
            metadata = split.metadata
            content = split.page_content
            
            # Construct a title from headers
            title_parts = [metadata.get(h) for _, h in headers_to_split_on if metadata.get(h)]
            title = " - ".join(title_parts) if title_parts else f"Section {i+1}"
            
            # Use content as description
            c = Control(
                id=f"doc-{uuid.uuid4().hex[:8]}", # Generate ID because Unstructured doesn't have one
                title=title,
                props=[
                    Property(name="description", value=content),
                    Property(name="source_headers", value=str(metadata))
                ]
            )
            controls.append(c)
            
        # 4. Wrap in Catalog
        metadata = Metadata(
            title=f"Imported PDF: {file_path.split('/')[-1]}",
            **{"last-modified": datetime.now().isoformat()},
            version="1.0",
            **{"oscal-version": "1.0.0"}
        )
        
        return Catalog(
            uuid=str(uuid.uuid4()),
            metadata=metadata,
            groups=[],
            controls=controls # Flat list for now
        )
