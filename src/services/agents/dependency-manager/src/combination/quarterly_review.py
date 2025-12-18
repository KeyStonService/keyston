"""
季度審查引擎
Quarterly Review Engine
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReviewStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ReviewCategory(Enum):
    MARKET_FEEDBACK = "market_feedback"
    INTERNAL_CAPABILITY = "internal_capability"
    FINANCIAL_PERFORMANCE = "financial_performance"
    STRATEGY_ALIGNMENT = "strategy_alignment"


@dataclass
class ReviewItem:
    category: ReviewCategory
    metric_name: str
    target_value: float
    actual_value: float
    unit: str = ""
    notes: str = ""

    @property
    def achievement_rate(self) -> float:
        return (self.actual_value / self.target_value * 100) if self.target_value else 0


@dataclass
class QuarterlyReview:
    quarter: str  # e.g., "2024Q1"
    start_date: datetime
    end_date: datetime
    status: ReviewStatus
    items: list[ReviewItem] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class QuarterlyReviewEngine:
    """季度審查引擎"""

    def __init__(self):
        self._reviews: dict[str, QuarterlyReview] = {}
        self._review_templates = self._load_templates()

    def _load_templates(self) -> dict[str, list[dict]]:
        return {
            'market_feedback': [
                {'metric': '用戶滿意度', 'target': 80.0, 'unit': '%'},
                {'metric': '競爭對手追蹤', 'target': 10.0, 'unit': '項'},
                {'metric': '市場趨勢監控', 'target': 5.0, 'unit': '項'},
            ],
            'internal_capability': [
                {'metric': '團隊技能成長', 'target': 15.0, 'unit': '%'},
                {'metric': '技術債務', 'target': 20.0, 'unit': '%'},
                {'metric': '資源利用率', 'target': 75.0, 'unit': '%'},
            ],
            'financial_performance': [
                {'metric': 'ROI達成率', 'target': 100.0, 'unit': '%'},
                {'metric': '成本控制', 'target': 100.0, 'unit': '%'},
                {'metric': '營收成長', 'target': 20.0, 'unit': '%'},
            ],
        }

    def create_review(self, quarter: str) -> QuarterlyReview:
        year = int(quarter[:4])
        q = int(quarter[-1])
        start_month = (q - 1) * 3 + 1

        start_date = datetime(year, start_month, 1)
        end_month = start_month + 2
        end_date = datetime(year, end_month, 28)

        review = QuarterlyReview(
            quarter=quarter,
            start_date=start_date,
            end_date=end_date,
            status=ReviewStatus.SCHEDULED
        )
        self._reviews[quarter] = review
        return review

    def add_review_item(self, quarter: str, category: ReviewCategory, metric: str, target: float, actual: float, unit: str = "", notes: str = ""):
        if quarter not in self._reviews:
            self.create_review(quarter)

        item = ReviewItem(category, metric, target, actual, unit, notes)
        self._reviews[quarter].items.append(item)

    def complete_review(self, quarter: str) -> QuarterlyReview:
        if quarter not in self._reviews:
            raise ValueError(f"審查 {quarter} 不存在")

        review = self._reviews[quarter]
        review.status = ReviewStatus.COMPLETED
        review.recommendations = self._generate_recommendations(review)
        review.next_actions = self._generate_actions(review)
        return review

    def _generate_recommendations(self, review: QuarterlyReview) -> list[str]:
        recs = []
        for item in review.items:
            if item.achievement_rate < 70:
                recs.append(f"建議加強 {item.metric_name}，目前達成率僅 {item.achievement_rate:.1f}%")
            elif item.achievement_rate > 120:
                recs.append(f"{item.metric_name} 表現優異，可考慮提高目標")

        if not recs:
            recs.append("整體表現良好，維持當前策略")
        return recs

    def _generate_actions(self, review: QuarterlyReview) -> list[str]:
        actions = []
        low_performers = [i for i in review.items if i.achievement_rate < 80]

        for item in low_performers[:3]:
            actions.append(f"制定 {item.metric_name} 改善計畫")

        if not actions:
            actions.append("持續監控並準備下季度審查")
        return actions

    def get_review(self, quarter: str) -> QuarterlyReview | None:
        return self._reviews.get(quarter)

    def list_reviews(self) -> list[dict]:
        return [{'quarter': r.quarter, 'status': r.status.value, 'items_count': len(r.items)} for r in self._reviews.values()]

    def generate_report(self, quarter: str, format_type: str = 'markdown') -> str:
        review = self._reviews.get(quarter)
        if not review:
            return f"審查 {quarter} 不存在"

        if format_type == 'markdown':
            return self._markdown_report(review)
        return self._text_report(review)

    def _markdown_report(self, review: QuarterlyReview) -> str:
        lines = [
            f"# 季度審查報告：{review.quarter}",
            f"**狀態：** {review.status.value}",
            f"**期間：** {review.start_date.strftime('%Y-%m-%d')} ~ {review.end_date.strftime('%Y-%m-%d')}",
            "",
            "## 審查項目",
            "| 類別 | 指標 | 目標 | 實際 | 達成率 |",
            "|------|------|------|------|--------|",
        ]

        for item in review.items:
            lines.append(f"| {item.category.value} | {item.metric_name} | {item.target_value}{item.unit} | {item.actual_value}{item.unit} | {item.achievement_rate:.1f}% |")

        if review.recommendations:
            lines.extend(["", "## 建議", ""])
            for r in review.recommendations:
                lines.append(f"- {r}")

        if review.next_actions:
            lines.extend(["", "## 下一步行動", ""])
            for a in review.next_actions:
                lines.append(f"- {a}")

        return '\n'.join(lines)

    def _text_report(self, review: QuarterlyReview) -> str:
        lines = [
            f"季度審查報告：{review.quarter}",
            "=" * 40,
            f"狀態：{review.status.value}",
            "",
            "審查項目：",
        ]

        for item in review.items:
            lines.append(f"  - {item.metric_name}: {item.actual_value}/{item.target_value} ({item.achievement_rate:.1f}%)")

        return '\n'.join(lines)
