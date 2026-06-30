from abc import ABC, abstractmethod


class QueryPreprocessor(ABC):
    """Abstract interface defining required behaviors for query preprocessing/normalization."""

    @abstractmethod
    def preprocess(self, query: str) -> str:
        """Sanitize, normalize, or expand search query string inputs."""
        pass
