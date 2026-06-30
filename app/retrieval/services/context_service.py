from typing import List
from app.retrieval.schemas.query import RetrievalResultItem


class ContextService:
    """Formats retrieved text segments into clean context blocks for downstream LLM consumers."""

    def format_context_block(self, items: List[RetrievalResultItem]) -> str:
        """Combine lists of retrieval results into a single formatted string context block."""
        if not items:
            return ""
        
        blocks = []
        for idx, item in enumerate(items):
            blocks.append(
                f"--- Context Chunk {idx + 1} (Source: {item.original_filename}, Section: {item.section_title}, Page: {item.page_number}) ---\n"
                f"{item.text_content.strip()}"
            )
        return "\n\n".join(blocks)
