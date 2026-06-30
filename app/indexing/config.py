import os

# Semantic indexing configurations
CHUNK_SIZE = int(os.getenv("INDEXING_CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("INDEXING_CHUNK_OVERLAP", 64))
MIN_CHUNK_LENGTH = int(os.getenv("INDEXING_MIN_CHUNK_LENGTH", 20))
MAX_CHUNK_LENGTH = int(os.getenv("INDEXING_MAX_CHUNK_LENGTH", 1024))

# Embedding model configurations
EMBEDDING_MODEL_NAME = os.getenv("INDEXING_EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIMENSION = int(os.getenv("INDEXING_EMBEDDING_DIMENSION", 1024))
BATCH_SIZE = int(os.getenv("INDEXING_BATCH_SIZE", 32))
CONCURRENCY_LIMIT = int(os.getenv("INDEXING_CONCURRENCY_LIMIT", 5))

# Vector database collection name
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
