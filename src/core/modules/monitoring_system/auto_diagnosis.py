"""
Auto Diagnosis Engine (自動診斷引擎)

Automatic root cause analysis and diagnosis

Reference: AIOps platforms perform anomaly detection, event correlation, and predictive analysis [5]
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DiagnosisStatus(Enum):
    """Status of a diagnosis"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RootCauseConfidence(Enum):
    """Confidence level in root cause identification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


@dataclass
class RootCause:
    """A potential root cause"""
    cause_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    component: str = ""
    confidence: RootCauseConfidence = RootCauseConfidence.MEDIUM
    evidence: list[str] = field(default_factory=list)
    related_metrics: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            'cause_id': self.cause_id,
            'description': self.description,
            'component': self.component,
            'confidence': self.confidence.value,
            'evidence': self.evidence,
            'related_metrics': self.related_metrics,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class DiagnosisContext:
    """Context for diagnosis"""
    anomaly_id: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    logs: list[str] = field(default_factory=list)
    traces: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    related_metrics: dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    additional_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosisResult:
    """Result of a diagnosis"""
    diagnosis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    anomaly_id: str = ""
    status: DiagnosisStatus = DiagnosisStatus.PENDING
    root_causes: list[RootCause] = field(default_factory=list)
    summary: str = ""
    recommendations: list[str] = field(default_factory=list)
    diagnosis_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    context: DiagnosisContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            'diagnosis_id': self.diagnosis_id,
            'anomaly_id': self.anomaly_id,
            'status': self.status.value,
            'root_causes': [rc.to_dict() for rc in self.root_causes],
            'summary': self.summary,
            'recommendations': self.recommendations,
            'diagnosis_time_ms': self.diagnosis_time_ms,
            'timestamp': self.timestamp.isoformat()
        }


class AutoDiagnosisEngine:
    """
    Auto Diagnosis Engine (自動診斷引擎)
    
    Automatic root cause analysis with AI-driven insights
    
    Reference: AIOps platforms perform anomaly detection, event correlation [5]
    """

    def __init__(self):
        self._diagnosis_rules: dict[str, Callable[[DiagnosisContext], list[RootCause]]] = {}
        self._component_dependencies: dict[str, list[str]] = {}
        self._history: list[DiagnosisResult] = []

    def register_diagnosis_rule(
        self,
        name: str,
        rule: Callable[[DiagnosisContext], list[RootCause]]
    ) -> None:
        """Register a diagnosis rule"""
        self._diagnosis_rules[name] = rule

    def set_component_dependencies(
        self,
        component: str,
        dependencies: list[str]
    ) -> None:
        """Set dependencies for a component"""
        self._component_dependencies[component] = dependencies

    def _analyze_logs(self, logs: list[str]) -> list[str]:
        """Analyze logs for evidence"""
        evidence = []
        error_keywords = ['error', 'exception', 'failed', 'timeout', 'refused', 'unavailable']

        for log in logs:
            log_lower = log.lower()
            for keyword in error_keywords:
                if keyword in log_lower:
                    evidence.append(f"Log indicates {keyword}: {log[:100]}...")
                    break

        return evidence

    def _analyze_related_metrics(
        self,
        metric_name: str,
        related_metrics: dict[str, float]
    ) -> list[RootCause]:
        """Analyze related metrics for potential causes"""
        causes = []

        # Check for resource-related issues
        resource_metrics = ['cpu', 'memory', 'disk', 'network']
        for resource in resource_metrics:
            for name, value in related_metrics.items():
                if resource in name.lower():
                    if value > 90:  # High utilization
                        causes.append(RootCause(
                            description=f"High {resource} utilization ({value:.1f}%) may be causing issues",
                            component=resource,
                            confidence=RootCauseConfidence.MEDIUM,
                            evidence=[f"{name} = {value:.1f}%"],
                            related_metrics=[name]
                        ))

        return causes

    def _analyze_dependencies(
        self,
        component: str,
        context: DiagnosisContext
    ) -> list[RootCause]:
        """Analyze component dependencies"""
        causes = []
        dependencies = self._component_dependencies.get(component, [])

        for dep in dependencies:
            # Check if dependency has issues in related metrics
            for metric_name, value in context.related_metrics.items():
                if dep.lower() in metric_name.lower():
                    if 'error' in metric_name.lower() and value > 0:
                        causes.append(RootCause(
                            description=f"Dependency {dep} showing errors",
                            component=dep,
                            confidence=RootCauseConfidence.MEDIUM,
                            evidence=[f"{metric_name} = {value}"],
                            related_metrics=[metric_name]
                        ))

        return causes

    def diagnose(self, context: DiagnosisContext) -> DiagnosisResult:
        """
        Perform diagnosis on the given context
        
        Reference: Detection → Auto Diagnosis → Execute Fix → Verify → Log [9]
        """
        import time
        start_time = time.time()

        result = DiagnosisResult(
            anomaly_id=context.anomaly_id,
            status=DiagnosisStatus.IN_PROGRESS,
            context=context
        )

        try:
            root_causes = []

            # Run custom diagnosis rules
            for _rule_name, rule in self._diagnosis_rules.items():
                try:
                    causes = rule(context)
                    root_causes.extend(causes)
                except Exception:
                    pass

            # Analyze logs
            log_evidence = self._analyze_logs(context.logs)
            if log_evidence:
                root_causes.append(RootCause(
                    description="Log analysis indicates potential issues",
                    component="logs",
                    confidence=RootCauseConfidence.LOW,
                    evidence=log_evidence
                ))

            # Analyze related metrics
            metric_causes = self._analyze_related_metrics(
                context.metric_name,
                context.related_metrics
            )
            root_causes.extend(metric_causes)

            # Analyze dependencies
            component = context.metric_name.split('.')[0] if '.' in context.metric_name else 'unknown'
            dep_causes = self._analyze_dependencies(component, context)
            root_causes.extend(dep_causes)

            # Sort by confidence
            confidence_order = {
                RootCauseConfidence.CERTAIN: 4,
                RootCauseConfidence.HIGH: 3,
                RootCauseConfidence.MEDIUM: 2,
                RootCauseConfidence.LOW: 1
            }
            root_causes.sort(key=lambda x: confidence_order[x.confidence], reverse=True)

            result.root_causes = root_causes
            result.status = DiagnosisStatus.COMPLETED

            # Generate summary
            if root_causes:
                top_cause = root_causes[0]
                result.summary = f"Most likely cause: {top_cause.description} (confidence: {top_cause.confidence.value})"
            else:
                result.summary = "No root cause identified. Further investigation needed."

            # Generate recommendations
            result.recommendations = RecommendationGenerator().generate(result)

        except Exception as e:
            result.status = DiagnosisStatus.FAILED
            result.summary = f"Diagnosis failed: {str(e)}"

        result.diagnosis_time_ms = int((time.time() - start_time) * 1000)
        self._history.append(result)

        return result

    def get_history(self) -> list[DiagnosisResult]:
        """Get diagnosis history"""
        return self._history.copy()


class RecommendationGenerator:
    """
    Recommendation Generator
    
    Generates actionable recommendations based on diagnosis results
    """

    def __init__(self):
        self._templates: dict[str, list[str]] = {
            'cpu': [
                "Review CPU-intensive processes",
                "Consider horizontal scaling",
                "Check for inefficient algorithms"
            ],
            'memory': [
                "Check for memory leaks",
                "Review memory allocation patterns",
                "Consider increasing memory limits"
            ],
            'disk': [
                "Clean up unnecessary files",
                "Check for disk-intensive operations",
                "Consider expanding storage"
            ],
            'network': [
                "Check network connectivity",
                "Review network configuration",
                "Look for network bottlenecks"
            ],
            'database': [
                "Review slow queries",
                "Check database connections",
                "Optimize database indexes"
            ],
            'default': [
                "Review system logs",
                "Check recent changes",
                "Monitor the situation"
            ]
        }

    def generate(self, diagnosis: DiagnosisResult) -> list[str]:
        """Generate recommendations based on diagnosis"""
        recommendations = []

        for cause in diagnosis.root_causes:
            component = cause.component.lower()

            # Get component-specific recommendations
            if component in self._templates:
                recommendations.extend(self._templates[component])
            else:
                # Check if component matches any template key
                for key, recs in self._templates.items():
                    if key in component:
                        recommendations.extend(recs)
                        break
                else:
                    recommendations.extend(self._templates['default'])

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)

        return unique_recommendations[:5]  # Return top 5 recommendations
