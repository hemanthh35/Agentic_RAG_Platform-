import re
import uuid
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from app.indexing import config

logger = logging.getLogger(__name__)


class Chunk(BaseModel):
    """Standardized vector document chunk object representation."""
    chunk_id: str
    document_id: str
    chunk_index: int
    text_content: str
    character_count: int
    word_count: int
    metadata: Dict[str, Any]


class HierarchicalChunker:
    """Intelligent hierarchical chunking engine preserving document structure context."""

    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        chunk_overlap: int = config.CHUNK_OVERLAP,
        min_length: int = config.MIN_CHUNK_LENGTH
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_length = min_length

    def chunk_document(self, text: str, document_id: uuid.UUID, filename: str) -> List[Chunk]:
        """Hierarchical chunking coordinating section, paragraph, and sentence parsing."""
        if not text:
            return []

        # Step 1: Detect sections (by headers like #, ## or underline patterns)
        # We split by header matches but keep header titles linked to text
        section_splits = self._split_by_sections(text)
        
        chunks: List[Chunk] = []
        chunk_index = 0

        for section_title, section_text in section_splits:
            # Step 2: Split section into paragraphs
            paragraphs = [p.strip() for p in section_text.split("\n\n") if p.strip()]
            
            current_buffer = ""
            for paragraph in paragraphs:
                # If paragraph itself fits in current buffer without exceeding chunk_size
                if len(current_buffer) + len(paragraph) + 2 <= self.chunk_size:
                    current_buffer += ("\n\n" if current_buffer else "") + paragraph
                else:
                    # Flush current buffer if it meets minimum length
                    if len(current_buffer) >= self.min_length:
                        chunks.append(self._create_chunk(current_buffer, document_id, chunk_index, section_title, filename))
                        chunk_index += 1
                        
                        # Apply overlap from end of current buffer
                        current_buffer = current_buffer[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                    
                    # If paragraph alone exceeds chunk size, split by sentences
                    if len(paragraph) > self.chunk_size:
                        sentences = self._split_by_sentences(paragraph)
                        for sentence in sentences:
                            if len(current_buffer) + len(sentence) + 1 <= self.chunk_size:
                                current_buffer += (" " if current_buffer else "") + sentence
                            else:
                                if len(current_buffer) >= self.min_length:
                                    chunks.append(self._create_chunk(current_buffer, document_id, chunk_index, section_title, filename))
                                    chunk_index += 1
                                    current_buffer = current_buffer[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                                
                                # If sentence alone exceeds chunk size, hard split it
                                if len(sentence) > self.chunk_size:
                                    for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
                                        sub_chunk = sentence[i:i + self.chunk_size]
                                        if len(sub_chunk) >= self.min_length:
                                            chunks.append(self._create_chunk(sub_chunk, document_id, chunk_index, section_title, filename))
                                            chunk_index += 1
                                    current_buffer = ""
                                else:
                                    current_buffer = sentence
                    else:
                        current_buffer = paragraph

            # Flush remaining buffer for this section
            if current_buffer and len(current_buffer) >= self.min_length:
                chunks.append(self._create_chunk(current_buffer, document_id, chunk_index, section_title, filename))
                chunk_index += 1

        logger.info(f"HierarchicalChunker completed chunking for {filename}: created {len(chunks)} chunks.")
        return chunks

    def _split_by_sections(self, text: str) -> List[tuple]:
        """Split text by Markdown headings, retaining heading context."""
        # Detect headings like: # Section Title
        header_pattern = re.compile(r'^(#+\s+.+)$', re.MULTILINE)
        splits = header_pattern.split(text)
        
        if len(splits) <= 1:
            return [("Root", text)]

        sections = []
        # First split element is text before first heading (e.g. intro)
        if splits[0].strip():
            sections.append(("Introduction", splits[0]))

        # Heading and content pair up sequentially
        for i in range(1, len(splits), 2):
            heading = splits[i].strip("# ").strip()
            content = splits[i+1] if i+1 < len(splits) else ""
            sections.append((heading, content))

        return sections

    def _split_by_sentences(self, text: str) -> List[str]:
        """Splits paragraph by basic sentence terminators."""
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_chunk(self, content: str, document_id: uuid.UUID, index: int, section: str, filename: str) -> Chunk:
        """Create a Chunk schema with populated metadata tags."""
        chunk_id = str(uuid.uuid4())
        return Chunk(
            chunk_id=chunk_id,
            document_id=str(document_id),
            chunk_index=index,
            text_content=content,
            character_count=len(content),
            word_count=len(content.split()),
            metadata={
                "document_id": str(document_id),
                "chunk_id": chunk_id,
                "chunk_index": index,
                "section_title": section,
                "source_filename": filename,
                "page_number": 1 # Default placeholder for plaintext/md, PDF overrides it in later indexing services
            }
        )
