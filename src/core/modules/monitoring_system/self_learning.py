"""
Self Learning Engine (自我學習引擎)

Continuous improvement from incidents and events

Reference: AI-driven infrastructure that detects anomalies, neutralizes risks, and learns from each incident [5]
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PatternType(Enum):
    """Types of learned patterns"""
    ANOMALY = "anomaly"
    INCIDENT = "incident"
    REMEDIATION = "remediation"
    FAILURE = "failure"
    SUCCESS = "success"


class LearningSource(Enum):
    """Sources of learning"""
    MONITORING = "monitoring"
    DIAGNOSIS = "diagnosis"
    REMEDIATION = "remediation"
    USER_FEEDBACK = "user_feedback"
    MANUAL_INPUT = "manual_input"


@dataclass
class IncidentPattern:
    """A learned incident pattern"""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: PatternType = PatternType.INCIDENT
    description: str = ""
    conditions: list[dict[str, Any]] = field(default_factory=list)
    frequency: int = 1
    last_seen: datetime = field(default_factory=datetime.now)
    first_seen: datetime = field(default_factory=datetime.now)
    successful_remediations: list[str] = field(default_factory=list)
    failed_remediations: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def increment(self) -> None:
        """Increment pattern frequency"""
        self.frequency += 1
        self.last_seen = datetime.now()

    def add_successful_remediation(self, remediation_id: str) -> None:
        """Record a successful remediation"""
        if remediation_id not in self.successful_remediations:
            self.successful_remediations.append(remediation_id)

    def add_failed_remediation(self, remediation_id: str) -> None:
        """Record a failed remediation"""
        if remediation_id not in self.failed_remediations:
            self.failed_remediations.append(remediation_id)

    def get_success_rate(self) -> float:
        """Get remediation success rate"""
        total = len(self.successful_remediations) + len(self.failed_remediations)
        if total == 0:
            return 0.0
        return len(self.successful_remediations) / total

    def to_dict(self) -> dict[str, Any]:
        return {
            'pattern_id': self.pattern_id,
            'type': self.pattern_type.value,
            'description': self.description,
            'conditions': self.conditions,
            'frequency': self.frequency,
            'last_seen': self.last_seen.isoformat(),
            'first_seen': self.first_seen.isoformat(),
            'success_rate': self.get_success_rate(),
            'tags': self.tags
        }


@dataclass
class LearningOutcome:
    """Outcome of a learning process"""
    outcome_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: LearningSource = LearningSource.MONITORING
    description: str = ""
    patterns_identified: int = 0
    patterns_updated: int = 0
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            'outcome_id': self.outcome_id,
            'source': self.source.value,
            'description': self.description,
            'patterns_identified': self.patterns_identified,
            'patterns_updated': self.patterns_updated,
            'insights': self.insights,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


class PatternLearner:
    """
    Pattern Learner
    
    Identifies and learns patterns from incidents
    """

    def __init__(self, similarity_threshold: float = 0.7):
        self._patterns: dict[str, IncidentPattern] = {}
        self._similarity_threshold = similarity_threshold

    def _calculate_similarity(
        self,
        conditions1: list[dict[str, Any]],
        conditions2: list[dict[str, Any]]
    ) -> float:
        """Calculate similarity between two sets of conditions"""
        if not conditions1 or not conditions2:
            return 0.0

        # Simple key-based similarity
        keys1 = set()
        keys2 = set()

        for cond in conditions1:
            if isinstance(cond, dict):
                keys1.update(cond.keys())

        for cond in conditions2:
            if isinstance(cond, dict):
                keys2.update(cond.keys())

        if not keys1 or not keys2:
            return 0.0

        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)

        return intersection / union if union > 0 else 0.0

    def find_similar_pattern(
        self,
        conditions: list[dict[str, Any]]
    ) -> IncidentPattern | None:
        """Find a similar existing pattern"""
        best_match = None
        best_similarity = 0.0

        for pattern in self._patterns.values():
            similarity = self._calculate_similarity(conditions, pattern.conditions)
            if similarity > best_similarity and similarity >= self._similarity_threshold:
                best_similarity = similarity
                best_match = pattern

        return best_match

    def learn(
        self,
        conditions: list[dict[str, Any]],
        pattern_type: PatternType = PatternType.INCIDENT,
        description: str = "",
        tags: list[str] | None = None
    ) -> IncidentPattern:
        """Learn from conditions - create new pattern or update existing"""
        existing = self.find_similar_pattern(conditions)

        if existing:
            existing.increment()
            return existing

        # Create new pattern
        pattern = IncidentPattern(
            pattern_type=pattern_type,
            description=description,
            conditions=conditions,
            tags=tags or []
        )
        self._patterns[pattern.pattern_id] = pattern
        return pattern

    def get_patterns(self) -> list[IncidentPattern]:
        """Get all learned patterns"""
        return list(self._patterns.values())

    def get_frequent_patterns(self, min_frequency: int = 3) -> list[IncidentPattern]:
        """Get frequently occurring patterns"""
        return [p for p in self._patterns.values() if p.frequency >= min_frequency]


class EffectivenessTracker:
    """
    Effectiveness Tracker
    
    Tracks effectiveness of remediations and generates insights
    """

    def __init__(self):
        self._remediation_outcomes: dict[str, dict[str, Any]] = {}
        self._playbook_stats: dict[str, dict[str, int]] = {}

    def record_outcome(
        self,
        remediation_id: str,
        playbook_id: str,
        success: bool,
        execution_time_ms: int,
        anomaly_resolved: bool
    ) -> None:
        """Record a remediation outcome"""
        self._remediation_outcomes[remediation_id] = {
            'playbook_id': playbook_id,
            'success': success,
            'execution_time_ms': execution_time_ms,
            'anomaly_resolved': anomaly_resolved,
            'timestamp': datetime.now()
        }

        # Update playbook stats
        if playbook_id not in self._playbook_stats:
            self._playbook_stats[playbook_id] = {
                'total': 0,
                'success': 0,
                'resolved': 0,
                'total_time_ms': 0
            }

        stats = self._playbook_stats[playbook_id]
        stats['total'] += 1
        if success:
            stats['success'] += 1
        if anomaly_resolved:
            stats['resolved'] += 1
        stats['total_time_ms'] += execution_time_ms

    def get_playbook_effectiveness(self, playbook_id: str) -> dict[str, Any]:
        """Get effectiveness stats for a playbook"""
        stats = self._playbook_stats.get(playbook_id, {})
        if not stats:
            return {'effectiveness': 0.0, 'resolution_rate': 0.0}

        total = stats.get('total', 0)
        if total == 0:
            return {'effectiveness': 0.0, 'resolution_rate': 0.0}

        return {
            'effectiveness': stats.get('success', 0) / total,
            'resolution_rate': stats.get('resolved', 0) / total,
            'avg_time_ms': stats.get('total_time_ms', 0) / total,
            'total_executions': total
        }

    def get_insights(self) -> list[str]:
        """Generate insights from tracked data"""
        insights = []

        for playbook_id, stats in self._playbook_stats.items():
            total = stats.get('total', 0)
            if total < 3:
                continue

            effectiveness = stats.get('success', 0) / total
            resolution_rate = stats.get('resolved', 0) / total

            if effectiveness < 0.5:
                insights.append(
                    f"Playbook {playbook_id} has low effectiveness ({effectiveness:.1%}). "
                    "Consider reviewing and updating remediation actions."
                )

            if resolution_rate < effectiveness:
                insights.append(
                    f"Playbook {playbook_id} executes successfully but doesn't always resolve issues. "
                    "Consider adding additional remediation steps."
                )

        return insights


class SelfLearningEngine:
    """
    Self Learning Engine (自我學習引擎)
    
    Continuous improvement from incidents and events
    
    Reference: AI-driven infrastructure learns from each incident [5]
    """

    def __init__(self):
        self._pattern_learner = PatternLearner()
        self._effectiveness_tracker = EffectivenessTracker()
        self._learning_outcomes: list[LearningOutcome] = []

    @property
    def pattern_learner(self) -> PatternLearner:
        return self._pattern_learner

    @property
    def effectiveness_tracker(self) -> EffectivenessTracker:
        return self._effectiveness_tracker

    def learn_from_incident(
        self,
        conditions: list[dict[str, Any]],
        description: str = "",
        tags: list[str] | None = None
    ) -> IncidentPattern:
        """Learn from an incident"""
        return self._pattern_learner.learn(
            conditions=conditions,
            pattern_type=PatternType.INCIDENT,
            description=description,
            tags=tags
        )

    def record_remediation_outcome(
        self,
        remediation_id: str,
        playbook_id: str,
        success: bool,
        execution_time_ms: int,
        anomaly_resolved: bool,
        pattern_id: str | None = None
    ) -> None:
        """Record outcome of a remediation"""
        self._effectiveness_tracker.record_outcome(
            remediation_id=remediation_id,
            playbook_id=playbook_id,
            success=success,
            execution_time_ms=execution_time_ms,
            anomaly_resolved=anomaly_resolved
        )

        # Update pattern if provided
        if pattern_id:
            patterns = self._pattern_learner.get_patterns()
            for pattern in patterns:
                if pattern.pattern_id == pattern_id:
                    if success:
                        pattern.add_successful_remediation(playbook_id)
                    else:
                        pattern.add_failed_remediation(playbook_id)
                    break

    def analyze_and_learn(self) -> LearningOutcome:
        """Analyze data and generate learning outcomes"""
        outcome = LearningOutcome(
            source=LearningSource.MONITORING,
            description="Periodic analysis of monitoring data"
        )

        # Count patterns
        patterns = self._pattern_learner.get_patterns()
        frequent_patterns = self._pattern_learner.get_frequent_patterns()

        outcome.patterns_identified = len(patterns)

        # Generate insights
        insights = self._effectiveness_tracker.get_insights()
        outcome.insights = insights

        # Generate recommendations
        recommendations = []

        for pattern in frequent_patterns:
            if pattern.get_success_rate() < 0.5 and pattern.successful_remediations:
                recommendations.append(
                    f"Pattern '{pattern.description}' has low success rate. "
                    f"Review remediation strategy."
                )
            elif not pattern.successful_remediations:
                recommendations.append(
                    f"No successful remediations for pattern '{pattern.description}'. "
                    f"Consider creating a new playbook."
                )

        outcome.recommendations = recommendations
        self._learning_outcomes.append(outcome)

        return outcome

    def get_recommended_playbook(
        self,
        conditions: list[dict[str, Any]]
    ) -> str | None:
        """Get recommended playbook based on learned patterns"""
        pattern = self._pattern_learner.find_similar_pattern(conditions)

        if pattern and pattern.successful_remediations:
            # Return most successful remediation
            return pattern.successful_remediations[0]

        return None

    def get_learning_summary(self) -> dict[str, Any]:
        """Get summary of learning progress"""
        patterns = self._pattern_learner.get_patterns()

        return {
            'total_patterns': len(patterns),
            'frequent_patterns': len(self._pattern_learner.get_frequent_patterns()),
            'total_learning_outcomes': len(self._learning_outcomes),
            'insights': self._effectiveness_tracker.get_insights(),
            'timestamp': datetime.now().isoformat()
        }
