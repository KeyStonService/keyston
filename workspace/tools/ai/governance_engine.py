#!/usr/bin/env python3
"""
AI Governance Engine - 人工智慧治理引擎
=====================================

Purpose: ML-powered decision making for instant execution pipeline
Provides intelligent governance, pattern recognition, and risk assessment

This is a stub implementation with a real interface that can be enhanced
with actual ML models later.

Key Features:
- AST-based code analysis
- Pattern recognition for naming conventions
- Risk scoring and impact assessment
- Confidence-based decision making
- Real-time optimization recommendations
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class DecisionType(Enum):
    """Decision types"""
    APPROVE = "approve"
    REJECT = "reject"
    NEEDS_REVIEW = "needs_review"
    CONDITIONAL_APPROVE = "conditional_approve"


@dataclass
class AnalysisResult:
    """AI analysis result"""
    decision: DecisionType
    confidence: float  # 0.0 - 1.0
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 100.0
    patterns_found: List[str] = field(default_factory=list)
    conflicts_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodebaseMetrics:
    """Codebase metrics"""
    total_files: int = 0
    total_lines: int = 0
    yaml_files: int = 0
    python_files: int = 0
    complexity_score: float = 0.0
    naming_consistency: float = 0.0
    pattern_confidence: float = 0.0


class AIGovernanceEngine:
    """
    AI Governance Engine for intelligent decision making
    
    Currently a mock implementation with real interface.
    Can be enhanced with actual ML models (TensorFlow, PyTorch, etc.)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.accuracy_target = self.config.get("accuracy_target", 0.97)
        self.risk_threshold = self.config.get("risk_threshold", 75.0)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.85)
        
        # Pattern database (would be ML model in production)
        self.known_patterns = {
            "kubernetes": r"(deployment|service|configmap|pod|namespace)",
            "naming_convention": r"^[a-z][a-z0-9-]*$",
            "version_pattern": r"v\d+\.\d+\.\d+",
            "environment": r"(prod|dev|staging|test)",
        }
        
        self.analysis_count = 0
        self.cache = {}
    
    def analyze_codebase(self, 
                        repo_path: Path,
                        include_patterns: List[str] = None) -> CodebaseMetrics:
        """
        Analyze entire codebase structure
        
        In production: Would use AST parsing, ML pattern recognition
        Current: Simple file-based analysis
        """
        metrics = CodebaseMetrics()
        
        if not repo_path.exists():
            return metrics
        
        # Count files and basic metrics
        for file_path in repo_path.rglob("*"):
            if file_path.is_file():
                metrics.total_files += 1
                
                if file_path.suffix in [".yaml", ".yml"]:
                    metrics.yaml_files += 1
                elif file_path.suffix == ".py":
                    metrics.python_files += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        metrics.total_lines += len(f.readlines())
                except (IOError, OSError, UnicodeDecodeError):
                    # Skip files that cannot be read
                    pass
        
        # Calculate derived metrics
        if metrics.total_files > 0:
            metrics.complexity_score = min(100.0, metrics.total_files / 10.0)
            metrics.naming_consistency = 85.0  # Mock - would be ML-calculated
            metrics.pattern_confidence = 92.0  # Mock - would be ML-calculated
        
        return metrics
    
    def detect_naming_patterns(self, 
                              resources: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Detect naming patterns from resources
        
        In production: ML-based pattern recognition
        Current: Rule-based pattern matching
        """
        patterns = {
            "kubernetes_standard": 0,
            "semantic_versioning": 0,
            "environment_prefixed": 0,
            "hyphen_separated": 0,
        }
        
        total = len(resources)
        if total == 0:
            return {"patterns": patterns, "confidence": 0.0}
        
        for resource in resources:
            name = resource.get("name", "")
            
            # Check patterns
            if re.search(self.known_patterns["kubernetes"], name):
                patterns["kubernetes_standard"] += 1
            if re.search(self.known_patterns["version_pattern"], name):
                patterns["semantic_versioning"] += 1
            if re.search(self.known_patterns["environment"], name):
                patterns["environment_prefixed"] += 1
            if re.search(r"^[a-z0-9-]+$", name):
                patterns["hyphen_separated"] += 1
        
        # Calculate confidence
        max_pattern = max(patterns.values())
        confidence = (max_pattern / total) if total > 0 else 0.0
        
        return {
            "patterns": patterns,
            "confidence": confidence,
            "total_analyzed": total,
            "dominant_pattern": max(patterns, key=patterns.get)
        }
    
    def assess_risk(self, 
                   change_type: str,
                   impact_scope: str,
                   affected_resources: int) -> Tuple[RiskLevel, float]:
        """
        Assess risk of changes
        
        In production: ML-based risk prediction
        Current: Rule-based risk scoring
        """
        risk_score = 0.0
        
        # Change type risk
        change_risks = {
            "create": 10.0,
            "update": 30.0,
            "delete": 80.0,
            "migrate": 50.0,
        }
        risk_score += change_risks.get(change_type, 20.0)
        
        # Scope risk
        scope_risks = {
            "global": 40.0,
            "namespace": 20.0,
            "service": 10.0,
            "resource": 5.0,
        }
        risk_score += scope_risks.get(impact_scope, 15.0)
        
        # Scale risk
        if affected_resources > 100:
            risk_score += 30.0
        elif affected_resources > 50:
            risk_score += 20.0
        elif affected_resources > 10:
            risk_score += 10.0
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return risk_level, risk_score
    
    def detect_conflicts(self, 
                        resources: List[Dict[str, str]]) -> List[str]:
        """
        Detect naming conflicts and anti-patterns
        
        In production: ML-based anomaly detection
        Current: Rule-based conflict detection
        """
        conflicts = []
        names_seen = set()
        
        for resource in resources:
            name = resource.get("name", "")
            
            # Check for duplicates
            if name in names_seen:
                conflicts.append(f"Duplicate name detected: {name}")
            names_seen.add(name)
            
            # Check for anti-patterns
            if name.startswith("-") or name.endswith("-"):
                conflicts.append(f"Anti-pattern: Name starts/ends with hyphen: {name}")
            
            if "__" in name:
                conflicts.append(f"Anti-pattern: Double underscore in name: {name}")
            
            if len(name) > 63:
                conflicts.append(f"Anti-pattern: Name too long (>63 chars): {name}")
        
        return conflicts
    
    def make_decision(self,
                     context: Dict[str, Any],
                     analysis_type: str = "general") -> AnalysisResult:
        """
        Make AI-powered governance decision
        
        Main decision-making interface
        """
        self.analysis_count += 1
        
        # Extract context
        change_type = context.get("change_type", "unknown")
        impact_scope = context.get("impact_scope", "resource")
        resources = context.get("resources", [])
        affected_count = context.get("affected_resources", len(resources))
        
        # Assess risk
        risk_level, risk_score = self.assess_risk(
            change_type, impact_scope, affected_count
        )
        
        # Detect patterns
        pattern_analysis = self.detect_naming_patterns(resources)
        
        # Detect conflicts
        conflicts = self.detect_conflicts(resources)
        
        # Calculate confidence
        confidence = pattern_analysis["confidence"]
        if conflicts:
            confidence *= 0.8  # Reduce confidence if conflicts found
        
        # Make decision
        if risk_score >= self.risk_threshold:
            decision = DecisionType.REJECT
            recommendations = [
                "Risk score too high for automated approval",
                "Manual review required",
                f"Reduce affected resources or change scope"
            ]
        elif confidence < self.confidence_threshold:
            decision = DecisionType.NEEDS_REVIEW
            recommendations = [
                "Pattern confidence below threshold",
                "Additional validation recommended",
                "Review naming conventions"
            ]
        elif conflicts:
            decision = DecisionType.CONDITIONAL_APPROVE
            recommendations = [
                "Fix detected conflicts before deployment",
                f"Address {len(conflicts)} naming issues"
            ]
        else:
            decision = DecisionType.APPROVE
            recommendations = [
                "All checks passed",
                "Risk within acceptable limits",
                "Patterns consistent with codebase"
            ]
        
        return AnalysisResult(
            decision=decision,
            confidence=confidence,
            risk_level=risk_level,
            risk_score=risk_score,
            patterns_found=[pattern_analysis["dominant_pattern"]],
            conflicts_detected=conflicts,
            recommendations=recommendations,
            metadata={
                "analysis_type": analysis_type,
                "pattern_analysis": pattern_analysis,
                "analysis_number": self.analysis_count,
            }
        )
    
    def optimize_configuration(self, 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize configuration based on learned patterns
        
        In production: ML-based optimization
        Current: Rule-based optimization
        """
        optimized = config.copy()
        
        # Add recommendations
        optimized["recommendations"] = [
            "Use consistent naming patterns",
            "Follow Kubernetes best practices",
            "Implement semantic versioning",
            "Add proper labels and annotations"
        ]
        
        # Add default values if missing
        if "namespace" not in optimized:
            optimized["namespace"] = "machinenativenops-system"
        
        if "labels" not in optimized:
            optimized["labels"] = {
                "app.kubernetes.io/managed-by": "machinenativenops",
                "app.kubernetes.io/part-of": "instant-execution"
            }
        
        return optimized
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics"""
        return {
            "total_analyses": self.analysis_count,
            "accuracy_target": self.accuracy_target,
            "confidence_threshold": self.confidence_threshold,
            "risk_threshold": self.risk_threshold,
            "cache_size": len(self.cache),
        }


def main():
    """Demo/Test entry point"""
    print("=" * 70)
    print("AI Governance Engine - Demo")
    print("=" * 70)
    print()
    
    # Create engine
    engine = AIGovernanceEngine({
        "accuracy_target": 0.97,
        "risk_threshold": 75.0,
        "confidence_threshold": 0.85,
    })
    
    # Test analysis
    context = {
        "change_type": "create",
        "impact_scope": "namespace",
        "affected_resources": 5,
        "resources": [
            {"name": "machinenativenops-api-v1"},
            {"name": "machinenativenops-worker-v1"},
            {"name": "machinenativenops-db-config"},
            {"name": "prod-ingress-controller"},
            {"name": "monitoring-stack"},
        ]
    }
    
    print("Analyzing deployment context...")
    result = engine.make_decision(context, "deployment")
    
    print(f"\n✅ Decision: {result.decision.value.upper()}")
    print(f"📊 Confidence: {result.confidence:.1%}")
    print(f"⚠️  Risk Level: {result.risk_level.value.upper()}")
    print(f"📈 Risk Score: {result.risk_score:.1f}/100")
    
    print(f"\n🔍 Patterns Found:")
    for pattern in result.patterns_found:
        print(f"   - {pattern}")
    
    if result.conflicts_detected:
        print(f"\n⚠️  Conflicts Detected:")
        for conflict in result.conflicts_detected:
            print(f"   - {conflict}")
    
    print(f"\n💡 Recommendations:")
    for rec in result.recommendations:
        print(f"   - {rec}")
    
    print(f"\n📊 Engine Metrics:")
    metrics = engine.get_metrics()
    for key, value in metrics.items():
        print(f"   - {key}: {value}")
    
    print()


if __name__ == "__main__":
    main()
