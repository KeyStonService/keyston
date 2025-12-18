"""
Unified System Controller - Central orchestration for all SynergyMesh phases

This module provides the central controller that unifies all 22 phases of
the SynergyMesh system into a cohesive operational framework.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System operational states"""
    OFFLINE = 'offline'
    INITIALIZING = 'initializing'
    READY = 'ready'
    RUNNING = 'running'
    DEGRADED = 'degraded'
    MAINTENANCE = 'maintenance'
    SHUTTING_DOWN = 'shutting_down'
    ERROR = 'error'


class PhaseCategory(Enum):
    """Phase categories for grouping"""
    CORE_COORDINATION = 'core_coordination'       # Phases 1-2
    AI_DECISION = 'ai_decision'                   # Phases 3-6
    KNOWLEDGE_TRAINING = 'knowledge_training'     # Phase 7
    EXECUTION = 'execution'                       # Phases 8-9
    SAFETY_MONITORING = 'safety_monitoring'       # Phases 10-12
    YAML_VALIDATION = 'yaml_validation'           # Phase 13
    ADVANCED_ARCHITECTURE = 'advanced_architecture'  # Phases 14-18
    MCP_SERVERS = 'mcp_servers'                   # Phase 19
    SLSA_PROVENANCE = 'slsa_provenance'          # Phase 20
    CLOUD_DELEGATION = 'cloud_delegation'         # Phase 21
    UNIFIED_INTEGRATION = 'unified_integration'   # Phase 22


@dataclass
class PhaseDefinition:
    """Definition of a system phase"""
    id: int
    name: str
    description: str
    category: PhaseCategory
    module_path: str
    dependencies: List[int] = field(default_factory=list)
    enabled: bool = True
    critical: bool = False  # If True, system cannot run without this phase


@dataclass
class PhaseState:
    """Runtime state of a phase"""
    phase_id: int
    status: str = 'not_initialized'
    initialized_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    error_count: int = 0
    request_count: int = 0
    health_score: float = 100.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    uptime_seconds: float = 0.0
    phases_healthy: int = 0
    phases_degraded: int = 0
    phases_unhealthy: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class UnifiedSystemController:
    """
    Unified System Controller - 統一系統控制器
    
    Central orchestration layer that:
    - Manages all 22 phases as a unified system
    - Provides cross-phase communication
    - Handles system-wide health monitoring
    - Coordinates graceful startup and shutdown
    - Routes requests to appropriate phases
    """
    
    # Phase definitions for all 22 phases
    PHASE_DEFINITIONS = [
        PhaseDefinition(1, "Core Autonomous Coordination", "自主協調核心", 
                       PhaseCategory.CORE_COORDINATION, "core.main_system", critical=True),
        PhaseDefinition(2, "Advanced Interaction & Orchestration", "進階互動與編排",
                       PhaseCategory.CORE_COORDINATION, "core.main_system", dependencies=[1]),
        PhaseDefinition(3, "AI Decision Engine", "AI決策引擎",
                       PhaseCategory.AI_DECISION, "core.ai_decision_engine", dependencies=[1, 2]),
        PhaseDefinition(4, "Autonomous Trust & Governance", "自主信任與治理",
                       PhaseCategory.AI_DECISION, "core.autonomous_trust_engine", dependencies=[3]),
        PhaseDefinition(5, "AI Quality & Bug Prevention", "AI品質與漏洞預防",
                       PhaseCategory.AI_DECISION, "core.auto_bug_detector", dependencies=[3, 4]),
        PhaseDefinition(6, "AI Supreme Directive Constitution", "AI最高指令憲法",
                       PhaseCategory.AI_DECISION, "core.ai_constitution", dependencies=[4], critical=True),
        PhaseDefinition(7, "Knowledge & Skills Training", "知識與技能訓練",
                       PhaseCategory.KNOWLEDGE_TRAINING, "core.training_system", dependencies=[1, 3]),
        PhaseDefinition(8, "Execution Engine & Tech Stack", "執行引擎與技術棧",
                       PhaseCategory.EXECUTION, "core.execution_engine", dependencies=[1, 6]),
        PhaseDefinition(9, "Complete Execution Architecture", "完整執行架構",
                       PhaseCategory.EXECUTION, "core.execution_architecture", dependencies=[8]),
        PhaseDefinition(10, "Safety Mechanisms", "安全機制",
                        PhaseCategory.SAFETY_MONITORING, "core.safety_mechanisms", dependencies=[6], critical=True),
        PhaseDefinition(11, "Intelligent Monitoring & Remediation", "智能監控與修復",
                        PhaseCategory.SAFETY_MONITORING, "core.monitoring_system", dependencies=[10]),
        PhaseDefinition(12, "CI Error Auto-Handler", "CI錯誤自動處理",
                        PhaseCategory.SAFETY_MONITORING, "core.ci_error_handler", dependencies=[11]),
        PhaseDefinition(13, "Deep Verifiable YAML System", "深度可驗證YAML系統",
                        PhaseCategory.YAML_VALIDATION, "core.yaml_module_system", dependencies=[6]),
        PhaseDefinition(14, "Advanced System Architecture", "進階系統架構",
                        PhaseCategory.ADVANCED_ARCHITECTURE, "advanced-architecture", dependencies=[9]),
        PhaseDefinition(15, "Intelligent Automation", "智能自動化",
                        PhaseCategory.ADVANCED_ARCHITECTURE, "intelligent-automation", dependencies=[14]),
        PhaseDefinition(16, "Autonomous System", "自主系統",
                        PhaseCategory.ADVANCED_ARCHITECTURE, "autonomous-system", dependencies=[15]),
        PhaseDefinition(17, "Intelligent Hyperautomation", "智能超自動化",
                        PhaseCategory.ADVANCED_ARCHITECTURE, "intelligent-hyperautomation", dependencies=[16]),
        PhaseDefinition(18, "Automation Architect", "自動化架構師",
                        PhaseCategory.ADVANCED_ARCHITECTURE, "automation-architect", dependencies=[17]),
        PhaseDefinition(19, "MCP Servers Enhanced", "增強型MCP服務器",
                        PhaseCategory.MCP_SERVERS, "core.mcp_servers_enhanced", dependencies=[9]),
        PhaseDefinition(20, "SLSA L3 Provenance System", "SLSA L3來源追溯系統",
                        PhaseCategory.SLSA_PROVENANCE, "core.slsa_provenance", dependencies=[13]),
        PhaseDefinition(21, "Cloud Agent Delegation", "雲端代理委派系統",
                        PhaseCategory.CLOUD_DELEGATION, "core.cloud_agent_delegation", dependencies=[19]),
        PhaseDefinition(22, "Unified System Integration", "統一系統整合",
                        PhaseCategory.UNIFIED_INTEGRATION, "core.unified_integration", 
                        dependencies=list(range(1, 22)), critical=True),
    ]
    
    def __init__(self):
        """Initialize the unified system controller"""
        self._state = SystemState.OFFLINE
        self._phases: Dict[int, PhaseState] = {}
        self._phase_instances: Dict[int, Any] = {}
        self._metrics = SystemMetrics()
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._startup_time: Optional[datetime] = None
        self._is_running = False
        
        # Initialize phase states
        for phase_def in self.PHASE_DEFINITIONS:
            self._phases[phase_def.id] = PhaseState(phase_id=phase_def.id)
            
    async def initialize(self) -> bool:
        """
        Initialize all phases in dependency order
        
        Returns:
            True if initialization successful
        """
        if self._state != SystemState.OFFLINE:
            logger.warning("System already initialized or running")
            return False
            
        self._state = SystemState.INITIALIZING
        logger.info("Initializing SynergyMesh Unified System...")
        
        try:
            # Initialize phases in dependency order
            initialization_order = self._compute_initialization_order()
            
            for phase_id in initialization_order:
                phase_def = self._get_phase_definition(phase_id)
                if not phase_def or not phase_def.enabled:
                    continue
                    
                success = await self._initialize_phase(phase_id)
                if not success and phase_def.critical:
                    logger.error(f"Critical phase {phase_id} failed to initialize")
                    self._state = SystemState.ERROR
                    return False
                    
            self._state = SystemState.READY
            self._startup_time = datetime.now(timezone.utc)
            await self._emit_event('system_initialized', {'timestamp': self._startup_time})
            logger.info("SynergyMesh Unified System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self._state = SystemState.ERROR
            return False
            
    async def start(self) -> bool:
        """Start the unified system"""
        if self._state not in (SystemState.READY, SystemState.MAINTENANCE):
            logger.error(f"Cannot start system in state: {self._state}")
            return False
            
        logger.info("Starting SynergyMesh Unified System...")
        
        try:
            # Start all phases
            for phase_id in self._phases:
                phase_state = self._phases[phase_id]
                if phase_state.status == 'initialized':
                    phase_state.status = 'running'
                    phase_state.last_activity = datetime.now(timezone.utc)
                    
            self._state = SystemState.RUNNING
            self._is_running = True
            await self._emit_event('system_started', {'timestamp': datetime.now(timezone.utc)})
            logger.info("SynergyMesh Unified System started")
            return True
            
        except Exception as e:
            logger.error(f"System start failed: {e}")
            self._state = SystemState.ERROR
            return False
            
    async def stop(self) -> bool:
        """Stop the unified system gracefully"""
        if self._state != SystemState.RUNNING:
            logger.warning("System not running")
            return True
            
        self._state = SystemState.SHUTTING_DOWN
        logger.info("Stopping SynergyMesh Unified System...")
        
        try:
            # Stop phases in reverse dependency order
            initialization_order = self._compute_initialization_order()
            
            for phase_id in reversed(initialization_order):
                await self._stop_phase(phase_id)
                
            self._state = SystemState.OFFLINE
            self._is_running = False
            await self._emit_event('system_stopped', {'timestamp': datetime.now(timezone.utc)})
            logger.info("SynergyMesh Unified System stopped")
            return True
            
        except Exception as e:
            logger.error(f"System stop failed: {e}")
            return False
            
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request through the unified system
        
        Args:
            request: Request with type and parameters
            
        Returns:
            Processing result
        """
        if self._state != SystemState.RUNNING:
            return {'success': False, 'error': 'System not running'}
            
        request_id = str(uuid4())
        request_type = request.get('type', 'unknown')
        start_time = datetime.now(timezone.utc)
        
        self._metrics.total_requests += 1
        
        try:
            # Route request to appropriate phases
            phases_to_invoke = self._route_request(request_type)
            
            results = {}
            for phase_id in phases_to_invoke:
                phase_result = await self._invoke_phase(phase_id, request)
                results[f'phase_{phase_id}'] = phase_result
                
                # Update phase metrics
                phase_state = self._phases.get(phase_id)
                if phase_state:
                    phase_state.request_count += 1
                    phase_state.last_activity = datetime.now(timezone.utc)
                    
            end_time = datetime.now(timezone.utc)
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            self._metrics.successful_requests += 1
            self._update_average_latency(duration_ms)
            
            return {
                'success': True,
                'request_id': request_id,
                'request_type': request_type,
                'phases_invoked': phases_to_invoke,
                'results': results,
                'duration_ms': duration_ms
            }
            
        except Exception as e:
            self._metrics.failed_requests += 1
            logger.error(f"Request processing failed: {e}")
            return {
                'success': False,
                'request_id': request_id,
                'error': str(e)
            }
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        phase_statuses = {}
        for phase_id, phase_state in self._phases.items():
            phase_def = self._get_phase_definition(phase_id)
            phase_statuses[phase_id] = {
                'name': phase_def.name if phase_def else 'Unknown',
                'category': phase_def.category.value if phase_def else 'unknown',
                'status': phase_state.status,
                'health_score': phase_state.health_score,
                'request_count': phase_state.request_count,
                'error_count': phase_state.error_count,
                'last_activity': phase_state.last_activity.isoformat() if phase_state.last_activity else None
            }
            
        uptime = 0.0
        if self._startup_time:
            uptime = (datetime.now(timezone.utc) - self._startup_time).total_seconds()
            
        return {
            'state': self._state.value,
            'uptime_seconds': uptime,
            'phases': phase_statuses,
            'metrics': {
                'total_requests': self._metrics.total_requests,
                'successful_requests': self._metrics.successful_requests,
                'failed_requests': self._metrics.failed_requests,
                'success_rate': self._metrics.successful_requests / max(self._metrics.total_requests, 1),
                'average_latency_ms': self._metrics.average_latency_ms
            },
            'health': self._compute_system_health()
        }
        
    def get_phase_status(self, phase_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific phase"""
        phase_state = self._phases.get(phase_id)
        phase_def = self._get_phase_definition(phase_id)
        
        if not phase_state or not phase_def:
            return None
            
        return {
            'id': phase_id,
            'name': phase_def.name,
            'description': phase_def.description,
            'category': phase_def.category.value,
            'status': phase_state.status,
            'health_score': phase_state.health_score,
            'request_count': phase_state.request_count,
            'error_count': phase_state.error_count,
            'initialized_at': phase_state.initialized_at.isoformat() if phase_state.initialized_at else None,
            'last_activity': phase_state.last_activity.isoformat() if phase_state.last_activity else None,
            'dependencies': phase_def.dependencies,
            'critical': phase_def.critical
        }
        
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    async def _initialize_phase(self, phase_id: int) -> bool:
        """Initialize a specific phase"""
        phase_state = self._phases.get(phase_id)
        phase_def = self._get_phase_definition(phase_id)
        
        if not phase_state or not phase_def:
            return False
            
        logger.info(f"Initializing phase {phase_id}: {phase_def.name}")
        
        try:
            # Simulated initialization - in production, would load actual module
            await asyncio.sleep(0.01)  # Simulate initialization time
            
            phase_state.status = 'initialized'
            phase_state.initialized_at = datetime.now(timezone.utc)
            phase_state.health_score = 100.0
            
            logger.info(f"Phase {phase_id} initialized successfully")
            return True
            
        except Exception as e:
            phase_state.status = 'error'
            phase_state.error_count += 1
            logger.error(f"Failed to initialize phase {phase_id}: {e}")
            return False
            
    async def _stop_phase(self, phase_id: int) -> bool:
        """Stop a specific phase"""
        phase_state = self._phases.get(phase_id)
        if not phase_state:
            return False
            
        phase_state.status = 'stopped'
        phase_state.last_activity = datetime.now(timezone.utc)
        return True
        
    async def _invoke_phase(self, phase_id: int, request: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a phase to process a request"""
        phase_state = self._phases.get(phase_id)
        phase_def = self._get_phase_definition(phase_id)
        
        if not phase_state or phase_state.status != 'running':
            return {'success': False, 'error': f'Phase {phase_id} not running'}
            
        # Simulated phase invocation
        await asyncio.sleep(0.005)  # Simulate processing time
        
        return {
            'success': True,
            'phase_id': phase_id,
            'phase_name': phase_def.name if phase_def else 'Unknown',
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
    def _route_request(self, request_type: str) -> List[int]:
        """Route a request to appropriate phases based on type"""
        routing_map = {
            'natural_language': [1, 2],
            'decision': [3, 4],
            'quality_check': [5, 6],
            'training': [7],
            'execution': [8, 9],
            'safety_check': [10],
            'monitoring': [11],
            'ci_error': [12],
            'yaml_validation': [13],
            'automation': [14, 15, 16, 17, 18],
            'mcp_tool': [19],
            'provenance': [20],
            'cloud_delegation': [21],
            'system_status': [22],
        }
        
        return routing_map.get(request_type, [1])  # Default to phase 1
        
    def _compute_initialization_order(self) -> List[int]:
        """Compute initialization order based on dependencies"""
        visited = set()
        order = []
        
        def visit(phase_id: int):
            if phase_id in visited:
                return
            visited.add(phase_id)
            
            phase_def = self._get_phase_definition(phase_id)
            if phase_def:
                for dep_id in phase_def.dependencies:
                    visit(dep_id)
                order.append(phase_id)
                
        for phase_def in self.PHASE_DEFINITIONS:
            visit(phase_def.id)
            
        return order
        
    def _get_phase_definition(self, phase_id: int) -> Optional[PhaseDefinition]:
        """Get phase definition by ID"""
        for phase_def in self.PHASE_DEFINITIONS:
            if phase_def.id == phase_id:
                return phase_def
        return None
        
    def _compute_system_health(self) -> Dict[str, Any]:
        """Compute overall system health"""
        healthy = 0
        degraded = 0
        unhealthy = 0
        
        for phase_state in self._phases.values():
            if phase_state.status == 'running' and phase_state.health_score >= 80:
                healthy += 1
            elif phase_state.status in ('initialized', 'running') and phase_state.health_score >= 50:
                degraded += 1
            else:
                unhealthy += 1
                
        total = len(self._phases)
        overall_score = (healthy * 100 + degraded * 50) / max(total, 1)
        
        if unhealthy > 0:
            status = 'unhealthy'
        elif degraded > 0:
            status = 'degraded'
        else:
            status = 'healthy'
            
        return {
            'status': status,
            'score': overall_score,
            'phases_healthy': healthy,
            'phases_degraded': degraded,
            'phases_unhealthy': unhealthy,
            'total_phases': total
        }
        
    def _update_average_latency(self, new_latency: float) -> None:
        """Update running average latency"""
        count = self._metrics.successful_requests
        if count == 1:
            self._metrics.average_latency_ms = new_latency
        else:
            # Running average
            self._metrics.average_latency_ms = (
                (self._metrics.average_latency_ms * (count - 1) + new_latency) / count
            )
            
    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Event handler error for {event}: {e}")


# Factory function
def create_unified_controller() -> UnifiedSystemController:
    """Create a new UnifiedSystemController instance"""
    return UnifiedSystemController()
