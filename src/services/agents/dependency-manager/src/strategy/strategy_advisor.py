"""
策略顧問 - 技術能力評估與市場時機分析

此模組提供：
- 技術能力評估框架
- 市場時機分析
- 競爭對手分析
- 策略推薦生成

Copyright (c) 2024 SynergyMesh
MIT License
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CapabilityLevel(Enum):
    """能力等級"""
    NOVICE = "初學"
    BEGINNER = "入門"
    INTERMEDIATE = "中級"
    ADVANCED = "高級"
    EXPERT = "專家"


class MarketMaturity(Enum):
    """市場成熟度"""
    EMERGING = "新興市場"
    GROWING = "成長市場"
    MATURE = "成熟市場"
    DECLINING = "衰退市場"


class StrategicPriority(Enum):
    """策略優先級"""
    CRITICAL = "關鍵"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"
    OPTIONAL = "可選"


@dataclass
class TechCapability:
    """技術能力項目"""
    name: str
    level: CapabilityLevel
    team_members: int
    experience_years: float
    certifications: list[str] = field(default_factory=list)
    tools_proficiency: dict[str, str] = field(default_factory=dict)

    def get_score(self) -> int:
        """計算能力分數 (0-100)"""
        level_scores = {
            CapabilityLevel.NOVICE: 20,
            CapabilityLevel.BEGINNER: 40,
            CapabilityLevel.INTERMEDIATE: 60,
            CapabilityLevel.ADVANCED: 80,
            CapabilityLevel.EXPERT: 100
        }
        base = level_scores[self.level]

        # 加分項
        exp_bonus = min(10, self.experience_years * 2)
        cert_bonus = min(10, len(self.certifications) * 2)
        team_bonus = min(10, self.team_members)

        return min(100, base + exp_bonus + cert_bonus + team_bonus)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'name': self.name,
            'level': self.level.value,
            'team_members': self.team_members,
            'experience_years': self.experience_years,
            'certifications': self.certifications,
            'tools_proficiency': self.tools_proficiency,
            'score': self.get_score()
        }


@dataclass
class TechCapabilityAssessment:
    """技術能力評估報告"""
    assessed_at: datetime
    capabilities: dict[str, TechCapability]
    infrastructure_readiness: float  # 0-1
    process_maturity: float  # 0-1
    culture_alignment: float  # 0-1

    def get_overall_score(self) -> float:
        """計算整體分數"""
        if not self.capabilities:
            return 0.0

        cap_avg = sum(c.get_score() for c in self.capabilities.values()) / len(self.capabilities)

        weighted = (
            cap_avg * 0.5 +
            self.infrastructure_readiness * 100 * 0.2 +
            self.process_maturity * 100 * 0.15 +
            self.culture_alignment * 100 * 0.15
        )

        return round(weighted, 2)

    def get_strengths(self) -> list[str]:
        """獲取優勢領域"""
        return [
            name for name, cap in self.capabilities.items()
            if cap.get_score() >= 70
        ]

    def get_gaps(self) -> list[str]:
        """獲取能力缺口"""
        return [
            name for name, cap in self.capabilities.items()
            if cap.get_score() < 50
        ]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'assessed_at': self.assessed_at.isoformat(),
            'capabilities': {k: v.to_dict() for k, v in self.capabilities.items()},
            'infrastructure_readiness': self.infrastructure_readiness,
            'process_maturity': self.process_maturity,
            'culture_alignment': self.culture_alignment,
            'overall_score': self.get_overall_score(),
            'strengths': self.get_strengths(),
            'gaps': self.get_gaps()
        }


@dataclass
class CompetitorProfile:
    """競爭對手資料"""
    name: str
    market_share: float
    strengths: list[str]
    weaknesses: list[str]
    recent_moves: list[str]
    threat_level: str  # low, medium, high


@dataclass
class MarketTimingAnalysis:
    """市場時機分析"""
    analyzed_at: datetime
    market_name: str
    maturity: MarketMaturity
    growth_rate: float  # 年增長率
    market_size: float  # 市場規模 (USD)
    entry_barriers: list[str]
    opportunities: list[str]
    threats: list[str]
    competitors: list[CompetitorProfile]
    timing_score: float  # 進入時機分數 0-100
    window_duration_months: int | None  # 機會窗口

    def get_recommendation(self) -> str:
        """獲取進入建議"""
        if self.timing_score >= 80:
            return "強烈建議立即進入"
        elif self.timing_score >= 60:
            return "建議積極準備進入"
        elif self.timing_score >= 40:
            return "建議觀望並持續評估"
        else:
            return "建議暫緩，等待更好時機"

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'analyzed_at': self.analyzed_at.isoformat(),
            'market_name': self.market_name,
            'maturity': self.maturity.value,
            'growth_rate': self.growth_rate,
            'market_size': self.market_size,
            'entry_barriers': self.entry_barriers,
            'opportunities': self.opportunities,
            'threats': self.threats,
            'competitors': [vars(c) for c in self.competitors],
            'timing_score': self.timing_score,
            'window_duration_months': self.window_duration_months,
            'recommendation': self.get_recommendation()
        }


@dataclass
class StrategyRecommendation:
    """策略推薦"""
    strategy_name: str
    priority: StrategicPriority
    rationale: str
    prerequisites: list[str]
    expected_outcomes: list[str]
    estimated_timeline_months: int
    estimated_investment: dict[str, float]  # 各類投資金額
    risks: list[dict[str, str]]  # risk, mitigation
    success_metrics: dict[str, str]
    confidence_score: float  # 0-100

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'strategy_name': self.strategy_name,
            'priority': self.priority.value,
            'rationale': self.rationale,
            'prerequisites': self.prerequisites,
            'expected_outcomes': self.expected_outcomes,
            'estimated_timeline_months': self.estimated_timeline_months,
            'estimated_investment': self.estimated_investment,
            'risks': self.risks,
            'success_metrics': self.success_metrics,
            'confidence_score': self.confidence_score
        }


class StrategyAdvisor:
    """
    策略顧問
    
    提供全面的策略建議服務：
    - 技術能力評估
    - 市場時機分析
    - 競爭對手分析
    - 策略推薦
    """

    def __init__(self):
        """初始化策略顧問"""
        self._capability_frameworks = self._load_capability_frameworks()
        self._market_data = {}
        self._competitor_db = {}

    def _load_capability_frameworks(self) -> dict[str, list[str]]:
        """載入能力評估框架"""
        return {
            'development': [
                'frontend', 'backend', 'mobile', 'devops',
                'database', 'cloud', 'security', 'testing'
            ],
            'data': [
                'analytics', 'ml_ai', 'data_engineering',
                'visualization', 'governance'
            ],
            'business': [
                'product_management', 'ux_design', 'marketing',
                'sales', 'customer_success'
            ],
            'infrastructure': [
                'networking', 'storage', 'compute',
                'monitoring', 'disaster_recovery'
            ]
        }

    def assess_capabilities(
        self,
        team_profile: dict[str, Any],
        focus_areas: list[str] | None = None
    ) -> TechCapabilityAssessment:
        """
        評估團隊技術能力
        
        Args:
            team_profile: 團隊資料
            focus_areas: 重點評估領域
            
        Returns:
            技術能力評估報告
        """
        capabilities = {}

        # 處理團隊技能資料
        skills = team_profile.get('skills', {})
        for skill_name, skill_data in skills.items():
            if focus_areas and skill_name not in focus_areas:
                continue

            # 解析能力等級
            level_str = skill_data.get('level', 'beginner')
            level_map = {
                'novice': CapabilityLevel.NOVICE,
                'beginner': CapabilityLevel.BEGINNER,
                'intermediate': CapabilityLevel.INTERMEDIATE,
                'advanced': CapabilityLevel.ADVANCED,
                'expert': CapabilityLevel.EXPERT
            }
            level = level_map.get(level_str.lower(), CapabilityLevel.BEGINNER)

            capabilities[skill_name] = TechCapability(
                name=skill_name,
                level=level,
                team_members=skill_data.get('team_members', 1),
                experience_years=skill_data.get('experience_years', 1.0),
                certifications=skill_data.get('certifications', []),
                tools_proficiency=skill_data.get('tools', {})
            )

        # 評估基礎設施就緒度
        infra = team_profile.get('infrastructure', {})
        infra_score = self._calculate_infra_score(infra)

        # 評估流程成熟度
        process = team_profile.get('process', {})
        process_score = self._calculate_process_score(process)

        # 評估文化契合度
        culture = team_profile.get('culture', {})
        culture_score = self._calculate_culture_score(culture)

        return TechCapabilityAssessment(
            assessed_at=datetime.now(),
            capabilities=capabilities,
            infrastructure_readiness=infra_score,
            process_maturity=process_score,
            culture_alignment=culture_score
        )

    def _calculate_infra_score(self, infra: dict) -> float:
        """計算基礎設施分數"""
        factors = {
            'has_cloud': 0.3,
            'has_ci_cd': 0.25,
            'has_monitoring': 0.2,
            'has_security': 0.15,
            'has_backup': 0.1
        }

        score = 0.0
        for factor, weight in factors.items():
            if infra.get(factor, False):
                score += weight

        return score

    def _calculate_process_score(self, process: dict) -> float:
        """計算流程成熟度分數"""
        factors = {
            'has_agile': 0.2,
            'has_code_review': 0.2,
            'has_documentation': 0.15,
            'has_testing': 0.2,
            'has_release_process': 0.15,
            'has_incident_response': 0.1
        }

        score = 0.0
        for factor, weight in factors.items():
            if process.get(factor, False):
                score += weight

        return score

    def _calculate_culture_score(self, culture: dict) -> float:
        """計算文化契合度分數"""
        factors = {
            'innovation_mindset': 0.25,
            'customer_focus': 0.25,
            'collaboration': 0.2,
            'continuous_learning': 0.15,
            'risk_tolerance': 0.15
        }

        score = 0.0
        for factor, weight in factors.items():
            value = culture.get(factor, 0.5)
            score += value * weight

        return score

    def analyze_market_timing(
        self,
        market_name: str,
        market_data: dict | None = None
    ) -> MarketTimingAnalysis:
        """
        分析市場進入時機
        
        Args:
            market_name: 市場名稱
            market_data: 市場數據（可選）
            
        Returns:
            市場時機分析報告
        """
        # 使用提供的數據或預設數據
        data = market_data or self._get_default_market_data(market_name)

        # 判斷市場成熟度
        growth_rate = data.get('growth_rate', 0.1)
        if growth_rate > 0.3:
            maturity = MarketMaturity.EMERGING
        elif growth_rate > 0.1:
            maturity = MarketMaturity.GROWING
        elif growth_rate > 0:
            maturity = MarketMaturity.MATURE
        else:
            maturity = MarketMaturity.DECLINING

        # 解析競爭對手
        competitors = []
        for comp_data in data.get('competitors', []):
            competitors.append(CompetitorProfile(
                name=comp_data.get('name', 'Unknown'),
                market_share=comp_data.get('market_share', 0),
                strengths=comp_data.get('strengths', []),
                weaknesses=comp_data.get('weaknesses', []),
                recent_moves=comp_data.get('recent_moves', []),
                threat_level=comp_data.get('threat_level', 'medium')
            ))

        # 計算時機分數
        timing_score = self._calculate_timing_score(data, maturity, competitors)

        return MarketTimingAnalysis(
            analyzed_at=datetime.now(),
            market_name=market_name,
            maturity=maturity,
            growth_rate=growth_rate,
            market_size=data.get('market_size', 0),
            entry_barriers=data.get('entry_barriers', []),
            opportunities=data.get('opportunities', []),
            threats=data.get('threats', []),
            competitors=competitors,
            timing_score=timing_score,
            window_duration_months=data.get('window_months')
        )

    def _get_default_market_data(self, market_name: str) -> dict:
        """獲取預設市場數據"""
        defaults = {
            'saas': {
                'growth_rate': 0.18,
                'market_size': 195000000000,
                'entry_barriers': ['技術門檻', '客戶獲取成本', '資金需求'],
                'opportunities': ['企業數位轉型', '遠程工作需求', 'AI 整合'],
                'threats': ['競爭激烈', '客戶流失', '定價壓力'],
                'window_months': 24
            },
            'fintech': {
                'growth_rate': 0.25,
                'market_size': 340000000000,
                'entry_barriers': ['監管合規', '資金需求', '信任建立'],
                'opportunities': ['數位支付', '嵌入式金融', '加密貨幣'],
                'threats': ['監管風險', '傳統銀行競爭', '安全事件'],
                'window_months': 18
            },
            'ai_ml': {
                'growth_rate': 0.35,
                'market_size': 150000000000,
                'entry_barriers': ['人才稀缺', '運算資源', '數據需求'],
                'opportunities': ['自動化需求', '決策支援', '個性化服務'],
                'threats': ['技術變化快', '倫理問題', '大廠競爭'],
                'window_months': 12
            },
            'ecommerce': {
                'growth_rate': 0.12,
                'market_size': 5700000000000,
                'entry_barriers': ['物流建設', '品牌認知', '價格競爭'],
                'opportunities': ['跨境電商', '社交電商', 'D2C 模式'],
                'threats': ['巨頭壟斷', '利潤壓縮', '客戶獲取成本'],
                'window_months': 36
            }
        }

        return defaults.get(market_name.lower().replace(' ', '_'), {
            'growth_rate': 0.1,
            'market_size': 1000000000,
            'entry_barriers': ['未知'],
            'opportunities': ['待評估'],
            'threats': ['待評估'],
            'window_months': 24
        })

    def _calculate_timing_score(
        self,
        data: dict,
        maturity: MarketMaturity,
        competitors: list[CompetitorProfile]
    ) -> float:
        """計算市場進入時機分數"""
        score = 50.0  # 基礎分

        # 根據成熟度調整
        maturity_adjustments = {
            MarketMaturity.EMERGING: 20,
            MarketMaturity.GROWING: 15,
            MarketMaturity.MATURE: -5,
            MarketMaturity.DECLINING: -20
        }
        score += maturity_adjustments.get(maturity, 0)

        # 根據增長率調整
        growth_rate = data.get('growth_rate', 0)
        if growth_rate > 0.2:
            score += 15
        elif growth_rate > 0.1:
            score += 10
        elif growth_rate < 0:
            score -= 15

        # 根據競爭強度調整
        if competitors:
            high_threat = sum(1 for c in competitors if c.threat_level == 'high')
            if high_threat > 2:
                score -= 15
            elif high_threat > 0:
                score -= 5

        # 根據機會數量調整
        opps = len(data.get('opportunities', []))
        score += min(10, opps * 3)

        # 根據威脅數量調整
        threats = len(data.get('threats', []))
        score -= min(10, threats * 2)

        return max(0, min(100, score))

    def generate_recommendations(
        self,
        capability_assessment: TechCapabilityAssessment,
        market_analysis: MarketTimingAnalysis,
        business_goals: list[str],
        constraints: dict | None = None
    ) -> list[StrategyRecommendation]:
        """
        生成策略推薦
        
        Args:
            capability_assessment: 能力評估
            market_analysis: 市場分析
            business_goals: 業務目標
            constraints: 限制條件
            
        Returns:
            策略推薦列表
        """
        recommendations = []
        constraints = constraints or {}

        # 分析能力與市場的匹配度
        overall_score = capability_assessment.get_overall_score()
        timing_score = market_analysis.timing_score

        # 根據能力水平推薦策略
        if overall_score >= 70 and timing_score >= 60:
            # 高能力 + 好時機 → 積極擴張
            recommendations.append(self._create_expansion_strategy(
                capability_assessment, market_analysis, constraints
            ))

        if overall_score < 50:
            # 能力不足 → 建設基礎
            recommendations.append(self._create_foundation_strategy(
                capability_assessment, constraints
            ))

        if 'growth' in [g.lower() for g in business_goals]:
            # 追求增長 → 市場擴張策略
            recommendations.append(self._create_growth_strategy(
                market_analysis, constraints
            ))

        if 'innovation' in [g.lower() for g in business_goals]:
            # 追求創新 → 技術創新策略
            recommendations.append(self._create_innovation_strategy(
                capability_assessment, constraints
            ))

        if 'profitability' in [g.lower() for g in business_goals]:
            # 追求獲利 → 效率優化策略
            recommendations.append(self._create_efficiency_strategy(
                capability_assessment, constraints
            ))

        # 按優先級和信心分數排序
        recommendations.sort(
            key=lambda r: (
                list(StrategicPriority).index(r.priority),
                -r.confidence_score
            )
        )

        return recommendations

    def _create_expansion_strategy(
        self,
        cap: TechCapabilityAssessment,
        market: MarketTimingAnalysis,
        constraints: dict
    ) -> StrategyRecommendation:
        """創建擴張策略"""
        budget = constraints.get('budget', 1000000)

        return StrategyRecommendation(
            strategy_name="積極市場擴張",
            priority=StrategicPriority.HIGH,
            rationale=f"團隊能力 ({cap.get_overall_score():.0f}分) 與市場時機 ({market.timing_score:.0f}分) 均有利",
            prerequisites=[
                "完成核心產品開發",
                "建立基礎客戶群",
                "確保資金到位"
            ],
            expected_outcomes=[
                "市場份額提升 20%",
                "營收增長 50%",
                "品牌知名度提升"
            ],
            estimated_timeline_months=18,
            estimated_investment={
                'marketing': budget * 0.4,
                'sales': budget * 0.3,
                'product': budget * 0.2,
                'operations': budget * 0.1
            },
            risks=[
                {'risk': '資金燃燒過快', 'mitigation': '設定明確的里程碑和止損點'},
                {'risk': '競爭對手反擊', 'mitigation': '建立差異化優勢'},
                {'risk': '執行能力不足', 'mitigation': '引入專業人才'}
            ],
            success_metrics={
                'customer_acquisition': '月新增 > 1000',
                'revenue_growth': 'MoM > 10%',
                'market_share': '目標市場 > 10%'
            },
            confidence_score=75.0
        )

    def _create_foundation_strategy(
        self,
        cap: TechCapabilityAssessment,
        constraints: dict
    ) -> StrategyRecommendation:
        """創建基礎建設策略"""
        gaps = cap.get_gaps()
        budget = constraints.get('budget', 500000)

        return StrategyRecommendation(
            strategy_name="技術能力建設",
            priority=StrategicPriority.CRITICAL,
            rationale=f"團隊能力存在缺口: {', '.join(gaps[:3])}",
            prerequisites=[
                "管理層認同投資需求",
                "確定重點發展領域",
                "建立人才招募管道"
            ],
            expected_outcomes=[
                "技術能力提升 30%",
                "降低技術債務",
                "提升交付效率"
            ],
            estimated_timeline_months=12,
            estimated_investment={
                'training': budget * 0.3,
                'hiring': budget * 0.4,
                'tools': budget * 0.2,
                'consulting': budget * 0.1
            },
            risks=[
                {'risk': '人才流失', 'mitigation': '建立留才機制'},
                {'risk': '學習曲線長', 'mitigation': '提供充足培訓'},
                {'risk': '短期產出降低', 'mitigation': '做好預期管理'}
            ],
            success_metrics={
                'capability_score': '提升至 70+',
                'team_retention': '> 90%',
                'delivery_velocity': '提升 > 20%'
            },
            confidence_score=85.0
        )

    def _create_growth_strategy(
        self,
        market: MarketTimingAnalysis,
        constraints: dict
    ) -> StrategyRecommendation:
        """創建增長策略"""
        budget = constraints.get('budget', 800000)

        return StrategyRecommendation(
            strategy_name="高速增長策略",
            priority=StrategicPriority.HIGH,
            rationale=f"目標市場 ({market.market_name}) 年增長率 {market.growth_rate:.0%}",
            prerequisites=[
                "產品市場契合驗證",
                "銷售流程標準化",
                "客戶成功體系建立"
            ],
            expected_outcomes=[
                "用戶數量翻倍",
                "ARR 增長 100%",
                "NRR > 120%"
            ],
            estimated_timeline_months=12,
            estimated_investment={
                'sales': budget * 0.35,
                'marketing': budget * 0.3,
                'customer_success': budget * 0.2,
                'product': budget * 0.15
            },
            risks=[
                {'risk': '單位經濟學惡化', 'mitigation': '監控 CAC/LTV'},
                {'risk': '服務品質下降', 'mitigation': '同步擴充支援團隊'},
                {'risk': '現金流壓力', 'mitigation': '確保融資到位'}
            ],
            success_metrics={
                'user_growth': 'MoM > 15%',
                'arr': '年末達到 $XM',
                'churn_rate': '< 5%'
            },
            confidence_score=70.0
        )

    def _create_innovation_strategy(
        self,
        cap: TechCapabilityAssessment,
        constraints: dict
    ) -> StrategyRecommendation:
        """創建創新策略"""
        strengths = cap.get_strengths()
        budget = constraints.get('budget', 600000)

        return StrategyRecommendation(
            strategy_name="技術創新領先",
            priority=StrategicPriority.MEDIUM,
            rationale=f"在 {', '.join(strengths[:2])} 領域具備創新基礎",
            prerequisites=[
                "創新文化建立",
                "研發資源保障",
                "容錯機制設計"
            ],
            expected_outcomes=[
                "推出創新功能/產品",
                "建立技術護城河",
                "提升產業影響力"
            ],
            estimated_timeline_months=18,
            estimated_investment={
                'r_and_d': budget * 0.5,
                'talent': budget * 0.25,
                'infrastructure': budget * 0.15,
                'partnerships': budget * 0.1
            },
            risks=[
                {'risk': '創新失敗', 'mitigation': '採用精實創新方法'},
                {'risk': '資源分散', 'mitigation': '聚焦少數項目'},
                {'risk': '時間過長', 'mitigation': '設定 MVP 里程碑'}
            ],
            success_metrics={
                'innovation_output': '> 2 新產品/功能',
                'tech_patents': '> 1 專利申請',
                'industry_recognition': '獎項/媒體報導'
            },
            confidence_score=60.0
        )

    def _create_efficiency_strategy(
        self,
        cap: TechCapabilityAssessment,
        constraints: dict
    ) -> StrategyRecommendation:
        """創建效率優化策略"""
        budget = constraints.get('budget', 400000)

        return StrategyRecommendation(
            strategy_name="營運效率優化",
            priority=StrategicPriority.MEDIUM,
            rationale="提升獲利能力，降低成本",
            prerequisites=[
                "清楚的成本結構分析",
                "流程效率評估",
                "自動化機會識別"
            ],
            expected_outcomes=[
                "營運成本降低 20%",
                "利潤率提升",
                "現金流改善"
            ],
            estimated_timeline_months=9,
            estimated_investment={
                'automation': budget * 0.4,
                'process_improvement': budget * 0.25,
                'training': budget * 0.2,
                'tools': budget * 0.15
            },
            risks=[
                {'risk': '員工抵抗', 'mitigation': '充分溝通變革目的'},
                {'risk': '短期效率下降', 'mitigation': '分階段實施'},
                {'risk': '過度削減', 'mitigation': '保護核心競爭力'}
            ],
            success_metrics={
                'cost_reduction': '> 20%',
                'gross_margin': '> 60%',
                'operating_efficiency': '人均產出提升 > 15%'
            },
            confidence_score=80.0
        )

    def generate_report(
        self,
        cap: TechCapabilityAssessment,
        market: MarketTimingAnalysis,
        recommendations: list[StrategyRecommendation]
    ) -> str:
        """生成策略顧問報告"""
        report = []
        report.append("# 策略顧問報告")
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # 能力評估摘要
        report.append("\n## 一、技術能力評估")
        report.append(f"\n**整體分數**: {cap.get_overall_score():.1f}/100")
        report.append(f"- 基礎設施就緒度: {cap.infrastructure_readiness:.0%}")
        report.append(f"- 流程成熟度: {cap.process_maturity:.0%}")
        report.append(f"- 文化契合度: {cap.culture_alignment:.0%}")

        if cap.get_strengths():
            report.append(f"\n**優勢領域**: {', '.join(cap.get_strengths())}")
        if cap.get_gaps():
            report.append(f"\n**能力缺口**: {', '.join(cap.get_gaps())}")

        # 市場分析摘要
        report.append("\n## 二、市場時機分析")
        report.append(f"\n**目標市場**: {market.market_name}")
        report.append(f"**市場成熟度**: {market.maturity.value}")
        report.append(f"**年增長率**: {market.growth_rate:.0%}")
        report.append(f"**時機分數**: {market.timing_score:.0f}/100")
        report.append(f"**建議**: {market.get_recommendation()}")

        if market.opportunities:
            report.append("\n**主要機會**:")
            for opp in market.opportunities[:3]:
                report.append(f"- {opp}")

        if market.threats:
            report.append("\n**主要威脅**:")
            for threat in market.threats[:3]:
                report.append(f"- {threat}")

        # 策略推薦
        report.append("\n## 三、策略推薦")
        for i, rec in enumerate(recommendations, 1):
            report.append(f"\n### {i}. {rec.strategy_name}")
            report.append(f"**優先級**: {rec.priority.value}")
            report.append(f"**信心指數**: {rec.confidence_score:.0f}%")
            report.append(f"**預估週期**: {rec.estimated_timeline_months} 個月")
            report.append(f"\n**理由**: {rec.rationale}")

            report.append("\n**預期成果**:")
            for outcome in rec.expected_outcomes:
                report.append(f"- {outcome}")

            report.append("\n**成功指標**:")
            for metric, target in rec.success_metrics.items():
                report.append(f"- {metric}: {target}")

            report.append("\n**風險與對策**:")
            for risk in rec.risks:
                report.append(f"- {risk['risk']} → {risk['mitigation']}")

        return '\n'.join(report)
