"""
Cloud Provider Adapter - Adapters for different cloud providers

This module provides adapters for executing tasks on various cloud
providers including AWS Lambda, Google Cloud Functions, and Azure Functions.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported cloud provider types"""
    AWS = 'aws'
    GCP = 'gcp'
    AZURE = 'azure'
    LOCAL = 'local'


class ProviderStatus(Enum):
    """Provider availability status"""
    AVAILABLE = 'available'
    DEGRADED = 'degraded'
    UNAVAILABLE = 'unavailable'
    MAINTENANCE = 'maintenance'


@dataclass
class ProviderConfig:
    """Configuration for a cloud provider"""
    name: str
    provider_type: ProviderType
    enabled: bool = True
    region: str = 'us-east-1'
    runtime: str = 'nodejs18.x'
    timeout: int = 300  # seconds
    memory_size: int = 1024  # MB
    environment_variables: Dict[str, str] = field(default_factory=dict)
    vpc_config: Optional[Dict[str, Any]] = None
    layers: List[str] = field(default_factory=list)
    concurrency_limit: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'providerType': self.provider_type.value,
            'enabled': self.enabled,
            'region': self.region,
            'runtime': self.runtime,
            'timeout': self.timeout,
            'memorySize': self.memory_size,
            'environmentVariables': self.environment_variables,
            'vpcConfig': self.vpc_config,
            'layers': self.layers,
            'concurrencyLimit': self.concurrency_limit,
            'metadata': self.metadata
        }


@dataclass
class ExecutionResult:
    """Result of a cloud execution"""
    execution_id: str
    provider: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    billed_duration_ms: float = 0.0
    memory_used_mb: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'executionId': self.execution_id,
            'provider': self.provider,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'logs': self.logs,
            'durationMs': self.duration_ms,
            'billedDurationMs': self.billed_duration_ms,
            'memoryUsedMb': self.memory_used_mb,
            'startedAt': self.started_at.isoformat(),
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }


class CloudProviderAdapter:
    """
    Base adapter for cloud providers
    
    Provides common functionality for executing tasks on
    various cloud providers.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize the adapter
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self._status = ProviderStatus.AVAILABLE
        self._execution_count = 0
        self._error_count = 0
        self._last_execution: Optional[datetime] = None
        
    @property
    def status(self) -> ProviderStatus:
        """Get provider status"""
        return self._status
        
    @property
    def is_available(self) -> bool:
        """Check if provider is available"""
        return (
            self.config.enabled and
            self._status in (ProviderStatus.AVAILABLE, ProviderStatus.DEGRADED)
        )
        
    async def execute(self, task: Any) -> ExecutionResult:
        """
        Execute a task on this provider
        
        Args:
            task: Task to execute
            
        Returns:
            ExecutionResult with execution details
        """
        execution_id = str(uuid4())
        result = ExecutionResult(
            execution_id=execution_id,
            provider=self.config.name,
            status='running'
        )
        
        try:
            self._execution_count += 1
            
            # Execute based on provider type
            if self.config.provider_type == ProviderType.AWS:
                execution_result = await self._execute_aws(task)
            elif self.config.provider_type == ProviderType.GCP:
                execution_result = await self._execute_gcp(task)
            elif self.config.provider_type == ProviderType.AZURE:
                execution_result = await self._execute_azure(task)
            else:
                execution_result = await self._execute_local(task)
                
            result.result = execution_result
            result.status = 'success'
            result.completed_at = datetime.now(timezone.utc)
            result.duration_ms = (
                result.completed_at - result.started_at
            ).total_seconds() * 1000
            
            self._last_execution = datetime.now(timezone.utc)
            
        except Exception as e:
            self._error_count += 1
            result.status = 'error'
            result.error = str(e)
            result.completed_at = datetime.now(timezone.utc)
            
            # Update status if error rate is high
            if self._error_count / max(self._execution_count, 1) > 0.5:
                self._status = ProviderStatus.DEGRADED
                
            logger.error(f'Execution failed on {self.config.name}: {e}')
            
        return result
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the provider
        
        Returns:
            Health check result
        """
        try:
            # Simulate health check
            await asyncio.sleep(0.05)
            
            error_rate = self._error_count / max(self._execution_count, 1)
            
            if error_rate > 0.5:
                self._status = ProviderStatus.DEGRADED
            elif error_rate > 0.8:
                self._status = ProviderStatus.UNAVAILABLE
            else:
                self._status = ProviderStatus.AVAILABLE
                
            return {
                'healthy': self._status == ProviderStatus.AVAILABLE,
                'status': self._status.value,
                'execution_count': self._execution_count,
                'error_count': self._error_count,
                'error_rate': error_rate,
                'last_execution': self._last_execution.isoformat() if self._last_execution else None
            }
            
        except Exception as e:
            self._status = ProviderStatus.UNAVAILABLE
            return {
                'healthy': False,
                'status': self._status.value,
                'error': str(e)
            }
            
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            'name': self.config.name,
            'provider_type': self.config.provider_type.value,
            'status': self._status.value,
            'execution_count': self._execution_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(self._execution_count, 1),
            'last_execution': self._last_execution.isoformat() if self._last_execution else None,
            'config': self.config.to_dict()
        }
        
    def reset_stats(self) -> None:
        """Reset provider statistics"""
        self._execution_count = 0
        self._error_count = 0
        self._status = ProviderStatus.AVAILABLE
        
    async def _execute_aws(self, task: Any) -> Dict[str, Any]:
        """Execute on AWS Lambda"""
        # Simulate AWS Lambda invocation
        await asyncio.sleep(0.1)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Executed on AWS Lambda',
                'task_id': getattr(task, 'id', str(uuid4())),
                'task_type': getattr(task, 'type', 'unknown'),
                'region': self.config.region,
                'runtime': self.config.runtime
            }
        }
        
    async def _execute_gcp(self, task: Any) -> Dict[str, Any]:
        """Execute on Google Cloud Functions"""
        # Simulate GCP Cloud Function invocation
        await asyncio.sleep(0.1)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Executed on Google Cloud Functions',
                'task_id': getattr(task, 'id', str(uuid4())),
                'task_type': getattr(task, 'type', 'unknown'),
                'region': self.config.region,
                'runtime': self.config.runtime
            }
        }
        
    async def _execute_azure(self, task: Any) -> Dict[str, Any]:
        """Execute on Azure Functions"""
        # Simulate Azure Functions invocation
        await asyncio.sleep(0.1)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Executed on Azure Functions',
                'task_id': getattr(task, 'id', str(uuid4())),
                'task_type': getattr(task, 'type', 'unknown'),
                'region': self.config.region,
                'runtime': self.config.runtime
            }
        }
        
    async def _execute_local(self, task: Any) -> Dict[str, Any]:
        """Execute locally (for testing)"""
        await asyncio.sleep(0.05)
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Executed locally',
                'task_id': getattr(task, 'id', str(uuid4())),
                'task_type': getattr(task, 'type', 'unknown')
            }
        }


class AWSLambdaAdapter(CloudProviderAdapter):
    """Adapter for AWS Lambda"""
    
    def __init__(
        self,
        name: str,
        region: str = 'us-east-1',
        **kwargs
    ):
        config = ProviderConfig(
            name=name,
            provider_type=ProviderType.AWS,
            region=region,
            **kwargs
        )
        super().__init__(config)


class GCPCloudFunctionsAdapter(CloudProviderAdapter):
    """Adapter for Google Cloud Functions"""
    
    def __init__(
        self,
        name: str,
        region: str = 'us-central1',
        **kwargs
    ):
        # Map GCP runtime naming
        if 'runtime' not in kwargs:
            kwargs['runtime'] = 'nodejs18'
            
        config = ProviderConfig(
            name=name,
            provider_type=ProviderType.GCP,
            region=region,
            **kwargs
        )
        super().__init__(config)


class AzureFunctionsAdapter(CloudProviderAdapter):
    """Adapter for Azure Functions"""
    
    def __init__(
        self,
        name: str,
        region: str = 'eastus',
        **kwargs
    ):
        if 'runtime' not in kwargs:
            kwargs['runtime'] = 'node'
            
        config = ProviderConfig(
            name=name,
            provider_type=ProviderType.AZURE,
            region=region,
            **kwargs
        )
        super().__init__(config)


# Factory functions
def create_provider_adapter(
    provider_type: ProviderType,
    name: str,
    **kwargs
) -> CloudProviderAdapter:
    """Create a provider adapter for the specified type"""
    if provider_type == ProviderType.AWS:
        return AWSLambdaAdapter(name, **kwargs)
    elif provider_type == ProviderType.GCP:
        return GCPCloudFunctionsAdapter(name, **kwargs)
    elif provider_type == ProviderType.AZURE:
        return AzureFunctionsAdapter(name, **kwargs)
    else:
        config = ProviderConfig(
            name=name,
            provider_type=provider_type,
            **kwargs
        )
        return CloudProviderAdapter(config)


def create_provider_config(
    name: str,
    provider_type: ProviderType,
    **kwargs
) -> ProviderConfig:
    """Create a provider configuration"""
    return ProviderConfig(
        name=name,
        provider_type=provider_type,
        **kwargs
    )
