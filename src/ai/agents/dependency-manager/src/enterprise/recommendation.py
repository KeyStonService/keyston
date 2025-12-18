"""
智能推薦引擎 (Intelligent Recommendation Engine)

提供 AI 驅動的依賴管理建議：
- 依賴項健康度評分
- 替代方案推薦
- 升級路徑規劃
- 風險預測與預警
- 最佳實踐建議

第三優先級：創新突破階段 - 智能化應用開發
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import math
import re


class HealthFactor(Enum):
    """健康度因素"""
    MAINTENANCE_ACTIVITY = "maintenance"     # 維護活躍度
    SECURITY_HISTORY = "security"            # 安全歷史
    COMMUNITY_SIZE = "community"             # 社群規模
    DOCUMENTATION_QUALITY = "documentation"  # 文件品質
    VERSION_STABILITY = "stability"          # 版本穩定性
    LICENSE_CLARITY = "license"              # 授權清晰度
    DEPENDENCY_COUNT = "dependencies"        # 依賴數量
    BACKWARD_COMPATIBILITY = "compatibility" # 向後相容性


class RecommendationType(Enum):
    """建議類型"""
    UPGRADE = "upgrade"                # 升級建議
    REPLACE = "replace"                # 替換建議
    REMOVE = "remove"                  # 移除建議
    SECURITY_FIX = "security_fix"      # 安全修復
    CONSOLIDATE = "consolidate"        # 整合建議
    BEST_PRACTICE = "best_practice"    # 最佳實踐


class RiskLevel(Enum):
    """風險等級"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class HealthScore:
    """健康度評分"""
    overall_score: float  # 0-100
    factors: Dict[HealthFactor, float] = field(default_factory=dict)
    grade: str = "C"  # A, B, C, D, F
    trend: str = "stable"  # improving, stable, declining
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """計算等級"""
        if self.overall_score >= 90:
            self.grade = "A"
        elif self.overall_score >= 80:
            self.grade = "B"
        elif self.overall_score >= 70:
            self.grade = "C"
        elif self.overall_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"


@dataclass
class Alternative:
    """替代方案"""
    name: str
    version: str
    health_score: float
    migration_effort: str  # low, medium, high
    compatibility_score: float  # 0-100
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    migration_guide_url: Optional[str] = None


@dataclass
class UpgradePath:
    """升級路徑"""
    current_version: str
    target_version: str
    intermediate_versions: List[str] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    estimated_effort_hours: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    automated_migration_available: bool = False


@dataclass
class RiskPrediction:
    """風險預測"""
    dependency_name: str
    risk_type: str
    probability: float  # 0-1
    impact_level: RiskLevel
    predicted_date: Optional[datetime] = None
    mitigation_actions: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """建議"""
    rec_type: RecommendationType
    dependency_name: str
    priority: int  # 1-10, 10 最高
    title: str
    description: str
    actions: List[str] = field(default_factory=list)
    estimated_benefit: float = 0.0
    estimated_effort_hours: float = 0.0
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)


class IntelligentRecommendation:
    """
    智能推薦引擎
    
    基於多維度分析提供依賴管理的智能建議，包括：
    - 健康度評估
    - 替代方案發現
    - 升級路徑規劃
    - 風險預測
    """
    
    # 知名套件資料庫（模擬）
    KNOWN_PACKAGES = {
        # npm
        "lodash": {"alternatives": ["ramda", "underscore"], "category": "utility"},
        "moment": {"alternatives": ["dayjs", "date-fns", "luxon"], "category": "datetime"},
        "request": {"alternatives": ["axios", "got", "node-fetch"], "category": "http"},
        "express": {"alternatives": ["fastify", "koa", "hapi"], "category": "web"},
        "jquery": {"alternatives": ["vanilla-js", "cash-dom"], "category": "dom"},
        # python
        "requests": {"alternatives": ["httpx", "aiohttp"], "category": "http"},
        "django": {"alternatives": ["flask", "fastapi", "starlette"], "category": "web"},
        "pandas": {"alternatives": ["polars", "vaex"], "category": "data"},
        "numpy": {"alternatives": ["jax", "cupy"], "category": "numeric"},
    }
    
    # 已知棄用套件
    DEPRECATED_PACKAGES = {
        "request": "2020-02-11",
        "moment": "2020-09-01",
        "jquery": "not-deprecated-but-legacy",
    }
    
    def __init__(self):
        """初始化推薦引擎"""
        self._health_cache: Dict[str, HealthScore] = {}
        self._recommendations: List[Recommendation] = []
        self._risk_predictions: List[RiskPrediction] = []
    
    # ==================== 健康度評估 ====================
    
    def calculate_health_score(self,
                              dependency_name: str,
                              version: str,
                              metadata: Optional[Dict[str, Any]] = None) -> HealthScore:
        """
        計算依賴項健康度評分
        
        Args:
            dependency_name: 依賴名稱
            version: 版本
            metadata: 額外元資料
            
        Returns:
            健康度評分
        """
        metadata = metadata or {}
        factors: Dict[HealthFactor, float] = {}
        
        # 維護活躍度 (基於最後更新時間)
        last_update = metadata.get("last_update_days", 30)
        if last_update < 30:
            factors[HealthFactor.MAINTENANCE_ACTIVITY] = 100
        elif last_update < 90:
            factors[HealthFactor.MAINTENANCE_ACTIVITY] = 80
        elif last_update < 180:
            factors[HealthFactor.MAINTENANCE_ACTIVITY] = 60
        elif last_update < 365:
            factors[HealthFactor.MAINTENANCE_ACTIVITY] = 40
        else:
            factors[HealthFactor.MAINTENANCE_ACTIVITY] = 20
        
        # 安全歷史
        vuln_count = metadata.get("vulnerability_count", 0)
        factors[HealthFactor.SECURITY_HISTORY] = max(0, 100 - vuln_count * 20)
        
        # 社群規模 (基於星星數或下載量)
        stars = metadata.get("stars", 0)
        downloads = metadata.get("weekly_downloads", 0)
        if stars > 10000 or downloads > 1000000:
            factors[HealthFactor.COMMUNITY_SIZE] = 100
        elif stars > 1000 or downloads > 100000:
            factors[HealthFactor.COMMUNITY_SIZE] = 80
        elif stars > 100 or downloads > 10000:
            factors[HealthFactor.COMMUNITY_SIZE] = 60
        else:
            factors[HealthFactor.COMMUNITY_SIZE] = 40
        
        # 文件品質
        has_docs = metadata.get("has_documentation", True)
        has_examples = metadata.get("has_examples", False)
        doc_score = 50
        if has_docs:
            doc_score += 30
        if has_examples:
            doc_score += 20
        factors[HealthFactor.DOCUMENTATION_QUALITY] = doc_score
        
        # 版本穩定性
        is_stable = not version.startswith("0.")
        has_breaking = metadata.get("has_breaking_changes", False)
        stability = 70
        if is_stable:
            stability += 20
        if not has_breaking:
            stability += 10
        factors[HealthFactor.VERSION_STABILITY] = min(100, stability)
        
        # 授權清晰度
        license_type = metadata.get("license", "unknown")
        known_licenses = ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"]
        if license_type in known_licenses:
            factors[HealthFactor.LICENSE_CLARITY] = 100
        elif license_type and license_type != "unknown":
            factors[HealthFactor.LICENSE_CLARITY] = 70
        else:
            factors[HealthFactor.LICENSE_CLARITY] = 30
        
        # 依賴數量
        dep_count = metadata.get("dependency_count", 0)
        if dep_count < 5:
            factors[HealthFactor.DEPENDENCY_COUNT] = 100
        elif dep_count < 10:
            factors[HealthFactor.DEPENDENCY_COUNT] = 80
        elif dep_count < 20:
            factors[HealthFactor.DEPENDENCY_COUNT] = 60
        else:
            factors[HealthFactor.DEPENDENCY_COUNT] = 40
        
        # 向後相容性
        factors[HealthFactor.BACKWARD_COMPATIBILITY] = 80 if not has_breaking else 50
        
        # 計算加權總分
        weights = {
            HealthFactor.MAINTENANCE_ACTIVITY: 0.15,
            HealthFactor.SECURITY_HISTORY: 0.25,
            HealthFactor.COMMUNITY_SIZE: 0.10,
            HealthFactor.DOCUMENTATION_QUALITY: 0.10,
            HealthFactor.VERSION_STABILITY: 0.15,
            HealthFactor.LICENSE_CLARITY: 0.10,
            HealthFactor.DEPENDENCY_COUNT: 0.05,
            HealthFactor.BACKWARD_COMPATIBILITY: 0.10,
        }
        
        overall = sum(factors.get(f, 50) * w for f, w in weights.items())
        
        # 檢查是否為已知棄用套件
        if dependency_name.lower() in self.DEPRECATED_PACKAGES:
            overall = min(overall, 50)  # 降低評分
        
        score = HealthScore(overall_score=overall, factors=factors)
        self._health_cache[dependency_name] = score
        
        return score
    
    # ==================== 替代方案推薦 ====================
    
    def find_alternatives(self,
                         dependency_name: str,
                         current_version: str,
                         ecosystem: str = "npm") -> List[Alternative]:
        """
        尋找替代方案
        
        Args:
            dependency_name: 依賴名稱
            current_version: 目前版本
            ecosystem: 生態系統
            
        Returns:
            替代方案列表
        """
        alternatives = []
        
        # 查找已知替代方案
        pkg_info = self.KNOWN_PACKAGES.get(dependency_name.lower(), {})
        alt_names = pkg_info.get("alternatives", [])
        
        for alt_name in alt_names:
            # 模擬計算替代方案評分
            health = self.calculate_health_score(alt_name, "latest", {
                "stars": 5000,
                "weekly_downloads": 500000,
                "has_documentation": True
            })
            
            migration_effort = self._estimate_migration_effort(
                dependency_name, alt_name
            )
            
            compatibility = self._estimate_compatibility(
                dependency_name, alt_name
            )
            
            alternatives.append(Alternative(
                name=alt_name,
                version="latest",
                health_score=health.overall_score,
                migration_effort=migration_effort,
                compatibility_score=compatibility,
                pros=self._get_alternative_pros(alt_name),
                cons=self._get_alternative_cons(alt_name)
            ))
        
        # 按健康度排序
        alternatives.sort(key=lambda x: x.health_score, reverse=True)
        
        return alternatives
    
    def _estimate_migration_effort(self, from_pkg: str, to_pkg: str) -> str:
        """估算遷移工作量"""
        # 簡化邏輯：相同類別的套件遷移較容易
        from_info = self.KNOWN_PACKAGES.get(from_pkg.lower(), {})
        to_info = self.KNOWN_PACKAGES.get(to_pkg.lower(), {})
        
        if from_info.get("category") == to_info.get("category"):
            return "medium"
        return "high"
    
    def _estimate_compatibility(self, from_pkg: str, to_pkg: str) -> float:
        """估算相容性"""
        # 模擬相容性評估
        from_info = self.KNOWN_PACKAGES.get(from_pkg.lower(), {})
        to_info = self.KNOWN_PACKAGES.get(to_pkg.lower(), {})
        
        if from_info.get("category") == to_info.get("category"):
            return 75.0
        return 50.0
    
    def _get_alternative_pros(self, pkg_name: str) -> List[str]:
        """取得替代方案優點"""
        pros_map = {
            "dayjs": ["輕量化 (2KB)", "API 相容 moment", "不可變設計"],
            "date-fns": ["模組化", "Tree-shaking 友好", "TypeScript 支援"],
            "axios": ["Promise 基礎", "瀏覽器/Node 通用", "攔截器支援"],
            "fastify": ["高效能", "Schema 驗證", "插件生態"],
            "httpx": ["async 支援", "HTTP/2 支援", "現代化 API"],
            "polars": ["高效能", "Lazy 評估", "Rust 核心"],
        }
        return pros_map.get(pkg_name.lower(), ["活躍維護", "現代化設計"])
    
    def _get_alternative_cons(self, pkg_name: str) -> List[str]:
        """取得替代方案缺點"""
        cons_map = {
            "dayjs": ["插件需另外載入", "部分時區功能有限"],
            "fastify": ["學習曲線", "生態較小"],
            "polars": ["API 不同於 pandas", "社群較小"],
        }
        return cons_map.get(pkg_name.lower(), ["需要學習新 API"])
    
    # ==================== 升級路徑規劃 ====================
    
    def plan_upgrade_path(self,
                         dependency_name: str,
                         current_version: str,
                         target_version: str) -> UpgradePath:
        """
        規劃升級路徑
        
        Args:
            dependency_name: 依賴名稱
            current_version: 目前版本
            target_version: 目標版本
            
        Returns:
            升級路徑
        """
        # 解析版本
        current = self._parse_version(current_version)
        target = self._parse_version(target_version)
        
        intermediate = []
        breaking_changes = []
        risk = RiskLevel.LOW
        effort = 1.0
        
        # 判斷升級類型
        if target[0] > current[0]:
            # 主版本升級
            risk = RiskLevel.HIGH
            effort = 8.0
            breaking_changes.append(f"主版本升級 {current[0]} -> {target[0]}")
            
            # 建議中間版本
            for major in range(current[0] + 1, target[0] + 1):
                intermediate.append(f"{major}.0.0")
        
        elif target[1] > current[1]:
            # 次版本升級
            risk = RiskLevel.MEDIUM
            effort = 4.0
            
            if target[1] - current[1] > 5:
                for minor in range(current[1] + 5, target[1], 5):
                    intermediate.append(f"{current[0]}.{minor}.0")
        
        else:
            # 修補版本升級
            risk = RiskLevel.LOW
            effort = 1.0
        
        return UpgradePath(
            current_version=current_version,
            target_version=target_version,
            intermediate_versions=intermediate,
            breaking_changes=breaking_changes,
            estimated_effort_hours=effort,
            risk_level=risk,
            automated_migration_available=(risk == RiskLevel.LOW)
        )
    
    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """解析版本號"""
        # 移除前綴
        version = re.sub(r'^[v^~>=<]*', '', version)
        parts = version.split('.')
        
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(re.sub(r'[^0-9].*', '', parts[2])) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)
    
    # ==================== 風險預測 ====================
    
    def predict_risks(self,
                     dependencies: List[Dict[str, Any]]) -> List[RiskPrediction]:
        """
        預測風險
        
        Args:
            dependencies: 依賴項列表
            
        Returns:
            風險預測列表
        """
        predictions = []
        
        for dep in dependencies:
            name = dep.get("name", "unknown")
            version = dep.get("version", "0.0.0")
            
            # 檢查棄用風險
            if name.lower() in self.DEPRECATED_PACKAGES:
                predictions.append(RiskPrediction(
                    dependency_name=name,
                    risk_type="deprecation",
                    probability=0.9,
                    impact_level=RiskLevel.HIGH,
                    mitigation_actions=[
                        f"考慮替換 {name}",
                        "檢視替代方案",
                        "規劃遷移時程"
                    ]
                ))
            
            # 檢查版本過舊風險
            parsed = self._parse_version(version)
            if parsed[0] == 0:  # 0.x.x 版本
                predictions.append(RiskPrediction(
                    dependency_name=name,
                    risk_type="stability",
                    probability=0.6,
                    impact_level=RiskLevel.MEDIUM,
                    mitigation_actions=[
                        "監控版本更新",
                        "準備升級計畫",
                        "增加測試覆蓋"
                    ]
                ))
            
            # 安全風險預測
            vuln_count = dep.get("vulnerabilities", 0)
            if vuln_count > 0:
                predictions.append(RiskPrediction(
                    dependency_name=name,
                    risk_type="security",
                    probability=0.95,
                    impact_level=RiskLevel.CRITICAL if vuln_count >= 3 else RiskLevel.HIGH,
                    mitigation_actions=[
                        "立即修補漏洞",
                        "升級至安全版本",
                        "評估影響範圍"
                    ]
                ))
        
        self._risk_predictions = predictions
        return predictions
    
    # ==================== 建議生成 ====================
    
    def generate_recommendations(self,
                                dependencies: List[Dict[str, Any]]) -> List[Recommendation]:
        """
        生成建議
        
        Args:
            dependencies: 依賴項列表
            
        Returns:
            建議列表
        """
        recommendations = []
        
        for dep in dependencies:
            name = dep.get("name", "unknown")
            version = dep.get("version", "0.0.0")
            
            # 安全建議
            if dep.get("vulnerabilities", 0) > 0:
                recommendations.append(Recommendation(
                    rec_type=RecommendationType.SECURITY_FIX,
                    dependency_name=name,
                    priority=10,
                    title=f"修復 {name} 的安全漏洞",
                    description=f"發現 {dep.get('vulnerabilities', 0)} 個安全漏洞",
                    actions=[
                        f"升級 {name} 至最新版本",
                        "執行安全掃描確認",
                        "更新相關測試"
                    ],
                    estimated_effort_hours=2.0,
                    confidence=0.95
                ))
            
            # 升級建議
            if dep.get("outdated"):
                recommendations.append(Recommendation(
                    rec_type=RecommendationType.UPGRADE,
                    dependency_name=name,
                    priority=7,
                    title=f"升級 {name}",
                    description="發現新版本可用",
                    actions=[
                        "檢視變更日誌",
                        "更新依賴版本",
                        "執行回歸測試"
                    ],
                    estimated_effort_hours=1.0,
                    confidence=0.8
                ))
            
            # 替換建議
            if name.lower() in self.DEPRECATED_PACKAGES:
                alternatives = self.find_alternatives(name, version)
                if alternatives:
                    best_alt = alternatives[0]
                    recommendations.append(Recommendation(
                        rec_type=RecommendationType.REPLACE,
                        dependency_name=name,
                        priority=8,
                        title=f"替換 {name} 為 {best_alt.name}",
                        description=f"{name} 已不再維護，建議替換為 {best_alt.name}",
                        actions=[
                            f"安裝 {best_alt.name}",
                            "更新匯入語句",
                            "修改 API 呼叫",
                            "移除舊依賴"
                        ],
                        estimated_effort_hours=4.0,
                        confidence=0.75
                    ))
        
        # 按優先級排序
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        self._recommendations = recommendations
        
        return recommendations
    
    # ==================== 報告生成 ====================
    
    def generate_insight_report(self,
                               dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成洞察報告
        
        Args:
            dependencies: 依賴項列表
            
        Returns:
            洞察報告
        """
        # 計算健康度
        health_scores = []
        for dep in dependencies:
            score = self.calculate_health_score(
                dep.get("name", "unknown"),
                dep.get("version", "0.0.0"),
                dep
            )
            health_scores.append({
                "name": dep.get("name"),
                "score": score.overall_score,
                "grade": score.grade
            })
        
        # 預測風險
        risks = self.predict_risks(dependencies)
        
        # 生成建議
        recommendations = self.generate_recommendations(dependencies)
        
        # 統計
        avg_health = sum(h["score"] for h in health_scores) / len(health_scores) if health_scores else 0
        critical_risks = len([r for r in risks if r.impact_level == RiskLevel.CRITICAL])
        high_priority_recs = len([r for r in recommendations if r.priority >= 8])
        
        return {
            "summary": {
                "total_dependencies": len(dependencies),
                "average_health_score": avg_health,
                "critical_risks": critical_risks,
                "high_priority_recommendations": high_priority_recs
            },
            "health_scores": health_scores,
            "risks": [
                {
                    "dependency": r.dependency_name,
                    "type": r.risk_type,
                    "probability": r.probability,
                    "impact": r.impact_level.value,
                    "mitigations": r.mitigation_actions
                }
                for r in risks
            ],
            "recommendations": [
                {
                    "type": r.rec_type.value,
                    "dependency": r.dependency_name,
                    "priority": r.priority,
                    "title": r.title,
                    "actions": r.actions,
                    "effort_hours": r.estimated_effort_hours
                }
                for r in recommendations
            ]
        }
    
    def format_report_zh_tw(self, report: Dict[str, Any]) -> str:
        """
        生成繁體中文報告
        
        Args:
            report: 報告資料
            
        Returns:
            格式化報告
        """
        lines = [
            "=" * 60,
            "🤖 智能洞察報告 - 依賴管理建議",
            "=" * 60,
            "",
            "📊 摘要",
            "-" * 40,
            f"  依賴項總數：{report['summary']['total_dependencies']}",
            f"  平均健康度：{report['summary']['average_health_score']:.1f}/100",
            f"  關鍵風險：{report['summary']['critical_risks']} 個",
            f"  高優先建議：{report['summary']['high_priority_recommendations']} 項",
            "",
            "🏥 健康度評分",
            "-" * 40,
        ]
        
        # 健康度排行
        sorted_health = sorted(report["health_scores"], 
                               key=lambda x: x["score"], reverse=True)
        for h in sorted_health[:10]:
            grade_emoji = {"A": "🌟", "B": "✅", "C": "⚠️", "D": "🔶", "F": "🔴"}
            emoji = grade_emoji.get(h["grade"], "❓")
            lines.append(f"  {emoji} {h['name']}: {h['score']:.0f} ({h['grade']})")
        
        lines.extend([
            "",
            "⚠️ 風險預警",
            "-" * 40,
        ])
        
        risk_emoji = {
            "critical": "🚨",
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        
        for r in report["risks"][:5]:
            emoji = risk_emoji.get(r["impact"], "❓")
            lines.append(f"  {emoji} [{r['type']}] {r['dependency']}")
            lines.append(f"     發生機率：{r['probability']*100:.0f}%")
        
        lines.extend([
            "",
            "💡 建議行動",
            "-" * 40,
        ])
        
        type_zh = {
            "security_fix": "🔒 安全修復",
            "upgrade": "⬆️ 升級",
            "replace": "🔄 替換",
            "remove": "🗑️ 移除",
            "consolidate": "📦 整合",
            "best_practice": "✨ 最佳實踐"
        }
        
        for r in report["recommendations"][:10]:
            type_label = type_zh.get(r["type"], r["type"])
            lines.append(f"  [{r['priority']}/10] {type_label}")
            lines.append(f"     {r['title']}")
            lines.append(f"     預估工時：{r['effort_hours']:.1f} 小時")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)
