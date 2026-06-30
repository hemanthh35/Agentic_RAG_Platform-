import logging
from typing import Dict, List, Optional
from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Thread-safe catalog repository registering and resolving retrieval providers."""

    def __init__(self):
        self._providers: Dict[str, BaseRetrievalProvider] = {}

    def register_provider(self, provider: BaseRetrievalProvider) -> None:
        """Register a search provider instance."""
        key = provider.name.lower()
        self._providers[key] = provider
        logger.info(f"Successfully registered search provider: '{key}'")

    def get_provider(self, name: str) -> Optional[BaseRetrievalProvider]:
        """Resolve search provider instance by key name."""
        return self._providers.get(name.lower())

    def list_providers(self) -> List[str]:
        """List registered provider names."""
        return list(self._providers.keys())


# Shared registry instance
provider_registry = ProviderRegistry()
