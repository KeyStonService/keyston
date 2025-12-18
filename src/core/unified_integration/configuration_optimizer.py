"""
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh Configuration Optimizer
                    配置優化器 - 智能配置管理與調優
═══════════════════════════════════════════════════════════════════════════════

This module provides intelligent configuration optimization capabilities,
enabling automatic tuning, validation, and recommendation of system settings.

Core Capabilities:
- Configuration validation and schema enforcement (配置驗證與架構強制)
- Performance-based auto-tuning (基於性能的自動調優)
- Configuration drift detection (配置漂移偵測)
- Recommendation engine (建議引擎)
- Environment-specific optimization (環境特定優化)

Design Principles:
- Safe configuration changes with rollback support
- Evidence-based optimization recommendations
- Minimal disruption during configuration updates
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4
import json
from pathlib import Path

logger = logging.getLogger(__name__)


# Environment-specific concurrency optimization thresholds
# These can be adjusted based on infrastructure capacity
CONCURRENCY_THRESHOLDS = {
    'production': {
        'min_recommended': 50,
        'default_recommended': 100,
        'max_recommended': 200,
        'upper_warning_threshold': 500
    },
    'development': {
        'recommended': 10,
        'warning_threshold': 20
    }
}


class OptimizationCategory(Enum):
    """Categories of configuration optimization"""
    PERFORMANCE = 'performance'
    RELIABILITY = 'reliability'
    SECURITY = 'security'
    COST = 'cost'
    COMPLIANCE = 'compliance'


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INFORMATIONAL = 'informational'


class ConfigurationScope(Enum):
    """Scope of configuration"""
    GLOBAL = 'global'
    SERVICE = 'service'
    COMPONENT = 'component'
    ENVIRONMENT = 'environment'


class ValidationSeverity(Enum):
    """Severity of validation issues"""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'


@dataclass
class ConfigurationRule:
    """A configuration validation/optimization rule"""
    rule_id: str
    name: str
    description: str
    category: OptimizationCategory
    scope: ConfigurationScope
    validator: Callable
    optimizer: Optional[Callable] = None
    enabled: bool = True
    priority: int = 0
    tags: Set[str] = field(default_factory=set)


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'issues': self.issues,
            'warnings': self.warnings,
            'validated_at': self.validated_at.isoformat()
        }


@dataclass
class OptimizationRecommendation:
    """A configuration optimization recommendation"""
    recommendation_id: str
    title: str
    description: str
    category: OptimizationCategory
    priority: RecommendationPriority
    config_key: str
    current_value: Any
    recommended_value: Any
    expected_impact: str
    reasoning: List[str] = field(default_factory=list)
    auto_apply: bool = False
    requires_restart: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'recommendation_id': self.recommendation_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority.value,
            'config_key': self.config_key,
            'current_value': self.current_value,
            'recommended_value': self.recommended_value,
            'expected_impact': self.expected_impact,
            'reasoning': self.reasoning,
            'auto_apply': self.auto_apply,
            'requires_restart': self.requires_restart,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ConfigurationSnapshot:
    """A snapshot of configuration for tracking changes"""
    snapshot_id: str
    config: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = 'manual'
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DriftReport:
    """Report of configuration drift"""
    report_id: str
    baseline_snapshot_id: str
    current_snapshot_id: str
    drifted_keys: List[Dict[str, Any]] = field(default_factory=list)
    added_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    drift_score: float = 0.0
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'baseline_snapshot_id': self.baseline_snapshot_id,
            'current_snapshot_id': self.current_snapshot_id,
            'drifted_keys': self.drifted_keys,
            'added_keys': self.added_keys,
            'removed_keys': self.removed_keys,
            'drift_score': self.drift_score,
            'detected_at': self.detected_at.isoformat()
        }


@dataclass
class OptimizerConfig:
    """Configuration for the optimizer"""
    name: str = 'synergymesh-optimizer'
    enable_auto_optimization: bool = False
    enable_drift_detection: bool = True
    drift_check_interval_seconds: int = 300
    max_snapshots: int = 100
    auto_apply_threshold: float = 0.9


class ConfigurationOptimizer:
    """
    Configuration Optimizer - 配置優化器
    
    Intelligent configuration management providing:
    - Schema validation and enforcement
    - Performance-based auto-tuning
    - Configuration drift detection
    - Optimization recommendations
    - Safe configuration updates with rollback
    
    Usage:
        optimizer = ConfigurationOptimizer()
        
        # Validate configuration
        result = optimizer.validate(config)
        
        # Get optimization recommendations
        recommendations = optimizer.analyze(config)
        
        # Apply recommendation
        optimizer.apply_recommendation(recommendation_id)
    """
    
    def __init__(self, config: Optional[OptimizerConfig] = None):
        """Initialize the configuration optimizer"""
        self.config = config or OptimizerConfig()
        
        # Rules storage
        self._rules: Dict[str, ConfigurationRule] = {}
        
        # Snapshots for drift detection
        self._snapshots: List[ConfigurationSnapshot] = []
        self._baseline_snapshot: Optional[ConfigurationSnapshot] = None
        
        # Recommendations
        self._recommendations: Dict[str, OptimizationRecommendation] = {}
        self._applied_recommendations: List[str] = []
        
        # Performance metrics for optimization
        self._performance_metrics: Dict[str, List[Dict[str, Any]]] = {}
        
        # Statistics
        self._stats = {
            'validations': 0,
            'recommendations_generated': 0,
            'recommendations_applied': 0,
            'drift_detections': 0
        }
        
        # Initialize default rules
        self._init_default_rules()
        
        logger.info("ConfigurationOptimizer initialized - 配置優化器已初始化")
    
    def _init_default_rules(self) -> None:
        """Initialize default validation and optimization rules"""
        # Performance rules
        self.add_rule(ConfigurationRule(
            rule_id='perf-concurrent-tasks',
            name='Concurrent Tasks Limit',
            description='Validate and optimize concurrent task limits',
            category=OptimizationCategory.PERFORMANCE,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_concurrent_tasks,
            optimizer=self._optimize_concurrent_tasks,
            tags={'performance', 'scaling'}
        ))
        
        self.add_rule(ConfigurationRule(
            rule_id='perf-timeout',
            name='Timeout Configuration',
            description='Validate timeout settings',
            category=OptimizationCategory.PERFORMANCE,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_timeouts,
            tags={'performance', 'reliability'}
        ))
        
        # Security rules
        self.add_rule(ConfigurationRule(
            rule_id='sec-safety-mechanisms',
            name='Safety Mechanisms',
            description='Ensure safety mechanisms are enabled',
            category=OptimizationCategory.SECURITY,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_safety_mechanisms,
            tags={'security', 'safety'}
        ))
        
        self.add_rule(ConfigurationRule(
            rule_id='sec-slsa-provenance',
            name='SLSA Provenance',
            description='Validate SLSA provenance configuration',
            category=OptimizationCategory.COMPLIANCE,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_slsa_config,
            tags={'security', 'compliance', 'slsa'}
        ))
        
        # Reliability rules
        self.add_rule(ConfigurationRule(
            rule_id='rel-circuit-breaker',
            name='Circuit Breaker',
            description='Validate circuit breaker configuration',
            category=OptimizationCategory.RELIABILITY,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_circuit_breaker,
            optimizer=self._optimize_circuit_breaker,
            tags={'reliability', 'resilience'}
        ))
        
        self.add_rule(ConfigurationRule(
            rule_id='rel-health-check',
            name='Health Check Interval',
            description='Validate health check configuration',
            category=OptimizationCategory.RELIABILITY,
            scope=ConfigurationScope.GLOBAL,
            validator=self._validate_health_check,
            tags={'reliability', 'monitoring'}
        ))
        
        logger.debug(f"Initialized {len(self._rules)} default rules")
    
    def add_rule(self, rule: ConfigurationRule) -> None:
        """Add a validation/optimization rule"""
        self._rules[rule.rule_id] = rule
        logger.debug(f"Added rule: {rule.rule_id}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule"""
        return self._rules.pop(rule_id, None) is not None
    
    def validate(
        self,
        config: Dict[str, Any],
        categories: Optional[List[OptimizationCategory]] = None
    ) -> ValidationResult:
        """
        Validate configuration against all applicable rules
        
        驗證配置對所有適用規則
        
        Args:
            config: Configuration to validate
            categories: Optional list of categories to validate
            
        Returns:
            ValidationResult with issues and warnings
        """
        self._stats['validations'] += 1
        
        issues = []
        warnings = []
        
        for rule in self._rules.values():
            if not rule.enabled:
                continue
            
            if categories and rule.category not in categories:
                continue
            
            try:
                result = rule.validator(config)
                
                if isinstance(result, dict):
                    if result.get('issues'):
                        issues.extend(result['issues'])
                    if result.get('warnings'):
                        warnings.extend(result['warnings'])
                elif result is False:
                    issues.append({
                        'rule_id': rule.rule_id,
                        'severity': ValidationSeverity.ERROR.value,
                        'message': f'Rule {rule.name} failed validation'
                    })
            except Exception as e:
                logger.warning(f"Rule {rule.rule_id} validation error: {e}")
                warnings.append({
                    'rule_id': rule.rule_id,
                    'severity': ValidationSeverity.WARNING.value,
                    'message': f'Rule validation error: {str(e)}'
                })
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings
        )
    
    def analyze(
        self,
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None
    ) -> List[OptimizationRecommendation]:
        """
        Analyze configuration and generate optimization recommendations
        
        分析配置並生成優化建議
        
        Args:
            config: Current configuration
            metrics: Optional performance metrics
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        for rule in self._rules.values():
            if not rule.enabled or not rule.optimizer:
                continue
            
            try:
                result = rule.optimizer(config, metrics)
                
                if result:
                    if isinstance(result, list):
                        recommendations.extend(result)
                    elif isinstance(result, OptimizationRecommendation):
                        recommendations.append(result)
            except Exception as e:
                logger.warning(f"Rule {rule.rule_id} optimization error: {e}")
        
        # Store recommendations
        for rec in recommendations:
            self._recommendations[rec.recommendation_id] = rec
            self._stats['recommendations_generated'] += 1
        
        return recommendations
    
    def apply_recommendation(
        self,
        recommendation_id: str,
        config: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Apply a recommendation to the configuration
        
        應用建議到配置
        
        Args:
            recommendation_id: ID of recommendation to apply
            config: Current configuration
            
        Returns:
            Tuple of (updated config, success)
        """
        recommendation = self._recommendations.get(recommendation_id)
        if not recommendation:
            return config, False
        
        # Create snapshot before applying
        self.create_snapshot(config, source='pre-optimization')
        
        try:
            # Apply the recommendation
            updated_config = self._apply_config_change(
                config,
                recommendation.config_key,
                recommendation.recommended_value
            )
            
            # Track applied recommendation
            self._applied_recommendations.append(recommendation_id)
            self._stats['recommendations_applied'] += 1
            
            logger.info(f"Applied recommendation: {recommendation_id}")
            return updated_config, True
            
        except Exception as e:
            logger.error(f"Failed to apply recommendation: {e}")
            return config, False
    
    def create_snapshot(
        self,
        config: Dict[str, Any],
        source: str = 'manual'
    ) -> ConfigurationSnapshot:
        """
        Create a configuration snapshot
        
        創建配置快照
        
        Args:
            config: Configuration to snapshot
            source: Source of the snapshot
            
        Returns:
            Created snapshot
        """
        snapshot = ConfigurationSnapshot(
            snapshot_id=f"snap-{uuid4().hex[:8]}",
            config=config.copy(),
            source=source
        )
        
        self._snapshots.append(snapshot)
        
        # Trim old snapshots
        if len(self._snapshots) > self.config.max_snapshots:
            self._snapshots = self._snapshots[-self.config.max_snapshots:]
        
        return snapshot
    
    def set_baseline(self, config: Dict[str, Any]) -> ConfigurationSnapshot:
        """
        Set the baseline configuration for drift detection
        
        設置基準配置用於漂移偵測
        
        Args:
            config: Baseline configuration
            
        Returns:
            Baseline snapshot
        """
        self._baseline_snapshot = ConfigurationSnapshot(
            snapshot_id=f"baseline-{uuid4().hex[:8]}",
            config=config.copy(),
            source='baseline'
        )
        return self._baseline_snapshot
    
    def detect_drift(self, current_config: Dict[str, Any]) -> Optional[DriftReport]:
        """
        Detect configuration drift from baseline
        
        偵測配置漂移
        
        Args:
            current_config: Current configuration
            
        Returns:
            DriftReport if drift detected, None otherwise
        """
        if not self._baseline_snapshot:
            logger.warning("No baseline set for drift detection")
            return None
        
        self._stats['drift_detections'] += 1
        
        baseline = self._baseline_snapshot.config
        current_snapshot = self.create_snapshot(current_config, source='drift-check')
        
        drifted_keys = []
        added_keys = []
        removed_keys = []
        
        # Check for drifted and removed keys
        all_baseline_keys = self._flatten_config(baseline)
        all_current_keys = self._flatten_config(current_config)
        
        for key in all_baseline_keys:
            if key not in all_current_keys:
                removed_keys.append(key)
            elif all_baseline_keys[key] != all_current_keys[key]:
                drifted_keys.append({
                    'key': key,
                    'baseline_value': all_baseline_keys[key],
                    'current_value': all_current_keys[key]
                })
        
        # Check for added keys
        for key in all_current_keys:
            if key not in all_baseline_keys:
                added_keys.append(key)
        
        # Calculate drift score
        total_keys = len(set(all_baseline_keys.keys()) | set(all_current_keys.keys()))
        changed_keys = len(drifted_keys) + len(added_keys) + len(removed_keys)
        drift_score = changed_keys / max(total_keys, 1)
        
        if changed_keys == 0:
            return None
        
        return DriftReport(
            report_id=f"drift-{uuid4().hex[:8]}",
            baseline_snapshot_id=self._baseline_snapshot.snapshot_id,
            current_snapshot_id=current_snapshot.snapshot_id,
            drifted_keys=drifted_keys,
            added_keys=added_keys,
            removed_keys=removed_keys,
            drift_score=drift_score
        )
    
    def record_metrics(
        self,
        config_key: str,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Record performance metrics for a configuration key
        
        記錄配置鍵的性能指標
        
        Args:
            config_key: Configuration key
            metrics: Performance metrics
        """
        if config_key not in self._performance_metrics:
            self._performance_metrics[config_key] = []
        
        self._performance_metrics[config_key].append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': metrics
        })
        
        # Keep only last 100 entries per key
        if len(self._performance_metrics[config_key]) > 100:
            self._performance_metrics[config_key] = self._performance_metrics[config_key][-100:]
    
    def get_recommendations(
        self,
        category: Optional[OptimizationCategory] = None
    ) -> List[OptimizationRecommendation]:
        """Get all recommendations, optionally filtered by category"""
        recommendations = list(self._recommendations.values())
        
        if category:
            recommendations = [r for r in recommendations if r.category == category]
        
        return sorted(recommendations, key=lambda r: r.priority.value)
    
    def get_snapshots(
        self,
        limit: int = 10
    ) -> List[ConfigurationSnapshot]:
        """Get recent configuration snapshots"""
        return self._snapshots[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            'validations': self._stats['validations'],
            'recommendations_generated': self._stats['recommendations_generated'],
            'recommendations_applied': self._stats['recommendations_applied'],
            'drift_detections': self._stats['drift_detections'],
            'active_rules': sum(1 for r in self._rules.values() if r.enabled),
            'total_rules': len(self._rules),
            'snapshots_count': len(self._snapshots),
            'has_baseline': self._baseline_snapshot is not None
        }
    
    # ========== Helper Methods ==========
    
    def _flatten_config(
        self,
        config: Dict[str, Any],
        prefix: str = ''
    ) -> Dict[str, Any]:
        """Flatten nested configuration to dot-notation keys"""
        result = {}
        
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                result.update(self._flatten_config(value, full_key))
            else:
                result[full_key] = value
        
        return result
    
    def _apply_config_change(
        self,
        config: Dict[str, Any],
        key: str,
        value: Any
    ) -> Dict[str, Any]:
        """Apply a configuration change using dot-notation key"""
        result = config.copy()
        parts = key.split('.')
        
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
        return result
    
    # ========== Default Validators ==========
    
    def _validate_concurrent_tasks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate concurrent tasks configuration"""
        issues = []
        warnings = []
        
        max_tasks = config.get('max_concurrent_tasks', 100)
        
        if max_tasks < 1:
            issues.append({
                'rule_id': 'perf-concurrent-tasks',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'max_concurrent_tasks must be at least 1',
                'key': 'max_concurrent_tasks',
                'value': max_tasks
            })
        elif max_tasks > 1000:
            warnings.append({
                'rule_id': 'perf-concurrent-tasks',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'max_concurrent_tasks is very high, may cause resource issues',
                'key': 'max_concurrent_tasks',
                'value': max_tasks
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    def _validate_timeouts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate timeout configuration"""
        issues = []
        warnings = []
        
        task_timeout = config.get('task_timeout_seconds', 300)
        request_timeout = config.get('request_timeout_seconds', 30)
        
        if task_timeout < 1:
            issues.append({
                'rule_id': 'perf-timeout',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'task_timeout_seconds must be at least 1',
                'key': 'task_timeout_seconds',
                'value': task_timeout
            })
        
        if request_timeout < 1:
            issues.append({
                'rule_id': 'perf-timeout',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'request_timeout_seconds must be at least 1',
                'key': 'request_timeout_seconds',
                'value': request_timeout
            })
        
        if request_timeout > task_timeout:
            warnings.append({
                'rule_id': 'perf-timeout',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'request_timeout should be less than task_timeout',
                'key': 'request_timeout_seconds'
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    def _validate_safety_mechanisms(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate safety mechanisms configuration"""
        issues = []
        warnings = []
        
        env = config.get('environment', 'development')
        safety_enabled = config.get('enable_safety_mechanisms', True)
        
        if env == 'production' and not safety_enabled:
            issues.append({
                'rule_id': 'sec-safety-mechanisms',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'Safety mechanisms must be enabled in production',
                'key': 'enable_safety_mechanisms',
                'value': safety_enabled
            })
        elif not safety_enabled:
            warnings.append({
                'rule_id': 'sec-safety-mechanisms',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'Safety mechanisms are disabled',
                'key': 'enable_safety_mechanisms',
                'value': safety_enabled
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    def _validate_slsa_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SLSA provenance configuration"""
        issues = []
        warnings = []
        
        slsa_enabled = config.get('enable_slsa_provenance', True)
        env = config.get('environment', 'development')
        
        if env == 'production' and not slsa_enabled:
            warnings.append({
                'rule_id': 'sec-slsa-provenance',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'SLSA provenance is recommended for production',
                'key': 'enable_slsa_provenance',
                'value': slsa_enabled
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    def _validate_circuit_breaker(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate circuit breaker configuration"""
        issues = []
        warnings = []
        
        cb_enabled = config.get('enable_circuit_breaker', True)
        cb_threshold = config.get('circuit_breaker_threshold', 5)
        env = config.get('environment', 'development')
        
        if env == 'production' and not cb_enabled:
            warnings.append({
                'rule_id': 'rel-circuit-breaker',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'Circuit breaker is recommended for production',
                'key': 'enable_circuit_breaker'
            })
        
        if cb_enabled and cb_threshold < 1:
            issues.append({
                'rule_id': 'rel-circuit-breaker',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'Circuit breaker threshold must be at least 1',
                'key': 'circuit_breaker_threshold',
                'value': cb_threshold
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    def _validate_health_check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate health check configuration"""
        issues = []
        warnings = []
        
        interval = config.get('health_check_interval_seconds', 60)
        
        if interval < 5:
            issues.append({
                'rule_id': 'rel-health-check',
                'severity': ValidationSeverity.ERROR.value,
                'message': 'Health check interval must be at least 5 seconds',
                'key': 'health_check_interval_seconds',
                'value': interval
            })
        elif interval > 300:
            warnings.append({
                'rule_id': 'rel-health-check',
                'severity': ValidationSeverity.WARNING.value,
                'message': 'Health check interval is very long, issues may go undetected',
                'key': 'health_check_interval_seconds',
                'value': interval
            })
        
        return {'issues': issues, 'warnings': warnings}
    
    # ========== Default Optimizers ==========
    
    def _optimize_concurrent_tasks(
        self,
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[OptimizationRecommendation]:
        """Generate recommendations for concurrent task optimization"""
        current_value = config.get('max_concurrent_tasks', 100)
        env = config.get('environment', 'development')
        
        # Environment-based recommendations using configurable thresholds
        recommended_value = current_value
        reasoning = []
        
        if env == 'production':
            prod_thresholds = CONCURRENCY_THRESHOLDS['production']
            if current_value < prod_thresholds['min_recommended']:
                recommended_value = prod_thresholds['default_recommended']
                reasoning.append("Production environments typically need higher concurrency")
            elif current_value > prod_thresholds['upper_warning_threshold']:
                recommended_value = prod_thresholds['max_recommended']
                reasoning.append("Very high concurrency may cause resource contention")
        elif env == 'development':
            dev_thresholds = CONCURRENCY_THRESHOLDS['development']
            if current_value > dev_thresholds['warning_threshold']:
                recommended_value = dev_thresholds['recommended']
                reasoning.append("Development environments work well with lower concurrency")
        
        if recommended_value == current_value:
            return None
        
        return OptimizationRecommendation(
            recommendation_id=f"rec-{uuid4().hex[:8]}",
            title='Optimize Concurrent Tasks',
            description=f'Adjust max_concurrent_tasks from {current_value} to {recommended_value}',
            category=OptimizationCategory.PERFORMANCE,
            priority=RecommendationPriority.MEDIUM,
            config_key='max_concurrent_tasks',
            current_value=current_value,
            recommended_value=recommended_value,
            expected_impact='Improved resource utilization',
            reasoning=reasoning,
            auto_apply=False,
            requires_restart=False
        )
    
    def _optimize_circuit_breaker(
        self,
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[OptimizationRecommendation]:
        """Generate recommendations for circuit breaker optimization"""
        cb_enabled = config.get('enable_circuit_breaker', True)
        cb_threshold = config.get('circuit_breaker_threshold', 5)
        env = config.get('environment', 'development')
        
        if not cb_enabled and env == 'production':
            return OptimizationRecommendation(
                recommendation_id=f"rec-{uuid4().hex[:8]}",
                title='Enable Circuit Breaker',
                description='Enable circuit breaker for production resilience',
                category=OptimizationCategory.RELIABILITY,
                priority=RecommendationPriority.HIGH,
                config_key='enable_circuit_breaker',
                current_value=cb_enabled,
                recommended_value=True,
                expected_impact='Improved fault tolerance and system stability',
                reasoning=[
                    'Circuit breaker prevents cascade failures',
                    'Required for production-grade resilience'
                ],
                auto_apply=False,
                requires_restart=False
            )
        
        return None


# Factory function
def create_configuration_optimizer(
    config: Optional[OptimizerConfig] = None
) -> ConfigurationOptimizer:
    """Create a new ConfigurationOptimizer instance"""
    return ConfigurationOptimizer(config)
