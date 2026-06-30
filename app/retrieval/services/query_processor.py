import re
from app.retrieval.interfaces.query_processor_interface import QueryPreprocessor


class QueryProcessor(QueryPreprocessor):
    """Active query processor implementing sanitization and whitespace compression."""

    def preprocess(self, query: str) -> str:
        if not query:
            return ""
            
        # 1. Clean whitespace
        normalized = query.strip()
        
        # 2. Lowercase standard characters
        normalized = normalized.lower()
        
        # 3. Clean internal multi-whitespaces
        normalized = re.sub(r"\s+", " ", normalized)
        
        # 4. Clean control characters
        normalized = re.sub(r"[\x00-\x1F\x7F]", "", normalized)
        
        return normalized
