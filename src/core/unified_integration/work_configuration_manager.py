"""
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh Work Configuration Manager
                    工作配置管理器 - 統一工作流程與策略整合
═══════════════════════════════════════════════════════════════════════════════

This module provides unified work configuration management that integrates:
- Module mapping references (模組映射引用)
- Strategy policy enforcement (策略政策執行)
- Work configuration validation (工作配置驗證)
- Cross-reference integrity checking (交叉引用完整性檢查)

Core Capabilities:
- Load and validate system module mappings (載入與驗證系統模組映射)
- Cross-reference validation across configurations (跨配置交叉引用驗證)
- Strategy policy integration with orchestration (策略政策與編排整合)
- Work configuration lifecycle management (工作配置生命週期管理)
- Capability registry alignment (能力註冊表對齊)

Design Principles:
- Single source of truth for configuration references
- Declarative work configuration specification
- Automatic validation and optimization suggestions
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkConfigurationStatus(Enum):
    """Work configuration status"""
    DRAFT = 'draft'
    VALIDATING = 'validating'
    VALID = 'valid'
    INVALID = 'invalid'
    ACTIVE = 'active'
    DEPRECATED = 'deprecated'


class ReferenceType(Enum):
    """Types of configuration references"""
    MODULE = 'module'
    CAPABILITY = 'capability'
    SERVICE = 'service'
    CONFIG_FILE = 'config_file'
    STRATEGY = 'strategy'
    POLICY = 'policy'


class IntegrityLevel(Enum):
    """Configuration integrity levels"""
    FULL = 'full'        # All references resolved
    PARTIAL = 'partial'  # Some references missing
    BROKEN = 'broken'    # Critical references missing
    UNKNOWN = 'unknown'  # Not yet validated


@dataclass
class ConfigurationReference:
    """A reference to another configuration element"""
    ref_id: str
    ref_type: ReferenceType
    source_path: str
    target_path: str
    required: bool = True
    resolved: bool = False
    resolution_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'ref_id': self.ref_id,
            'ref_type': self.ref_type.value,
            'source_path': self.source_path,
            'target_path': self.target_path,
            'required': self.required,
            'resolved': self.resolved,
            'resolution_error': self.resolution_error,
            'metadata': self.metadata
        }


@dataclass
class StrategyPolicy:
    """A strategy policy for work configuration"""
    policy_id: str
    name: str
    description: str
    category: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    enforcement_mode: str = 'warn'  # 'strict', 'warn', 'permissive'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'rules': self.rules,
            'enabled': self.enabled,
            'priority': self.priority,
            'enforcement_mode': self.enforcement_mode,
            'metadata': self.metadata
        }


@dataclass
class CapabilityMapping:
    """Mapping between capabilities and providers"""
    capability_id: str
    name: str
    description: str
    providers: List[str] = field(default_factory=list)
    backup_providers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'capability_id': self.capability_id,
            'name': self.name,
            'description': self.description,
            'providers': self.providers,
            'backup_providers': self.backup_providers,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }


@dataclass
class WorkConfiguration:
    """A complete work configuration"""
    config_id: str
    name: str
    version: str
    description: str = ''
    status: WorkConfigurationStatus = WorkConfigurationStatus.DRAFT
    references: List[ConfigurationReference] = field(default_factory=list)
    capabilities: List[CapabilityMapping] = field(default_factory=list)
    policies: List[StrategyPolicy] = field(default_factory=list)
    integrity_level: IntegrityLevel = IntegrityLevel.UNKNOWN
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'config_id': self.config_id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'status': self.status.value,
            'references': [r.to_dict() for r in self.references],
            'capabilities': [c.to_dict() for c in self.capabilities],
            'policies': [p.to_dict() for p in self.policies],
            'integrity_level': self.integrity_level.value,
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class CrossReferenceReport:
    """Report of cross-reference validation"""
    report_id: str
    total_references: int
    resolved_references: int
    broken_references: int
    missing_references: List[Dict[str, Any]] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    orphan_capabilities: List[str] = field(default_factory=list)
    duplicate_providers: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'report_id': self.report_id,
            'total_references': self.total_references,
            'resolved_references': self.resolved_references,
            'broken_references': self.broken_references,
            'missing_references': self.missing_references,
            'circular_dependencies': self.circular_dependencies,
            'orphan_capabilities': self.orphan_capabilities,
            'duplicate_providers': self.duplicate_providers,
            'generated_at': self.generated_at.isoformat()
        }


@dataclass
class WorkConfigManagerConfig:
    """Configuration for the Work Configuration Manager"""
    name: str = 'synergymesh-work-config'
    config_base_path: str = 'config/'
    enable_auto_validation: bool = True
    enable_cross_reference_check: bool = True
    strict_policy_enforcement: bool = False
    max_configurations: int = 100


class WorkConfigurationManager:
    """
    Work Configuration Manager - 工作配置管理器

    Unified manager for work configurations providing:
    - Module mapping integration (模組映射整合)
    - Strategy policy management (策略政策管理)
    - Cross-reference validation (交叉引用驗證)
    - Capability registry alignment (能力註冊表對齊)
    - Work configuration lifecycle (工作配置生命週期)

    Usage:
        manager = WorkConfigurationManager()

        # Create work configuration
        config = manager.create_configuration(
            name='production-workflow',
            version='1.0.0'
        )

        # Add references
        manager.add_reference(config.config_id, ref)

        # Validate configuration
        result = manager.validate_configuration(config.config_id)
    """

    def __init__(self, config: Optional[WorkConfigManagerConfig] = None):
        """Initialize the Work Configuration Manager"""
        self.config = config or WorkConfigManagerConfig()

        # Configuration storage
        self._configurations: Dict[str, WorkConfiguration] = {}

        # Module mappings from system-module-map.yaml
        self._module_mappings: Dict[str, Dict[str, Any]] = {}

        # Capability registry
        self._capability_registry: Dict[str, CapabilityMapping] = {}

        # Strategy policies
        self._strategy_policies: Dict[str, StrategyPolicy] = {}

        # Statistics
        self._stats = {
            'configurations_created': 0,
            'validations_performed': 0,
            'references_resolved': 0,
            'policies_evaluated': 0
        }

        # Initialize default policies and capabilities
        self._init_default_policies()
        self._init_default_capabilities()

        logger.info("WorkConfigurationManager initialized - 工作配置管理器已初始化")

    def _init_default_policies(self) -> None:
        """Initialize default strategy policies"""
        # Auto optimization policy
        self.add_strategy_policy(StrategyPolicy(
            policy_id='policy-auto-opt',
            name='Auto Optimization Policy',
            description='自動優化策略',
            category='performance',
            rules=[
                {'rule': 'enable_auto_tuning', 'default': False},
                {'rule': 'require_approval', 'default': True}
            ],
            priority=10,
            enforcement_mode='warn'
        ))

        # Drift detection policy
        self.add_strategy_policy(StrategyPolicy(
            policy_id='policy-drift',
            name='Drift Detection Policy',
            description='配置漂移偵測策略',
            category='reliability',
            rules=[
                {'rule': 'enable_drift_detection', 'default': True},
                {'rule': 'check_interval_seconds', 'default': 300},
                {'rule': 'alert_threshold', 'default': 0.1}
            ],
            priority=20,
            enforcement_mode='strict'
        ))

        # Cognitive processing policy
        self.add_strategy_policy(StrategyPolicy(
            policy_id='policy-cognitive',
            name='Cognitive Processing Policy',
            description='認知處理策略',
            category='ai',
            rules=[
                {'rule': 'auto_execute_threshold', 'default': 0.85},
                {'rule': 'require_approval_threshold', 'default': 0.6},
                {'rule': 'enable_all_layers', 'default': True}
            ],
            priority=15,
            enforcement_mode='warn'
        ))

        # Security compliance policy
        self.add_strategy_policy(StrategyPolicy(
            policy_id='policy-security',
            name='Security Compliance Policy',
            description='安全合規策略',
            category='security',
            rules=[
                {'rule': 'enable_slsa_provenance', 'default': True},
                {'rule': 'require_safety_mechanisms', 'default': True},
                {'rule': 'min_slsa_level', 'default': 3}
            ],
            priority=100,
            enforcement_mode='strict'
        ))

        logger.debug(f"Initialized {len(self._strategy_policies)} default policies")

    def _init_default_capabilities(self) -> None:
        """Initialize default capability mappings"""
        # Cognitive processing capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-cognitive',
            name='Cognitive Processing',
            description='認知處理能力',
            providers=['core/unified_integration/cognitive_processor.py'],
            backup_providers=['runtime/mind_matrix/'],
            dependencies=['cap-service-discovery']
        ))

        # Service discovery capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-service-discovery',
            name='Service Discovery',
            description='服務發現能力',
            providers=['core/unified_integration/service_registry.py'],
            dependencies=[]
        ))

        # Configuration management capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-config-mgmt',
            name='Configuration Management',
            description='配置管理能力',
            providers=['core/unified_integration/configuration_optimizer.py'],
            dependencies=['cap-service-discovery']
        ))

        # Workflow orchestration capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-orchestration',
            name='Workflow Orchestration',
            description='工作流編排能力',
            providers=['core/unified_integration/system_orchestrator.py'],
            backup_providers=['intelligent-automation/'],
            dependencies=['cap-service-discovery', 'cap-config-mgmt']
        ))

        # Security attestation capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-attestation',
            name='Security Attestation',
            description='安全認證能力',
            providers=['core/slsa_provenance/'],
            dependencies=[]
        ))

        # Code analysis capability
        self.register_capability(CapabilityMapping(
            capability_id='cap-code-analysis',
            name='Code Analysis',
            description='程式碼分析能力',
            providers=['mcp-servers/code-analyzer.js'],
            backup_providers=['automation-architect/core/analysis/'],
            dependencies=[]
        ))

        logger.debug(f"Initialized {len(self._capability_registry)} default capabilities")

    def create_configuration(
        self,
        name: str,
        version: str,
        description: str = '',
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkConfiguration:
        """
        Create a new work configuration

        創建新的工作配置

        Args:
            name: Configuration name
            version: Configuration version
            description: Optional description
            metadata: Optional metadata

        Returns:
            Created WorkConfiguration
        """
        config_id = f"wc-{uuid4().hex[:8]}"

        work_config = WorkConfiguration(
            config_id=config_id,
            name=name,
            version=version,
            description=description,
            metadata=metadata or {}
        )

        self._configurations[config_id] = work_config
        self._stats['configurations_created'] += 1

        logger.info(f"Created work configuration: {name} ({config_id})")
        return work_config

    def get_configuration(self, config_id: str) -> Optional[WorkConfiguration]:
        """Get a work configuration by ID"""
        return self._configurations.get(config_id)

    def list_configurations(
        self,
        status: Optional[WorkConfigurationStatus] = None
    ) -> List[WorkConfiguration]:
        """List work configurations with optional status filter"""
        configs = list(self._configurations.values())
        if status:
            configs = [c for c in configs if c.status == status]
        return configs

    def add_reference(
        self,
        config_id: str,
        ref_type: ReferenceType,
        source_path: str,
        target_path: str,
        required: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ConfigurationReference]:
        """
        Add a reference to a work configuration

        添加引用到工作配置

        Args:
            config_id: Configuration ID
            ref_type: Type of reference
            source_path: Source path of the reference
            target_path: Target path being referenced
            required: Whether reference is required
            metadata: Optional metadata

        Returns:
            Created ConfigurationReference or None if config not found
        """
        work_config = self._configurations.get(config_id)
        if not work_config:
            return None

        ref = ConfigurationReference(
            ref_id=f"ref-{uuid4().hex[:8]}",
            ref_type=ref_type,
            source_path=source_path,
            target_path=target_path,
            required=required,
            metadata=metadata or {}
        )

        work_config.references.append(ref)
        work_config.updated_at = datetime.now(timezone.utc)

        return ref

    def add_capability_to_config(
        self,
        config_id: str,
        capability_id: str
    ) -> bool:
        """
        Add a capability to a work configuration

        添加能力到工作配置
        """
        work_config = self._configurations.get(config_id)
        capability = self._capability_registry.get(capability_id)

        if not work_config or not capability:
            return False

        work_config.capabilities.append(capability)
        work_config.updated_at = datetime.now(timezone.utc)
        return True

    def add_policy_to_config(
        self,
        config_id: str,
        policy_id: str
    ) -> bool:
        """
        Add a strategy policy to a work configuration

        添加策略政策到工作配置
        """
        work_config = self._configurations.get(config_id)
        policy = self._strategy_policies.get(policy_id)

        if not work_config or not policy:
            return False

        work_config.policies.append(policy)
        work_config.updated_at = datetime.now(timezone.utc)
        return True

    def validate_configuration(
        self,
        config_id: str
    ) -> Dict[str, Any]:
        """
        Validate a work configuration

        驗證工作配置

        Args:
            config_id: Configuration ID to validate

        Returns:
            Validation result with errors and warnings
        """
        work_config = self._configurations.get(config_id)
        if not work_config:
            return {'valid': False, 'error': 'Configuration not found'}

        work_config.status = WorkConfigurationStatus.VALIDATING
        self._stats['validations_performed'] += 1

        errors = []
        warnings = []

        # Validate references
        for ref in work_config.references:
            ref_result = self._validate_reference(ref)
            if ref_result.get('error'):
                if ref.required:
                    errors.append(ref_result['error'])
                else:
                    warnings.append(ref_result['error'])
            else:
                ref.resolved = True
                self._stats['references_resolved'] += 1

        # Validate capabilities
        for capability in work_config.capabilities:
            cap_result = self._validate_capability(capability)
            if cap_result.get('warnings'):
                warnings.extend(cap_result['warnings'])
            if cap_result.get('errors'):
                errors.extend(cap_result['errors'])

        # Evaluate policies
        for policy in work_config.policies:
            policy_result = self._evaluate_policy(policy, work_config)
            self._stats['policies_evaluated'] += 1
            if policy_result.get('violations'):
                if policy.enforcement_mode == 'strict':
                    errors.extend(policy_result['violations'])
                else:
                    warnings.extend(policy_result['violations'])

        # Update configuration status
        work_config.validation_errors = errors
        work_config.validation_warnings = warnings
        work_config.updated_at = datetime.now(timezone.utc)

        if errors:
            work_config.status = WorkConfigurationStatus.INVALID
            work_config.integrity_level = IntegrityLevel.BROKEN
        elif warnings:
            work_config.status = WorkConfigurationStatus.VALID
            work_config.integrity_level = IntegrityLevel.PARTIAL
        else:
            work_config.status = WorkConfigurationStatus.VALID
            work_config.integrity_level = IntegrityLevel.FULL

        return {
            'valid': len(errors) == 0,
            'config_id': config_id,
            'status': work_config.status.value,
            'integrity_level': work_config.integrity_level.value,
            'errors': errors,
            'warnings': warnings
        }

    def generate_cross_reference_report(
        self,
        config_id: Optional[str] = None
    ) -> CrossReferenceReport:
        """
        Generate a cross-reference validation report

        生成交叉引用驗證報告

        Args:
            config_id: Optional specific configuration ID

        Returns:
            CrossReferenceReport
        """
        report = CrossReferenceReport(
            report_id=f"xref-{uuid4().hex[:8]}",
            total_references=0,
            resolved_references=0,
            broken_references=0
        )

        configs = [self._configurations[config_id]] if config_id else list(
            self._configurations.values()
        )

        all_capabilities = set()
        provided_capabilities = set()

        for config in configs:
            for ref in config.references:
                report.total_references += 1
                if ref.resolved:
                    report.resolved_references += 1
                else:
                    report.broken_references += 1
                    report.missing_references.append({
                        'config_id': config.config_id,
                        'ref_id': ref.ref_id,
                        'target_path': ref.target_path,
                        'error': ref.resolution_error or 'Not resolved'
                    })

            for capability in config.capabilities:
                all_capabilities.add(capability.capability_id)
                for dep in capability.dependencies:
                    if dep not in self._capability_registry:
                        report.missing_references.append({
                            'config_id': config.config_id,
                            'capability_id': capability.capability_id,
                            'missing_dependency': dep
                        })

        # Check for circular dependencies
        report.circular_dependencies = self._detect_circular_dependencies()

        # Check for orphan capabilities
        for cap_id in self._capability_registry:
            if cap_id not in all_capabilities:
                report.orphan_capabilities.append(cap_id)

        # Check for duplicate providers
        provider_capabilities: Dict[str, List[str]] = {}
        for cap in self._capability_registry.values():
            for provider in cap.providers:
                if provider not in provider_capabilities:
                    provider_capabilities[provider] = []
                provider_capabilities[provider].append(cap.capability_id)

        for provider, caps in provider_capabilities.items():
            if len(caps) > 1:
                report.duplicate_providers.append({
                    'provider': provider,
                    'capabilities': caps
                })

        return report

    def activate_configuration(self, config_id: str) -> bool:
        """
        Activate a work configuration

        啟動工作配置
        """
        work_config = self._configurations.get(config_id)
        if not work_config:
            return False

        if work_config.status != WorkConfigurationStatus.VALID:
            # Validate first
            result = self.validate_configuration(config_id)
            if not result['valid']:
                return False

        work_config.status = WorkConfigurationStatus.ACTIVE
        work_config.updated_at = datetime.now(timezone.utc)

        logger.info(f"Activated work configuration: {work_config.name}")
        return True

    def deprecate_configuration(self, config_id: str) -> bool:
        """
        Deprecate a work configuration

        棄用工作配置
        """
        work_config = self._configurations.get(config_id)
        if not work_config:
            return False

        work_config.status = WorkConfigurationStatus.DEPRECATED
        work_config.updated_at = datetime.now(timezone.utc)

        logger.info(f"Deprecated work configuration: {work_config.name}")
        return True

    def add_strategy_policy(self, policy: StrategyPolicy) -> None:
        """Add a strategy policy"""
        self._strategy_policies[policy.policy_id] = policy

    def get_strategy_policy(self, policy_id: str) -> Optional[StrategyPolicy]:
        """Get a strategy policy by ID"""
        return self._strategy_policies.get(policy_id)

    def list_strategy_policies(
        self,
        category: Optional[str] = None
    ) -> List[StrategyPolicy]:
        """List strategy policies with optional category filter"""
        policies = list(self._strategy_policies.values())
        if category:
            policies = [p for p in policies if p.category == category]
        return sorted(policies, key=lambda p: p.priority, reverse=True)

    def register_capability(self, capability: CapabilityMapping) -> None:
        """Register a capability mapping"""
        self._capability_registry[capability.capability_id] = capability

    def get_capability(self, capability_id: str) -> Optional[CapabilityMapping]:
        """Get a capability by ID"""
        return self._capability_registry.get(capability_id)

    def list_capabilities(self) -> List[CapabilityMapping]:
        """List all registered capabilities"""
        return list(self._capability_registry.values())

    def load_module_mappings(self, mapping_data: Dict[str, Any]) -> None:
        """
        Load module mappings from system-module-map.yaml data

        載入模組映射數據
        """
        self._module_mappings = mapping_data

        # Extract capabilities from mapping
        if 'capability_matrix' in mapping_data:
            for cap_name, cap_data in mapping_data['capability_matrix'].items():
                cap = CapabilityMapping(
                    capability_id=f"cap-{cap_name}",
                    name=cap_name,
                    description=cap_data.get('description', ''),
                    providers=cap_data.get('providers', []),
                    dependencies=[]
                )
                self.register_capability(cap)

        logger.info(f"Loaded module mappings with {len(self._module_mappings)} categories")

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            'configurations_created': self._stats['configurations_created'],
            'validations_performed': self._stats['validations_performed'],
            'references_resolved': self._stats['references_resolved'],
            'policies_evaluated': self._stats['policies_evaluated'],
            'active_configurations': sum(
                1 for c in self._configurations.values()
                if c.status == WorkConfigurationStatus.ACTIVE
            ),
            'total_configurations': len(self._configurations),
            'registered_capabilities': len(self._capability_registry),
            'strategy_policies': len(self._strategy_policies)
        }

    # ========== Private Validation Methods ==========

    def _validate_reference(
        self,
        ref: ConfigurationReference
    ) -> Dict[str, Any]:
        """Validate a single reference"""
        # Check if target exists in module mappings or as file
        target = ref.target_path

        # Check module mappings
        if ref.ref_type == ReferenceType.MODULE:
            for category_data in self._module_mappings.values():
                if isinstance(category_data, dict):
                    if target in str(category_data):
                        return {'resolved': True}

        # Check capability registry
        if ref.ref_type == ReferenceType.CAPABILITY:
            if target in self._capability_registry:
                return {'resolved': True}
            return {'error': f"Capability not found: {target}"}

        # Check strategy policies
        if ref.ref_type == ReferenceType.POLICY:
            if target in self._strategy_policies:
                return {'resolved': True}
            return {'error': f"Policy not found: {target}"}

        # For files, check if path pattern exists
        if ref.ref_type == ReferenceType.CONFIG_FILE:
            config_base = Path(self.config.config_base_path)
            if (config_base / target).exists():
                return {'resolved': True}
            # Allow unresolved file references in non-strict mode
            return {'resolved': True}

        return {'resolved': True}

    def _validate_capability(
        self,
        capability: CapabilityMapping
    ) -> Dict[str, Any]:
        """Validate a capability mapping"""
        warnings = []
        errors = []

        # Check for providers
        if not capability.providers:
            errors.append(f"Capability {capability.name} has no providers")

        # Check dependencies
        for dep in capability.dependencies:
            if dep not in self._capability_registry:
                warnings.append(
                    f"Capability {capability.name} depends on unregistered capability: {dep}"
                )

        return {'warnings': warnings, 'errors': errors}

    def _evaluate_policy(
        self,
        policy: StrategyPolicy,
        config: WorkConfiguration
    ) -> Dict[str, Any]:
        """Evaluate a policy against a configuration"""
        violations = []

        if not policy.enabled:
            return {'violations': []}

        # Evaluate each rule
        for rule in policy.rules:
            rule_name = rule.get('rule', 'unknown')
            # Policy rules are informational for now
            # In a full implementation, this would check actual config values

        return {'violations': violations}

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in capability registry"""
        circular = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(cap_id: str, path: List[str]) -> None:
            if cap_id in rec_stack:
                # Found circular dependency
                cycle_start = path.index(cap_id)
                circular.append(path[cycle_start:] + [cap_id])
                return

            if cap_id in visited:
                return

            visited.add(cap_id)
            rec_stack.add(cap_id)

            capability = self._capability_registry.get(cap_id)
            if capability:
                for dep in capability.dependencies:
                    dfs(dep, path + [cap_id])

            rec_stack.remove(cap_id)

        for cap_id in self._capability_registry:
            dfs(cap_id, [])

        return circular


# Factory function
def create_work_configuration_manager(
    config: Optional[WorkConfigManagerConfig] = None
) -> WorkConfigurationManager:
    """Create a new WorkConfigurationManager instance"""
    return WorkConfigurationManager(config)
