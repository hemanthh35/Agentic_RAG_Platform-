import asyncio
import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.config.settings import retrieval_settings

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """Executes query search retrieval across multiple providers in parallel with timeout boundaries."""

    def __init__(self, providers: List[BaseRetrievalProvider]):
        self.providers = providers

    async def execute_parallel(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> List[RetrievalResultItem]:
        if not self.providers:
            return []

        timeout_sec = timeout if timeout is not None else retrieval_settings.PROVIDER_TIMEOUT_SECONDS
        
        async def safe_retrieve(provider: BaseRetrievalProvider) -> List[RetrievalResultItem]:
            try:
                # Wrap execution in wait_for block
                return await asyncio.wait_for(
                    provider.retrieve(query, limit, filters),
                    timeout=timeout_sec
                )
            except asyncio.TimeoutError:
                logger.error(f"Search provider '{provider.name}' timed out after {timeout_sec}s.")
                return []
            except Exception as err:
                logger.error(f"Search provider '{provider.name}' encountered unexpected failure: {err}")
                return []

        # Run concurrent coroutines
        tasks = [safe_retrieve(p) for p in self.providers]
        results_list = await asyncio.gather(*tasks)

        combined = []
        for res in results_list:
            combined.extend(res)
            
        return combined
