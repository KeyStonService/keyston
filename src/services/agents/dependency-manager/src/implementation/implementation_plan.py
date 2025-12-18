"""
12 個月實施計劃 (Implementation Plan)

提供完整的實施路徑規劃、里程碑追蹤和任務管理功能。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class PhaseType(Enum):
    """階段類型"""
    FOUNDATION = "foundation"      # 基礎建設期
    CAPABILITY = "capability"      # 能力建構期
    SCALING = "scaling"            # 規模化期
    OPTIMIZATION = "optimization"  # 優化成熟期


class TaskStatus(Enum):
    """任務狀態"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任務優先級"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """任務"""
    id: str
    name: str
    description: str
    owner: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.NOT_STARTED
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    start_date: datetime | None = None
    end_date: datetime | None = None
    completed_date: datetime | None = None
    notes: str = ""

    def is_overdue(self) -> bool:
        """檢查是否逾期"""
        if self.end_date and self.status != TaskStatus.COMPLETED:
            return datetime.now() > self.end_date
        return False

    def progress_percentage(self) -> float:
        """計算進度百分比"""
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        if self.estimated_hours > 0:
            return min(100.0, (self.actual_hours / self.estimated_hours) * 100)
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner': self.owner,
            'priority': self.priority.value,
            'status': self.status.value,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'dependencies': self.dependencies,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'progress': self.progress_percentage(),
            'is_overdue': self.is_overdue()
        }


@dataclass
class Milestone:
    """里程碑"""
    id: str
    name: str
    description: str
    target_date: datetime
    tasks: list[Task] = field(default_factory=list)
    completed: bool = False
    completed_date: datetime | None = None
    deliverables: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)

    def progress_percentage(self) -> float:
        """計算里程碑進度"""
        if not self.tasks:
            return 100.0 if self.completed else 0.0
        completed_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return (completed_tasks / len(self.tasks)) * 100

    def is_on_track(self) -> bool:
        """檢查是否按計劃進行"""
        if self.completed:
            return True
        expected_progress = self._calculate_expected_progress()
        return self.progress_percentage() >= expected_progress * 0.9  # 允許 10% 偏差

    def _calculate_expected_progress(self) -> float:
        """計算預期進度"""
        if not self.tasks:
            return 0.0
        earliest_start = min(
            (t.start_date for t in self.tasks if t.start_date),
            default=datetime.now()
        )
        total_duration = (self.target_date - earliest_start).days
        elapsed = (datetime.now() - earliest_start).days
        if total_duration <= 0:
            return 100.0
        return min(100.0, (elapsed / total_duration) * 100)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_date': self.target_date.isoformat(),
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'progress': self.progress_percentage(),
            'is_on_track': self.is_on_track(),
            'deliverables': self.deliverables,
            'success_criteria': self.success_criteria,
            'tasks': [t.to_dict() for t in self.tasks]
        }


@dataclass
class Phase:
    """實施階段"""
    id: str
    name: str
    phase_type: PhaseType
    description: str
    start_month: int  # 1-12
    end_month: int    # 1-12
    milestones: list[Milestone] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    key_activities: list[str] = field(default_factory=list)
    expected_outcomes: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def duration_months(self) -> int:
        """階段持續月數"""
        return self.end_month - self.start_month + 1

    def progress_percentage(self) -> float:
        """計算階段進度"""
        if not self.milestones:
            return 0.0
        return sum(m.progress_percentage() for m in self.milestones) / len(self.milestones)

    def is_current(self, current_month: int) -> bool:
        """檢查是否為當前階段"""
        return self.start_month <= current_month <= self.end_month

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'phase_type': self.phase_type.value,
            'description': self.description,
            'start_month': self.start_month,
            'end_month': self.end_month,
            'duration_months': self.duration_months(),
            'progress': self.progress_percentage(),
            'objectives': self.objectives,
            'key_activities': self.key_activities,
            'expected_outcomes': self.expected_outcomes,
            'risks': self.risks,
            'milestones': [m.to_dict() for m in self.milestones]
        }


class ImplementationPlan:
    """12 個月實施計劃"""

    def __init__(self, project_name: str, start_date: datetime | None = None):
        """
        初始化實施計劃
        
        Args:
            project_name: 專案名稱
            start_date: 開始日期（預設為今天）
        """
        self.project_name = project_name
        self.start_date = start_date or datetime.now()
        self.phases: list[Phase] = []
        self._initialize_default_phases()

    def _initialize_default_phases(self) -> None:
        """初始化預設的 4 個階段"""

        # Phase 1: 基礎建設期 (第 1-3 月)
        phase1 = Phase(
            id="phase_1",
            name="基礎建設期",
            phase_type=PhaseType.FOUNDATION,
            description="完成團隊技能評估、建立開發環境、選定核心提示詞並開始試點",
            start_month=1,
            end_month=3,
            objectives=[
                "完成團隊技能評估與培訓規劃",
                "建立開發環境與工具鏈",
                "選定核心提示詞並開始小規模試點"
            ],
            key_activities=[
                "進行團隊技能盤點",
                "制定培訓計劃",
                "搭建開發環境",
                "配置 CI/CD 流水線",
                "評估並選擇核心提示詞",
                "啟動試點專案"
            ],
            expected_outcomes=[
                "團隊技能評估報告",
                "培訓計劃文檔",
                "開發環境就緒",
                "核心提示詞選擇報告",
                "試點專案啟動"
            ],
            risks=[
                "團隊技能差距過大",
                "工具鏈整合困難",
                "核心提示詞選擇錯誤"
            ]
        )

        # Phase 2: 能力建構期 (第 4-6 月)
        phase2 = Phase(
            id="phase_2",
            name="能力建構期",
            phase_type=PhaseType.CAPABILITY,
            description="深化核心技術能力、完成首個專案、建立標準化流程",
            start_month=4,
            end_month=6,
            objectives=[
                "深化核心提示詞相關技術能力",
                "完成第一個完整項目的開發與測試",
                "建立標準化開發流程與文檔"
            ],
            key_activities=[
                "執行技術培訓計劃",
                "進行專案開發",
                "建立代碼審查流程",
                "撰寫技術文檔",
                "進行測試與品質保證",
                "收集經驗教訓"
            ],
            expected_outcomes=[
                "技術能力提升報告",
                "第一個完整專案交付",
                "標準化開發流程文檔",
                "經驗教訓總結"
            ],
            risks=[
                "專案延期",
                "技術債務累積",
                "文檔不完整"
            ]
        )

        # Phase 3: 規模化期 (第 7-9 月)
        phase3 = Phase(
            id="phase_3",
            name="規模化期",
            phase_type=PhaseType.SCALING,
            description="擴大團隊規模、引入衛星提示詞、建立持續改進機制",
            start_month=7,
            end_month=9,
            objectives=[
                "擴大團隊規模，提升開發產能",
                "引入衛星提示詞，豐富產品組合",
                "建立用戶回饋機制與持續改進流程"
            ],
            key_activities=[
                "招聘新團隊成員",
                "進行新人培訓",
                "評估並引入衛星提示詞",
                "擴展產品功能",
                "建立用戶回饋收集機制",
                "實施持續改進"
            ],
            expected_outcomes=[
                "團隊規模擴展完成",
                "衛星提示詞整合完成",
                "產品功能豐富化",
                "用戶回饋系統上線"
            ],
            risks=[
                "招聘困難",
                "新人培訓效果不佳",
                "衛星提示詞整合問題"
            ]
        )

        # Phase 4: 優化成熟期 (第 10-12 月)
        phase4 = Phase(
            id="phase_4",
            name="優化成熟期",
            phase_type=PhaseType.OPTIMIZATION,
            description="評估策略成效、調整發展方向、準備下一年度規劃",
            start_month=10,
            end_month=12,
            objectives=[
                "評估各提示詞策略成效",
                "調整未來發展方向",
                "準備下一年度的技術路線圖"
            ],
            key_activities=[
                "收集並分析各項指標數據",
                "進行策略成效評估",
                "識別改進機會",
                "制定調整計劃",
                "規劃下一年度路線圖",
                "進行年度總結"
            ],
            expected_outcomes=[
                "策略成效評估報告",
                "調整建議文檔",
                "下一年度技術路線圖",
                "年度總結報告"
            ],
            risks=[
                "數據收集不完整",
                "評估標準不一致",
                "規劃與實際脫節"
            ]
        )

        self.phases = [phase1, phase2, phase3, phase4]

    def get_current_phase(self) -> Phase | None:
        """獲取當前階段"""
        elapsed_days = (datetime.now() - self.start_date).days
        current_month = (elapsed_days // 30) + 1  # 簡化計算
        current_month = min(current_month, 12)

        for phase in self.phases:
            if phase.is_current(current_month):
                return phase
        return None

    def get_phase_by_id(self, phase_id: str) -> Phase | None:
        """根據 ID 獲取階段"""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None

    def add_milestone(self, phase_id: str, milestone: Milestone) -> bool:
        """添加里程碑到指定階段"""
        phase = self.get_phase_by_id(phase_id)
        if phase:
            phase.milestones.append(milestone)
            return True
        return False

    def add_task(self, phase_id: str, milestone_id: str, task: Task) -> bool:
        """添加任務到指定里程碑"""
        phase = self.get_phase_by_id(phase_id)
        if phase:
            for milestone in phase.milestones:
                if milestone.id == milestone_id:
                    milestone.tasks.append(task)
                    return True
        return False

    def overall_progress(self) -> float:
        """計算整體進度"""
        if not self.phases:
            return 0.0
        return sum(p.progress_percentage() for p in self.phases) / len(self.phases)

    def get_upcoming_milestones(self, days: int = 30) -> list[Milestone]:
        """獲取即將到期的里程碑"""
        upcoming = []
        cutoff_date = datetime.now() + timedelta(days=days)

        for phase in self.phases:
            for milestone in phase.milestones:
                if not milestone.completed and milestone.target_date <= cutoff_date:
                    upcoming.append(milestone)

        return sorted(upcoming, key=lambda m: m.target_date)

    def get_overdue_tasks(self) -> list[Task]:
        """獲取逾期任務"""
        overdue = []
        for phase in self.phases:
            for milestone in phase.milestones:
                for task in milestone.tasks:
                    if task.is_overdue():
                        overdue.append(task)
        return overdue

    def generate_report(self, format_type: str = "markdown") -> str:
        """
        生成實施計劃報告
        
        Args:
            format_type: 報告格式 (markdown/text)
        
        Returns:
            格式化的報告字符串
        """
        if format_type == "markdown":
            return self._generate_markdown_report()
        else:
            return self._generate_text_report()

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式報告"""
        lines = [
            f"# {self.project_name} - 12 個月實施計劃",
            "",
            f"**開始日期：** {self.start_date.strftime('%Y-%m-%d')}",
            f"**整體進度：** {self.overall_progress():.1f}%",
            "",
            "---",
            ""
        ]

        for phase in self.phases:
            lines.append(f"## {phase.name} (第 {phase.start_month}-{phase.end_month} 月)")
            lines.append("")
            lines.append(f"**階段類型：** {phase.phase_type.value}")
            lines.append(f"**進度：** {phase.progress_percentage():.1f}%")
            lines.append("")
            lines.append(f"**描述：** {phase.description}")
            lines.append("")

            if phase.objectives:
                lines.append("### 目標")
                for obj in phase.objectives:
                    lines.append(f"- {obj}")
                lines.append("")

            if phase.key_activities:
                lines.append("### 關鍵活動")
                for activity in phase.key_activities:
                    lines.append(f"- {activity}")
                lines.append("")

            if phase.milestones:
                lines.append("### 里程碑")
                for milestone in phase.milestones:
                    status = "✅" if milestone.completed else "⏳"
                    lines.append(f"- {status} **{milestone.name}** - {milestone.target_date.strftime('%Y-%m-%d')} ({milestone.progress_percentage():.0f}%)")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_text_report(self) -> str:
        """生成純文字格式報告"""
        lines = [
            f"{self.project_name} - 12 個月實施計劃",
            "=" * 50,
            "",
            f"開始日期：{self.start_date.strftime('%Y-%m-%d')}",
            f"整體進度：{self.overall_progress():.1f}%",
            "",
        ]

        for phase in self.phases:
            lines.append("-" * 50)
            lines.append(f"{phase.name} (第 {phase.start_month}-{phase.end_month} 月)")
            lines.append(f"進度：{phase.progress_percentage():.1f}%")
            lines.append(f"描述：{phase.description}")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'project_name': self.project_name,
            'start_date': self.start_date.isoformat(),
            'overall_progress': self.overall_progress(),
            'phases': [p.to_dict() for p in self.phases]
        }
