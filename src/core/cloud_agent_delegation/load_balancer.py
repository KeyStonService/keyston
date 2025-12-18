"""
Load Balancer - Load balancing across cloud providers

This module provides load balancing capabilities for distributing
tasks across multiple cloud providers.
"""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class BalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = 'round-robin'
    WEIGHTED_ROUND_ROBIN = 'weighted-round-robin'
    LEAST_CONNECTIONS = 'least-connections'
    RANDOM = 'random'
    WEIGHTED_RANDOM = 'weighted-random'


class HealthStatus(Enum):
    """Health status of a provider"""
    HEALTHY = 'healthy'
    UNHEALTHY = 'unhealthy'
    DEGRADED = 'degraded'
    UNKNOWN = 'unknown'


@dataclass
class ProviderHealth:
    """Health information for a provider"""
    provider: str
    status: HealthStatus
    last_check: datetime
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    latency_ms: float = 0.0
    active_connections: int = 0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'provider': self.provider,
            'status': self.status.value,
            'lastCheck': self.last_check.isoformat(),
            'consecutiveFailures': self.consecutive_failures,
            'consecutiveSuccesses': self.consecutive_successes,
            'latencyMs': self.latency_ms,
            'activeConnections': self.active_connections,
            'errorRate': self.error_rate,
            'metadata': self.metadata
        }
        
    @property
    def is_healthy(self) -> bool:
        """Check if provider is healthy"""
        return self.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)


@dataclass
class BalancerConfig:
    """Configuration for the load balancer"""
    strategy: BalancingStrategy = BalancingStrategy.WEIGHTED_ROUND_ROBIN
    weights: Dict[str, int] = field(default_factory=dict)
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 10  # seconds
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    failover_enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 1  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'strategy': self.strategy.value,
            'weights': self.weights,
            'healthCheckInterval': self.health_check_interval,
            'healthCheckTimeout': self.health_check_timeout,
            'unhealthyThreshold': self.unhealthy_threshold,
            'healthyThreshold': self.healthy_threshold,
            'failoverEnabled': self.failover_enabled,
            'maxRetries': self.max_retries,
            'retryDelay': self.retry_delay
        }


class LoadBalancer:
    """
    Load balancer for cloud providers
    
    Distributes tasks across multiple providers using
    configurable strategies and health monitoring.
    """
    
    def __init__(self, config: Optional[BalancerConfig] = None):
        """
        Initialize the load balancer
        
        Args:
            config: Balancer configuration
        """
        self.config = config or BalancerConfig()
        self._providers: Dict[str, Any] = {}
        self._health: Dict[str, ProviderHealth] = {}
        self._round_robin_index = 0
        self._weighted_index = 0
        self._weighted_list: List[str] = []
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False
        self._connection_counts: Dict[str, int] = {}
        
    async def start(self) -> None:
        """Start the load balancer"""
        if self._is_running:
            return
            
        self._is_running = True
        self._rebuild_weighted_list()
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info('LoadBalancer started')
        
    async def stop(self) -> None:
        """Stop the load balancer"""
        self._is_running = False
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
                
        logger.info('LoadBalancer stopped')
        
    def register_provider(
        self,
        name: str,
        provider: Any,
        weight: int = 1
    ) -> None:
        """
        Register a provider with the load balancer
        
        Args:
            name: Provider name
            provider: Provider instance
            weight: Load balancing weight
        """
        self._providers[name] = provider
        self.config.weights[name] = weight
        self._connection_counts[name] = 0
        
        # Initialize health status
        self._health[name] = ProviderHealth(
            provider=name,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.now(timezone.utc)
        )
        
        self._rebuild_weighted_list()
        logger.info(f'Registered provider: {name} (weight: {weight})')
        
    def unregister_provider(self, name: str) -> bool:
        """Unregister a provider"""
        if name not in self._providers:
            return False
            
        del self._providers[name]
        self.config.weights.pop(name, None)
        self._health.pop(name, None)
        self._connection_counts.pop(name, None)
        
        self._rebuild_weighted_list()
        logger.info(f'Unregistered provider: {name}')
        return True
        
    async def select_provider(self) -> Optional[str]:
        """
        Select a provider based on the balancing strategy
        
        Returns:
            Selected provider name or None if none available
        """
        healthy_providers = self._get_healthy_providers()
        
        if not healthy_providers:
            logger.warning('No healthy providers available')
            return None
            
        strategy = self.config.strategy
        
        if strategy == BalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(healthy_providers)
            
        elif strategy == BalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._select_weighted_round_robin(healthy_providers)
            
        elif strategy == BalancingStrategy.LEAST_CONNECTIONS:
            return self._select_least_connections(healthy_providers)
            
        elif strategy == BalancingStrategy.RANDOM:
            return random.choice(healthy_providers)
            
        elif strategy == BalancingStrategy.WEIGHTED_RANDOM:
            return self._select_weighted_random(healthy_providers)
            
        return healthy_providers[0] if healthy_providers else None
        
    def get_provider(self, name: str) -> Optional[Any]:
        """Get a provider by name"""
        return self._providers.get(name)
        
    def get_health(self, name: str) -> Optional[ProviderHealth]:
        """Get health status of a provider"""
        return self._health.get(name)
        
    def list_providers(
        self,
        healthy_only: bool = False
    ) -> List[str]:
        """List all registered providers"""
        if healthy_only:
            return self._get_healthy_providers()
        return list(self._providers.keys())
        
    def set_weight(self, name: str, weight: int) -> bool:
        """Set the weight for a provider"""
        if name not in self._providers:
            return False
            
        self.config.weights[name] = weight
        self._rebuild_weighted_list()
        return True
        
    def increment_connections(self, name: str) -> None:
        """Increment active connection count for a provider"""
        if name in self._connection_counts:
            self._connection_counts[name] += 1
            
    def decrement_connections(self, name: str) -> None:
        """Decrement active connection count for a provider"""
        if name in self._connection_counts:
            self._connection_counts[name] = max(0, self._connection_counts[name] - 1)
            
    def update_health(
        self,
        name: str,
        healthy: bool,
        latency_ms: float = 0.0
    ) -> None:
        """
        Update health status of a provider
        
        Args:
            name: Provider name
            healthy: Whether the health check passed
            latency_ms: Response latency
        """
        if name not in self._health:
            return
            
        health = self._health[name]
        health.last_check = datetime.now(timezone.utc)
        health.latency_ms = latency_ms
        health.active_connections = self._connection_counts.get(name, 0)
        
        if healthy:
            health.consecutive_failures = 0
            health.consecutive_successes += 1
            
            if health.consecutive_successes >= self.config.healthy_threshold:
                health.status = HealthStatus.HEALTHY
        else:
            health.consecutive_successes = 0
            health.consecutive_failures += 1
            
            if health.consecutive_failures >= self.config.unhealthy_threshold:
                health.status = HealthStatus.UNHEALTHY
            elif health.consecutive_failures > 0:
                health.status = HealthStatus.DEGRADED
                
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        total_connections = sum(self._connection_counts.values())
        healthy_count = len(self._get_healthy_providers())
        
        provider_stats = {}
        for name, health in self._health.items():
            provider_stats[name] = {
                'status': health.status.value,
                'connections': self._connection_counts.get(name, 0),
                'weight': self.config.weights.get(name, 1),
                'latency_ms': health.latency_ms,
                'error_rate': health.error_rate
            }
            
        return {
            'strategy': self.config.strategy.value,
            'total_providers': len(self._providers),
            'healthy_providers': healthy_count,
            'total_connections': total_connections,
            'providers': provider_stats
        }
        
    def _get_healthy_providers(self) -> List[str]:
        """Get list of healthy provider names"""
        return [
            name for name, health in self._health.items()
            if health.is_healthy
        ]
        
    def _select_round_robin(self, providers: List[str]) -> str:
        """Select using round-robin strategy"""
        if not providers:
            return None
            
        provider = providers[self._round_robin_index % len(providers)]
        self._round_robin_index += 1
        return provider
        
    def _select_weighted_round_robin(self, providers: List[str]) -> str:
        """Select using weighted round-robin strategy"""
        # Filter weighted list to only healthy providers
        available = [p for p in self._weighted_list if p in providers]
        
        if not available:
            return self._select_round_robin(providers)
            
        provider = available[self._weighted_index % len(available)]
        self._weighted_index += 1
        return provider
        
    def _select_least_connections(self, providers: List[str]) -> str:
        """Select using least-connections strategy"""
        if not providers:
            return None
            
        return min(
            providers,
            key=lambda p: self._connection_counts.get(p, 0)
        )
        
    def _select_weighted_random(self, providers: List[str]) -> str:
        """Select using weighted random strategy"""
        if not providers:
            return None
            
        weights = [self.config.weights.get(p, 1) for p in providers]
        total = sum(weights)
        
        if total == 0:
            return random.choice(providers)
            
        r = random.uniform(0, total)
        cumulative = 0
        
        for provider, weight in zip(providers, weights):
            cumulative += weight
            if r <= cumulative:
                return provider
                
        return providers[-1]
        
    def _rebuild_weighted_list(self) -> None:
        """Rebuild the weighted provider list"""
        self._weighted_list = []
        
        for provider, weight in self.config.weights.items():
            self._weighted_list.extend([provider] * weight)
            
    async def _health_check_loop(self) -> None:
        """Background task for health checking"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                for name, provider in self._providers.items():
                    try:
                        start = datetime.now(timezone.utc)
                        
                        # Perform health check
                        if hasattr(provider, 'health_check'):
                            result = await asyncio.wait_for(
                                provider.health_check(),
                                timeout=self.config.health_check_timeout
                            )
                            healthy = result.get('healthy', True)
                        else:
                            # Simulate health check
                            await asyncio.sleep(0.05)
                            healthy = True
                            
                        end = datetime.now(timezone.utc)
                        latency_ms = (end - start).total_seconds() * 1000
                        
                        self.update_health(name, healthy, latency_ms)
                        
                    except asyncio.TimeoutError:
                        self.update_health(name, False, self.config.health_check_timeout * 1000)
                    except Exception as e:
                        logger.error(f'Health check failed for {name}: {e}')
                        self.update_health(name, False)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Health check loop error: {e}')


# Factory functions
def create_load_balancer(
    strategy: BalancingStrategy = BalancingStrategy.WEIGHTED_ROUND_ROBIN,
    **kwargs
) -> LoadBalancer:
    """Create a new LoadBalancer instance"""
    config = BalancerConfig(strategy=strategy, **kwargs)
    return LoadBalancer(config)


def create_balancer_config(**kwargs) -> BalancerConfig:
    """Create a new BalancerConfig"""
    return BalancerConfig(**kwargs)


# Default weights from cloud-agent-delegation.yml
def get_default_weights() -> Dict[str, int]:
    """Get default provider weights"""
    return {
        'aws': 40,
        'gcp': 35,
        'azure': 25
    }
