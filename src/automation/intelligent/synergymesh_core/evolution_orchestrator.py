"""
Evolution Orchestrator - 演化編排器
自動演化決策引擎 / Automated Evolution Decision Engine

This module provides AI-powered orchestration for system evolution,
automatically reading evolution state and generating actionable refactor plans.

Core Capabilities:
- Read and analyze evolution-state.yaml
- Apply AI Constitution constraints
- Generate prioritized refactor action plans
- Integrate with ecosystem orchestrator
- Output executable refactor tasks

設計原則: AI 自動讀取演化狀態並產生行動計畫
Integration: Works with ecosystem_orchestrator.py and evolution reporting system
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ActionPriority(Enum):
    """Priority levels for refactor actions"""
    P0_CRITICAL = "P0"  # Must fix immediately
    P1_HIGH = "P1"      # High priority
    P2_MEDIUM = "P2"    # Medium priority
    P3_LOW = "P3"       # Low priority


class ActionStatus(Enum):
    """Status of a refactor action"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass
class EvolutionState:
    """Represents the current evolution state of the system"""
    generated_at: str
    overall_score: float
    metrics: dict[str, Any]
    objectives: list[dict[str, Any]]
    config_version: str


@dataclass
class RefactorAction:
    """Represents a single refactor action to be taken"""
    action_id: str
    priority: ActionPriority
    objective_id: str
    cluster: str
    description: str
    playbook_path: str | None = None
    commands: list[str] = field(default_factory=list)
    expected_improvement: float = 0.0
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    constraints_checked: bool = False


@dataclass
class ActionPlan:
    """Complete action plan for system evolution"""
    plan_id: str
    generated_at: datetime
    based_on_state: str  # evolution-state.yaml timestamp
    current_score: float
    target_score: float
    actions: list[RefactorAction] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    estimated_duration: str = "TBD"


class EvolutionOrchestrator:
    """
    AI-powered orchestrator for system evolution.
    
    Reads evolution-state.yaml, applies constraints, and generates
    prioritized refactor action plans.
    """
    
    def __init__(self, repo_root: Path | None = None):
        """Initialize the Evolution Orchestrator
        
        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = repo_root or Path(__file__).resolve().parents[3]
        self.evolution_state_path = self.repo_root / "knowledge/evolution-state.yaml"
        self.config_path = self.repo_root / "config/system-evolution.yaml"
        self.constitution_path = self.repo_root / "config/ai-constitution.yaml"
        
        self.evolution_state: EvolutionState | None = None
        self.config: dict[str, Any] = {}
        self.constraints: list[str] = []
        
        logger.info(f"Evolution Orchestrator initialized with repo root: {self.repo_root}")
    
    def load_evolution_state(self) -> EvolutionState:
        """Load the current evolution state from YAML
        
        Returns:
            EvolutionState object with current metrics and scores
        """
        if not self.evolution_state_path.exists():
            raise FileNotFoundError(
                f"Evolution state not found: {self.evolution_state_path}"
            )
        
        with self.evolution_state_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        self.evolution_state = EvolutionState(
            generated_at=data["generated_at"],
            overall_score=data["overall_score"],
            metrics=data["metrics"],
            objectives=data["objectives"],
            config_version=data["config_version"]
        )
        
        logger.info(
            f"Loaded evolution state: score={self.evolution_state.overall_score}/100, "
            f"generated={self.evolution_state.generated_at}"
        )
        return self.evolution_state
    
    def load_config(self) -> dict[str, Any]:
        """Load system evolution configuration and constraints
        
        Returns:
            Configuration dictionary with objectives and constraints
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with self.config_path.open("r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        self.constraints = self.config.get("constraints", [])
        
        logger.info(
            f"Loaded config v{self.config.get('version')}: "
            f"{len(self.constraints)} constraints"
        )
        return self.config
    
    def analyze_objectives(self) -> list[dict[str, Any]]:
        """Analyze objectives and identify areas needing improvement
        
        Returns:
            List of objectives sorted by priority (lowest score first)
        """
        if not self.evolution_state:
            raise RuntimeError("Evolution state not loaded. Call load_evolution_state() first.")
        
        # Sort objectives by score (lowest first = highest priority)
        sorted_objectives = sorted(
            self.evolution_state.objectives,
            key=lambda obj: obj["score"]
        )
        
        logger.info(
            f"Analyzed {len(sorted_objectives)} objectives. "
            f"Lowest score: {sorted_objectives[0]['name']} = "
            f"{sorted_objectives[0]['score']}/100"
        )
        
        return sorted_objectives
    
    def generate_actions_for_objective(
        self,
        objective: dict[str, Any]
    ) -> list[RefactorAction]:
        """Generate refactor actions for a specific objective
        
        Args:
            objective: Objective dictionary with score and metadata
            
        Returns:
            List of RefactorAction objects
        """
        actions: list[RefactorAction] = []
        obj_id = objective["id"]
        obj_name = objective["name"]
        score = objective["score"]
        
        # Determine priority based on score
        if score < 50:
            priority = ActionPriority.P0_CRITICAL
        elif score < 75:
            priority = ActionPriority.P1_HIGH
        elif score < 90:
            priority = ActionPriority.P2_MEDIUM
        else:
            priority = ActionPriority.P3_LOW
        
        # Generate specific actions based on objective type
        if obj_id == "language-governance" and score < 100:
            # Check language governance report for violations
            action = RefactorAction(
                action_id=f"{obj_id}-violations",
                priority=priority,
                objective_id=obj_id,
                cluster="governance",
                description=f"解決語言違規問題 (當前: {objective['value']} 個違規)",
                playbook_path="docs/refactor_playbooks/03_refactor/governance/governance__policy_refactor.md",
                commands=[
                    "python3 tools/generate-language-governance-report.py",
                    "# Review violations in governance/language-governance-report.md",
                    "# Update affected clusters' refactor playbooks"
                ],
                expected_improvement=100 - score,
                constraints_checked=True
            )
            actions.append(action)
        
        elif obj_id == "security" and score < 100:
            # Check semgrep report for high severity issues
            action = RefactorAction(
                action_id=f"{obj_id}-high-severity",
                priority=ActionPriority.P0_CRITICAL,  # Security is always P0
                objective_id=obj_id,
                cluster="core",
                description=f"修復 Semgrep 高風險問題 (當前: {objective['value']} 個問題)",
                playbook_path="docs/refactor_playbooks/03_refactor/core/core__architecture_refactor.md",
                commands=[
                    "# Review security issues in governance/semgrep-report.json",
                    "# Create security refactor playbooks for affected clusters",
                    "# Apply fixes following playbook guidelines"
                ],
                expected_improvement=100 - score,
                constraints_checked=True
            )
            actions.append(action)
        
        elif obj_id == "refactor-playbook-coverage" and score < 100:
            # Find clusters without playbooks
            coverage = objective["value"]
            missing_clusters = int((1.0 - coverage) * 8)  # Assuming 8 total clusters
            
            action = RefactorAction(
                action_id=f"{obj_id}-missing-playbooks",
                priority=priority,
                objective_id=obj_id,
                cluster="all",
                description=f"為 {missing_clusters} 個 clusters 建立 refactor playbooks",
                commands=[
                    "# Identify missing clusters from cluster-heatmap.json",
                    "for cluster in <missing_clusters>; do",
                    "  python3 tools/generate-refactor-playbook.py --cluster $cluster",
                    "done",
                    "python3 tools/evolution/generate_evolution_report.py"
                ],
                expected_improvement=100 - score,
                constraints_checked=True
            )
            actions.append(action)
        
        return actions
    
    def check_constraints(self, action: RefactorAction) -> tuple[bool, list[str]]:
        """Check if an action violates any constraints
        
        Args:
            action: RefactorAction to validate
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        for constraint in self.constraints:
            # Check for safety-critical modification constraint
            if "safety-critical" in constraint and action.cluster == "autonomous":
                if "自動修改" in constraint or "automatic modification" in action.description.lower():
                    violations.append(
                        f"Constraint violation: {constraint} (action: {action.action_id})"
                    )
            
            # Check for architecture boundary constraint
            if "architecture skeletons" in constraint or "邊界" in constraint:
                if "core" in action.cluster and "apps" in action.description:
                    violations.append(
                        f"Constraint violation: Architecture boundary (action: {action.action_id})"
                    )
            
            # Check for forbidden languages constraint
            if "forbidden_languages" in constraint or "PHP/Perl" in constraint:
                if "PHP" in action.description or "Perl" in action.description:
                    violations.append(
                        f"Constraint violation: Forbidden language (action: {action.action_id})"
                    )
        
        is_valid = len(violations) == 0
        action.constraints_checked = True
        
        return is_valid, violations
    
    def generate_action_plan(self) -> ActionPlan:
        """Generate complete action plan based on current evolution state
        
        Returns:
            ActionPlan with prioritized refactor actions
        """
        if not self.evolution_state:
            self.load_evolution_state()
        
        if not self.config:
            self.load_config()
        
        # Analyze objectives and sort by priority
        sorted_objectives = self.analyze_objectives()
        
        # Generate actions for each objective
        all_actions: list[RefactorAction] = []
        
        for objective in sorted_objectives:
            if objective["score"] < 100:  # Only generate actions for non-perfect scores
                actions = self.generate_actions_for_objective(objective)
                
                # Validate actions against constraints
                for action in actions:
                    is_valid, violations = self.check_constraints(action)
                    if not is_valid:
                        logger.warning(
                            f"Action {action.action_id} has constraint violations: "
                            f"{violations}"
                        )
                        action.status = ActionStatus.BLOCKED
                
                all_actions.extend(actions)
        
        # Sort actions by priority
        all_actions.sort(key=lambda a: a.priority.value)
        
        # Create action plan
        plan = ActionPlan(
            plan_id=f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generated_at=datetime.now(),
            based_on_state=self.evolution_state.generated_at,
            current_score=self.evolution_state.overall_score,
            target_score=100.0,
            actions=all_actions,
            constraints=self.constraints,
            estimated_duration=self._estimate_duration(all_actions)
        )
        
        logger.info(
            f"Generated action plan: {len(all_actions)} actions, "
            f"current={plan.current_score}/100, target={plan.target_score}/100"
        )
        
        return plan
    
    def _estimate_duration(self, actions: list[RefactorAction]) -> str:
        """Estimate total duration for all actions
        
        Args:
            actions: List of refactor actions
            
        Returns:
            Human-readable duration estimate
        """
        # Simple heuristic: P0=2h, P1=1h, P2=30m, P3=15m per action
        duration_map = {
            ActionPriority.P0_CRITICAL: 2.0,
            ActionPriority.P1_HIGH: 1.0,
            ActionPriority.P2_MEDIUM: 0.5,
            ActionPriority.P3_LOW: 0.25
        }
        
        total_hours = sum(duration_map[action.priority] for action in actions)
        
        if total_hours < 1:
            return f"{int(total_hours * 60)} minutes"
        elif total_hours < 8:
            return f"{total_hours:.1f} hours"
        else:
            days = total_hours / 8
            return f"{days:.1f} days"
    
    def export_plan_to_markdown(self, plan: ActionPlan, output_path: Path | None = None) -> str:
        """Export action plan to markdown format
        
        Args:
            plan: ActionPlan to export
            output_path: Optional path to save markdown file
            
        Returns:
            Markdown content as string
        """
        lines = []
        lines.append("# 🤖 System Evolution Action Plan")
        lines.append(f"\n生成時間: {plan.generated_at.isoformat()}")
        lines.append(f"基於狀態: {plan.based_on_state}")
        lines.append(f"計畫 ID: {plan.plan_id}\n")
        
        lines.append("## 📊 當前狀態")
        lines.append(f"- 目前分數: **{plan.current_score}/100**")
        lines.append(f"- 目標分數: **{plan.target_score}/100**")
        lines.append(f"- 待執行動作: **{len(plan.actions)}** 個")
        lines.append(f"- 預估時程: **{plan.estimated_duration}**\n")
        
        lines.append("## 🔒 演化約束")
        for constraint in plan.constraints:
            lines.append(f"- {constraint}")
        lines.append("")
        
        # Group actions by priority
        for priority in ActionPriority:
            priority_actions = [a for a in plan.actions if a.priority == priority]
            if not priority_actions:
                continue
            
            lines.append(f"## {priority.value}: {priority.name.replace('_', ' ').title()}")
            lines.append(f"**{len(priority_actions)} 個動作**\n")
            
            for action in priority_actions:
                lines.append(f"### [{action.status.value.upper()}] {action.description}")
                lines.append(f"- **Action ID**: `{action.action_id}`")
                lines.append(f"- **Objective**: {action.objective_id}")
                lines.append(f"- **Cluster**: {action.cluster}")
                lines.append(f"- **Expected Improvement**: +{action.expected_improvement:.1f} points")
                
                if action.playbook_path:
                    lines.append(f"- **Playbook**: `{action.playbook_path}`")
                
                if action.constraints_checked:
                    status_icon = "✅" if action.status != ActionStatus.BLOCKED else "❌"
                    lines.append(f"- **Constraints**: {status_icon} Checked")
                
                if action.commands:
                    lines.append("\n**執行步驟:**")
                    lines.append("```bash")
                    for cmd in action.commands:
                        lines.append(cmd)
                    lines.append("```")
                
                lines.append("")
        
        lines.append("---")
        lines.append("本計畫由 `evolution_orchestrator.py` 自動生成")
        
        markdown_content = "\n".join(lines)
        
        # Optionally save to file
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                f.write(markdown_content)
            logger.info(f"Action plan saved to: {output_path}")
        
        return markdown_content
    
    async def orchestrate(self) -> ActionPlan:
        """Main orchestration method - async entry point
        
        Returns:
            Complete ActionPlan ready for execution
        """
        logger.info("Starting evolution orchestration...")
        
        # Load current state and config
        self.load_evolution_state()
        self.load_config()
        
        # Generate action plan
        plan = self.generate_action_plan()
        
        # Export plan
        output_path = self.repo_root / "docs/evolution/CURRENT_ACTION_PLAN.md"
        self.export_plan_to_markdown(plan, output_path)
        
        logger.info(f"Orchestration complete. Plan: {plan.plan_id}")
        
        return plan


# Standalone execution
def main():
    """Standalone execution for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    
    orchestrator = EvolutionOrchestrator()
    
    try:
        # Load and analyze
        orchestrator.load_evolution_state()
        orchestrator.load_config()
        
        # Generate plan
        plan = orchestrator.generate_action_plan()
        
        # Export to markdown
        output_path = orchestrator.repo_root / "docs/evolution/CURRENT_ACTION_PLAN.md"
        orchestrator.export_plan_to_markdown(plan, output_path)
        
        print("\n✅ Evolution action plan generated successfully!")
        print(f"📄 Plan ID: {plan.plan_id}")
        print(f"📊 Current Score: {plan.current_score}/100")
        print(f"🎯 Target Score: {plan.target_score}/100")
        print(f"📋 Actions: {len(plan.actions)}")
        print(f"⏱️  Estimated Duration: {plan.estimated_duration}")
        print(f"💾 Saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        raise


if __name__ == "__main__":
    main()
