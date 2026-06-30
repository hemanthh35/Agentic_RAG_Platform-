import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from app.indexing import config

logger = logging.getLogger(__name__)


class BaseEmbeddingProvider(ABC):
    """Abstract interface for replaceable vector embedding providers."""

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate high-dimensional vector embeddings for a list of string chunks."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """The output vector dimensions of the embedding model."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name/Identifier of the embedding model."""
        pass


class SimulatedEmbeddingProvider(BaseEmbeddingProvider):
    """Offline-resilient simulated mock embedding provider generating pseudo-random deterministic vectors."""

    def __init__(self, dimension: int = config.EMBEDDING_DIMENSION, model_name: str = config.EMBEDDING_MODEL_NAME):
        self._dimension = dimension
        self._model_name = model_name

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate deterministic mock floats using hashes of the text content."""
        embeddings = []
        for text in texts:
            # Generate seed from md5 hash of text
            hasher = hashlib.md5(text.encode("utf-8"))
            seed = int(hasher.hexdigest(), 16) % (2**32 - 1)
            
            # Seed generator to yield deterministic vectors for the same text
            rng = np.random.default_rng(seed)
            vector = rng.standard_normal(self._dimension)
            
            # Normalize vector to unit length (L2 norm)
            norm = np.linalg.norm(vector)
            normalized_vector = (vector / norm).tolist() if norm > 0 else vector.tolist()
            embeddings.append(normalized_vector)
            
        return embeddings

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model_name + " (Simulated)"


class BGEM3Provider(BaseEmbeddingProvider):
    """Production provider using sentence-transformers to execute BGE-M3 embedding extraction."""

    def __init__(self, model_name: str = config.EMBEDDING_MODEL_NAME, dimension: int = config.EMBEDDING_DIMENSION):
        self._model_name = model_name
        self._dimension = dimension
        self._model = None

    def _load_model(self):
        """Lazy loads SentenceTransformer to prevent startup lag or unnecessary memory usage."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model '{self._model_name}'...")
                self._model = SentenceTransformer(self._model_name)
                logger.info("SentenceTransformer model loaded successfully.")
            except Exception as e:
                logger.warning(
                    f"Could not load SentenceTransformer '{self._model_name}': {e}. "
                    "Falling back to SimulatedEmbeddingProvider."
                )
                raise ImportError("Model loading failed")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Extract vectors using sentence-transformers, falling back to simulated generation on failure."""
        try:
            self._load_model()
            # Perform batch inference
            embeddings = self._model.encode(
                texts,
                batch_size=config.BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            return [emb.tolist() for emb in embeddings]
        except Exception:
            # Resilient fallback to prevent server/queue crashes in constrained/offline environments
            logger.info("Executing offline-resilient SimulatedEmbeddingProvider fallback.")
            simulated = SimulatedEmbeddingProvider(dimension=self._dimension, model_name=self._model_name)
            return simulated.embed_texts(texts)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model_name
