"""
執行與偵錯系統示範
Run & Debug System Demonstration

這個腳本展示如何使用執行與偵錯系統的各種功能。
"""

import asyncio
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.run_debug.engine import (
    get_engine, ConfigurationManager, LaunchConfiguration,
    DebugState, BreakpointType
)
from src.core.run_debug.adapters.python_adapter import PythonDebugAdapter
from src.core.run_debug.chat_interface import ChatDebugInterface


async def demo_basic_debugging():
    """示範基本偵錯功能"""
    print("=" * 60)
    print("示範 1: 基本偵錯功能")
    print("=" * 60)
    
    # 初始化引擎
    engine = get_engine()
    engine.register_adapter('python', PythonDebugAdapter())
    
    # 建立配置
    config = LaunchConfiguration(
        name="Demo: Sample App",
        type="python",
        request="launch",
        program=str(Path(__file__).parent / "sample_app.py"),
        console="integratedTerminal"
    )
    
    # 建立會話
    print("\n✅ 建立偵錯會話...")
    session = await engine.create_session(config)
    print(f"   會話 ID: {session.session_id}")
    
    # 設定斷點
    print("\n✅ 設定斷點...")
    bp1 = session.add_breakpoint(
        str(Path(__file__).parent / "sample_app.py"),
        25,  # Calculator.divide 方法
        BreakpointType.LINE
    )
    print(f"   斷點 {bp1.id} 已設定在第 {bp1.line} 行")
    
    bp2 = session.add_breakpoint(
        str(Path(__file__).parent / "sample_app.py"),
        50,  # process_numbers 函數
        BreakpointType.CONDITIONAL,
        condition="average > 50"
    )
    print(f"   條件斷點 {bp2.id} 已設定（條件: {bp2.condition}）")
    
    # 列出斷點
    print("\n✅ 斷點列表:")
    for bp in session.get_breakpoints():
        print(f"   [{bp.id}] {bp.file}:{bp.line} ({bp.type.value})")
    
    print("\n✅ 基本偵錯示範完成！")


async def demo_chat_interface():
    """示範聊天式偵錯介面"""
    print("\n" + "=" * 60)
    print("示範 2: 聊天式偵錯介面")
    print("=" * 60)
    
    interface = ChatDebugInterface()
    
    # 測試各種自然語言命令
    test_messages = [
        "幫助",
        "啟動偵錯",
        "在第 10 行設定斷點",
        "顯示變數",
        "x 的值是多少",
        "為什麼會錯誤",
        "如何修復",
        "如何優化這段程式碼",
    ]
    
    for message in test_messages:
        print(f"\n👤 使用者: {message}")
        response = await interface.process_message(message)
        print(f"🤖 AI: {response}")
        await asyncio.sleep(0.5)  # 模擬思考時間
    
    print("\n✅ 聊天式偵錯示範完成！")


async def demo_advanced_features():
    """示範進階功能"""
    print("\n" + "=" * 60)
    print("示範 3: 進階功能")
    print("=" * 60)
    
    engine = get_engine()
    
    # 示範配置管理
    print("\n✅ 配置管理:")
    workspace_path = Path(__file__).parent
    config_manager = ConfigurationManager(workspace_path)
    
    # 建立範例配置
    example_config = LaunchConfiguration(
        name="Advanced Example",
        type="python",
        request="launch",
        program="${workspaceFolder}/sample_app.py",
        args=["--verbose"],
        env={"DEBUG": "true"},
        console="integratedTerminal"
    )
    
    config_manager.save_configuration(example_config)
    print(f"   已儲存配置: {example_config.name}")
    
    # 載入配置
    configs = config_manager.load_configurations()
    print(f"   已載入 {len(configs)} 個配置")
    for config in configs:
        print(f"   - {config.name} ({config.type})")
    
    print("\n✅ 進階功能示範完成！")


async def demo_error_analysis():
    """示範錯誤分析"""
    print("\n" + "=" * 60)
    print("示範 4: 智能錯誤分析")
    print("=" * 60)
    
    from src.core.run_debug.chat_interface import ErrorAnalyzer
    
    analyzer = ErrorAnalyzer()
    
    # 分析不同類型的錯誤
    error_types = [
        ('ZeroDivisionError', 'division by zero'),
        ('NameError', "name 'x' is not defined"),
        ('TypeError', "unsupported operand type(s) for +: 'int' and 'str'"),
        ('IndexError', 'list index out of range'),
    ]
    
    for error_type, error_message in error_types:
        print(f"\n📋 分析錯誤: {error_type}")
        analysis = analyzer.analyze(error_type, error_message, [])
        
        print(f"   說明: {analysis['explanation']}")
        print(f"   可能原因:")
        for cause in analysis['possible_causes'][:2]:
            print(f"     • {cause}")
        print(f"   建議修復:")
        for fix in analysis['suggested_fixes'][:2]:
            print(f"     • {fix}")
    
    print("\n✅ 錯誤分析示範完成！")


async def demo_code_optimization():
    """示範程式碼優化建議"""
    print("\n" + "=" * 60)
    print("示範 5: 程式碼優化建議")
    print("=" * 60)
    
    from src.core.run_debug.chat_interface import CodeOptimizer
    
    optimizer = CodeOptimizer()
    
    # 測試程式碼範例
    test_codes = [
        """
result = []
for x in items:
    result.append(x * 2)
        """,
        """
message = "Hello " + name + "!"
        """,
        """
total = sum([x * x for x in range(1000)])
        """
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n📝 程式碼範例 {i}:")
        print(code.strip())
        
        suggestions = optimizer.analyze_code(code)
        if suggestions:
            print(f"\n   💡 優化建議:")
            for sugg in suggestions:
                print(f"     • {sugg['name']}: {sugg['suggestion']}")
                print(f"       範例: {sugg['example']}")
        else:
            print(f"   ✅ 程式碼看起來不錯！")
    
    print("\n✅ 程式碼優化示範完成！")


async def interactive_demo():
    """互動式示範"""
    print("\n" + "=" * 60)
    print("互動式示範")
    print("=" * 60)
    print("\n這是一個互動式聊天偵錯示範。")
    print("您可以用自然語言與 AI 偵錯助手對話。")
    print("輸入 'exit' 結束示範。\n")
    
    interface = ChatDebugInterface()
    
    while True:
        try:
            user_input = input("您: ").strip()
            
            if user_input.lower() in ['exit', 'quit', '退出']:
                print("感謝使用！再見！")
                break
            
            if not user_input:
                continue
            
            response = await interface.process_message(user_input)
            print(f"\nAI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n感謝使用！再見！")
            break
        except Exception as e:
            print(f"錯誤: {e}")


async def main():
    """主程式"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     MachineNativeOps 執行與偵錯系統 - 完整示範               ║
║                                                              ║
║     這個示範展示了系統的各種功能：                           ║
║     1. 基本偵錯功能                                          ║
║     2. 聊天式偵錯介面                                        ║
║     3. 進階功能                                              ║
║     4. 智能錯誤分析                                          ║
║     5. 程式碼優化建議                                        ║
║     6. 互動式示範                                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 執行各個示範
    await demo_basic_debugging()
    await demo_chat_interface()
    await demo_advanced_features()
    await demo_error_analysis()
    await demo_code_optimization()
    
    # 詢問是否進入互動模式
    print("\n" + "=" * 60)
    choice = input("\n要進入互動式示範嗎？(y/n): ").strip().lower()
    if choice == 'y':
        await interactive_demo()
    
    print("\n" + "=" * 60)
    print("所有示範完成！")
    print("=" * 60)
    print("""
下一步：
  1. 查看完整文檔: docs/RUN_DEBUG_SYSTEM.md
  2. 閱讀快速入門: docs/RUN_DEBUG_QUICKSTART.md
  3. 嘗試範例程式: examples/debug-examples/sample_app.py
  4. 使用命令列工具: python -m src.core.run-debug.cli
  5. 建立自己的配置: .vscode/launch.json
    """)


if __name__ == "__main__":
    asyncio.run(main())