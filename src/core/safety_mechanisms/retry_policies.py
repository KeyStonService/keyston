"""
Retry Policies for HLP Executor Core

Implements intelligent retry strategies with exponential backoff, jitter,
and risk-adaptive delays for robust error handling.

This module provides retry policies that adapt to system conditions and
risk levels to optimize recovery from transient failures.
"""

import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    FIBONACCI = "fibonacci"
    RISK_ADAPTIVE = "risk-adaptive"


class RetryOutcome(Enum):
    """Outcome of a retry operation."""
    SUCCESS = "success"
    RETRY = "retry"
    EXHAUSTED = "exhausted"
    ABORT = "abort"


@dataclass
class RetryConfig:
    """Configuration for retry policies."""
    max_attempts: int = 5
    base_delay_ms: int = 2000
    max_delay_ms: int = 30000
    jitter_enabled: bool = True
    jitter_min: float = 0.8
    jitter_max: float = 1.2
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_multiplier: float = 2.0
    risk_adaptive: bool = True
    timeout_ms: int | None = None


@dataclass
class RetryResult:
    """Result of a retry operation."""
    outcome: RetryOutcome
    attempts: int
    total_delay_ms: int
    last_error: str | None = None
    success: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class RetryPolicy:
    """
    Implements various retry policies with intelligent backoff strategies.
    
    Features:
    - Exponential backoff with configurable multiplier
    - Jitter to prevent thundering herd
    - Risk-adaptive delays based on system risk score
    - Multiple retry strategies (exponential, linear, fixed, Fibonacci)
    - Configurable maximum attempts and delays
    """
    
    def __init__(self, config: RetryConfig | None = None):
        """
        Initialize the RetryPolicy.
        
        Args:
            config: Retry configuration (uses defaults if None)
        """
        self.config = config or RetryConfig()
        logger.info(
            "RetryPolicy initialized: strategy=%s, max_attempts=%d, base_delay=%dms",
            self.config.strategy.value,
            self.config.max_attempts,
            self.config.base_delay_ms
        )
    
    def calculate_delay(self, attempt: int, risk_score: float = 0.0) -> int:
        """
        Calculate retry delay based on attempt number and risk score.
        
        Args:
            attempt: Current attempt number (0-based)
            risk_score: Risk score (0.0-1.0), higher means more risk
        
        Returns:
            Delay in milliseconds
        """
        if attempt < 0:
            return 0
        
        # Calculate base delay based on strategy
        if self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self._exponential_delay(attempt)
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self._linear_delay(attempt)
        elif self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay_ms
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self._fibonacci_delay(attempt)
        elif self.config.strategy == RetryStrategy.RISK_ADAPTIVE:
            delay = self._risk_adaptive_delay(attempt, risk_score)
        else:
            delay = self._exponential_delay(attempt)
        
        # Apply jitter if enabled
        if self.config.jitter_enabled:
            delay = self._apply_jitter(delay)
        
        # Apply risk factor if risk-adaptive is enabled
        if self.config.risk_adaptive and self.config.strategy != RetryStrategy.RISK_ADAPTIVE:
            delay = self._apply_risk_factor(delay, risk_score)
        
        # Cap at maximum delay
        delay = min(delay, self.config.max_delay_ms)
        
        return int(delay)
    
    def execute_with_retry(
        self,
        func: Callable[[], Any],
        risk_score: float = 0.0,
        context: dict[str, Any] | None = None
    ) -> RetryResult:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            risk_score: Risk score (0.0-1.0)
            context: Optional context dictionary
        
        Returns:
            RetryResult with execution details
        """
        attempts = 0
        total_delay_ms = 0
        last_error = None
        
        start_time = datetime.utcnow()
        
        while attempts < self.config.max_attempts:
            try:
                # Execute the function
                result = func()
                
                # Success
                return RetryResult(
                    outcome=RetryOutcome.SUCCESS,
                    attempts=attempts + 1,
                    total_delay_ms=total_delay_ms,
                    success=True,
                    metadata={
                        "result": result,
                        "elapsed_ms": self._elapsed_ms(start_time)
                    }
                )
            
            except Exception as e:
                last_error = str(e)
                attempts += 1
                
                logger.warning(
                    "Attempt %d/%d failed: %s",
                    attempts,
                    self.config.max_attempts,
                    last_error
                )
                
                # Check if we should retry
                if attempts >= self.config.max_attempts:
                    break
                
                # Check timeout if configured
                if self.config.timeout_ms:
                    elapsed = self._elapsed_ms(start_time)
                    if elapsed >= self.config.timeout_ms:
                        logger.warning("Retry timeout reached: %dms", elapsed)
                        return RetryResult(
                            outcome=RetryOutcome.ABORT,
                            attempts=attempts,
                            total_delay_ms=total_delay_ms,
                            last_error=last_error,
                            success=False,
                            metadata={"reason": "timeout", "elapsed_ms": elapsed}
                        )
                
                # Calculate delay and wait
                delay = self.calculate_delay(attempts - 1, risk_score)
                total_delay_ms += delay
                
                logger.debug(
                    "Waiting %dms before retry (attempt %d/%d, risk_score=%.2f)",
                    delay,
                    attempts,
                    self.config.max_attempts,
                    risk_score
                )
                
                time.sleep(delay / 1000.0)
        
        # All retries exhausted
        return RetryResult(
            outcome=RetryOutcome.EXHAUSTED,
            attempts=attempts,
            total_delay_ms=total_delay_ms,
            last_error=last_error,
            success=False,
            metadata={"elapsed_ms": self._elapsed_ms(start_time)}
        )
    
    def _exponential_delay(self, attempt: int) -> int:
        """Calculate exponential backoff delay."""
        return int(self.config.base_delay_ms * (self.config.backoff_multiplier ** attempt))
    
    def _linear_delay(self, attempt: int) -> int:
        """Calculate linear backoff delay."""
        return int(self.config.base_delay_ms * (attempt + 1))
    
    def _fibonacci_delay(self, attempt: int) -> int:
        """Calculate Fibonacci backoff delay."""
        fib = self._fibonacci(attempt + 1)
        return int(self.config.base_delay_ms * fib)
    
    def _risk_adaptive_delay(self, attempt: int, risk_score: float) -> int:
        """Calculate risk-adaptive delay."""
        base_delay = self._exponential_delay(attempt)
        risk_factor = 1.0 + risk_score  # Higher risk = longer delay
        return int(base_delay * risk_factor)
    
    def _apply_jitter(self, delay: int) -> int:
        """Apply jitter to delay to prevent thundering herd."""
        jitter = random.uniform(self.config.jitter_min, self.config.jitter_max)
        return int(delay * jitter)
    
    def _apply_risk_factor(self, delay: int, risk_score: float) -> int:
        """Apply risk factor to delay."""
        risk_factor = 1.0 + risk_score
        return int(delay * risk_factor)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def _elapsed_ms(self, start_time: datetime) -> int:
        """Calculate elapsed time in milliseconds."""
        elapsed = datetime.utcnow() - start_time
        return int(elapsed.total_seconds() * 1000)


def hlp_executor_retry_policy(attempt: int, risk_score: float) -> int:
    """
    HLP Executor specific retry policy with exponential backoff + jitter + risk-adaptive delays.
    
    This is a convenience function for the HLP Executor Core Plugin.
    
    Args:
        attempt: Current retry attempt (0-based)
        risk_score: Risk score (0.0-1.0), higher means more risk
    
    Returns:
        Delay in milliseconds
    
    Examples:
        >>> hlp_executor_retry_policy(0, 0.0)  # First retry, low risk
        # Returns ~2000ms with jitter
        
        >>> hlp_executor_retry_policy(2, 0.8)  # Third retry, high risk
        # Returns ~14400ms (8000 * 1.8) with jitter
    """
    config = RetryConfig(
        max_attempts=5,
        base_delay_ms=2000,
        max_delay_ms=30000,
        jitter_enabled=True,
        jitter_min=0.8,
        jitter_max=1.2,
        strategy=RetryStrategy.RISK_ADAPTIVE,
        backoff_multiplier=2.0,
        risk_adaptive=True
    )
    
    policy = RetryPolicy(config)
    return policy.calculate_delay(attempt, risk_score)


def create_retry_policy(
    strategy: str = "exponential",
    max_attempts: int = 5,
    base_delay_ms: int = 2000,
    max_delay_ms: int = 30000,
    **kwargs
) -> RetryPolicy:
    """
    Factory function to create a retry policy.
    
    Args:
        strategy: Retry strategy ('exponential', 'linear', 'fixed', 'fibonacci', 'risk-adaptive')
        max_attempts: Maximum number of retry attempts
        base_delay_ms: Base delay in milliseconds
        max_delay_ms: Maximum delay in milliseconds
        **kwargs: Additional configuration options
    
    Returns:
        Configured RetryPolicy instance
    """
    try:
        strategy_enum = RetryStrategy(strategy)
    except ValueError:
        logger.warning("Invalid strategy '%s', using 'exponential'", strategy)
        strategy_enum = RetryStrategy.EXPONENTIAL
    
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay_ms=base_delay_ms,
        max_delay_ms=max_delay_ms,
        strategy=strategy_enum,
        **kwargs
    )
    
    return RetryPolicy(config)
