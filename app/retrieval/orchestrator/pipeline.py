import asyncio
import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.config.settings import retrieval_settings
from app.retrieval.manager.circuit_breaker import ProviderCircuitBreaker
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class RetrievalPipeline:
    """Executes query search retrieval across multiple providers in parallel with timeout boundaries."""

    def __init__(
        self,
        providers: List[BaseRetrievalProvider],
        circuit_breaker: Optional[ProviderCircuitBreaker] = None
    ):
        self.providers = providers
        self.circuit_breaker = circuit_breaker

    async def execute_parallel(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        if not self.providers:
            return []

        correlation_id = context.tracing.correlation_id
        timeout_sec = context.configuration.timeout_sec
        
        async def safe_retrieve(provider: BaseRetrievalProvider) -> List[RetrievalResultItem]:
            # Circuit breaker check before executing search
            if self.circuit_breaker and not self.circuit_breaker.is_allowed(provider.name):
                logger.warning(
                    f"[CorrelationID: {correlation_id}] Bypassing search provider '{provider.name}' - "
                    f"Circuit Breaker is OPEN."
                )
                return []

            try:
                results = await asyncio.wait_for(
                    provider.retrieve(context),
                    timeout=timeout_sec
                )
                
                # Record success on circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_success(provider.name)
                    
                return results
            except asyncio.TimeoutError:
                logger.error(
                    f"[CorrelationID: {correlation_id}] Search provider '{provider.name}' timed out after {timeout_sec}s."
                )
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure(provider.name)
                return []
            except Exception as err:
                logger.error(
                    f"[CorrelationID: {correlation_id}] Search provider '{provider.name}' encountered unexpected failure: {err}"
                )
                if self.circuit_breaker:
                    self.circuit_breaker.record_failure(provider.name)
                return []

        # Run concurrent coroutines
        tasks = [safe_retrieve(p) for p in self.providers]
        results_list = await asyncio.gather(*tasks)

        combined = []
        for res in results_list:
            combined.extend(res)
            
        return combined

