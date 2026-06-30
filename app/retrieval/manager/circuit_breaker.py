import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ProviderCircuitBreaker:
    """Manages search provider connection health states to prevent persistent query blocks."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 10.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        
        # State mapping: provider_name -> state ("healthy", "degraded", "open", "half_open")
        self._states: Dict[str, str] = {}
        self._failures: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}

    def is_allowed(self, provider_name: str) -> bool:
        """Verify if querying the provider is permitted under current circuit states."""
        name_key = provider_name.lower()
        state = self._states.get(name_key, "healthy")
        
        if state == "open":
            last_fail = self._last_failure_time.get(name_key, 0.0)
            # If cooldown period expired, transition to half_open to probe
            if time.time() - last_fail > self.recovery_timeout_seconds:
                self._states[name_key] = "half_open"
                logger.info(f"Circuit Breaker for provider '{provider_name}' transitioned to HALF_OPEN. Probing connection.")
                return True
            return False
            
        return True

    def record_success(self, provider_name: str) -> None:
        """Reset failures counter and restore provider circuit state to healthy."""
        name_key = provider_name.lower()
        self._failures[name_key] = 0
        state = self._states.get(name_key, "healthy")
        
        if state in ("open", "half_open", "degraded"):
            self._states[name_key] = "healthy"
            logger.info(f"Circuit Breaker for provider '{provider_name}' recovered to HEALTHY state.")

    def record_failure(self, provider_name: str) -> None:
        """Increment failure counter and transition states to open if threshold exceeded."""
        name_key = provider_name.lower()
        self._failures[name_key] = self._failures.get(name_key, 0) + 1
        self._last_failure_time[name_key] = time.time()
        
        failures_count = self._failures[name_key]
        if failures_count >= self.failure_threshold:
            self._states[name_key] = "open"
            logger.warning(
                f"Circuit Breaker for provider '{provider_name}' is OPEN due to {failures_count} consecutive failures. "
                f"Cooldown block for {self.recovery_timeout_seconds}s initiated."
            )
        else:
            self._states[name_key] = "degraded"
            logger.info(f"Circuit Breaker for provider '{provider_name}' is DEGRADED ({failures_count}/{self.failure_threshold} failures).")

    def get_state(self, provider_name: str) -> str:
        """Retrieve state code for a provider."""
        return self._states.get(provider_name.lower(), "healthy")
