"""
Safety Net System (多層安全網)

Multi-layer safety net providing defense in depth.

Reference: Three-layer architecture with human-in-the-loop oversight,
machine learning safety net, and automatic safeguards [9]
"""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


class SafetyLayer(Enum):
    """Layers in the safety net"""
    LAYER_1_INPUT_VALIDATION = 1     # Input validation and sanitization
    LAYER_2_PERMISSION_CHECK = 2     # Permission and authorization
    LAYER_3_RESOURCE_LIMIT = 3       # Resource limits and quotas
    LAYER_4_BEHAVIOR_CHECK = 4       # Behavior analysis
    LAYER_5_OUTPUT_VALIDATION = 5    # Output validation
    LAYER_6_AUDIT_LOG = 6           # Audit logging


@dataclass
class SafetyCheck:
    """A safety check in the safety net"""
    name: str
    description: str
    layer: SafetyLayer
    check_function: Callable[[Any], bool]
    on_failure: Optional[Callable[[Any], None]] = None
    enabled: bool = True
    blocking: bool = True  # If True, failure blocks the operation
    priority: int = 0


@dataclass
class SafetyCheckResult:
    """Result of a safety check"""
    check_name: str
    layer: SafetyLayer
    passed: bool
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class SafetyNetConfig:
    """Configuration for safety net"""
    name: str = "default"
    fail_fast: bool = True  # Stop at first failure
    require_all_layers: bool = False  # Require checks in all layers
    log_all_checks: bool = True
    max_retries: int = 0


T = TypeVar('T')


class SafetyNet:
    """
    Multi-Layer Safety Net System
    
    Provides defense in depth through multiple safety layers,
    each performing specific types of checks.
    
    Layers:
    1. Input Validation - Sanitize and validate inputs
    2. Permission Check - Authorization and access control
    3. Resource Limit - Quotas and resource bounds
    4. Behavior Check - Pattern and behavior analysis
    5. Output Validation - Validate outputs before delivery
    6. Audit Log - Record all actions
    
    Example:
        safety = SafetyNet()
        safety.add_check(SafetyCheck(
            name="sql_injection",
            layer=SafetyLayer.LAYER_1_INPUT_VALIDATION,
            check_function=lambda x: not contains_sql_injection(x)
        ))
        result = await safety.execute(operation, input_data)
    """
    
    def __init__(self, config: Optional[SafetyNetConfig] = None):
        self.config = config or SafetyNetConfig()
        self._checks: Dict[SafetyLayer, List[SafetyCheck]] = {
            layer: [] for layer in SafetyLayer
        }
        self._results_history: List[List[SafetyCheckResult]] = []
        self._blocked_count = 0
        self._passed_count = 0
        
        # Register default checks
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register default safety checks for each layer"""
        # Layer 1: Input validation
        self.add_check(SafetyCheck(
            name="null_check",
            description="Check for null/None inputs",
            layer=SafetyLayer.LAYER_1_INPUT_VALIDATION,
            check_function=lambda x: x is not None,
            priority=0
        ))
        
        # Layer 2: Permission check (placeholder)
        self.add_check(SafetyCheck(
            name="basic_permission",
            description="Basic permission check",
            layer=SafetyLayer.LAYER_2_PERMISSION_CHECK,
            check_function=lambda x: True,  # Always pass by default
            priority=0
        ))
        
        # Layer 6: Audit log
        self.add_check(SafetyCheck(
            name="audit_log",
            description="Log operation for audit",
            layer=SafetyLayer.LAYER_6_AUDIT_LOG,
            check_function=lambda x: True,  # Always pass
            blocking=False,
            priority=100
        ))
    
    def add_check(self, check: SafetyCheck) -> None:
        """Add a safety check to the appropriate layer"""
        self._checks[check.layer].append(check)
        # Sort by priority within layer
        self._checks[check.layer].sort(key=lambda c: c.priority)
    
    def remove_check(self, name: str) -> bool:
        """Remove a safety check by name"""
        for layer_checks in self._checks.values():
            for check in layer_checks:
                if check.name == name:
                    layer_checks.remove(check)
                    return True
        return False
    
    def enable_check(self, name: str) -> bool:
        """Enable a safety check"""
        for layer_checks in self._checks.values():
            for check in layer_checks:
                if check.name == name:
                    check.enabled = True
                    return True
        return False
    
    def disable_check(self, name: str) -> bool:
        """Disable a safety check"""
        for layer_checks in self._checks.values():
            for check in layer_checks:
                if check.name == name:
                    check.enabled = False
                    return True
        return False
    
    async def validate(self, data: Any) -> List[SafetyCheckResult]:
        """
        Run all safety checks on data
        
        Args:
            data: Data to validate
            
        Returns:
            List of SafetyCheckResult for all checks
        """
        results: List[SafetyCheckResult] = []
        
        # Process each layer in order
        for layer in SafetyLayer:
            layer_results = await self._run_layer_checks(layer, data)
            results.extend(layer_results)
            
            # Check for blocking failures
            if self.config.fail_fast:
                blocking_failures = [
                    r for r in layer_results 
                    if not r.passed and self._is_blocking(r.check_name)
                ]
                if blocking_failures:
                    break
        
        # Store results
        self._results_history.append(results)
        
        # Update counters
        all_passed = all(r.passed for r in results if self._is_blocking(r.check_name))
        if all_passed:
            self._passed_count += 1
        else:
            self._blocked_count += 1
        
        return results
    
    async def _run_layer_checks(
        self, 
        layer: SafetyLayer, 
        data: Any
    ) -> List[SafetyCheckResult]:
        """Run all checks for a specific layer"""
        results: List[SafetyCheckResult] = []
        
        for check in self._checks[layer]:
            if not check.enabled:
                continue
            
            try:
                passed = check.check_function(data)
                if asyncio.iscoroutine(passed):
                    passed = await passed
                
                result = SafetyCheckResult(
                    check_name=check.name,
                    layer=layer,
                    passed=passed,
                    timestamp=datetime.now()
                )
                
                if not passed and check.on_failure:
                    try:
                        if asyncio.iscoroutinefunction(check.on_failure):
                            await check.on_failure(data)
                        else:
                            check.on_failure(data)
                    except Exception:
                        pass
                
            except Exception as e:
                result = SafetyCheckResult(
                    check_name=check.name,
                    layer=layer,
                    passed=False,
                    timestamp=datetime.now(),
                    error=str(e)
                )
            
            results.append(result)
            
            # Fail fast if blocking check fails
            if self.config.fail_fast and not result.passed and check.blocking:
                break
        
        return results
    
    def _is_blocking(self, check_name: str) -> bool:
        """Check if a check is blocking"""
        for layer_checks in self._checks.values():
            for check in layer_checks:
                if check.name == check_name:
                    return check.blocking
        return True
    
    async def execute(
        self, 
        operation: Callable[[T], Any], 
        data: T
    ) -> Any:
        """
        Execute operation with safety net protection
        
        Args:
            operation: Operation to execute
            data: Input data
            
        Returns:
            Operation result if all checks pass
            
        Raises:
            SafetyCheckError: If any blocking check fails
        """
        # Run validation
        results = await self.validate(data)
        
        # Check for failures
        failures = [r for r in results if not r.passed and self._is_blocking(r.check_name)]
        
        if failures:
            raise SafetyCheckError(
                f"Safety check failed: {failures[0].check_name}",
                failures=failures
            )
        
        # Execute operation
        if asyncio.iscoroutinefunction(operation):
            return await operation(data)
        else:
            return operation(data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get safety net statistics"""
        total_checks = sum(len(checks) for checks in self._checks.values())
        enabled_checks = sum(
            len([c for c in checks if c.enabled]) 
            for checks in self._checks.values()
        )
        
        return {
            "name": self.config.name,
            "total_checks": total_checks,
            "enabled_checks": enabled_checks,
            "blocked_operations": self._blocked_count,
            "passed_operations": self._passed_count,
            "block_rate": (
                self._blocked_count / (self._blocked_count + self._passed_count)
                if (self._blocked_count + self._passed_count) > 0
                else 0
            ),
            "checks_by_layer": {
                layer.name: len([c for c in self._checks[layer] if c.enabled])
                for layer in SafetyLayer
            }
        }
    
    def get_recent_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent validation results"""
        recent = self._results_history[-limit:]
        return [
            {
                "timestamp": results[0].timestamp.isoformat() if results else None,
                "total_checks": len(results),
                "passed": len([r for r in results if r.passed]),
                "failed": len([r for r in results if not r.passed]),
                "failures": [
                    {"check": r.check_name, "layer": r.layer.name}
                    for r in results if not r.passed
                ]
            }
            for results in recent
        ]
    
    def list_checks(self) -> List[Dict[str, Any]]:
        """List all registered checks"""
        checks = []
        for layer in SafetyLayer:
            for check in self._checks[layer]:
                checks.append({
                    "name": check.name,
                    "description": check.description,
                    "layer": layer.name,
                    "enabled": check.enabled,
                    "blocking": check.blocking,
                    "priority": check.priority
                })
        return checks


class SafetyCheckError(Exception):
    """Error raised when safety check fails"""
    
    def __init__(self, message: str, failures: List[SafetyCheckResult]):
        super().__init__(message)
        self.failures = failures
