from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.providers.registry import provider_registry


class ProviderFactory:
    """Factory resolver returning active provider instances from the registry."""

    @staticmethod
    def get_provider(name: str) -> BaseRetrievalProvider:
        """Resolve the requested provider instance from registry. Raises ValueError if missing."""
        provider = provider_registry.get_provider(name)
        if not provider:
            raise ValueError(f"Search provider '{name}' is not registered inside factory catalog.")
        return provider
