"""
AI Decision Engine - AI 決策引擎
Phase 3: Core Intelligent Decision Making

This module provides AI-driven intelligent decision making capabilities
for the SynergyMesh autonomous coordination grid.

Core Capabilities:
- Intelligent decision making based on context and history
- Predictive analysis for proactive actions
- Multi-criteria decision optimization
- Autonomous strategy selection

設計原則: AI 驅動的智能決策引擎，基於歷史數據的預測性維護
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions"""
    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"


class DecisionPriority(Enum):
    """Decision priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""
    VERY_HIGH = "very_high"  # > 0.9
    HIGH = "high"            # > 0.75
    MEDIUM = "medium"        # > 0.5
    LOW = "low"              # > 0.25
    UNCERTAIN = "uncertain"  # <= 0.25


@dataclass
class DecisionContext:
    """Context for making decisions"""
    context_id: str
    domain: str
    current_state: Dict[str, Any] = field(default_factory=dict)
    historical_data: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionOption:
    """A possible decision option"""
    option_id: str
    name: str
    description: str
    expected_outcome: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    benefit_score: float = 0.0
    confidence: float = 0.0
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """A made decision"""
    decision_id: str
    decision_type: DecisionType
    priority: DecisionPriority
    selected_option: DecisionOption
    alternatives: List[DecisionOption] = field(default_factory=list)
    reasoning: str = ""
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    made_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Result of predictive analysis"""
    prediction_id: str
    prediction_type: str
    predicted_outcome: Dict[str, Any]
    probability: float
    confidence: float
    factors: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class AIDecisionEngine:
    """
    AI 決策引擎 - 智能決策核心
    
    AI Decision Engine for intelligent autonomous decision making.
    Provides predictive analysis and multi-criteria optimization.
    
    Features:
    - 智能決策: Intelligent decision making based on context
    - 預測分析: Predictive analysis for proactive actions
    - 多準則優化: Multi-criteria decision optimization
    - 自主策略: Autonomous strategy selection
    
    設計目標:
    - 零人工干預決策: No human intervention required
    - 預測性維護: Predictive maintenance
    - 自主學習: Self-learning from outcomes
    """
    
    # Decision weights for different criteria
    DEFAULT_WEIGHTS = {
        "benefit": 0.4,
        "risk": 0.3,
        "confidence": 0.2,
        "prerequisites_met": 0.1
    }
    
    def __init__(self):
        """Initialize the AI Decision Engine"""
        self.decision_history: List[Decision] = []
        self.prediction_history: List[PredictionResult] = []
        self.decision_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self.learned_patterns: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configuration
        self.config = {
            "min_confidence_threshold": 0.5,
            "max_alternatives": 5,
            "learning_enabled": True,
            "auto_execute_threshold": 0.85
        }
        
        # Statistics
        self.stats = {
            "decisions_made": 0,
            "predictions_made": 0,
            "successful_decisions": 0,
            "learning_cycles": 0
        }
        
        logger.info("AIDecisionEngine initialized - AI 決策引擎已初始化")
    
    async def make_decision(
        self,
        context: DecisionContext,
        options: List[DecisionOption],
        decision_type: DecisionType = DecisionType.OPERATIONAL,
        priority: DecisionPriority = DecisionPriority.MEDIUM
    ) -> Decision:
        """
        Make an intelligent decision based on context and options
        
        基於上下文和選項做出智能決策
        
        Args:
            context: Decision context with current state and history
            options: Available decision options
            decision_type: Type of decision
            priority: Decision priority
            
        Returns:
            Made decision with selected option and reasoning
        """
        decision_id = f"dec-{uuid.uuid4().hex[:8]}"
        
        # Score and rank options
        scored_options = await self._score_options(context, options)
        
        # Select best option
        best_option = scored_options[0] if scored_options else None
        
        if not best_option:
            logger.warning("No valid options available for decision")
            return self._create_fallback_decision(decision_id, decision_type, priority)
        
        # Determine confidence level
        confidence_level = self._calculate_confidence_level(best_option.confidence)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(context, best_option, scored_options)
        
        # Create decision
        decision = Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            priority=priority,
            selected_option=best_option,
            alternatives=scored_options[1:self.config["max_alternatives"]],
            reasoning=reasoning,
            confidence_level=confidence_level,
            metadata={
                "context_id": context.context_id,
                "domain": context.domain,
                "options_evaluated": len(options)
            }
        )
        
        # Store in history
        self.decision_history.append(decision)
        self.stats["decisions_made"] += 1
        
        # Learn from decision if enabled
        if self.config["learning_enabled"]:
            self._learn_from_decision(context, decision)
        
        logger.info(
            f"Decision made: {decision_id} - {best_option.name} "
            f"(confidence: {confidence_level.value})"
        )
        
        return decision
    
    async def _score_options(
        self,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> List[DecisionOption]:
        """Score and rank decision options"""
        scored_options = []
        weights = self.DEFAULT_WEIGHTS
        
        for option in options:
            # Calculate composite score
            prereqs_met = self._check_prerequisites(option, context)
            
            score = (
                weights["benefit"] * option.benefit_score +
                weights["risk"] * (1 - option.risk_score) +
                weights["confidence"] * option.confidence +
                weights["prerequisites_met"] * (1.0 if prereqs_met else 0.0)
            )
            
            # Adjust based on historical patterns
            historical_boost = self._get_historical_boost(option, context.domain)
            score *= (1 + historical_boost)
            
            # Update option with calculated values
            option.confidence = min(score, 1.0)
            scored_options.append(option)
        
        # Sort by confidence (score)
        scored_options.sort(key=lambda x: x.confidence, reverse=True)
        
        return scored_options
    
    def _check_prerequisites(
        self,
        option: DecisionOption,
        context: DecisionContext
    ) -> bool:
        """Check if all prerequisites are met"""
        if not option.prerequisites:
            return True
        
        # Check against context constraints
        for prereq in option.prerequisites:
            if prereq in context.constraints:
                continue
            # Check if prerequisite is satisfied by current state
            if prereq not in context.current_state:
                return False
        
        return True
    
    def _get_historical_boost(self, option: DecisionOption, domain: str) -> float:
        """Get boost factor based on historical success"""
        if domain not in self.learned_patterns:
            return 0.0
        
        patterns = self.learned_patterns[domain]
        similar_decisions = [
            p for p in patterns
            if p.get("option_name") == option.name and p.get("success", False)
        ]
        
        if not similar_decisions:
            return 0.0
        
        success_rate = len(similar_decisions) / len(patterns)
        return min(success_rate * 0.2, 0.2)  # Max 20% boost
    
    def _calculate_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Calculate confidence level from score"""
        if confidence > 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence > 0.75:
            return ConfidenceLevel.HIGH
        elif confidence > 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence > 0.25:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.UNCERTAIN
    
    def _generate_reasoning(
        self,
        context: DecisionContext,
        selected: DecisionOption,
        alternatives: List[DecisionOption]
    ) -> str:
        """Generate human-readable reasoning for decision"""
        parts = [
            f"Selected '{selected.name}' based on:",
            f"- Benefit score: {selected.benefit_score:.2f}",
            f"- Risk score: {selected.risk_score:.2f}",
            f"- Confidence: {selected.confidence:.2f}"
        ]
        
        if alternatives and len(alternatives) > 1:
            runner_up = alternatives[1] if len(alternatives) > 1 else alternatives[0]
            parts.append(
                f"- Preferred over '{runner_up.name}' (confidence: {runner_up.confidence:.2f})"
            )
        
        if context.objectives:
            parts.append(f"- Aligns with objectives: {', '.join(context.objectives[:3])}")
        
        return "\n".join(parts)
    
    def _create_fallback_decision(
        self,
        decision_id: str,
        decision_type: DecisionType,
        priority: DecisionPriority
    ) -> Decision:
        """Create a fallback decision when no options are valid"""
        fallback_option = DecisionOption(
            option_id="fallback",
            name="No Action",
            description="No valid options available; recommend human review",
            confidence=0.0
        )
        
        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            priority=priority,
            selected_option=fallback_option,
            reasoning="No valid options available for automated decision",
            confidence_level=ConfidenceLevel.UNCERTAIN
        )
    
    def _learn_from_decision(
        self,
        context: DecisionContext,
        decision: Decision
    ) -> None:
        """Learn from decision for future improvements"""
        if context.domain not in self.learned_patterns:
            self.learned_patterns[context.domain] = []
        
        pattern = {
            "decision_id": decision.decision_id,
            "option_name": decision.selected_option.name,
            "confidence": decision.selected_option.confidence,
            "context_hash": hash(frozenset(context.current_state.items())),
            "timestamp": datetime.now().isoformat(),
            "success": None  # To be updated when outcome is known
        }
        
        self.learned_patterns[context.domain].append(pattern)
        self.stats["learning_cycles"] += 1
    
    async def predict_outcome(
        self,
        current_state: Dict[str, Any],
        prediction_type: str,
        horizon: str = "short_term"
    ) -> PredictionResult:
        """
        Predict future outcome based on current state
        
        基於當前狀態預測未來結果
        
        Args:
            current_state: Current system state
            prediction_type: Type of prediction
            horizon: Prediction horizon (short_term, medium_term, long_term)
            
        Returns:
            Prediction result with probability and recommendations
        """
        prediction_id = f"pred-{uuid.uuid4().hex[:8]}"
        
        # Analyze patterns
        factors = self._analyze_prediction_factors(current_state, prediction_type)
        
        # Calculate probability based on factors
        probability = self._calculate_prediction_probability(factors)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            prediction_type, probability, factors
        )
        
        # Determine predicted outcome
        predicted_outcome = {
            "prediction_type": prediction_type,
            "horizon": horizon,
            "status": "likely" if probability > 0.6 else "uncertain",
            "impact": self._assess_impact(prediction_type, probability)
        }
        
        result = PredictionResult(
            prediction_id=prediction_id,
            prediction_type=prediction_type,
            predicted_outcome=predicted_outcome,
            probability=probability,
            confidence=min(probability + 0.1, 1.0),
            factors=factors,
            recommendations=recommendations
        )
        
        self.prediction_history.append(result)
        self.stats["predictions_made"] += 1
        
        logger.info(
            f"Prediction made: {prediction_id} - {prediction_type} "
            f"(probability: {probability:.2f})"
        )
        
        return result
    
    def _analyze_prediction_factors(
        self,
        current_state: Dict[str, Any],
        prediction_type: str
    ) -> List[Dict[str, Any]]:
        """Analyze factors affecting prediction"""
        factors = []
        
        # Analyze state indicators
        for key, value in current_state.items():
            factor = {
                "name": key,
                "value": value,
                "impact": self._calculate_factor_impact(key, value, prediction_type),
                "direction": "positive" if isinstance(value, (int, float)) and value > 0 else "neutral"
            }
            factors.append(factor)
        
        return factors
    
    def _calculate_factor_impact(
        self,
        factor_name: str,
        factor_value: Any,
        prediction_type: str
    ) -> float:
        """Calculate impact of a factor on prediction"""
        # Simplified impact calculation
        impact_weights = {
            "error_rate": -0.3,
            "success_rate": 0.3,
            "performance": 0.2,
            "reliability": 0.25,
            "load": -0.15
        }
        
        for key, weight in impact_weights.items():
            if key in factor_name.lower():
                if isinstance(factor_value, (int, float)):
                    return weight * min(factor_value, 1.0)
        
        return 0.1  # Default small positive impact
    
    def _calculate_prediction_probability(
        self,
        factors: List[Dict[str, Any]]
    ) -> float:
        """Calculate prediction probability from factors"""
        if not factors:
            return 0.5
        
        total_impact = sum(f.get("impact", 0) for f in factors)
        # Normalize to 0-1 range
        probability = 0.5 + (total_impact / max(len(factors), 1))
        return max(0.0, min(1.0, probability))
    
    def _generate_recommendations(
        self,
        prediction_type: str,
        probability: float,
        factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on prediction"""
        recommendations = []
        
        if probability < 0.4:
            recommendations.append("Consider preventive measures")
            recommendations.append("Review system configuration")
        elif probability > 0.8:
            recommendations.append("System is performing well")
            recommendations.append("Continue current strategy")
        else:
            recommendations.append("Monitor closely")
            recommendations.append("Prepare contingency plans")
        
        # Add factor-specific recommendations
        negative_factors = [f for f in factors if f.get("impact", 0) < 0]
        for factor in negative_factors[:2]:
            recommendations.append(f"Address {factor['name']} issue")
        
        return recommendations
    
    def _assess_impact(self, prediction_type: str, probability: float) -> str:
        """Assess the impact level of prediction"""
        if probability > 0.8:
            return "high_positive" if "success" in prediction_type.lower() else "high_negative"
        elif probability > 0.5:
            return "moderate"
        return "low"
    
    def record_outcome(
        self,
        decision_id: str,
        success: bool,
        outcome_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record the outcome of a decision for learning
        
        記錄決策結果以供學習
        """
        # Find decision in history
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                # Update learned patterns
                for domain, patterns in self.learned_patterns.items():
                    for pattern in patterns:
                        if pattern.get("decision_id") == decision_id:
                            pattern["success"] = success
                            pattern["outcome"] = outcome_data
                            break
                
                if success:
                    self.stats["successful_decisions"] += 1
                
                logger.info(f"Outcome recorded for decision {decision_id}: {'success' if success else 'failure'}")
                return
        
        logger.warning(f"Decision {decision_id} not found in history")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        return {
            "decisions_made": self.stats["decisions_made"],
            "predictions_made": self.stats["predictions_made"],
            "successful_decisions": self.stats["successful_decisions"],
            "success_rate": round(
                self.stats["successful_decisions"] / max(self.stats["decisions_made"], 1) * 100, 2
            ),
            "learning_cycles": self.stats["learning_cycles"],
            "domains_learned": list(self.learned_patterns.keys()),
            "total_patterns": sum(len(p) for p in self.learned_patterns.values())
        }
    
    def get_decision_history(
        self,
        limit: int = 10,
        decision_type: Optional[DecisionType] = None
    ) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        history = self.decision_history
        
        if decision_type:
            history = [d for d in history if d.decision_type == decision_type]
        
        return [
            {
                "decision_id": d.decision_id,
                "type": d.decision_type.value,
                "priority": d.priority.name,
                "selected": d.selected_option.name,
                "confidence": d.confidence_level.value,
                "made_at": d.made_at.isoformat()
            }
            for d in history[-limit:]
        ]


# Export classes
__all__ = [
    "AIDecisionEngine",
    "DecisionType",
    "DecisionPriority",
    "ConfidenceLevel",
    "DecisionContext",
    "DecisionOption",
    "Decision",
    "PredictionResult"
]
