"""
基本使用示例
Basic Usage Example

演示如何使用 Automation Architect 系統進行代碼分析
"""

import asyncio
import sys
from pathlib import Path

# 添加父目錄到路徑以便導入
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestration.pipeline import AnalysisPipeline


async def main():
    """主函數"""
    
    print("=== Automation Architect - 基本使用示例 ===\n")
    
    # 創建分析管線
    pipeline = AnalysisPipeline()
    
    # 示例代碼路徑 (可以替換為實際代碼路徑)
    code_path = str(Path(__file__).parent.parent / "core" / "analysis" / "static_analyzer.py")
    
    print(f"分析目標: {code_path}\n")
    
    # 執行分析
    print("開始執行代碼分析...")
    result = await pipeline.analyze(
        code_path=code_path,
        scenario='general',
        enable_repair=False,
        enable_verification=False
    )
    
    # 顯示結果
    print(f"\n分析狀態: {'成功' if result.success else '失敗'}")
    print(f"執行時間: {result.execution_time_ms:.2f}ms")
    print(f"消息: {result.message}\n")
    
    # 顯示靜態分析結果
    if result.analysis_results.get('static_analysis'):
        static = result.analysis_results['static_analysis']
        if static['status'] == 'completed':
            summary = static['summary']
            print("=== 靜態分析結果 ===")
            print(f"總問題數: {summary['total_issues']}")
            print(f"嚴重程度統計: {summary['severity_counts']}")
            print(f"分析時間: {summary['analysis_time_ms']:.2f}ms\n")
    
    # 顯示安全掃描結果
    if result.analysis_results.get('security_scan'):
        security = result.analysis_results['security_scan']
        if security['status'] == 'completed':
            report = security['report']
            print("=== 安全掃描結果 ===")
            print(f"總問題數: {report['total_issues']}")
            print(f"嚴重程度統計: {report['severity_counts']}")
            
            if report['critical_files']:
                print(f"包含嚴重問題的文件: {len(report['critical_files'])}")
            print()
    
    # 顯示性能分析結果
    if result.analysis_results.get('performance_analysis'):
        perf = result.analysis_results['performance_analysis']
        if perf['status'] == 'completed':
            print("=== 性能分析結果 ===")
            print(f"性能問題數: {perf['issues_count']}\n")
    
    print("=== 管線統計信息 ===")
    stats = pipeline.get_statistics()
    print(f"管線版本: {stats['pipeline_version']}")
    print(f"分析器: {list(stats['analyzers'].keys())}")
    print(f"修復工具: {list(stats['repair_tools'].keys())}")


if __name__ == '__main__':
    asyncio.run(main())
