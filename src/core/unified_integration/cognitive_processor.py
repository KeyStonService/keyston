"""
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh Enhanced Cognitive Processor
                    增強認知處理器 - 智能決策與推理引擎
═══════════════════════════════════════════════════════════════════════════════

This module provides enhanced cognitive processing capabilities for the
Mind Matrix, enabling intelligent decision making, pattern recognition,
and adaptive learning.

Core Capabilities:
- Multi-layer cognitive processing (多層認知處理)
- Pattern recognition and anomaly detection (模式識別與異常偵測)
- Decision support and recommendation (決策支援與建議)
- Context-aware reasoning (上下文感知推理)
- Adaptive learning integration (自適應學習整合)

Design Principles:
- Four-layer cognitive architecture (L1-Perception, L2-Reasoning, L3-Execution, L4-Proof)
- Evidence-based decision making
- Continuous improvement through feedback
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class CognitiveLayer(Enum):
    """Cognitive processing layers"""
    L1_PERCEPTION = 'perception'      # 感知層：遙測收集、異常偵測、時序漂移識別
    L2_REASONING = 'reasoning'        # 推理層：因果圖構建、風險評分、策略選擇
    L3_EXECUTION = 'execution'        # 執行層：多代理協作、同步屏障、回滾點生成
    L4_PROOF = 'proof'                # 證明層：審計鏈固化、SLSA 證據、行為可驗證性


class SignalType(Enum):
    """Types of cognitive signals"""
    TELEMETRY = 'telemetry'
    ANOMALY = 'anomaly'
    DRIFT = 'drift'
    ALERT = 'alert'
    DECISION = 'decision'
    ACTION = 'action'
    EVIDENCE = 'evidence'


class DecisionConfidence(Enum):
    """Decision confidence levels"""
    HIGH = 'high'        # > 0.85
    MEDIUM = 'medium'    # 0.6 - 0.85
    LOW = 'low'          # 0.3 - 0.6
    UNCERTAIN = 'uncertain'  # < 0.3


class RiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    NEGLIGIBLE = 'negligible'


@dataclass
class CognitiveSignal:
    """A signal processed by the cognitive system"""
    signal_id: str
    signal_type: SignalType
    layer: CognitiveLayer
    source: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'signal_id': self.signal_id,
            'signal_type': self.signal_type.value,
            'layer': self.layer.value,
            'source': self.source,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'priority': self.priority,
            'metadata': self.metadata
        }


@dataclass
class RiskAssessment:
    """Risk assessment result"""
    risk_id: str
    level: RiskLevel
    score: float  # 0.0 - 1.0
    factors: List[Dict[str, Any]] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Decision:
    """A decision made by the cognitive system"""
    decision_id: str
    action: str
    confidence: DecisionConfidence
    confidence_score: float
    reasoning: List[str] = field(default_factory=list)
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    risk_assessment: Optional[RiskAssessment] = None
    requires_approval: bool = False
    auto_execute: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'decision_id': self.decision_id,
            'action': self.action,
            'confidence': self.confidence.value,
            'confidence_score': self.confidence_score,
            'reasoning': self.reasoning,
            'alternatives': self.alternatives,
            'risk_assessment': {
                'level': self.risk_assessment.level.value,
                'score': self.risk_assessment.score,
                'factors': self.risk_assessment.factors,
                'mitigations': self.risk_assessment.mitigations
            } if self.risk_assessment else None,
            'requires_approval': self.requires_approval,
            'auto_execute': self.auto_execute,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class CognitiveContext:
    """Context for cognitive processing"""
    context_id: str
    session_id: str
    signals: List[CognitiveSignal] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProcessorConfig:
    """Configuration for the cognitive processor"""
    name: str = 'synergymesh-cognitive'
    enable_perception: bool = True
    enable_reasoning: bool = True
    enable_execution: bool = True
    enable_proof: bool = True
    max_signal_queue: int = 1000
    processing_timeout_seconds: int = 30
    auto_decision_threshold: float = 0.85
    require_approval_threshold: float = 0.6


class PerceptionLayer:
    """
    感知層 (L1) - Perception Layer
    
    Responsibilities:
    - 遙測收集 (Telemetry collection)
    - 異常偵測 (Anomaly detection)
    - 時序漂移識別 (Time series drift detection)
    """
    
    def __init__(self):
        """Initialize perception layer"""
        self._anomaly_detectors: List[Callable] = []
        self._drift_detectors: List[Callable] = []
        self._baselines: Dict[str, Any] = {}
        
        # Statistics
        self._stats = {
            'signals_processed': 0,
            'anomalies_detected': 0,
            'drifts_detected': 0
        }
        
        logger.debug("PerceptionLayer initialized - 感知層已初始化")
    
    async def process(
        self,
        signal: CognitiveSignal,
        context: CognitiveContext
    ) -> List[CognitiveSignal]:
        """
        Process a signal through the perception layer
        
        Args:
            signal: Input signal
            context: Processing context
            
        Returns:
            List of generated signals (may include anomaly/drift signals)
        """
        self._stats['signals_processed'] += 1
        output_signals = [signal]
        
        # Anomaly detection
        anomalies = await self._detect_anomalies(signal, context)
        if anomalies:
            self._stats['anomalies_detected'] += len(anomalies)
            output_signals.extend(anomalies)
        
        # Drift detection
        drifts = await self._detect_drifts(signal, context)
        if drifts:
            self._stats['drifts_detected'] += len(drifts)
            output_signals.extend(drifts)
        
        return output_signals
    
    async def _detect_anomalies(
        self,
        signal: CognitiveSignal,
        context: CognitiveContext
    ) -> List[CognitiveSignal]:
        """Detect anomalies in the signal"""
        anomalies = []
        
        for detector in self._anomaly_detectors:
            try:
                if asyncio.iscoroutinefunction(detector):
                    result = await detector(signal, context)
                else:
                    result = detector(signal, context)
                
                if result:
                    anomaly_signal = CognitiveSignal(
                        signal_id=f"anomaly-{uuid4().hex[:8]}",
                        signal_type=SignalType.ANOMALY,
                        layer=CognitiveLayer.L1_PERCEPTION,
                        source='perception-layer',
                        payload={
                            'original_signal': signal.signal_id,
                            'anomaly_type': result.get('type', 'unknown'),
                            'severity': result.get('severity', 'medium'),
                            'details': result.get('details', {})
                        },
                        confidence=result.get('confidence', 0.7)
                    )
                    anomalies.append(anomaly_signal)
            except Exception as e:
                logger.warning(f"Anomaly detector error: {e}")
        
        return anomalies
    
    async def _detect_drifts(
        self,
        signal: CognitiveSignal,
        context: CognitiveContext
    ) -> List[CognitiveSignal]:
        """Detect drifts in the signal"""
        drifts = []
        
        for detector in self._drift_detectors:
            try:
                if asyncio.iscoroutinefunction(detector):
                    result = await detector(signal, context, self._baselines)
                else:
                    result = detector(signal, context, self._baselines)
                
                if result:
                    drift_signal = CognitiveSignal(
                        signal_id=f"drift-{uuid4().hex[:8]}",
                        signal_type=SignalType.DRIFT,
                        layer=CognitiveLayer.L1_PERCEPTION,
                        source='perception-layer',
                        payload={
                            'original_signal': signal.signal_id,
                            'drift_type': result.get('type', 'unknown'),
                            'magnitude': result.get('magnitude', 0.0),
                            'baseline': result.get('baseline'),
                            'current': result.get('current')
                        },
                        confidence=result.get('confidence', 0.6)
                    )
                    drifts.append(drift_signal)
            except Exception as e:
                logger.warning(f"Drift detector error: {e}")
        
        return drifts
    
    def add_anomaly_detector(self, detector: Callable) -> None:
        """Add an anomaly detector"""
        self._anomaly_detectors.append(detector)
    
    def add_drift_detector(self, detector: Callable) -> None:
        """Add a drift detector"""
        self._drift_detectors.append(detector)
    
    def set_baseline(self, key: str, value: Any) -> None:
        """Set a baseline value for drift detection"""
        self._baselines[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get layer statistics"""
        return self._stats.copy()


class ReasoningLayer:
    """
    推理層 (L2) - Reasoning Layer
    
    Responsibilities:
    - 因果圖構建 (Causal graph construction)
    - 風險評分 (Risk scoring)
    - 策略選擇 (Strategy selection)
    """
    
    def __init__(self):
        """Initialize reasoning layer"""
        self._strategy_evaluators: List[Callable] = []
        self._risk_factors: Dict[str, float] = {}
        self._causal_relationships: Dict[str, List[str]] = {}
        
        # Statistics
        self._stats = {
            'signals_processed': 0,
            'decisions_made': 0,
            'risk_assessments': 0
        }
        
        logger.debug("ReasoningLayer initialized - 推理層已初始化")
    
    async def process(
        self,
        signals: List[CognitiveSignal],
        context: CognitiveContext
    ) -> Tuple[List[Decision], List[CognitiveSignal]]:
        """
        Process signals through the reasoning layer
        
        Args:
            signals: Input signals from perception layer
            context: Processing context
            
        Returns:
            Tuple of (decisions, output signals)
        """
        self._stats['signals_processed'] += len(signals)
        
        decisions = []
        output_signals = []
        
        # Analyze signals and generate decisions
        for signal in signals:
            # Perform risk assessment
            risk = await self._assess_risk(signal, context)
            self._stats['risk_assessments'] += 1
            
            # Generate decision if needed
            if self._requires_decision(signal, risk):
                decision = await self._make_decision(signal, risk, context)
                decisions.append(decision)
                self._stats['decisions_made'] += 1
                
                # Generate decision signal
                decision_signal = CognitiveSignal(
                    signal_id=f"decision-{decision.decision_id}",
                    signal_type=SignalType.DECISION,
                    layer=CognitiveLayer.L2_REASONING,
                    source='reasoning-layer',
                    payload=decision.to_dict(),
                    confidence=decision.confidence_score
                )
                output_signals.append(decision_signal)
        
        return decisions, output_signals
    
    async def _assess_risk(
        self,
        signal: CognitiveSignal,
        context: CognitiveContext
    ) -> RiskAssessment:
        """Assess risk for a signal"""
        factors = []
        total_score = 0.0
        
        # Base risk from signal type
        type_risk = {
            SignalType.ANOMALY: 0.7,
            SignalType.DRIFT: 0.5,
            SignalType.ALERT: 0.8,
            SignalType.TELEMETRY: 0.1
        }
        base_score = type_risk.get(signal.signal_type, 0.3)
        factors.append({
            'name': 'signal_type',
            'score': base_score,
            'description': f'Signal type: {signal.signal_type.value}'
        })
        total_score += base_score
        
        # Confidence-based risk adjustment
        confidence_factor = 1.0 - signal.confidence * 0.3
        factors.append({
            'name': 'confidence',
            'score': confidence_factor,
            'description': f'Confidence: {signal.confidence:.2f}'
        })
        total_score *= confidence_factor
        
        # Custom risk factors
        for factor_name, factor_weight in self._risk_factors.items():
            if factor_name in signal.payload:
                factor_score = float(signal.payload[factor_name]) * factor_weight
                factors.append({
                    'name': factor_name,
                    'score': factor_score,
                    'description': f'{factor_name}: {signal.payload[factor_name]}'
                })
                total_score += factor_score
        
        # Normalize score to range [0.0, 1.0]
        factor_count = max(len(factors), 1)  # Avoid division by zero
        average_score = total_score / factor_count
        normalized_score = max(0.0, min(average_score, 1.0))  # Clamp to [0, 1]
        
        # Determine risk level
        if normalized_score >= 0.8:
            level = RiskLevel.CRITICAL
        elif normalized_score >= 0.6:
            level = RiskLevel.HIGH
        elif normalized_score >= 0.4:
            level = RiskLevel.MEDIUM
        elif normalized_score >= 0.2:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.NEGLIGIBLE
        
        # Generate mitigations
        mitigations = self._generate_mitigations(level, factors)
        
        return RiskAssessment(
            risk_id=f"risk-{uuid4().hex[:8]}",
            level=level,
            score=normalized_score,
            factors=factors,
            mitigations=mitigations
        )
    
    def _requires_decision(
        self,
        signal: CognitiveSignal,
        risk: RiskAssessment
    ) -> bool:
        """Determine if a decision is required"""
        # Require decision for anomalies, alerts, and high-risk signals
        if signal.signal_type in [SignalType.ANOMALY, SignalType.ALERT]:
            return True
        if risk.level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return True
        return False
    
    async def _make_decision(
        self,
        signal: CognitiveSignal,
        risk: RiskAssessment,
        context: CognitiveContext
    ) -> Decision:
        """Make a decision based on signal and risk assessment"""
        # Gather reasoning
        reasoning = []
        reasoning.append(f"Signal type: {signal.signal_type.value}")
        reasoning.append(f"Risk level: {risk.level.value} (score: {risk.score:.2f})")
        
        # Evaluate strategies
        best_action = 'monitor'
        confidence_score = 0.5
        alternatives = []
        
        for evaluator in self._strategy_evaluators:
            try:
                if asyncio.iscoroutinefunction(evaluator):
                    result = await evaluator(signal, risk, context)
                else:
                    result = evaluator(signal, risk, context)
                
                if result and result.get('score', 0) > confidence_score:
                    alternatives.append({
                        'action': best_action,
                        'score': confidence_score
                    })
                    best_action = result.get('action', 'monitor')
                    confidence_score = result.get('score', 0.5)
                    reasoning.extend(result.get('reasoning', []))
            except Exception as e:
                logger.warning(f"Strategy evaluator error: {e}")
        
        # Default action based on risk level if no evaluators matched
        if confidence_score < 0.5:
            if risk.level == RiskLevel.CRITICAL:
                best_action = 'escalate_and_mitigate'
                confidence_score = 0.75
                reasoning.append("Critical risk requires immediate escalation")
            elif risk.level == RiskLevel.HIGH:
                best_action = 'alert_and_monitor'
                confidence_score = 0.7
                reasoning.append("High risk requires alerting")
            elif risk.level == RiskLevel.MEDIUM:
                best_action = 'investigate'
                confidence_score = 0.6
                reasoning.append("Medium risk requires investigation")
        
        # Determine confidence level
        if confidence_score >= 0.85:
            confidence = DecisionConfidence.HIGH
        elif confidence_score >= 0.6:
            confidence = DecisionConfidence.MEDIUM
        elif confidence_score >= 0.3:
            confidence = DecisionConfidence.LOW
        else:
            confidence = DecisionConfidence.UNCERTAIN
        
        # Determine if approval is required
        requires_approval = (
            risk.level in [RiskLevel.CRITICAL, RiskLevel.HIGH] or
            confidence == DecisionConfidence.LOW or
            confidence == DecisionConfidence.UNCERTAIN
        )
        
        return Decision(
            decision_id=f"dec-{uuid4().hex[:8]}",
            action=best_action,
            confidence=confidence,
            confidence_score=confidence_score,
            reasoning=reasoning,
            alternatives=alternatives,
            risk_assessment=risk,
            requires_approval=requires_approval,
            auto_execute=not requires_approval and confidence_score >= 0.85
        )
    
    def _generate_mitigations(
        self,
        level: RiskLevel,
        factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate mitigation recommendations"""
        mitigations = []
        
        if level == RiskLevel.CRITICAL:
            mitigations.extend([
                "Immediate escalation to on-call team",
                "Enable emergency response procedures",
                "Isolate affected components if possible"
            ])
        elif level == RiskLevel.HIGH:
            mitigations.extend([
                "Alert relevant stakeholders",
                "Increase monitoring frequency",
                "Prepare rollback procedures"
            ])
        elif level == RiskLevel.MEDIUM:
            mitigations.extend([
                "Schedule investigation within 24 hours",
                "Review related system logs"
            ])
        
        return mitigations
    
    def add_strategy_evaluator(self, evaluator: Callable) -> None:
        """Add a strategy evaluator"""
        self._strategy_evaluators.append(evaluator)
    
    def set_risk_factor(self, name: str, weight: float) -> None:
        """Set a risk factor weight"""
        self._risk_factors[name] = weight
    
    def add_causal_relationship(self, cause: str, effects: List[str]) -> None:
        """Add a causal relationship"""
        self._causal_relationships[cause] = effects
    
    def get_stats(self) -> Dict[str, Any]:
        """Get layer statistics"""
        return self._stats.copy()


class ExecutionLayer:
    """
    執行層 (L3) - Execution Layer
    
    Responsibilities:
    - 多代理協作 (Multi-agent coordination)
    - 同步屏障 (Synchronization barriers)
    - 回滾點生成 (Rollback point generation)
    """
    
    def __init__(self):
        """Initialize execution layer"""
        self._action_handlers: Dict[str, Callable] = {}
        self._rollback_handlers: Dict[str, Callable] = {}
        self._rollback_points: List[Dict[str, Any]] = []
        
        # Statistics
        self._stats = {
            'actions_executed': 0,
            'rollbacks_performed': 0,
            'rollback_points_created': 0
        }
        
        logger.debug("ExecutionLayer initialized - 執行層已初始化")
    
    async def execute(
        self,
        decisions: List[Decision],
        context: CognitiveContext
    ) -> List[CognitiveSignal]:
        """
        Execute decisions through the execution layer
        
        Args:
            decisions: Decisions to execute
            context: Processing context
            
        Returns:
            List of action signals
        """
        action_signals = []
        
        for decision in decisions:
            if not decision.auto_execute:
                # Skip decisions requiring approval
                logger.info(f"Decision {decision.decision_id} requires approval, skipping auto-execute")
                continue
            
            # Create rollback point
            rollback_point = await self._create_rollback_point(decision, context)
            self._stats['rollback_points_created'] += 1
            
            # Execute action
            try:
                result = await self._execute_action(decision, context)
                self._stats['actions_executed'] += 1
                
                # Generate action signal
                action_signal = CognitiveSignal(
                    signal_id=f"action-{uuid4().hex[:8]}",
                    signal_type=SignalType.ACTION,
                    layer=CognitiveLayer.L3_EXECUTION,
                    source='execution-layer',
                    payload={
                        'decision_id': decision.decision_id,
                        'action': decision.action,
                        'result': result,
                        'rollback_point_id': rollback_point['id']
                    },
                    confidence=1.0 if result.get('success', False) else 0.5
                )
                action_signals.append(action_signal)
                
            except Exception as e:
                logger.error(f"Action execution failed: {e}")
                
                # Attempt rollback
                if rollback_point:
                    await self._rollback(rollback_point)
                    self._stats['rollbacks_performed'] += 1
        
        return action_signals
    
    async def _create_rollback_point(
        self,
        decision: Decision,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Create a rollback point before executing action"""
        rollback_point = {
            'id': f"rbp-{uuid4().hex[:8]}",
            'decision_id': decision.decision_id,
            'action': decision.action,
            'state_snapshot': context.state.copy(),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        self._rollback_points.append(rollback_point)
        
        # Keep only last 100 rollback points
        if len(self._rollback_points) > 100:
            self._rollback_points = self._rollback_points[-100:]
        
        return rollback_point
    
    async def _execute_action(
        self,
        decision: Decision,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Execute an action"""
        handler = self._action_handlers.get(decision.action)
        
        if handler:
            if asyncio.iscoroutinefunction(handler):
                return await handler(decision, context)
            else:
                return handler(decision, context)
        else:
            # Default handler - log and return success
            logger.info(f"Executing action: {decision.action} (no custom handler)")
            return {'success': True, 'message': f'Action {decision.action} logged'}
    
    async def _rollback(self, rollback_point: Dict[str, Any]) -> bool:
        """Rollback to a previous point"""
        action = rollback_point.get('action')
        handler = self._rollback_handlers.get(action)
        
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(rollback_point)
                else:
                    handler(rollback_point)
                logger.info(f"Rollback completed for {rollback_point['id']}")
                return True
            except Exception as e:
                logger.error(f"Rollback failed: {e}")
                return False
        else:
            logger.warning(f"No rollback handler for action: {action}")
            return False
    
    def register_action_handler(self, action: str, handler: Callable) -> None:
        """Register an action handler"""
        self._action_handlers[action] = handler
    
    def register_rollback_handler(self, action: str, handler: Callable) -> None:
        """Register a rollback handler"""
        self._rollback_handlers[action] = handler
    
    def get_rollback_points(self) -> List[Dict[str, Any]]:
        """Get all rollback points"""
        return self._rollback_points.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get layer statistics"""
        return self._stats.copy()


class ProofLayer:
    """
    證明層 (L4) - Proof Layer
    
    Responsibilities:
    - 審計鏈固化 (Audit chain immutability)
    - SLSA 證據 (SLSA evidence generation)
    - 行為可驗證性 (Behavior verifiability)
    """
    
    def __init__(self):
        """Initialize proof layer"""
        self._audit_chain: List[Dict[str, Any]] = []
        self._evidence_generators: List[Callable] = []
        
        # Statistics
        self._stats = {
            'evidence_generated': 0,
            'audit_entries': 0,
            'verifications': 0
        }
        
        logger.debug("ProofLayer initialized - 證明層已初始化")
    
    async def generate_evidence(
        self,
        signals: List[CognitiveSignal],
        decisions: List[Decision],
        context: CognitiveContext
    ) -> List[CognitiveSignal]:
        """
        Generate evidence for the cognitive processing
        
        Args:
            signals: Processed signals
            decisions: Decisions made
            context: Processing context
            
        Returns:
            List of evidence signals
        """
        evidence_signals = []
        
        # Create audit entry
        audit_entry = {
            'entry_id': f"audit-{uuid4().hex[:8]}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'signals_count': len(signals),
            'decisions_count': len(decisions),
            'context_id': context.context_id,
            'session_id': context.session_id,
            'signal_ids': [s.signal_id for s in signals],
            'decision_ids': [d.decision_id for d in decisions]
        }
        
        self._audit_chain.append(audit_entry)
        self._stats['audit_entries'] += 1
        
        # Generate evidence for each decision
        for decision in decisions:
            evidence = await self._generate_decision_evidence(decision, context)
            self._stats['evidence_generated'] += 1
            
            evidence_signal = CognitiveSignal(
                signal_id=f"evidence-{uuid4().hex[:8]}",
                signal_type=SignalType.EVIDENCE,
                layer=CognitiveLayer.L4_PROOF,
                source='proof-layer',
                payload=evidence,
                confidence=1.0
            )
            evidence_signals.append(evidence_signal)
        
        # Run custom evidence generators
        for generator in self._evidence_generators:
            try:
                if asyncio.iscoroutinefunction(generator):
                    custom_evidence = await generator(signals, decisions, context)
                else:
                    custom_evidence = generator(signals, decisions, context)
                
                if custom_evidence:
                    evidence_signal = CognitiveSignal(
                        signal_id=f"evidence-{uuid4().hex[:8]}",
                        signal_type=SignalType.EVIDENCE,
                        layer=CognitiveLayer.L4_PROOF,
                        source='proof-layer-custom',
                        payload=custom_evidence,
                        confidence=1.0
                    )
                    evidence_signals.append(evidence_signal)
                    self._stats['evidence_generated'] += 1
            except Exception as e:
                logger.warning(f"Evidence generator error: {e}")
        
        return evidence_signals
    
    async def _generate_decision_evidence(
        self,
        decision: Decision,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Generate evidence for a decision"""
        return {
            'evidence_type': 'decision',
            'decision_id': decision.decision_id,
            'action': decision.action,
            'confidence_score': decision.confidence_score,
            'reasoning': decision.reasoning,
            'risk_level': decision.risk_assessment.level.value if decision.risk_assessment else None,
            'risk_score': decision.risk_assessment.score if decision.risk_assessment else None,
            'requires_approval': decision.requires_approval,
            'auto_execute': decision.auto_execute,
            'context_id': context.context_id,
            'session_id': context.session_id,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    async def verify_decision(
        self,
        decision_id: str
    ) -> Dict[str, Any]:
        """Verify a decision through the audit chain"""
        self._stats['verifications'] += 1
        
        # Find audit entry containing the decision
        for entry in self._audit_chain:
            if decision_id in entry.get('decision_ids', []):
                return {
                    'verified': True,
                    'decision_id': decision_id,
                    'audit_entry_id': entry['entry_id'],
                    'timestamp': entry['timestamp']
                }
        
        return {
            'verified': False,
            'decision_id': decision_id,
            'reason': 'Decision not found in audit chain'
        }
    
    def add_evidence_generator(self, generator: Callable) -> None:
        """Add a custom evidence generator"""
        self._evidence_generators.append(generator)
    
    def get_audit_chain(self) -> List[Dict[str, Any]]:
        """Get the audit chain"""
        return self._audit_chain.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get layer statistics"""
        return self._stats.copy()


class EnhancedCognitiveProcessor:
    """
    增強認知處理器 - Enhanced Cognitive Processor
    
    Central processor integrating all four cognitive layers:
    - L1 Perception: Signal analysis and anomaly detection
    - L2 Reasoning: Risk assessment and decision making
    - L3 Execution: Action execution with rollback support
    - L4 Proof: Evidence generation and audit trail
    
    Usage:
        processor = EnhancedCognitiveProcessor()
        await processor.start()
        
        # Process a signal
        result = await processor.process_signal(signal)
        
        # Get processing statistics
        stats = processor.get_stats()
    """
    
    def __init__(self, config: Optional[ProcessorConfig] = None):
        """Initialize the cognitive processor"""
        self.config = config or ProcessorConfig()
        
        # Initialize layers
        self.perception = PerceptionLayer()
        self.reasoning = ReasoningLayer()
        self.execution = ExecutionLayer()
        self.proof = ProofLayer()
        
        # Processing state
        self._is_running = False
        self._signal_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.max_signal_queue)
        self._processor_task: Optional[asyncio.Task] = None
        
        # Contexts
        self._contexts: Dict[str, CognitiveContext] = {}
        
        # Statistics
        self._stats = {
            'signals_received': 0,
            'signals_processed': 0,
            'processing_errors': 0
        }
        
        logger.info("EnhancedCognitiveProcessor initialized - 增強認知處理器已初始化")
    
    async def start(self) -> None:
        """Start the cognitive processor"""
        if self._is_running:
            return
        
        self._is_running = True
        self._processor_task = asyncio.create_task(self._processing_loop())
        
        logger.info("EnhancedCognitiveProcessor started - 增強認知處理器已啟動")
    
    async def stop(self) -> None:
        """Stop the cognitive processor"""
        self._is_running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("EnhancedCognitiveProcessor stopped - 增強認知處理器已停止")
    
    async def process_signal(
        self,
        signal: CognitiveSignal,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a signal through all cognitive layers
        
        處理信號通過所有認知層
        
        Args:
            signal: Signal to process
            session_id: Optional session ID for context tracking
            
        Returns:
            Processing result
        """
        self._stats['signals_received'] += 1
        
        # Get or create context
        session_id = session_id or str(uuid4())
        context = self._get_or_create_context(session_id)
        context.signals.append(signal)
        
        try:
            result = await self._process_through_layers(signal, context)
            self._stats['signals_processed'] += 1
            return result
        except Exception as e:
            self._stats['processing_errors'] += 1
            logger.error(f"Signal processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal_id': signal.signal_id
            }
    
    async def submit_signal(self, signal: CognitiveSignal) -> bool:
        """Submit a signal for asynchronous processing"""
        try:
            await self._signal_queue.put(signal)
            return True
        except asyncio.QueueFull:
            logger.warning("Signal queue full, signal dropped")
            return False
    
    async def _process_through_layers(
        self,
        signal: CognitiveSignal,
        context: CognitiveContext
    ) -> Dict[str, Any]:
        """Process signal through all enabled layers"""
        result = {
            'signal_id': signal.signal_id,
            'success': True,
            'layers_processed': [],
            'signals': [],
            'decisions': [],
            'evidence': []
        }
        
        # L1: Perception
        if self.config.enable_perception:
            perception_signals = await self.perception.process(signal, context)
            result['layers_processed'].append('perception')
            result['signals'].extend([s.to_dict() for s in perception_signals])
        else:
            perception_signals = [signal]
        
        # L2: Reasoning
        if self.config.enable_reasoning:
            decisions, reasoning_signals = await self.reasoning.process(perception_signals, context)
            result['layers_processed'].append('reasoning')
            result['decisions'].extend([d.to_dict() for d in decisions])
            result['signals'].extend([s.to_dict() for s in reasoning_signals])
            context.decisions.extend(decisions)
        else:
            decisions = []
            reasoning_signals = []
        
        # L3: Execution
        if self.config.enable_execution and decisions:
            action_signals = await self.execution.execute(decisions, context)
            result['layers_processed'].append('execution')
            result['signals'].extend([s.to_dict() for s in action_signals])
        else:
            action_signals = []
        
        # L4: Proof
        if self.config.enable_proof:
            all_signals = perception_signals + reasoning_signals + action_signals
            evidence_signals = await self.proof.generate_evidence(
                all_signals, decisions, context
            )
            result['layers_processed'].append('proof')
            result['evidence'].extend([s.to_dict() for s in evidence_signals])
        
        # Update context history
        context.history.append({
            'signal_id': signal.signal_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'decisions_made': len(decisions)
        })
        
        return result
    
    async def _processing_loop(self) -> None:
        """Background processing loop"""
        while self._is_running:
            try:
                signal = await asyncio.wait_for(
                    self._signal_queue.get(),
                    timeout=1.0
                )
                await self.process_signal(signal)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
    
    def _get_or_create_context(self, session_id: str) -> CognitiveContext:
        """Get or create a processing context"""
        if session_id not in self._contexts:
            self._contexts[session_id] = CognitiveContext(
                context_id=f"ctx-{uuid4().hex[:8]}",
                session_id=session_id
            )
        return self._contexts[session_id]
    
    def get_context(self, session_id: str) -> Optional[CognitiveContext]:
        """Get a processing context"""
        return self._contexts.get(session_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        return {
            'processor': self._stats.copy(),
            'perception': self.perception.get_stats(),
            'reasoning': self.reasoning.get_stats(),
            'execution': self.execution.get_stats(),
            'proof': self.proof.get_stats(),
            'is_running': self._is_running,
            'queue_size': self._signal_queue.qsize(),
            'active_contexts': len(self._contexts)
        }


# Factory function
def create_cognitive_processor(
    config: Optional[ProcessorConfig] = None
) -> EnhancedCognitiveProcessor:
    """Create a new EnhancedCognitiveProcessor instance"""
    return EnhancedCognitiveProcessor(config)
