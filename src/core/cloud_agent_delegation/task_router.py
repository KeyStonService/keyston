"""
Task Router - Intelligent task routing based on policies

This module provides intelligent routing of tasks to appropriate
cloud providers based on configurable rules and policies.
"""

import fnmatch
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategy types"""
    PATTERN_MATCH = 'pattern_match'
    PRIORITY_BASED = 'priority_based'
    ROUND_ROBIN = 'round_robin'
    LEAST_CONNECTIONS = 'least_connections'
    WEIGHTED = 'weighted'


@dataclass
class RoutingRule:
    """Definition of a routing rule"""
    id: str
    name: str
    pattern: str  # Pattern to match task type
    preferred_provider: str
    priority: str = 'medium'  # critical, high, medium, low
    max_parallel: int = 10
    timeout_override: Optional[int] = None
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    fallback_providers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'pattern': self.pattern,
            'preferredProvider': self.preferred_provider,
            'priority': self.priority,
            'maxParallel': self.max_parallel,
            'timeoutOverride': self.timeout_override,
            'enabled': self.enabled,
            'conditions': self.conditions,
            'fallbackProviders': self.fallback_providers,
            'metadata': self.metadata
        }
        
    def matches(self, task_type: str) -> bool:
        """Check if rule matches a task type"""
        if not self.enabled:
            return False
            
        # Support wildcard patterns like "analyze:*"
        if '*' in self.pattern:
            return fnmatch.fnmatch(task_type, self.pattern)
            
        # Support regex patterns
        if self.pattern.startswith('^') or self.pattern.endswith('$'):
            try:
                return bool(re.match(self.pattern, task_type))
            except re.error:
                return False
                
        # Exact match or prefix match
        return task_type == self.pattern or task_type.startswith(self.pattern + ':')


@dataclass
class RoutingResult:
    """Result of a routing decision"""
    task_id: str
    rule_id: Optional[str]
    rule_name: Optional[str]
    provider: str
    priority: str
    timeout: Optional[int] = None
    fallback_providers: List[str] = field(default_factory=list)
    matched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'taskId': self.task_id,
            'ruleId': self.rule_id,
            'ruleName': self.rule_name,
            'provider': self.provider,
            'priority': self.priority,
            'timeout': self.timeout,
            'fallbackProviders': self.fallback_providers,
            'matchedAt': self.matched_at.isoformat(),
            'metadata': self.metadata
        }


class TaskRouter:
    """
    Intelligent task router
    
    Routes tasks to appropriate cloud providers based on
    configurable rules, priorities, and conditions.
    """
    
    def __init__(
        self,
        default_provider: str = 'default',
        strategy: RoutingStrategy = RoutingStrategy.PATTERN_MATCH
    ):
        """
        Initialize the router
        
        Args:
            default_provider: Default provider when no rule matches
            strategy: Routing strategy to use
        """
        self.default_provider = default_provider
        self.strategy = strategy
        self._rules: Dict[str, RoutingRule] = {}
        self._priority_order = ['critical', 'high', 'medium', 'low']
        self._routing_history: List[RoutingResult] = []
        self._round_robin_index = 0
        
    def add_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule"""
        self._rules[rule.id] = rule
        logger.debug(f'Added routing rule: {rule.name}')
        
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a routing rule"""
        rule = self._rules.pop(rule_id, None)
        if rule:
            logger.debug(f'Removed routing rule: {rule.name}')
            return True
        return False
        
    def get_rule(self, rule_id: str) -> Optional[RoutingRule]:
        """Get a rule by ID"""
        return self._rules.get(rule_id)
        
    def list_rules(self, enabled_only: bool = False) -> List[RoutingRule]:
        """List all rules"""
        rules = list(self._rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules
        
    async def route(self, task: Any) -> RoutingResult:
        """
        Route a task to a provider
        
        Args:
            task: Task to route
            
        Returns:
            RoutingResult with provider selection
        """
        task_id = getattr(task, 'id', str(uuid4()))
        task_type = getattr(task, 'type', 'unknown')
        task_priority = getattr(task, 'priority', None)
        
        # Find matching rule
        matching_rule = self._find_matching_rule(task_type)
        
        if matching_rule:
            result = RoutingResult(
                task_id=task_id,
                rule_id=matching_rule.id,
                rule_name=matching_rule.name,
                provider=matching_rule.preferred_provider,
                priority=matching_rule.priority,
                timeout=matching_rule.timeout_override,
                fallback_providers=matching_rule.fallback_providers
            )
        else:
            # Use default routing
            result = RoutingResult(
                task_id=task_id,
                rule_id=None,
                rule_name=None,
                provider=self.default_provider,
                priority=task_priority.value if task_priority else 'medium'
            )
            
        # Record routing decision
        self._routing_history.append(result)
        
        # Keep history bounded
        if len(self._routing_history) > 10000:
            self._routing_history = self._routing_history[-5000:]
            
        logger.debug(f'Routed task {task_id} to {result.provider}')
        return result
        
    def evaluate_conditions(
        self,
        rule: RoutingRule,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate rule conditions against context
        
        Args:
            rule: Rule to evaluate
            context: Context data
            
        Returns:
            True if conditions are met
        """
        conditions = rule.conditions
        if not conditions:
            return True
            
        # Evaluate each condition
        for condition_type, condition_value in conditions.items():
            if condition_type == 'min_priority':
                task_priority = context.get('priority', 'medium')
                if self._priority_order.index(task_priority) > self._priority_order.index(condition_value):
                    return False
                    
            elif condition_type == 'max_payload_size':
                payload_size = context.get('payload_size', 0)
                if payload_size > condition_value:
                    return False
                    
            elif condition_type == 'time_window':
                # Check if current time is within allowed window
                start_hour = condition_value.get('start', 0)
                end_hour = condition_value.get('end', 24)
                current_hour = datetime.now(timezone.utc).hour
                if not (start_hour <= current_hour < end_hour):
                    return False
                    
            elif condition_type == 'environment':
                required_env = condition_value
                current_env = context.get('environment', 'production')
                if current_env != required_env:
                    return False
                    
        return True
        
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        provider_counts = {}
        rule_counts = {}
        
        for result in self._routing_history:
            provider_counts[result.provider] = provider_counts.get(result.provider, 0) + 1
            if result.rule_name:
                rule_counts[result.rule_name] = rule_counts.get(result.rule_name, 0) + 1
                
        return {
            'total_routes': len(self._routing_history),
            'rules_count': len(self._rules),
            'enabled_rules': len([r for r in self._rules.values() if r.enabled]),
            'provider_distribution': provider_counts,
            'rule_usage': rule_counts,
            'default_provider': self.default_provider,
            'strategy': self.strategy.value
        }
        
    def clear_history(self) -> None:
        """Clear routing history"""
        self._routing_history.clear()
        
    def _find_matching_rule(self, task_type: str) -> Optional[RoutingRule]:
        """Find the best matching rule for a task type"""
        matching_rules = []
        
        for rule in self._rules.values():
            if rule.matches(task_type):
                matching_rules.append(rule)
                
        if not matching_rules:
            return None
            
        # Sort by priority
        matching_rules.sort(
            key=lambda r: self._priority_order.index(r.priority)
            if r.priority in self._priority_order else len(self._priority_order)
        )
        
        return matching_rules[0]


# Factory functions
def create_task_router(
    default_provider: str = 'default',
    strategy: RoutingStrategy = RoutingStrategy.PATTERN_MATCH
) -> TaskRouter:
    """Create a new TaskRouter instance"""
    return TaskRouter(default_provider, strategy)


def create_routing_rule(
    name: str,
    pattern: str,
    preferred_provider: str,
    **kwargs
) -> RoutingRule:
    """Create a new RoutingRule"""
    return RoutingRule(
        id=str(uuid4()),
        name=name,
        pattern=pattern,
        preferred_provider=preferred_provider,
        **kwargs
    )


# Pre-defined routing rules based on cloud-agent-delegation.yml
def get_default_routing_rules() -> List[RoutingRule]:
    """Get default routing rules from configuration"""
    return [
        RoutingRule(
            id='code-analysis-rule',
            name='code-analysis',
            pattern='analyze:*',
            preferred_provider='aws',
            max_parallel=10,
            priority='high',
            fallback_providers=['gcp', 'azure']
        ),
        RoutingRule(
            id='auto-fix-rule',
            name='auto-fix',
            pattern='fix:*',
            preferred_provider='gcp',
            max_parallel=20,
            priority='high',
            fallback_providers=['aws', 'azure']
        ),
        RoutingRule(
            id='optimization-rule',
            name='optimization',
            pattern='optimize:*',
            preferred_provider='azure',
            max_parallel=5,
            priority='medium',
            fallback_providers=['aws', 'gcp']
        ),
        RoutingRule(
            id='security-scan-rule',
            name='security-scan',
            pattern='security:*',
            preferred_provider='aws',
            max_parallel=15,
            priority='critical',
            fallback_providers=['gcp', 'azure']
        ),
        RoutingRule(
            id='report-generation-rule',
            name='report-generation',
            pattern='report:*',
            preferred_provider='gcp',
            max_parallel=8,
            priority='low',
            fallback_providers=['aws', 'azure']
        )
    ]
