from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class RetrievalSettings(BaseSettings):
    """Configuration definitions for unified search operations, timeouts and thresholds."""
    
    DEFAULT_RETRIEVAL_LIMIT: int = 10
    DEFAULT_SIMILARITY_THRESHOLD: float = 0.0
    DEFAULT_RETRIEVAL_STRATEGY: str = "semantic"
    
    # Timout boundaries (seconds)
    PROVIDER_TIMEOUT_SECONDS: float = 5.0
    
    # Provider Feature Flags
    ENABLE_SEMANTIC_SEARCH: bool = True
    ENABLE_KEYWORD_SEARCH: bool = True
    ENABLE_HYBRID_SEARCH: bool = True
    
    # Cache duration (seconds)
    CACHE_EXPIRATION_SECONDS: int = 300

    model_config = ConfigDict(env_prefix="RAG_RETRIEVAL_")


retrieval_settings = RetrievalSettings()
