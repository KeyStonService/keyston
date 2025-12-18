"""
永續發展分析器 (Sustainable Development Analyzer)

功能：
- 碳足跡計算：依賴項的環境影響評估
- 能源效率分析：代碼與基礎設施的能源使用
- 綠色評分：ESG 合規性評估
- 永續建議：改善環境影響的具體建議

Features:
- Carbon Footprint Calculation: Environmental impact assessment of dependencies
- Energy Efficiency Analysis: Energy usage of code and infrastructure
- Green Score: ESG compliance assessment
- Sustainability Recommendations: Specific suggestions for improving environmental impact
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ImpactLevel(Enum):
    """環境影響等級"""
    MINIMAL = "minimal"         # 極低影響
    LOW = "low"                 # 低影響
    MODERATE = "moderate"       # 中等影響
    HIGH = "high"               # 高影響
    CRITICAL = "critical"       # 嚴重影響


class EnergyGrade(Enum):
    """能源效率等級"""
    A_PLUS = "A+"    # 極優
    A = "A"          # 優秀
    B = "B"          # 良好
    C = "C"          # 中等
    D = "D"          # 較差
    E = "E"          # 差
    F = "F"          # 極差


@dataclass
class CarbonFootprint:
    """碳足跡數據"""
    dependency_name: str
    version: str

    # 碳排放估算 (kg CO2e)
    build_emissions: float = 0.0        # 構建時排放
    runtime_emissions: float = 0.0      # 運行時排放
    transfer_emissions: float = 0.0     # 傳輸排放
    total_emissions: float = 0.0        # 總排放

    # 資源消耗
    cpu_intensity: float = 0.0          # CPU 密集度 (0-100)
    memory_footprint: float = 0.0       # 記憶體使用 (MB)
    network_usage: float = 0.0          # 網路使用 (MB/day)
    storage_footprint: float = 0.0      # 存儲使用 (MB)

    # 影響評估
    impact_level: ImpactLevel = ImpactLevel.LOW
    calculation_date: datetime | None = None
    methodology: str = "estimated"      # estimated, measured, certified

    def __post_init__(self):
        if self.calculation_date is None:
            self.calculation_date = datetime.now()
        self._calculate_total()
        self._assess_impact()

    def _calculate_total(self):
        """計算總碳排放"""
        self.total_emissions = (
            self.build_emissions +
            self.runtime_emissions +
            self.transfer_emissions
        )

    def _assess_impact(self):
        """評估環境影響等級"""
        if self.total_emissions < 0.01:
            self.impact_level = ImpactLevel.MINIMAL
        elif self.total_emissions < 0.1:
            self.impact_level = ImpactLevel.LOW
        elif self.total_emissions < 1.0:
            self.impact_level = ImpactLevel.MODERATE
        elif self.total_emissions < 10.0:
            self.impact_level = ImpactLevel.HIGH
        else:
            self.impact_level = ImpactLevel.CRITICAL


@dataclass
class EnergyEfficiency:
    """能源效率評估"""
    component_name: str
    component_type: str  # dependency, code, infrastructure

    # 效率指標
    energy_grade: EnergyGrade = EnergyGrade.C
    efficiency_score: float = 50.0      # 0-100

    # 能源使用詳情
    idle_power: float = 0.0             # 閒置功耗 (W)
    active_power: float = 0.0           # 活動功耗 (W)
    peak_power: float = 0.0             # 峰值功耗 (W)
    daily_energy: float = 0.0           # 日能耗 (kWh)
    monthly_energy: float = 0.0         # 月能耗 (kWh)

    # 優化建議
    optimization_potential: float = 0.0  # 優化潛力 (%)
    recommendations: list[str] = field(default_factory=list)

    def calculate_energy_cost(self, rate_per_kwh: float = 0.12) -> dict[str, float]:
        """計算能源成本"""
        return {
            'daily_cost': self.daily_energy * rate_per_kwh,
            'monthly_cost': self.monthly_energy * rate_per_kwh,
            'annual_cost': self.monthly_energy * 12 * rate_per_kwh,
            'savings_potential': self.monthly_energy * 12 * rate_per_kwh * (self.optimization_potential / 100)
        }


@dataclass
class GreenScore:
    """綠色評分"""
    project_name: str

    # 主要評分
    overall_score: float = 0.0          # 總分 (0-100)
    carbon_score: float = 0.0           # 碳排放評分
    energy_score: float = 0.0           # 能源效率評分
    resource_score: float = 0.0         # 資源使用評分
    lifecycle_score: float = 0.0        # 生命週期評分

    # ESG 合規
    esg_compliance: dict[str, bool] = field(default_factory=dict)
    certifications: list[str] = field(default_factory=list)

    # 趨勢
    score_history: list[dict[str, Any]] = field(default_factory=list)
    trend: str = "stable"               # improving, stable, declining

    # 報告
    assessment_date: datetime | None = None
    next_review: datetime | None = None

    def get_grade(self) -> str:
        """獲取綠色等級"""
        if self.overall_score >= 90:
            return "🌳 卓越 (Excellent)"
        elif self.overall_score >= 80:
            return "🌲 優秀 (Very Good)"
        elif self.overall_score >= 70:
            return "🌱 良好 (Good)"
        elif self.overall_score >= 60:
            return "🌿 中等 (Average)"
        elif self.overall_score >= 50:
            return "🍂 需改進 (Needs Improvement)"
        else:
            return "🍁 警告 (Poor)"


class SustainableAnalyzer:
    """
    永續發展分析器
    
    功能：
    - 分析依賴項的環境影響
    - 計算碳足跡
    - 評估能源效率
    - 生成永續發展報告
    
    Usage:
        analyzer = SustainableAnalyzer()
        analysis = analyzer.analyze_project(dependencies)
        report = analyzer.generate_report(analysis)
    """

    # 依賴項碳排放係數 (估算值)
    EMISSION_FACTORS = {
        # 按生態系統分類 (kg CO2e per install)
        'npm': {
            'base': 0.001,
            'per_mb': 0.0002,
            'per_dep': 0.0001
        },
        'pip': {
            'base': 0.0008,
            'per_mb': 0.00015,
            'per_dep': 0.00008
        },
        'go': {
            'base': 0.0006,
            'per_mb': 0.0001,
            'per_dep': 0.00005
        },
        'cargo': {
            'base': 0.0005,
            'per_mb': 0.00008,
            'per_dep': 0.00004
        },
        'maven': {
            'base': 0.002,
            'per_mb': 0.0003,
            'per_dep': 0.00015
        }
    }

    # 能源效率權重
    EFFICIENCY_WEIGHTS = {
        'cpu': 0.3,
        'memory': 0.25,
        'network': 0.2,
        'storage': 0.15,
        'lifecycle': 0.1
    }

    # ESG 框架
    ESG_FRAMEWORKS = {
        'gri': 'Global Reporting Initiative',
        'sasb': 'Sustainability Accounting Standards Board',
        'tcfd': 'Task Force on Climate-related Financial Disclosures',
        'cdp': 'Carbon Disclosure Project',
        'un_sdg': 'UN Sustainable Development Goals'
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """初始化分析器"""
        self.config = config or {}
        self.carbon_footprints: list[CarbonFootprint] = []
        self.energy_assessments: list[EnergyEfficiency] = []
        self.green_score: GreenScore | None = None

    def analyze_dependency(
        self,
        name: str,
        version: str,
        ecosystem: str,
        size_mb: float = 1.0,
        dependencies_count: int = 0
    ) -> CarbonFootprint:
        """
        分析單一依賴項的碳足跡
        
        Args:
            name: 依賴項名稱
            version: 版本號
            ecosystem: 生態系統 (npm, pip, go, etc.)
            size_mb: 大小 (MB)
            dependencies_count: 傳遞依賴數量
        
        Returns:
            CarbonFootprint: 碳足跡數據
        """
        factors = self.EMISSION_FACTORS.get(ecosystem, self.EMISSION_FACTORS['npm'])

        # 計算各項排放
        build_emissions = (
            factors['base'] +
            factors['per_mb'] * size_mb +
            factors['per_dep'] * dependencies_count
        )

        # 運行時排放（基於 CPU 和記憶體估算）
        runtime_emissions = build_emissions * 0.1  # 假設運行時為構建的 10%

        # 傳輸排放
        transfer_emissions = size_mb * 0.0001  # 每 MB 傳輸約 0.0001 kg CO2e

        footprint = CarbonFootprint(
            dependency_name=name,
            version=version,
            build_emissions=build_emissions,
            runtime_emissions=runtime_emissions,
            transfer_emissions=transfer_emissions,
            cpu_intensity=self._estimate_cpu_intensity(ecosystem, size_mb),
            memory_footprint=size_mb * 2,  # 估算記憶體使用
            network_usage=size_mb * 0.1,   # 估算每日網路使用
            storage_footprint=size_mb,
            methodology='estimated'
        )

        self.carbon_footprints.append(footprint)
        return footprint

    def _estimate_cpu_intensity(self, ecosystem: str, size_mb: float) -> float:
        """估算 CPU 密集度"""
        base_intensity = {
            'npm': 20,
            'pip': 15,
            'go': 25,
            'cargo': 30,
            'maven': 35
        }.get(ecosystem, 20)

        return min(100, base_intensity + (size_mb * 2))

    def analyze_energy_efficiency(
        self,
        component_name: str,
        component_type: str,
        metrics: dict[str, float]
    ) -> EnergyEfficiency:
        """
        分析能源效率
        
        Args:
            component_name: 組件名稱
            component_type: 組件類型
            metrics: 效能指標
        
        Returns:
            EnergyEfficiency: 能源效率評估
        """
        # 計算效率分數
        scores = {
            'cpu': 100 - min(100, metrics.get('cpu_usage', 50)),
            'memory': 100 - min(100, metrics.get('memory_usage', 50)),
            'network': 100 - min(100, metrics.get('network_usage', 30) * 2),
            'storage': 100 - min(100, metrics.get('storage_usage', 20) * 2),
            'lifecycle': metrics.get('lifecycle_efficiency', 70)
        }

        efficiency_score = sum(
            scores[k] * self.EFFICIENCY_WEIGHTS[k]
            for k in self.EFFICIENCY_WEIGHTS
        )

        # 確定等級
        energy_grade = self._score_to_grade(efficiency_score)

        # 估算功耗
        base_power = metrics.get('base_power', 10)
        idle_power = base_power * 0.3
        active_power = base_power
        peak_power = base_power * 1.5

        # 估算能耗 (假設 8 小時活動，16 小時閒置)
        daily_energy = (active_power * 8 + idle_power * 16) / 1000
        monthly_energy = daily_energy * 30

        # 生成建議
        recommendations = self._generate_efficiency_recommendations(scores)

        assessment = EnergyEfficiency(
            component_name=component_name,
            component_type=component_type,
            energy_grade=energy_grade,
            efficiency_score=efficiency_score,
            idle_power=idle_power,
            active_power=active_power,
            peak_power=peak_power,
            daily_energy=daily_energy,
            monthly_energy=monthly_energy,
            optimization_potential=max(0, 100 - efficiency_score),
            recommendations=recommendations
        )

        self.energy_assessments.append(assessment)
        return assessment

    def _score_to_grade(self, score: float) -> EnergyGrade:
        """將分數轉換為等級"""
        if score >= 95:
            return EnergyGrade.A_PLUS
        elif score >= 85:
            return EnergyGrade.A
        elif score >= 75:
            return EnergyGrade.B
        elif score >= 65:
            return EnergyGrade.C
        elif score >= 55:
            return EnergyGrade.D
        elif score >= 45:
            return EnergyGrade.E
        else:
            return EnergyGrade.F

    def _generate_efficiency_recommendations(
        self,
        scores: dict[str, float]
    ) -> list[str]:
        """生成效率優化建議"""
        recommendations = []

        if scores['cpu'] < 70:
            recommendations.append("🔧 優化 CPU 使用：考慮使用更高效的算法或非同步處理")
        if scores['memory'] < 70:
            recommendations.append("🔧 優化記憶體使用：檢查記憶體洩漏，使用串流處理大數據")
        if scores['network'] < 70:
            recommendations.append("🔧 減少網路使用：啟用壓縮，使用快取，批量處理請求")
        if scores['storage'] < 70:
            recommendations.append("🔧 優化存儲使用：清理不必要的依賴，使用更小的替代方案")
        if scores['lifecycle'] < 70:
            recommendations.append("🔧 改善生命週期管理：更新過時依賴，移除未使用的依賴")

        if not recommendations:
            recommendations.append("✅ 能源效率良好，繼續保持！")

        return recommendations

    def calculate_green_score(
        self,
        project_name: str,
        dependencies: list[dict[str, Any]]
    ) -> GreenScore:
        """
        計算專案綠色評分
        
        Args:
            project_name: 專案名稱
            dependencies: 依賴項列表
        
        Returns:
            GreenScore: 綠色評分
        """
        # 分析所有依賴項
        for dep in dependencies:
            self.analyze_dependency(
                name=dep.get('name', 'unknown'),
                version=dep.get('version', '0.0.0'),
                ecosystem=dep.get('ecosystem', 'npm'),
                size_mb=dep.get('size_mb', 1.0),
                dependencies_count=dep.get('dependencies_count', 0)
            )

        # 計算碳排放分數
        total_emissions = sum(cf.total_emissions for cf in self.carbon_footprints)
        carbon_score = max(0, 100 - (total_emissions * 10))

        # 計算能源分數（如果有評估）
        if self.energy_assessments:
            energy_score = sum(ea.efficiency_score for ea in self.energy_assessments) / len(self.energy_assessments)
        else:
            energy_score = 70  # 默認值

        # 計算資源分數
        total_memory = sum(cf.memory_footprint for cf in self.carbon_footprints)
        resource_score = max(0, 100 - (total_memory / 100))

        # 計算生命週期分數（基於依賴項數量和更新狀態）
        lifecycle_score = max(0, 100 - len(dependencies) * 0.5)

        # 計算總分
        overall_score = (
            carbon_score * 0.3 +
            energy_score * 0.3 +
            resource_score * 0.2 +
            lifecycle_score * 0.2
        )

        # ESG 合規評估
        esg_compliance = {
            'carbon_reporting': carbon_score >= 60,
            'energy_efficiency': energy_score >= 60,
            'resource_optimization': resource_score >= 60,
            'sustainable_practices': lifecycle_score >= 60
        }

        # 確定趨勢
        trend = 'stable'
        if overall_score >= 80:
            trend = 'improving'
        elif overall_score < 50:
            trend = 'declining'

        self.green_score = GreenScore(
            project_name=project_name,
            overall_score=overall_score,
            carbon_score=carbon_score,
            energy_score=energy_score,
            resource_score=resource_score,
            lifecycle_score=lifecycle_score,
            esg_compliance=esg_compliance,
            certifications=self._suggest_certifications(overall_score),
            trend=trend,
            assessment_date=datetime.now()
        )

        return self.green_score

    def _suggest_certifications(self, score: float) -> list[str]:
        """根據分數建議可申請的認證"""
        certifications = []

        if score >= 90:
            certifications.extend([
                "🏆 Green Software Foundation Certified",
                "🏆 Carbon Neutral Verified",
                "🏆 ISO 14001 Ready"
            ])
        elif score >= 80:
            certifications.extend([
                "🥈 Sustainable Software Badge",
                "🥈 Energy Star Partner Ready"
            ])
        elif score >= 70:
            certifications.append("🥉 Green Coding Initiative Member")

        return certifications

    def generate_report(self, format: str = 'text') -> str:
        """
        生成永續發展報告
        
        Args:
            format: 報告格式 (text, json, markdown)
        
        Returns:
            str: 格式化報告
        """
        if not self.green_score:
            return "尚未進行分析，請先調用 calculate_green_score()"

        if format == 'markdown':
            return self._generate_markdown_report()
        elif format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """生成文字報告"""
        gs = self.green_score

        report_lines = [
            "=" * 60,
            "🌍 永續發展分析報告",
            "=" * 60,
            f"專案名稱: {gs.project_name}",
            f"評估日期: {gs.assessment_date.strftime('%Y-%m-%d %H:%M')}",
            "",
            "📊 綠色評分",
            "-" * 40,
            f"總分: {gs.overall_score:.1f}/100 {gs.get_grade()}",
            f"  碳排放評分: {gs.carbon_score:.1f}",
            f"  能源效率評分: {gs.energy_score:.1f}",
            f"  資源使用評分: {gs.resource_score:.1f}",
            f"  生命週期評分: {gs.lifecycle_score:.1f}",
            "",
            "📈 趨勢: " + {
                'improving': '📈 改善中',
                'stable': '📊 穩定',
                'declining': '📉 下降中'
            }.get(gs.trend, '📊 穩定'),
            "",
            "🔍 ESG 合規狀態",
            "-" * 40,
        ]

        for key, value in gs.esg_compliance.items():
            status = "✅" if value else "❌"
            report_lines.append(f"  {status} {key.replace('_', ' ').title()}")

        if gs.certifications:
            report_lines.extend([
                "",
                "🏆 可申請認證",
                "-" * 40,
            ])
            for cert in gs.certifications:
                report_lines.append(f"  {cert}")

        # 碳足跡摘要
        if self.carbon_footprints:
            total_emissions = sum(cf.total_emissions for cf in self.carbon_footprints)
            report_lines.extend([
                "",
                "🌱 碳足跡摘要",
                "-" * 40,
                f"  總碳排放: {total_emissions:.4f} kg CO2e",
                f"  依賴項數量: {len(self.carbon_footprints)}",
            ])

            # 高影響依賴項
            high_impact = [cf for cf in self.carbon_footprints
                         if cf.impact_level in [ImpactLevel.HIGH, ImpactLevel.CRITICAL]]
            if high_impact:
                report_lines.append("  ⚠️ 高影響依賴項:")
                for cf in high_impact[:5]:
                    report_lines.append(f"    - {cf.dependency_name} ({cf.total_emissions:.4f} kg CO2e)")

        report_lines.extend([
            "",
            "=" * 60,
            "報告生成時間: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ])

        return "\n".join(report_lines)

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 報告"""
        gs = self.green_score

        report = f"""# 🌍 永續發展分析報告

## 專案資訊
- **專案名稱**: {gs.project_name}
- **評估日期**: {gs.assessment_date.strftime('%Y-%m-%d %H:%M')}

## 📊 綠色評分

| 指標 | 分數 |
|------|------|
| **總分** | {gs.overall_score:.1f}/100 {gs.get_grade()} |
| 碳排放評分 | {gs.carbon_score:.1f} |
| 能源效率評分 | {gs.energy_score:.1f} |
| 資源使用評分 | {gs.resource_score:.1f} |
| 生命週期評分 | {gs.lifecycle_score:.1f} |

## 📈 趨勢

"""
        trend_text = {
            'improving': '📈 改善中 - 持續保持！',
            'stable': '📊 穩定 - 尋找優化機會',
            'declining': '📉 下降中 - 需要關注'
        }.get(gs.trend, '📊 穩定')

        report += f"{trend_text}\n"

        report += """

## 🔍 ESG 合規狀態

| 項目 | 狀態 |
|------|------|
"""
        for key, value in gs.esg_compliance.items():
            status = "✅ 合規" if value else "❌ 待改進"
            report += f"| {key.replace('_', ' ').title()} | {status} |\n"

        if gs.certifications:
            report += "\n## 🏆 可申請認證\n\n"
            for cert in gs.certifications:
                report += f"- {cert}\n"

        return report

    def _generate_json_report(self) -> str:
        """生成 JSON 報告"""
        import json

        gs = self.green_score

        data = {
            'project_name': gs.project_name,
            'assessment_date': gs.assessment_date.isoformat(),
            'scores': {
                'overall': gs.overall_score,
                'carbon': gs.carbon_score,
                'energy': gs.energy_score,
                'resource': gs.resource_score,
                'lifecycle': gs.lifecycle_score
            },
            'grade': gs.get_grade(),
            'trend': gs.trend,
            'esg_compliance': gs.esg_compliance,
            'certifications': gs.certifications,
            'carbon_footprints': [
                {
                    'name': cf.dependency_name,
                    'version': cf.version,
                    'total_emissions': cf.total_emissions,
                    'impact_level': cf.impact_level.value
                }
                for cf in self.carbon_footprints
            ]
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    def get_recommendations(self) -> list[dict[str, Any]]:
        """
        獲取永續發展建議
        
        Returns:
            List[Dict]: 建議列表
        """
        recommendations = []

        if not self.green_score:
            return [{'type': 'info', 'message': '請先進行分析'}]

        gs = self.green_score

        # 碳排放建議
        if gs.carbon_score < 70:
            recommendations.append({
                'type': 'carbon',
                'priority': 'high',
                'title': '減少碳排放',
                'description': '考慮使用更輕量的依賴項或減少依賴數量',
                'potential_improvement': f'{70 - gs.carbon_score:.1f} 分'
            })

        # 能源效率建議
        if gs.energy_score < 70:
            recommendations.append({
                'type': 'energy',
                'priority': 'medium',
                'title': '提升能源效率',
                'description': '優化代碼效能，減少資源消耗',
                'potential_improvement': f'{70 - gs.energy_score:.1f} 分'
            })

        # 資源使用建議
        if gs.resource_score < 70:
            recommendations.append({
                'type': 'resource',
                'priority': 'medium',
                'title': '優化資源使用',
                'description': '減少記憶體和存儲使用，使用更高效的數據結構',
                'potential_improvement': f'{70 - gs.resource_score:.1f} 分'
            })

        # 生命週期建議
        if gs.lifecycle_score < 70:
            recommendations.append({
                'type': 'lifecycle',
                'priority': 'low',
                'title': '改善生命週期管理',
                'description': '定期更新依賴，移除未使用的依賴',
                'potential_improvement': f'{70 - gs.lifecycle_score:.1f} 分'
            })

        # 如果都很好
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'priority': 'info',
                'title': '永續表現優秀',
                'description': '繼續保持良好的永續發展實踐！',
                'potential_improvement': '維持現狀'
            })

        return recommendations
