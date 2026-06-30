import time
from app.retrieval.manager.circuit_breaker import ProviderCircuitBreaker


def test_circuit_breaker_transitions():
    """Verify that ProviderCircuitBreaker transitions correctly: Healthy -> Degraded -> Open -> Half-Open -> Healthy."""
    breaker = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout_seconds=0.2)
    
    # 1. Initial State
    assert breaker.is_allowed("test-db") is True
    
    # 2. Record First Failure -> Degraded
    breaker.record_failure("test-db")
    assert breaker.is_allowed("test-db") is True
    
    # 3. Record Consecutive Failures -> Open Circuit
    breaker.record_failure("test-db")
    breaker.record_failure("test-db")
    assert breaker.is_allowed("test-db") is False  # Request blocked
    
    # 4. Wait for Cooldown -> HALF_OPEN (Probe allowed)
    time.sleep(0.25)
    assert breaker.is_allowed("test-db") is True
    
    # 5. Success -> Recovers to HEALTHY
    breaker.record_success("test-db")
    assert breaker.is_allowed("test-db") is True
