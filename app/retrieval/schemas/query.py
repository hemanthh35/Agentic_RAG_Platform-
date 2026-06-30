from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class RetrievalRequest(BaseModel):
    """Schema for incoming knowledge retrieval query requests."""
    query: str = Field(..., description="The query string to search for")
    limit: int = Field(10, ge=1, le=100, description="Top-K limit of results to return")
    threshold: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Minimum relevance threshold score")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters (e.g., page_number, document_id, section)")
    strategy: str = Field("semantic", description="Retrieval strategy: semantic, keyword, or hybrid")


class RetrievalResultItem(BaseModel):
    """Schema representing an individual retrieved context chunk."""
    chunk_id: str = Field(..., description="Unique UUID representing the text chunk")
    document_id: str = Field(..., description="Unique UUID referencing the parent document")
    chunk_index: int = Field(..., description="Sequence position of the chunk in the document")
    text_content: str = Field(..., description="Raw text segment of the chunk")
    character_count: int = Field(..., description="Total characters in the text segment")
    word_count: int = Field(..., description="Total words in the text segment")
    page_number: int = Field(1, description="Page number where the chunk originates")
    section_title: str = Field("Root", description="Document section header containing the chunk")
    score: float = Field(..., description="Relevance ranking score (0.0 to 1.0)")
    original_filename: str = Field(..., description="Filename of the source document")


class RetrievalResponse(BaseModel):
    """Schema representing the unified response context payload."""
    query: str = Field(..., description="The processed search query")
    items: List[RetrievalResultItem] = Field(..., description="Ordered list of relevant context chunks")
    total_results: int = Field(..., description="Count of items retrieved after threshold filtering")
    execution_time_ms: float = Field(..., description="Latency duration of the search query execution")
    strategy_used: str = Field(..., description="Search strategy applied")
    providers_queried: List[str] = Field(..., description="Identified active source systems queried")
