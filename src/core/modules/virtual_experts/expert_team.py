"""
Virtual Expert Team (虛擬專家團隊)

Orchestrates virtual experts to provide collaborative consultation.

參考：構建可靠 AI 代理需要設計、測試和擴展的最佳實踐 [1]
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .expert_base import VirtualExpert


class ConsultationType(Enum):
    """Types of expert consultation."""

    CODE_REVIEW = "code_review"
    ARCHITECTURE_ADVICE = "architecture_advice"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DECISION_SUPPORT = "decision_support"
    TROUBLESHOOTING = "troubleshooting"
    BEST_PRACTICES = "best_practices"


@dataclass
class ExpertConsultation:
    """
    A consultation request to virtual experts.

    虛擬專家諮詢請求
    """

    id: str
    type: ConsultationType
    requester_id: str

    # Query
    query: str
    context: dict[str, Any] = field(default_factory=dict)
    domains: list[str] = field(default_factory=list)

    # Code (if applicable)
    code: str | None = None
    language: str | None = None

    # Status
    status: str = "pending"  # pending, in_progress, completed

    # Assigned experts
    assigned_experts: list[str] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # Priority
    priority: str = "normal"  # low, normal, high, urgent


@dataclass
class ConsultationResult:
    """
    Result of a virtual expert consultation.

    虛擬專家諮詢結果
    """

    consultation_id: str

    # Expert responses
    expert_responses: list[dict[str, Any]] = field(default_factory=list)

    # Synthesized result
    summary: str = ""
    recommendations: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)

    # Code review specifics (if applicable)
    issues: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[dict[str, Any]] = field(default_factory=list)
    quality_score: float = 0.0

    # Metadata
    total_experts_consulted: int = 0
    confidence_score: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)


class VirtualExpertTeam:
    """
    Virtual Expert Team Orchestrator.

    虛擬專家團隊協調器

    核心功能：
    1. 專家註冊與管理 - Expert registration and management
    2. 諮詢路由 - Consultation routing
    3. 多專家協作 - Multi-expert collaboration
    4. 結果綜合 - Result synthesis

    參考：代理策略層關注代理如何規劃、路由任務 [7]
    """

    def __init__(self) -> None:
        self.experts: dict[str, VirtualExpert] = {}
        self.consultations: dict[str, ExpertConsultation] = {}
        self.results: dict[str, ConsultationResult] = {}

        # Domain to expert mapping
        self.domain_experts: dict[str, list[str]] = {}

        # Initialize with default experts
        self._initialize_default_team()

    def _initialize_default_team(self) -> None:
        """Initialize the default expert team."""
        # Import module to avoid name shadowing issues
        try:
            from . import domain_experts as de
        except ImportError:
            import domain_experts as de  # type: ignore[import-not-found,no-redef]

        # Create expert instances using module reference
        experts = [
            de.DrAlexChen(),
            de.SarahWong(),
            de.MarcusJohnson(),
            de.LiWei(),
            de.EmmaThompson(),
            de.JamesMiller(),
        ]

        for expert in experts:
            self.register_expert(expert)

    def register_expert(self, expert: VirtualExpert) -> None:
        """Register a virtual expert."""
        self.experts[expert.id] = expert

        # Map domains to expert
        all_domains = (
            expert.knowledge.primary_domains
            + expert.knowledge.secondary_domains
            + expert.knowledge.specializations
        )

        for domain in all_domains:
            domain_lower = domain.lower()
            if domain_lower not in self.domain_experts:
                self.domain_experts[domain_lower] = []
            if expert.id not in self.domain_experts[domain_lower]:
                self.domain_experts[domain_lower].append(expert.id)

    def get_expert(self, expert_id: str) -> VirtualExpert | None:
        """Get an expert by ID."""
        return self.experts.get(expert_id)

    def find_experts_for_domains(self, domains: list[str]) -> list[VirtualExpert]:
        """Find experts that can handle given domains."""
        expert_ids = set()

        for domain in domains:
            domain_lower = domain.lower()

            # Direct match
            if domain_lower in self.domain_experts:
                expert_ids.update(self.domain_experts[domain_lower])

            # Partial match
            for key, ids in self.domain_experts.items():
                if domain_lower in key or key in domain_lower:
                    expert_ids.update(ids)

        return [self.experts[eid] for eid in expert_ids if eid in self.experts]

    def create_consultation(
        self,
        consultation_type: ConsultationType,
        query: str,
        requester_id: str,
        domains: list[str] | None = None,
        context: dict[str, Any] | None = None,
        code: str | None = None,
        language: str | None = None,
        priority: str = "normal",
    ) -> ExpertConsultation:
        """
        Create a new consultation request.

        創建諮詢請求
        """
        consultation_id = f"consult_{uuid.uuid4().hex[:8]}"

        # Auto-detect domains if not provided
        if not domains:
            domains = self._detect_domains(query, code)

        consultation = ExpertConsultation(
            id=consultation_id,
            type=consultation_type,
            requester_id=requester_id,
            query=query,
            context=context or {},
            domains=domains,
            code=code,
            language=language,
            priority=priority,
        )

        # Find and assign experts
        experts = self.find_experts_for_domains(domains)
        consultation.assigned_experts = [e.id for e in experts]

        self.consultations[consultation_id] = consultation
        return consultation

    def _detect_domains(self, query: str, code: str | None) -> list[str]:
        """Auto-detect relevant domains from query and code."""
        domains = []
        combined_text = (query + " " + (code or "")).lower()

        domain_keywords = {
            "security": ["password", "authentication", "injection", "xss", "csrf", "密碼", "安全"],
            "database": ["sql", "query", "index", "transaction", "數據庫", "索引", "查詢"],
            "performance": ["optimize", "performance", "slow", "cache", "性能", "優化", "緩存"],
            "architecture": ["design", "pattern", "microservice", "架構", "設計", "模式"],
            "ai": ["model", "prediction", "machine learning", "ml", "模型", "預測"],
            "deployment": ["deploy", "ci/cd", "docker", "kubernetes", "部署", "容器"],
            "nlp": ["intent", "language", "text", "意圖", "語言", "文本"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                domains.append(domain)

        # Default to general if no specific domains detected
        if not domains:
            domains = ["general"]

        return domains

    async def process_consultation(self, consultation_id: str) -> ConsultationResult:
        """
        Process a consultation request.

        處理諮詢請求
        """
        if consultation_id not in self.consultations:
            raise ValueError(f"Consultation not found: {consultation_id}")

        consultation = self.consultations[consultation_id]
        consultation.status = "in_progress"

        expert_responses = []
        all_issues = []
        all_suggestions = []
        all_recommendations = []

        # Get responses from each assigned expert
        for expert_id in consultation.assigned_experts:
            expert = self.experts.get(expert_id)
            if not expert:
                continue

            response = self._get_expert_response(expert, consultation)
            expert_responses.append(response)

            # Collect issues and suggestions
            if "issues" in response:
                all_issues.extend(response["issues"])
            if "suggestions" in response:
                all_suggestions.extend(response["suggestions"])
            if "recommendations" in response:
                all_recommendations.extend(response["recommendations"])

        # Synthesize results
        result = self._synthesize_results(
            consultation, expert_responses, all_issues, all_suggestions, all_recommendations
        )

        # Update consultation status
        consultation.status = "completed"
        consultation.completed_at = datetime.now()

        self.results[consultation_id] = result
        return result

    def _get_expert_response(
        self, expert: VirtualExpert, consultation: ExpertConsultation
    ) -> dict[str, Any]:
        """Get response from a specific expert."""
        response = {
            "expert_id": expert.id,
            "expert_name": expert.name,
            "expert_title": expert.title,
        }

        if consultation.type == ConsultationType.CODE_REVIEW and consultation.code:
            review = expert.review_code(consultation.code, consultation.language or "python")
            response.update(review)

        elif consultation.type in [
            ConsultationType.ARCHITECTURE_ADVICE,
            ConsultationType.BEST_PRACTICES,
            ConsultationType.DECISION_SUPPORT,
        ]:
            guidance = expert.provide_guidance(consultation.query, consultation.context)
            response.update(guidance)

        else:
            # Generic answer
            answer = expert.answer_question(consultation.query, consultation.context)
            response.update(answer)

        return response

    def _synthesize_results(
        self,
        consultation: ExpertConsultation,
        expert_responses: list[dict[str, Any]],
        all_issues: list[dict[str, Any]],
        all_suggestions: list[dict[str, Any]],
        all_recommendations: list[str],
    ) -> ConsultationResult:
        """Synthesize results from multiple experts."""

        # Deduplicate issues by message
        seen_issues = set()
        unique_issues = []
        for issue in all_issues:
            msg = issue.get("message", "")
            if msg not in seen_issues:
                seen_issues.add(msg)
                unique_issues.append(issue)

        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        unique_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 4))

        # Deduplicate recommendations
        unique_recommendations = list(dict.fromkeys(all_recommendations))

        # Calculate quality score
        quality_scores = [
            r.get("quality_score", 0.8) for r in expert_responses if "quality_score" in r
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.8

        # Generate summary
        summary = self._generate_summary(consultation, expert_responses, unique_issues)

        # Generate action items
        action_items = self._generate_action_items(unique_issues, unique_recommendations)

        return ConsultationResult(
            consultation_id=consultation.id,
            expert_responses=expert_responses,
            summary=summary,
            recommendations=unique_recommendations,
            action_items=action_items,
            issues=unique_issues,
            suggestions=all_suggestions,
            quality_score=avg_quality,
            total_experts_consulted=len(expert_responses),
            confidence_score=min(0.95, 0.5 + len(expert_responses) * 0.15),
        )

    def _generate_summary(
        self,
        consultation: ExpertConsultation,
        expert_responses: list[dict[str, Any]],
        issues: list[dict[str, Any]],
    ) -> str:
        """Generate a summary of the consultation."""
        expert_names = [r.get("expert_name", "Unknown") for r in expert_responses]

        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        high_count = sum(1 for i in issues if i.get("severity") == "high")

        summary_parts = [
            f"諮詢類型: {consultation.type.value}",
            f"參與專家: {', '.join(expert_names)}",
        ]

        if issues:
            summary_parts.append(f"發現問題: {len(issues)} 個")
            if critical_count > 0:
                summary_parts.append(f"  - 嚴重: {critical_count} 個")
            if high_count > 0:
                summary_parts.append(f"  - 高優先級: {high_count} 個")
        else:
            summary_parts.append("未發現明顯問題")

        return "\n".join(summary_parts)

    def _generate_action_items(
        self, issues: list[dict[str, Any]], recommendations: list[str]
    ) -> list[str]:
        """Generate action items from issues and recommendations."""
        action_items = []

        # Critical issues first
        for issue in issues:
            if issue.get("severity") == "critical":
                action_items.append(f"🚨 [緊急] {issue.get('message', '')}")

        # High priority issues
        for issue in issues:
            if issue.get("severity") == "high":
                action_items.append(f"⚠️ [高優先] {issue.get('message', '')}")

        # Top recommendations
        for rec in recommendations[:5]:
            action_items.append(f"💡 {rec}")

        return action_items

    def get_consultation(self, consultation_id: str) -> ExpertConsultation | None:
        """Get a consultation by ID."""
        return self.consultations.get(consultation_id)

    def get_result(self, consultation_id: str) -> ConsultationResult | None:
        """Get consultation result."""
        return self.results.get(consultation_id)

    def list_experts(self) -> list[dict[str, Any]]:
        """List all available experts."""
        return [
            {
                "id": expert.id,
                "name": expert.name,
                "title": expert.title,
                "avatar": expert.avatar,
                "role": expert.role,
                "department": expert.department,
                "primary_domains": expert.knowledge.primary_domains,
                "availability": expert.availability,
            }
            for expert in self.experts.values()
        ]

    def get_team_stats(self) -> dict[str, Any]:
        """Get team statistics."""
        return {
            "total_experts": len(self.experts),
            "total_consultations": len(self.consultations),
            "completed_consultations": sum(
                1 for c in self.consultations.values() if c.status == "completed"
            ),
            "domains_covered": len(self.domain_experts),
            "experts_by_department": self._count_by_department(),
        }

    def _count_by_department(self) -> dict[str, int]:
        """Count experts by department."""
        counts: dict[str, int] = {}
        for expert in self.experts.values():
            dept = expert.department
            counts[dept] = counts.get(dept, 0) + 1
        return counts
