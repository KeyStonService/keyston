# -*- coding: utf-8 -*-
"""
案例學習引擎 - 從成功案例中學習策略模式

此模組提供：
- 預載入成功企業案例（Netflix、Shopify、Stripe 等）
- 案例分析與模式識別
- 適用性評估
- 學習要點提取

Copyright (c) 2024 SynergyMesh
MIT License
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import json


class DevelopmentStrategy(Enum):
    """開發策略類型"""
    COMMERCIAL_ORIENTED = "商業導向開發"
    HIGH_MARKET_RETURN = "高市場回報應用開發"
    ENTERPRISE_GRADE = "企業級應用開發"
    HIGH_VALUE = "高價值應用程式開發"
    PROFESSIONAL = "專業級開發"
    ADVANCED = "高階開發"
    INTELLIGENT = "智能化應用開發"
    NEXT_GEN = "下世代應用開發"


class PhaseType(Enum):
    """發展階段類型"""
    INITIAL = "初期階段"
    GROWTH = "成長階段"
    MATURITY = "成熟階段"
    INNOVATION = "創新階段"
    TRANSFORMATION = "轉型階段"


@dataclass
class EvolutionPhase:
    """演進階段"""
    phase_type: PhaseType
    strategy: DevelopmentStrategy
    description: str
    key_actions: List[str]
    success_metrics: Dict[str, str]
    duration_months: Optional[int] = None
    investment_focus: Optional[str] = None
    risks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'phase_type': self.phase_type.value,
            'strategy': self.strategy.value,
            'description': self.description,
            'key_actions': self.key_actions,
            'success_metrics': self.success_metrics,
            'duration_months': self.duration_months,
            'investment_focus': self.investment_focus,
            'risks': self.risks
        }


@dataclass
class LessonLearned:
    """學習要點"""
    category: str
    title: str
    description: str
    applicability: List[str]  # 適用情境
    implementation_tips: List[str]
    common_mistakes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'applicability': self.applicability,
            'implementation_tips': self.implementation_tips,
            'common_mistakes': self.common_mistakes
        }


@dataclass
class CaseStudy:
    """案例研究"""
    company_name: str
    industry: str
    description: str
    founding_year: int
    evolution_phases: List[EvolutionPhase]
    lessons_learned: List[LessonLearned]
    key_success_factors: List[str]
    technology_stack: List[str]
    business_model: str
    market_position: str
    
    def get_phase_by_type(self, phase_type: PhaseType) -> Optional[EvolutionPhase]:
        """根據類型獲取階段"""
        for phase in self.evolution_phases:
            if phase.phase_type == phase_type:
                return phase
        return None
    
    def get_strategy_sequence(self) -> List[DevelopmentStrategy]:
        """獲取策略演進序列"""
        return [phase.strategy for phase in self.evolution_phases]
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'company_name': self.company_name,
            'industry': self.industry,
            'description': self.description,
            'founding_year': self.founding_year,
            'evolution_phases': [p.to_dict() for p in self.evolution_phases],
            'lessons_learned': [l.to_dict() for l in self.lessons_learned],
            'key_success_factors': self.key_success_factors,
            'technology_stack': self.technology_stack,
            'business_model': self.business_model,
            'market_position': self.market_position
        }


class CaseStudyEngine:
    """
    案例學習引擎
    
    從成功企業案例中學習策略模式，提供：
    - 案例庫管理
    - 模式識別
    - 適用性分析
    - 策略建議
    """
    
    def __init__(self):
        """初始化案例引擎"""
        self._case_studies: Dict[str, CaseStudy] = {}
        self._load_builtin_cases()
    
    def _load_builtin_cases(self):
        """載入內建案例"""
        # Netflix 案例
        self._case_studies['netflix'] = CaseStudy(
            company_name="Netflix",
            industry="串流媒體 / 娛樂",
            description="從 DVD 租賃轉型為全球最大串流平台，透過技術創新和內容投資建立護城河",
            founding_year=1997,
            evolution_phases=[
                EvolutionPhase(
                    phase_type=PhaseType.INITIAL,
                    strategy=DevelopmentStrategy.COMMERCIAL_ORIENTED,
                    description="從 DVD 租賃轉型線上串流，專注解決用戶便利性需求",
                    key_actions=[
                        "建立線上訂閱模式",
                        "開發推薦演算法原型",
                        "簡化用戶體驗",
                        "建立內容授權關係"
                    ],
                    success_metrics={
                        "用戶轉換率": "DVD 用戶轉線上 > 50%",
                        "客戶留存率": "> 90%",
                        "NPS": "> 60"
                    },
                    duration_months=36,
                    investment_focus="技術基礎設施",
                    risks=["內容授權成本", "技術穩定性"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.GROWTH,
                    strategy=DevelopmentStrategy.HIGH_MARKET_RETURN,
                    description="大量投資內容授權，快速擴展用戶基數",
                    key_actions=[
                        "擴大內容庫",
                        "優化推薦系統",
                        "國際化擴展",
                        "提升串流品質"
                    ],
                    success_metrics={
                        "用戶增長": "年增長 > 30%",
                        "觀看時長": "月均 > 40 小時",
                        "市佔率": "> 40%"
                    },
                    duration_months=48,
                    investment_focus="內容授權與行銷",
                    risks=["競爭加劇", "內容成本上升"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.MATURITY,
                    strategy=DevelopmentStrategy.HIGH_VALUE,
                    description="開發原創內容，建立品牌護城河",
                    key_actions=[
                        "投資原創內容",
                        "建立製作能力",
                        "全球化內容策略",
                        "建立 IP 資產"
                    ],
                    success_metrics={
                        "原創內容佔比": "> 50%",
                        "獲獎數量": "艾美獎 > 100",
                        "品牌價值": "全球 Top 50"
                    },
                    duration_months=60,
                    investment_focus="原創內容製作",
                    risks=["製作成本", "內容風險"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.INNOVATION,
                    strategy=DevelopmentStrategy.INTELLIGENT,
                    description="運用 AI 技術優化內容推薦，提升個人化體驗",
                    key_actions=[
                        "深度學習推薦系統",
                        "動態縮圖優化",
                        "內容製作 AI 輔助",
                        "互動式內容實驗"
                    ],
                    success_metrics={
                        "推薦準確度": "> 80%",
                        "跳出率降低": "> 30%",
                        "用戶滿意度": "> 4.5/5"
                    },
                    duration_months=None,
                    investment_focus="AI/ML 技術",
                    risks=["技術複雜度", "隱私問題"]
                )
            ],
            lessons_learned=[
                LessonLearned(
                    category="轉型策略",
                    title="漸進式轉型優於激進變革",
                    description="Netflix 保持 DVD 業務的同時發展串流，確保收入穩定",
                    applicability=["傳統企業數位轉型", "商業模式創新"],
                    implementation_tips=[
                        "維持核心收入來源",
                        "設立獨立團隊探索新業務",
                        "設定明確的轉換里程碑"
                    ],
                    common_mistakes=[
                        "過早放棄現有業務",
                        "資源分配失衡",
                        "忽視現有客戶需求"
                    ]
                ),
                LessonLearned(
                    category="技術投資",
                    title="推薦系統是核心競爭力",
                    description="個人化推薦減少用戶決策疲勞，提高黏著度",
                    applicability=["內容平台", "電商", "SaaS"],
                    implementation_tips=[
                        "從簡單規則開始",
                        "持續收集用戶反饋",
                        "A/B 測試驗證效果"
                    ],
                    common_mistakes=[
                        "過度依賴複雜演算法",
                        "忽視冷啟動問題",
                        "推薦同質化"
                    ]
                ),
                LessonLearned(
                    category="內容策略",
                    title="原創內容建立護城河",
                    description="獨家內容無法被競爭對手複製，形成差異化優勢",
                    applicability=["媒體平台", "教育平台", "遊戲"],
                    implementation_tips=[
                        "分析用戶喜好趨勢",
                        "與優秀創作者合作",
                        "建立數據驅動的製作流程"
                    ],
                    common_mistakes=[
                        "盲目追求數量",
                        "忽視本地化需求",
                        "過度依賴明星效應"
                    ]
                )
            ],
            key_success_factors=[
                "技術創新領先",
                "數據驅動決策",
                "用戶體驗至上",
                "勇於自我顛覆",
                "全球化視野"
            ],
            technology_stack=["Java", "Python", "Node.js", "Cassandra", "AWS"],
            business_model="訂閱制 (SVOD)",
            market_position="全球串流媒體領導者"
        )
        
        # Shopify 案例
        self._case_studies['shopify'] = CaseStudy(
            company_name="Shopify",
            industry="電子商務 / SaaS",
            description="提供一站式電商解決方案，讓任何人都能輕鬆開店，從小商家到大企業",
            founding_year=2006,
            evolution_phases=[
                EvolutionPhase(
                    phase_type=PhaseType.INITIAL,
                    strategy=DevelopmentStrategy.ENTERPRISE_GRADE,
                    description="提供穩定、可擴展的電商解決方案",
                    key_actions=[
                        "建立多租戶架構",
                        "簡化店面設置流程",
                        "整合支付功能",
                        "開發佈景主題系統"
                    ],
                    success_metrics={
                        "系統可用性": "> 99.9%",
                        "設置時間": "< 30 分鐘",
                        "客戶滿意度": "> 4.0/5"
                    },
                    duration_months=36,
                    investment_focus="平台穩定性",
                    risks=["技術債務累積", "擴展性瓶頸"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.GROWTH,
                    strategy=DevelopmentStrategy.HIGH_VALUE,
                    description="建立完整生態系統，創造平台價值",
                    key_actions=[
                        "開放 API 生態",
                        "推出 Shopify Payments",
                        "建立 App Store",
                        "開發物流解決方案"
                    ],
                    success_metrics={
                        "GMV 增長": "年增長 > 50%",
                        "App 數量": "> 5000",
                        "支付滲透率": "> 50%"
                    },
                    duration_months=48,
                    investment_focus="生態系統建設",
                    risks=["平台品質控制", "第三方依賴"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.MATURITY,
                    strategy=DevelopmentStrategy.PROFESSIONAL,
                    description="提升產品品質，支援大型企業客戶",
                    key_actions=[
                        "推出 Shopify Plus",
                        "企業級功能開發",
                        "專業服務團隊",
                        "合規認證取得"
                    ],
                    success_metrics={
                        "企業客戶數": "> 10000",
                        "Plus 收入佔比": "> 30%",
                        "客戶終身價值": "增長 > 50%"
                    },
                    duration_months=36,
                    investment_focus="企業功能",
                    risks=["產品複雜化", "客戶分層挑戰"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.INNOVATION,
                    strategy=DevelopmentStrategy.INTELLIGENT,
                    description="整合 AI 驅動的庫存管理和銷售預測",
                    key_actions=[
                        "AI 庫存優化",
                        "智能定價建議",
                        "銷售預測模型",
                        "智能店面設計"
                    ],
                    success_metrics={
                        "預測準確度": "> 85%",
                        "庫存週轉率": "提升 > 20%",
                        "商家增長率": "使用 AI 功能商家增長 > 30%"
                    },
                    duration_months=None,
                    investment_focus="AI/ML 能力",
                    risks=["數據隱私", "演算法偏見"]
                )
            ],
            lessons_learned=[
                LessonLearned(
                    category="平台策略",
                    title="降低進入門檻創造大量用戶",
                    description="簡化開店流程讓非技術人員也能使用",
                    applicability=["SaaS 平台", "工具類產品", "B2B 服務"],
                    implementation_tips=[
                        "提供免費試用或免費層",
                        "製作詳細教學資源",
                        "提供範本和預設配置"
                    ],
                    common_mistakes=[
                        "功能過於複雜",
                        "定價策略混亂",
                        "缺乏引導流程"
                    ]
                ),
                LessonLearned(
                    category="生態建設",
                    title="開放平台創造網絡效應",
                    description="開放 API 讓第三方開發者擴展平台能力",
                    applicability=["平台型產品", "開發者工具", "市集模式"],
                    implementation_tips=[
                        "設計清晰的 API 文檔",
                        "提供開發者激勵計畫",
                        "建立品質審核機制"
                    ],
                    common_mistakes=[
                        "API 設計不一致",
                        "缺乏開發者支援",
                        "平台抽成過高"
                    ]
                ),
                LessonLearned(
                    category="變現策略",
                    title="支付整合是重要收入來源",
                    description="Shopify Payments 創造可預測的收入流",
                    applicability=["電商平台", "市集", "金融科技"],
                    implementation_tips=[
                        "簡化支付流程",
                        "提供有競爭力的費率",
                        "確保合規性"
                    ],
                    common_mistakes=[
                        "忽視合規要求",
                        "費率不透明",
                        "支付體驗差"
                    ]
                )
            ],
            key_success_factors=[
                "簡化用戶體驗",
                "建立完整生態",
                "持續平台投資",
                "服務各種規模客戶",
                "開發者優先策略"
            ],
            technology_stack=["Ruby on Rails", "React", "GraphQL", "MySQL", "GCP"],
            business_model="訂閱制 + 交易抽成",
            market_position="全球領先電商 SaaS 平台"
        )
        
        # Stripe 案例
        self._case_studies['stripe'] = CaseStudy(
            company_name="Stripe",
            industry="金融科技 / 支付",
            description="為開發者設計的支付基礎設施，簡化線上支付整合",
            founding_year=2010,
            evolution_phases=[
                EvolutionPhase(
                    phase_type=PhaseType.INITIAL,
                    strategy=DevelopmentStrategy.ADVANCED,
                    description="為開發者打造最簡單的支付 API",
                    key_actions=[
                        "設計直觀的 API",
                        "優質文檔撰寫",
                        "簡化整合流程",
                        "提供測試沙箱"
                    ],
                    success_metrics={
                        "整合時間": "< 1 小時",
                        "開發者滿意度": "> 4.5/5",
                        "文檔完整度": "100%"
                    },
                    duration_months=24,
                    investment_focus="開發者體驗",
                    risks=["市場教育成本", "競爭對手"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.GROWTH,
                    strategy=DevelopmentStrategy.ENTERPRISE_GRADE,
                    description="擴展到企業級功能，支援複雜支付場景",
                    key_actions=[
                        "多幣種支援",
                        "訂閱管理功能",
                        "欺詐檢測系統",
                        "合規工具"
                    ],
                    success_metrics={
                        "支援貨幣數": "> 135",
                        "欺詐阻擋率": "> 99%",
                        "企業客戶數": "> 1000"
                    },
                    duration_months=36,
                    investment_focus="功能擴展",
                    risks=["複雜度增加", "維護成本"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.MATURITY,
                    strategy=DevelopmentStrategy.HIGH_VALUE,
                    description="建立金融基礎設施平台，超越支付",
                    key_actions=[
                        "推出 Stripe Atlas",
                        "開發 Stripe Capital",
                        "建立 Stripe Treasury",
                        "推出發卡服務"
                    ],
                    success_metrics={
                        "產品線數量": "> 10",
                        "客戶 ARPU": "增長 > 100%",
                        "平台 GMV": "> $500B"
                    },
                    duration_months=48,
                    investment_focus="平台擴展",
                    risks=["監管風險", "資本需求"]
                ),
                EvolutionPhase(
                    phase_type=PhaseType.INNOVATION,
                    strategy=DevelopmentStrategy.NEXT_GEN,
                    description="探索下世代金融技術和全球擴展",
                    key_actions=[
                        "加密貨幣支援",
                        "嵌入式金融",
                        "全球銀行連接",
                        "即時支付網絡"
                    ],
                    success_metrics={
                        "新市場進入": "> 10 國家/年",
                        "新產品收入": "> 20%",
                        "技術專利": "> 100"
                    },
                    duration_months=None,
                    investment_focus="創新與全球化",
                    risks=["監管不確定性", "技術風險"]
                )
            ],
            lessons_learned=[
                LessonLearned(
                    category="開發者體驗",
                    title="API 設計決定採用速度",
                    description="直觀的 API 和優質文檔降低採用障礙",
                    applicability=["開發者工具", "API 服務", "基礎設施"],
                    implementation_tips=[
                        "遵循 RESTful 設計原則",
                        "提供多語言 SDK",
                        "維護互動式文檔"
                    ],
                    common_mistakes=[
                        "API 版本管理混亂",
                        "文檔與代碼不同步",
                        "錯誤訊息不清楚"
                    ]
                ),
                LessonLearned(
                    category="產品擴展",
                    title="從單一功能擴展到平台",
                    description="支付功能是入口，金融服務是目的地",
                    applicability=["基礎設施服務", "B2B 工具", "垂直 SaaS"],
                    implementation_tips=[
                        "深入了解客戶工作流",
                        "識別相鄰產品機會",
                        "保持核心功能簡單"
                    ],
                    common_mistakes=[
                        "過早多元化",
                        "忽視核心產品",
                        "整合不夠緊密"
                    ]
                )
            ],
            key_success_factors=[
                "開發者優先",
                "卓越的文檔",
                "持續創新",
                "合規先行",
                "全球化思維"
            ],
            technology_stack=["Ruby", "Scala", "Go", "React", "AWS"],
            business_model="交易抽成 + 服務費",
            market_position="全球領先支付基礎設施"
        )
    
    def get_case(self, company: str) -> Optional[CaseStudy]:
        """獲取特定公司案例"""
        return self._case_studies.get(company.lower())
    
    def list_cases(self) -> List[str]:
        """列出所有案例"""
        return list(self._case_studies.keys())
    
    def add_case(self, key: str, case: CaseStudy):
        """添加新案例"""
        self._case_studies[key.lower()] = case
    
    def find_cases_by_industry(self, industry: str) -> List[CaseStudy]:
        """根據產業查找案例"""
        return [
            case for case in self._case_studies.values()
            if industry.lower() in case.industry.lower()
        ]
    
    def find_cases_by_strategy(self, strategy: DevelopmentStrategy) -> List[Tuple[CaseStudy, EvolutionPhase]]:
        """根據策略查找案例"""
        results = []
        for case in self._case_studies.values():
            for phase in case.evolution_phases:
                if phase.strategy == strategy:
                    results.append((case, phase))
        return results
    
    def analyze_strategy_patterns(self) -> Dict[str, Any]:
        """
        分析所有案例的策略模式
        
        Returns:
            策略模式分析結果
        """
        patterns = {
            'common_sequences': [],
            'strategy_frequency': {},
            'phase_duration_avg': {},
            'success_factors_frequency': {}
        }
        
        # 統計策略頻率
        for case in self._case_studies.values():
            for phase in case.evolution_phases:
                strategy = phase.strategy.value
                patterns['strategy_frequency'][strategy] = \
                    patterns['strategy_frequency'].get(strategy, 0) + 1
        
        # 計算階段平均時長
        phase_durations = {}
        for case in self._case_studies.values():
            for phase in case.evolution_phases:
                if phase.duration_months:
                    pt = phase.phase_type.value
                    if pt not in phase_durations:
                        phase_durations[pt] = []
                    phase_durations[pt].append(phase.duration_months)
        
        for pt, durations in phase_durations.items():
            patterns['phase_duration_avg'][pt] = sum(durations) / len(durations)
        
        # 統計成功因素
        for case in self._case_studies.values():
            for factor in case.key_success_factors:
                patterns['success_factors_frequency'][factor] = \
                    patterns['success_factors_frequency'].get(factor, 0) + 1
        
        # 識別常見策略序列
        sequences = []
        for case in self._case_studies.values():
            seq = [p.strategy.value for p in case.evolution_phases]
            sequences.append({
                'company': case.company_name,
                'sequence': seq
            })
        patterns['common_sequences'] = sequences
        
        return patterns
    
    def get_lessons_by_category(self, category: str) -> List[LessonLearned]:
        """根據類別獲取學習要點"""
        lessons = []
        for case in self._case_studies.values():
            for lesson in case.lessons_learned:
                if category.lower() in lesson.category.lower():
                    lessons.append(lesson)
        return lessons
    
    def recommend_strategy_sequence(
        self,
        industry: str,
        current_stage: PhaseType,
        resources: str = "moderate"  # low, moderate, high
    ) -> List[Dict[str, Any]]:
        """
        根據產業和現狀推薦策略序列
        
        Args:
            industry: 產業類型
            current_stage: 當前階段
            resources: 資源水平
            
        Returns:
            推薦的策略序列
        """
        recommendations = []
        
        # 找到相似產業的案例
        similar_cases = self.find_cases_by_industry(industry)
        if not similar_cases:
            similar_cases = list(self._case_studies.values())
        
        # 分析各階段策略
        stage_strategies = {}
        for case in similar_cases:
            for phase in case.evolution_phases:
                pt = phase.phase_type
                if pt not in stage_strategies:
                    stage_strategies[pt] = []
                stage_strategies[pt].append({
                    'strategy': phase.strategy,
                    'company': case.company_name,
                    'key_actions': phase.key_actions,
                    'duration': phase.duration_months
                })
        
        # 根據當前階段確定推薦序列
        stage_order = [
            PhaseType.INITIAL,
            PhaseType.GROWTH,
            PhaseType.MATURITY,
            PhaseType.INNOVATION,
            PhaseType.TRANSFORMATION
        ]
        
        current_idx = stage_order.index(current_stage)
        remaining_stages = stage_order[current_idx:]
        
        for stage in remaining_stages:
            if stage in stage_strategies:
                strategies = stage_strategies[stage]
                # 根據資源水平調整推薦
                if resources == "low":
                    # 優先選擇較短週期的策略
                    strategies.sort(key=lambda x: x.get('duration', 99) or 99)
                elif resources == "high":
                    # 可以選擇更激進的策略
                    pass
                
                recommendations.append({
                    'stage': stage.value,
                    'recommended_strategies': strategies[:3],
                    'rationale': f"基於 {len(strategies)} 個案例分析"
                })
        
        return recommendations
    
    def generate_report(self, company: str, language: str = "zh-TW") -> str:
        """
        生成案例分析報告
        
        Args:
            company: 公司名稱
            language: 報告語言
            
        Returns:
            格式化的報告
        """
        case = self.get_case(company)
        if not case:
            return f"找不到 {company} 的案例資料"
        
        report = []
        report.append(f"# {case.company_name} 案例分析報告")
        report.append(f"\n## 基本資訊")
        report.append(f"- **產業**: {case.industry}")
        report.append(f"- **成立年份**: {case.founding_year}")
        report.append(f"- **商業模式**: {case.business_model}")
        report.append(f"- **市場定位**: {case.market_position}")
        report.append(f"\n**概述**: {case.description}")
        
        report.append(f"\n## 發展演進")
        for i, phase in enumerate(case.evolution_phases, 1):
            report.append(f"\n### 階段 {i}: {phase.phase_type.value}")
            report.append(f"**策略**: {phase.strategy.value}")
            report.append(f"**描述**: {phase.description}")
            if phase.duration_months:
                report.append(f"**週期**: {phase.duration_months} 個月")
            report.append(f"\n**關鍵行動**:")
            for action in phase.key_actions:
                report.append(f"- {action}")
            report.append(f"\n**成功指標**:")
            for metric, value in phase.success_metrics.items():
                report.append(f"- {metric}: {value}")
        
        report.append(f"\n## 學習要點")
        for lesson in case.lessons_learned:
            report.append(f"\n### {lesson.title}")
            report.append(f"**類別**: {lesson.category}")
            report.append(f"**說明**: {lesson.description}")
            report.append(f"\n**實施建議**:")
            for tip in lesson.implementation_tips:
                report.append(f"- {tip}")
            report.append(f"\n**常見錯誤**:")
            for mistake in lesson.common_mistakes:
                report.append(f"- ⚠️ {mistake}")
        
        report.append(f"\n## 成功關鍵因素")
        for factor in case.key_success_factors:
            report.append(f"- ✓ {factor}")
        
        report.append(f"\n## 技術堆疊")
        report.append(f"{', '.join(case.technology_stack)}")
        
        return '\n'.join(report)
