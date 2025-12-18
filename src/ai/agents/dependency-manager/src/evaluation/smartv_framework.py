"""
SMART-V 評估框架

提供六維度量化評估模型：
- S: Scalability (可擴展性)
- M: Market Fit (市場適配度)
- A: Achievability (可實現性)
- R: ROI (投資報酬率)
- T: Technology Maturity (技術成熟度)
- V: Value Creation (價值創造)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json


class EvaluationDimension(Enum):
    """評估維度枚舉"""
    SCALABILITY = "scalability"
    MARKET_FIT = "market_fit"
    ACHIEVABILITY = "achievability"
    ROI = "roi"
    TECHNOLOGY_MATURITY = "technology_maturity"
    VALUE_CREATION = "value_creation"


class ScoreLevel(Enum):
    """評分等級"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


@dataclass
class EvaluationCriteria:
    """評估標準"""
    name: str
    description: str
    weight: float = 1.0
    min_score: int = 1
    max_score: int = 10


@dataclass
class DimensionScore:
    """維度評分結果"""
    dimension: EvaluationDimension
    score: float
    max_score: float = 10.0
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100
    
    @property
    def level(self) -> ScoreLevel:
        if self.score >= 9:
            return ScoreLevel.EXCELLENT
        elif self.score >= 7:
            return ScoreLevel.GOOD
        elif self.score >= 5:
            return ScoreLevel.AVERAGE
        elif self.score >= 3:
            return ScoreLevel.BELOW_AVERAGE
        else:
            return ScoreLevel.POOR


@dataclass
class SMARTVResult:
    """SMART-V 評估結果"""
    scores: Dict[EvaluationDimension, DimensionScore]
    weights: Dict[EvaluationDimension, float]
    weighted_total: float
    overall_grade: str
    recommendations: List[str]
    evaluation_date: str
    project_name: str
    evaluator: str = "SMART-V Framework"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "evaluation_date": self.evaluation_date,
            "evaluator": self.evaluator,
            "weighted_total": round(self.weighted_total, 2),
            "overall_grade": self.overall_grade,
            "scores": {
                dim.value: {
                    "score": score.score,
                    "percentage": round(score.percentage, 1),
                    "level": score.level.value,
                    "weight": self.weights[dim],
                    "weighted_score": round(score.score * self.weights[dim], 2),
                }
                for dim, score in self.scores.items()
            },
            "overall_recommendations": self.recommendations
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class BaseEvaluator:
    """評估器基類"""
    
    dimension: EvaluationDimension = None
    criteria: List[EvaluationCriteria] = []
    
    def __init__(self):
        self.criteria = self._get_criteria()
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return []
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        """Evaluate data based on configured criteria

        Args:
            data: Data to evaluate

        Returns:
            DimensionScore with evaluation results
        """
        if not self.dimension:
            raise ValueError("Dimension must be set in subclass")

        sub_scores = {}
        evidences = []

        # Evaluate each criterion
        for criterion in self.criteria:
            try:
                score = self._evaluate_criterion(criterion, data)
                sub_scores[criterion.name] = score

                # Collect evidence
                if score < criterion.threshold:
                    evidences.append(f"{criterion.name}: {score:.2f} (below threshold {criterion.threshold})")
            except Exception as e:
                logger.error(f"Error evaluating criterion {criterion.name}: {e}")
                sub_scores[criterion.name] = 0.0

        # Calculate overall score
        overall_score = self._calculate_score(sub_scores)

        return DimensionScore(
            dimension=self.dimension.value,
            score=overall_score,
            max_score=1.0,
            sub_scores=sub_scores,
            evidences=evidences
        )

    def _evaluate_criterion(self, criterion: EvaluationCriteria, data: Dict[str, Any]) -> float:
        """Evaluate a single criterion - override in subclass for custom logic

        Args:
            criterion: Criterion to evaluate
            data: Data to evaluate

        Returns:
            Score between 0.0 and 1.0
        """
        # Default implementation - subclasses should override
        return 1.0
    
    def _calculate_score(self, sub_scores: Dict[str, float]) -> float:
        if not sub_scores:
            return 0.0
        total_weight = sum(c.weight for c in self.criteria if c.name in sub_scores)
        if total_weight == 0:
            return sum(sub_scores.values()) / len(sub_scores)
        weighted_sum = sum(
            sub_scores.get(c.name, 0) * c.weight
            for c in self.criteria if c.name in sub_scores
        )
        return weighted_sum / total_weight
    
    def _generate_recommendations(self, sub_scores: Dict[str, float]) -> List[str]:
        recommendations = []
        for criterion in self.criteria:
            score = sub_scores.get(criterion.name, 0)
            if score < 5:
                recommendations.append(f"需要大幅改進 {criterion.description}")
            elif score < 7:
                recommendations.append(f"建議優化 {criterion.description}")
        return recommendations


class ScalabilityEvaluator(BaseEvaluator):
    """可擴展性評估器"""
    dimension = EvaluationDimension.SCALABILITY
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="architecture_scalability", description="技術架構可擴展性", weight=0.35),
            EvaluationCriteria(name="user_growth_potential", description="用戶增長潛力", weight=0.30),
            EvaluationCriteria(name="load_capacity", description="系統負載承受能力", weight=0.20),
            EvaluationCriteria(name="horizontal_scaling", description="水平擴展能力", weight=0.15),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "architecture_scalability": self._eval_arch(data),
            "user_growth_potential": self._eval_growth(data),
            "load_capacity": self._eval_load(data),
            "horizontal_scaling": self._eval_scale(data),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_arch(self, data: Dict[str, Any]) -> float:
        score = 5.0
        if data.get("microservices"): score += 2.0
        if data.get("containerized"): score += 1.5
        if data.get("cloud_native"): score += 1.5
        return min(score, 10.0)
    
    def _eval_growth(self, data: Dict[str, Any]) -> float:
        rate = data.get("growth_rate", 0)
        if rate >= 100: return 10.0
        elif rate >= 50: return 8.0
        elif rate >= 20: return 6.0
        elif rate >= 10: return 4.0
        return 2.0
    
    def _eval_load(self, data: Dict[str, Any]) -> float:
        current = data.get("current_rps", 0)
        max_rps = data.get("max_rps", 0)
        if max_rps == 0: return 5.0
        util = current / max_rps
        if util < 0.3: return 10.0
        elif util < 0.5: return 8.0
        elif util < 0.7: return 6.0
        elif util < 0.9: return 4.0
        return 2.0
    
    def _eval_scale(self, data: Dict[str, Any]) -> float:
        score = 4.0
        if data.get("auto_scaling"): score += 3.0
        if data.get("load_balancer"): score += 2.0
        if data.get("stateless"): score += 1.0
        return min(score, 10.0)


class MarketFitEvaluator(BaseEvaluator):
    """市場適配度評估器"""
    dimension = EvaluationDimension.MARKET_FIT
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="user_needs_match", description="目標用戶需求匹配度", weight=0.35),
            EvaluationCriteria(name="market_timing", description="市場時機成熟度", weight=0.25),
            EvaluationCriteria(name="competitive_analysis", description="競爭環境分析", weight=0.25),
            EvaluationCriteria(name="market_size", description="市場規模潛力", weight=0.15),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "user_needs_match": min(data.get("user_needs_score", 5), 10),
            "market_timing": self._eval_timing(data),
            "competitive_analysis": self._eval_competition(data),
            "market_size": self._eval_market(data),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_timing(self, data: Dict[str, Any]) -> float:
        maturity = data.get("market_maturity", "emerging")
        scores = {"emerging": 6.0, "growing": 9.0, "mature": 7.0, "declining": 3.0}
        return scores.get(maturity, 5.0)
    
    def _eval_competition(self, data: Dict[str, Any]) -> float:
        competitors = data.get("competitor_count", 0)
        diff = data.get("differentiation_level", "low")
        score = 5.0
        if competitors == 0: score += 2.0
        elif competitors <= 3: score += 1.0
        elif competitors > 10: score -= 1.0
        diff_bonus = {"high": 3.0, "medium": 1.5, "low": 0}
        return min(max(score + diff_bonus.get(diff, 0), 1.0), 10.0)
    
    def _eval_market(self, data: Dict[str, Any]) -> float:
        som = data.get("som", 0)
        if som >= 1_000_000_000: return 10.0
        elif som >= 100_000_000: return 8.0
        elif som >= 10_000_000: return 6.0
        elif som >= 1_000_000: return 4.0
        return 2.0


class AchievabilityEvaluator(BaseEvaluator):
    """可實現性評估器"""
    dimension = EvaluationDimension.ACHIEVABILITY
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="team_capability", description="團隊技術能力匹配度", weight=0.35),
            EvaluationCriteria(name="budget_timeline", description="預算與時程合理性", weight=0.30),
            EvaluationCriteria(name="technical_risk", description="技術風險評估", weight=0.20),
            EvaluationCriteria(name="resource_availability", description="資源可用性", weight=0.15),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "team_capability": self._eval_team(data),
            "budget_timeline": self._eval_budget(data),
            "technical_risk": self._eval_risk(data),
            "resource_availability": min(data.get("resource_availability_score", 5), 10),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_team(self, data: Dict[str, Any]) -> float:
        coverage = data.get("skill_coverage", 0)
        exp = data.get("experience_years", 0)
        score = 3.0 + (coverage / 100) * 4
        if exp >= 5: score += 3.0
        elif exp >= 3: score += 2.0
        elif exp >= 1: score += 1.0
        return min(score, 10.0)
    
    def _eval_budget(self, data: Dict[str, Any]) -> float:
        score = 4.0
        if data.get("budget_adequate"): score += 2.0
        if data.get("timeline_realistic"): score += 2.0
        buffer = data.get("buffer_percentage", 0)
        if buffer >= 20: score += 2.0
        elif buffer >= 10: score += 1.0
        return min(score, 10.0)
    
    def _eval_risk(self, data: Dict[str, Any]) -> float:
        risk = data.get("risk_level", "medium")
        scores = {"very_low": 10.0, "low": 8.0, "medium": 6.0, "high": 4.0, "very_high": 2.0}
        base = scores.get(risk, 5.0)
        mitigation = min(len(data.get("mitigation_plans", [])) * 0.5, 2.0)
        return min(base + mitigation, 10.0)


class ROIEvaluator(BaseEvaluator):
    """投資報酬率評估器"""
    dimension = EvaluationDimension.ROI
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="financial_return", description="預期財務回報", weight=0.40),
            EvaluationCriteria(name="cost_benefit", description="成本效益分析", weight=0.35),
            EvaluationCriteria(name="resource_efficiency", description="資源利用效率", weight=0.25),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "financial_return": self._eval_return(data),
            "cost_benefit": self._eval_cost(data),
            "resource_efficiency": self._eval_efficiency(data),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_return(self, data: Dict[str, Any]) -> float:
        roi = data.get("roi_percentage", 0)
        payback = data.get("payback_months", 36)
        roi_score = 10.0 if roi >= 300 else 8.0 if roi >= 200 else 6.0 if roi >= 100 else 4.0 if roi >= 50 else 2.0
        payback_score = 10.0 if payback <= 6 else 8.0 if payback <= 12 else 6.0 if payback <= 24 else 4.0 if payback <= 36 else 2.0
        return roi_score * 0.6 + payback_score * 0.4
    
    def _eval_cost(self, data: Dict[str, Any]) -> float:
        npv = data.get("npv", 0)
        irr = data.get("irr", 0)
        score = 5.0
        if npv > 0: score += 2.0
        if irr > 20: score += 3.0
        elif irr > 10: score += 2.0
        elif irr > 0: score += 1.0
        return min(score, 10.0)
    
    def _eval_efficiency(self, data: Dict[str, Any]) -> float:
        productivity = data.get("productivity_gain", 0)
        automation = data.get("automation_level", 0)
        return min(3.0 + (productivity / 100) * 4 + (automation / 100) * 3, 10.0)


class TechnologyMaturityEvaluator(BaseEvaluator):
    """技術成熟度評估器"""
    dimension = EvaluationDimension.TECHNOLOGY_MATURITY
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="tech_stability", description="相關技術穩定程度", weight=0.35),
            EvaluationCriteria(name="ecosystem", description="生態系統完整性", weight=0.35),
            EvaluationCriteria(name="learning_curve", description="學習曲線陡峭程度", weight=0.30),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "tech_stability": self._eval_stability(data),
            "ecosystem": self._eval_ecosystem(data),
            "learning_curve": self._eval_learning(data),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_stability(self, data: Dict[str, Any]) -> float:
        age = data.get("tech_age_years", 0)
        breaking = data.get("breaking_changes_yearly", 5)
        age_score = 10.0 if age >= 10 else 8.0 if age >= 5 else 6.0 if age >= 3 else 4.0 if age >= 1 else 2.0
        return max(age_score - min(breaking * 0.5, 3.0), 1.0)
    
    def _eval_ecosystem(self, data: Dict[str, Any]) -> float:
        libs = data.get("library_count", 0)
        community = data.get("community_size", 0)
        enterprise = data.get("enterprise_adoption", 0)
        score = 2.0
        if libs >= 10000: score += 2.5
        elif libs >= 1000: score += 2.0
        elif libs >= 100: score += 1.0
        if community >= 1000000: score += 2.5
        elif community >= 100000: score += 2.0
        elif community >= 10000: score += 1.0
        score += (enterprise / 100) * 3
        return min(score, 10.0)
    
    def _eval_learning(self, data: Dict[str, Any]) -> float:
        doc = data.get("documentation_quality", "medium")
        days = data.get("avg_onboarding_days", 30)
        doc_scores = {"excellent": 4.0, "good": 3.0, "medium": 2.0, "poor": 1.0}
        score = doc_scores.get(doc, 2.0)
        if days <= 7: score += 6.0
        elif days <= 14: score += 5.0
        elif days <= 30: score += 4.0
        elif days <= 60: score += 2.0
        else: score += 1.0
        return min(score, 10.0)


class ValueCreationEvaluator(BaseEvaluator):
    """價值創造評估器"""
    dimension = EvaluationDimension.VALUE_CREATION
    
    def _get_criteria(self) -> List[EvaluationCriteria]:
        return [
            EvaluationCriteria(name="competitive_advantage", description="長期競爭優勢", weight=0.35),
            EvaluationCriteria(name="brand_value", description="品牌價值提升", weight=0.30),
            EvaluationCriteria(name="innovation_impact", description="創新影響力", weight=0.35),
        ]
    
    def evaluate(self, data: Dict[str, Any]) -> DimensionScore:
        sub_scores = {
            "competitive_advantage": self._eval_advantage(data),
            "brand_value": self._eval_brand(data),
            "innovation_impact": self._eval_innovation(data),
        }
        return DimensionScore(
            dimension=self.dimension,
            score=self._calculate_score(sub_scores),
            details=sub_scores,
            recommendations=self._generate_recommendations(sub_scores)
        )
    
    def _eval_advantage(self, data: Dict[str, Any]) -> float:
        moat = data.get("moat_strength", "low")
        switching = data.get("switching_cost", "low")
        network = data.get("network_effects", False)
        moat_scores = {"very_high": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}
        switching_scores = {"very_high": 3.0, "high": 2.5, "medium": 1.5, "low": 0.5}
        score = 2.0 + moat_scores.get(moat, 1.0) + switching_scores.get(switching, 0.5)
        if network: score += 2.0
        return min(score, 10.0)
    
    def _eval_brand(self, data: Dict[str, Any]) -> float:
        recognition = data.get("brand_recognition", 0)
        loyalty = data.get("customer_loyalty", 0)
        nps = data.get("nps_score", 0)
        score = 2.0 + (recognition / 100) * 3 + (loyalty / 100) * 3
        if nps >= 50: score += 2.0
        elif nps >= 20: score += 1.5
        elif nps >= 0: score += 1.0
        return min(score, 10.0)
    
    def _eval_innovation(self, data: Dict[str, Any]) -> float:
        patents = data.get("patents", 0)
        industry_first = data.get("industry_first", False)
        leadership = data.get("tech_leadership", False)
        score = 3.0
        if patents >= 10: score += 2.0
        elif patents >= 5: score += 1.5
        elif patents >= 1: score += 1.0
        if industry_first: score += 2.5
        if leadership: score += 2.0
        return min(score, 10.0)


class SMARTVFramework:
    """SMART-V 評估框架主類"""
    
    def __init__(self):
        self.evaluators = {
            EvaluationDimension.SCALABILITY: ScalabilityEvaluator(),
            EvaluationDimension.MARKET_FIT: MarketFitEvaluator(),
            EvaluationDimension.ACHIEVABILITY: AchievabilityEvaluator(),
            EvaluationDimension.ROI: ROIEvaluator(),
            EvaluationDimension.TECHNOLOGY_MATURITY: TechnologyMaturityEvaluator(),
            EvaluationDimension.VALUE_CREATION: ValueCreationEvaluator(),
        }
        self.default_weights = {
            EvaluationDimension.SCALABILITY: 0.15,
            EvaluationDimension.MARKET_FIT: 0.20,
            EvaluationDimension.ACHIEVABILITY: 0.15,
            EvaluationDimension.ROI: 0.20,
            EvaluationDimension.TECHNOLOGY_MATURITY: 0.15,
            EvaluationDimension.VALUE_CREATION: 0.15,
        }
    
    def evaluate(self, project_name: str, data: Dict[str, Any], weights: Optional[Dict[EvaluationDimension, float]] = None) -> SMARTVResult:
        active_weights = weights or self.default_weights
        total = sum(active_weights.values())
        normalized = {k: v / total for k, v in active_weights.items()}
        
        scores = {}
        for dim, evaluator in self.evaluators.items():
            scores[dim] = evaluator.evaluate(data.get(dim.value, {}))
        
        weighted_total = sum(scores[d].score * normalized[d] for d in scores)
        grade = self._grade(weighted_total)
        
        recs = []
        for dim, score in scores.items():
            if score.score < 6:
                recs.extend([f"[{dim.value}] {r}" for r in score.recommendations[:2]])
        
        return SMARTVResult(
            scores=scores, weights=normalized, weighted_total=weighted_total,
            overall_grade=grade, recommendations=recs[:10],
            evaluation_date=datetime.now().isoformat(), project_name=project_name
        )
    
    def _grade(self, score: float) -> str:
        if score >= 9.0: return "A+"
        elif score >= 8.5: return "A"
        elif score >= 8.0: return "A-"
        elif score >= 7.5: return "B+"
        elif score >= 7.0: return "B"
        elif score >= 6.5: return "B-"
        elif score >= 6.0: return "C+"
        elif score >= 5.5: return "C"
        elif score >= 5.0: return "C-"
        elif score >= 4.0: return "D"
        return "F"
    
    def get_startup_weights(self) -> Dict[EvaluationDimension, float]:
        return {
            EvaluationDimension.MARKET_FIT: 0.25, EvaluationDimension.ROI: 0.25,
            EvaluationDimension.ACHIEVABILITY: 0.20, EvaluationDimension.VALUE_CREATION: 0.15,
            EvaluationDimension.SCALABILITY: 0.10, EvaluationDimension.TECHNOLOGY_MATURITY: 0.05,
        }
    
    def get_enterprise_weights(self) -> Dict[EvaluationDimension, float]:
        return {
            EvaluationDimension.SCALABILITY: 0.25, EvaluationDimension.TECHNOLOGY_MATURITY: 0.20,
            EvaluationDimension.VALUE_CREATION: 0.20, EvaluationDimension.ROI: 0.15,
            EvaluationDimension.MARKET_FIT: 0.15, EvaluationDimension.ACHIEVABILITY: 0.05,
        }
    
    def get_growth_weights(self) -> Dict[EvaluationDimension, float]:
        return {
            EvaluationDimension.SCALABILITY: 0.20, EvaluationDimension.MARKET_FIT: 0.20,
            EvaluationDimension.ROI: 0.20, EvaluationDimension.VALUE_CREATION: 0.15,
            EvaluationDimension.ACHIEVABILITY: 0.15, EvaluationDimension.TECHNOLOGY_MATURITY: 0.10,
        }
