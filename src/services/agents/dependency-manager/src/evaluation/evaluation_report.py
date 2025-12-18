"""
評估報告生成器

生成多格式的 SMART-V 評估報告。
"""

import json
from dataclasses import dataclass
from datetime import datetime

from .smartv_framework import EvaluationDimension, SMARTVResult


@dataclass
class ReportConfig:
    """報告配置"""
    include_details: bool = True
    include_recommendations: bool = True
    include_charts: bool = False
    language: str = "zh-TW"
    format: str = "markdown"


class EvaluationReportGenerator:
    """評估報告生成器"""

    DIMENSION_NAMES = {
        "zh-TW": {
            "scalability": "可擴展性",
            "market_fit": "市場適配度",
            "achievability": "可實現性",
            "roi": "投資報酬率",
            "technology_maturity": "技術成熟度",
            "value_creation": "價值創造",
        },
        "en": {
            "scalability": "Scalability",
            "market_fit": "Market Fit",
            "achievability": "Achievability",
            "roi": "ROI",
            "technology_maturity": "Technology Maturity",
            "value_creation": "Value Creation",
        }
    }

    GRADE_EMOJIS = {
        "A+": "🏆", "A": "🥇", "A-": "🥈",
        "B+": "🥉", "B": "⭐", "B-": "✨",
        "C+": "📊", "C": "📈", "C-": "📉",
        "D": "⚠️", "F": "❌"
    }

    LEVEL_INDICATORS = {
        "excellent": "🟢",
        "good": "🔵",
        "average": "🟡",
        "below_average": "🟠",
        "poor": "🔴"
    }

    def __init__(self, config: ReportConfig | None = None):
        self.config = config or ReportConfig()

    def generate(
        self,
        result: SMARTVResult,
        format: str | None = None
    ) -> str:
        """生成報告"""
        fmt = format or self.config.format

        if fmt == "markdown":
            return self._generate_markdown(result)
        elif fmt == "text":
            return self._generate_text(result)
        elif fmt == "json":
            return result.to_json()
        elif fmt == "html":
            return self._generate_html(result)
        else:
            return self._generate_text(result)

    def _get_dimension_name(self, dim: str) -> str:
        """獲取維度名稱"""
        names = self.DIMENSION_NAMES.get(self.config.language, self.DIMENSION_NAMES["zh-TW"])
        return names.get(dim, dim)

    def _generate_markdown(self, result: SMARTVResult) -> str:
        """生成 Markdown 格式報告"""
        lines = []

        # 標題
        lines.append("# 📊 SMART-V 評估報告")
        lines.append("")
        lines.append(f"**專案名稱**: {result.project_name}")
        lines.append(f"**評估日期**: {result.evaluation_date[:10]}")
        lines.append(f"**評估者**: {result.evaluator}")
        lines.append("")

        # 總體評分
        emoji = self.GRADE_EMOJIS.get(result.overall_grade, "📊")
        lines.append(f"## {emoji} 總體評分")
        lines.append("")
        lines.append("| 指標 | 數值 |")
        lines.append("|------|------|")
        lines.append(f"| 加權總分 | **{result.weighted_total:.2f}** / 10.0 |")
        lines.append(f"| 整體等級 | **{result.overall_grade}** |")
        lines.append("")

        # 維度評分
        lines.append("## 📈 維度評分詳情")
        lines.append("")
        lines.append("| 維度 | 分數 | 等級 | 權重 | 加權分 |")
        lines.append("|------|------|------|------|--------|")

        for dim, score in result.scores.items():
            dim_name = self._get_dimension_name(dim.value)
            indicator = self.LEVEL_INDICATORS.get(score.level.value, "⚪")
            weight = result.weights[dim]
            weighted = score.score * weight
            lines.append(
                f"| {indicator} {dim_name} | {score.score:.1f} | "
                f"{score.level.value} | {weight:.0%} | {weighted:.2f} |"
            )

        lines.append("")

        # 詳細分析
        if self.config.include_details:
            lines.append("## 🔍 詳細分析")
            lines.append("")

            for dim, score in result.scores.items():
                dim_name = self._get_dimension_name(dim.value)
                indicator = self.LEVEL_INDICATORS.get(score.level.value, "⚪")

                lines.append(f"### {indicator} {dim_name}")
                lines.append("")
                lines.append(f"- **分數**: {score.score:.1f} / 10.0 ({score.percentage:.1f}%)")
                lines.append(f"- **等級**: {score.level.value}")
                lines.append("")

                if score.details:
                    lines.append("**子項目評分**:")
                    for key, value in score.details.items():
                        if isinstance(value, (int, float)):
                            lines.append(f"- {key}: {value:.1f}")
                    lines.append("")

        # 改進建議
        if self.config.include_recommendations and result.recommendations:
            lines.append("## 💡 改進建議")
            lines.append("")
            for i, rec in enumerate(result.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        # 雷達圖資料（如果啟用）
        if self.config.include_charts:
            lines.append("## 📊 視覺化數據")
            lines.append("")
            lines.append("```json")
            chart_data = {
                "labels": [self._get_dimension_name(d.value) for d in result.scores],
                "values": [s.score for s in result.scores.values()]
            }
            lines.append(json.dumps(chart_data, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

        # 頁尾
        lines.append("---")
        lines.append(f"*報告生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)

    def _generate_text(self, result: SMARTVResult) -> str:
        """生成純文字格式報告"""
        lines = []

        lines.append("=" * 60)
        lines.append("SMART-V 評估報告")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"專案名稱: {result.project_name}")
        lines.append(f"評估日期: {result.evaluation_date[:10]}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("總體評分")
        lines.append("-" * 60)
        lines.append(f"加權總分: {result.weighted_total:.2f} / 10.0")
        lines.append(f"整體等級: {result.overall_grade}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("維度評分")
        lines.append("-" * 60)

        for dim, score in result.scores.items():
            dim_name = self._get_dimension_name(dim.value)
            weight = result.weights[dim]
            lines.append(f"  {dim_name}: {score.score:.1f} (權重: {weight:.0%})")

        lines.append("")

        if self.config.include_recommendations and result.recommendations:
            lines.append("-" * 60)
            lines.append("改進建議")
            lines.append("-" * 60)
            for i, rec in enumerate(result.recommendations, 1):
                lines.append(f"  {i}. {rec}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html(self, result: SMARTVResult) -> str:
        """生成 HTML 格式報告"""
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>SMART-V 評估報告 - {result.project_name}</title>
    <style>
        body {{ font-family: 'Microsoft JhengHei', sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .grade {{ font-size: 3em; text-align: center; }}
        .score-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .score-table th, .score-table td {{ border: 1px solid #ddd; padding: 12px; }}
        .score-table th {{ background-color: #3498db; color: white; }}
        .excellent {{ color: #27ae60; }}
        .good {{ color: #2980b9; }}
        .average {{ color: #f39c12; }}
        .below_average {{ color: #e67e22; }}
        .poor {{ color: #e74c3c; }}
        .recommendations {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>📊 SMART-V 評估報告</h1>
    <p><strong>專案</strong>: {result.project_name}</p>
    <p><strong>日期</strong>: {result.evaluation_date[:10]}</p>
    
    <div class="grade">
        {self.GRADE_EMOJIS.get(result.overall_grade, '📊')} {result.overall_grade}
        <br><small>({result.weighted_total:.2f} / 10.0)</small>
    </div>
    
    <h2>維度評分</h2>
    <table class="score-table">
        <tr>
            <th>維度</th>
            <th>分數</th>
            <th>等級</th>
            <th>權重</th>
        </tr>
"""

        for dim, score in result.scores.items():
            dim_name = self._get_dimension_name(dim.value)
            weight = result.weights[dim]
            level_class = score.level.value
            html += f"""
        <tr>
            <td>{dim_name}</td>
            <td>{score.score:.1f}</td>
            <td class="{level_class}">{score.level.value}</td>
            <td>{weight:.0%}</td>
        </tr>
"""

        html += """
    </table>
"""

        if self.config.include_recommendations and result.recommendations:
            html += """
    <h2>💡 改進建議</h2>
    <div class="recommendations">
        <ol>
"""
            for rec in result.recommendations:
                html += f"            <li>{rec}</li>\n"

            html += """
        </ol>
    </div>
"""

        html += f"""
    <hr>
    <p><small>報告生成於 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
</body>
</html>
"""
        return html

    def generate_comparison_report(
        self,
        results: list[SMARTVResult]
    ) -> str:
        """生成多專案比較報告"""
        lines = []

        lines.append("# 📊 SMART-V 專案比較報告")
        lines.append("")
        lines.append(f"**比較專案數**: {len(results)}")
        lines.append(f"**報告日期**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("")

        # 總分比較表
        lines.append("## 總體評分比較")
        lines.append("")

        header = "| 專案 | 總分 | 等級 |"
        separator = "|------|------|------|"
        lines.append(header)
        lines.append(separator)

        for result in sorted(results, key=lambda r: r.weighted_total, reverse=True):
            emoji = self.GRADE_EMOJIS.get(result.overall_grade, "📊")
            lines.append(f"| {result.project_name} | {result.weighted_total:.2f} | {emoji} {result.overall_grade} |")

        lines.append("")

        # 維度比較
        lines.append("## 維度評分比較")
        lines.append("")

        # 建立維度比較表
        dimensions = list(EvaluationDimension)
        header = "| 維度 | " + " | ".join([r.project_name for r in results]) + " |"
        separator = "|------|" + "|".join(["------"] * len(results)) + "|"

        lines.append(header)
        lines.append(separator)

        for dim in dimensions:
            dim_name = self._get_dimension_name(dim.value)
            scores = [f"{r.scores[dim].score:.1f}" for r in results]
            lines.append(f"| {dim_name} | " + " | ".join(scores) + " |")

        lines.append("")

        # 優劣勢分析
        lines.append("## 優劣勢分析")
        lines.append("")

        for result in results:
            lines.append(f"### {result.project_name}")

            # 找出最高和最低分維度
            sorted_dims = sorted(
                result.scores.items(),
                key=lambda x: x[1].score,
                reverse=True
            )

            best = sorted_dims[0]
            worst = sorted_dims[-1]

            lines.append(f"- **最強維度**: {self._get_dimension_name(best[0].value)} ({best[1].score:.1f})")
            lines.append(f"- **待改進維度**: {self._get_dimension_name(worst[0].value)} ({worst[1].score:.1f})")
            lines.append("")

        return "\n".join(lines)

    def generate_executive_summary(self, result: SMARTVResult) -> str:
        """生成執行摘要"""
        emoji = self.GRADE_EMOJIS.get(result.overall_grade, "📊")

        # 找出優勢和劣勢
        sorted_dims = sorted(
            result.scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )

        strengths = [d for d in sorted_dims[:2] if d[1].score >= 7]
        weaknesses = [d for d in sorted_dims[-2:] if d[1].score < 6]

        summary = f"""## 執行摘要

**專案**: {result.project_name}
**評估等級**: {emoji} {result.overall_grade} ({result.weighted_total:.1f}/10.0)

### 關鍵發現

"""

        if strengths:
            summary += "**優勢領域**:\n"
            for dim, score in strengths:
                summary += f"- {self._get_dimension_name(dim.value)}: {score.score:.1f}\n"
            summary += "\n"

        if weaknesses:
            summary += "**需要關注**:\n"
            for dim, score in weaknesses:
                summary += f"- {self._get_dimension_name(dim.value)}: {score.score:.1f}\n"
            summary += "\n"

        if result.recommendations:
            summary += "### 首要建議\n\n"
            for rec in result.recommendations[:3]:
                summary += f"- {rec}\n"

        return summary
