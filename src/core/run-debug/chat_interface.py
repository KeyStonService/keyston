"""
聊天式偵錯介面
Chat-based Debug Interface

使用自然語言進行偵錯的智能介面。
"""

import asyncio
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .engine import get_engine, DebugSession, DebugState
from .cli import DebugCLI


class IntentType(Enum):
    """意圖類型"""
    START_DEBUG = "start_debug"
    SET_BREAKPOINT = "set_breakpoint"
    REMOVE_BREAKPOINT = "remove_breakpoint"
    CONTINUE = "continue"
    STEP_OVER = "step_over"
    STEP_INTO = "step_into"
    STEP_OUT = "step_out"
    SHOW_VARIABLES = "show_variables"
    EVALUATE = "evaluate"
    SHOW_STACK = "show_stack"
    EXPLAIN_ERROR = "explain_error"
    SUGGEST_FIX = "suggest_fix"
    OPTIMIZE_CODE = "optimize_code"
    STOP_DEBUG = "stop_debug"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """意圖識別結果"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any]
    original_text: str


class NaturalLanguageProcessor:
    """自然語言處理器"""
    
    def __init__(self):
        self.patterns = {
            IntentType.START_DEBUG: [
                r"啟動.*偵錯",
                r"開始.*debug",
                r"start.*debug",
                r"執行.*偵錯",
            ],
            IntentType.SET_BREAKPOINT: [
                r"設定.*斷點.*第\s*(\d+)\s*行",
                r"在.*第\s*(\d+)\s*行.*設定斷點",
                r"break.*line\s*(\d+)",
                r"斷點.*(\d+)",
            ],
            IntentType.REMOVE_BREAKPOINT: [
                r"移除.*斷點\s*(\d+)",
                r"刪除.*斷點\s*(\d+)",
                r"remove.*breakpoint\s*(\d+)",
            ],
            IntentType.CONTINUE: [
                r"繼續執行",
                r"繼續",
                r"continue",
                r"執行",
            ],
            IntentType.STEP_OVER: [
                r"單步.*跳過",
                r"下一行",
                r"step over",
                r"next",
            ],
            IntentType.STEP_INTO: [
                r"單步.*進入",
                r"進入函數",
                r"step into",
                r"step in",
            ],
            IntentType.STEP_OUT: [
                r"單步.*跳出",
                r"跳出函數",
                r"step out",
            ],
            IntentType.SHOW_VARIABLES: [
                r"顯示.*變數",
                r"查看.*變數",
                r"show.*variables",
                r"變數.*值",
            ],
            IntentType.EVALUATE: [
                r"計算\s*(.+)",
                r"評估\s*(.+)",
                r"evaluate\s*(.+)",
                r"(.+).*的值",
            ],
            IntentType.SHOW_STACK: [
                r"堆疊.*追蹤",
                r"call stack",
                r"stack trace",
                r"顯示.*堆疊",
            ],
            IntentType.EXPLAIN_ERROR: [
                r"為什麼.*錯誤",
                r"為什麼.*崩潰",
                r"為什麼.*失敗",
                r"explain.*error",
                r"what.*wrong",
            ],
            IntentType.SUGGEST_FIX: [
                r"如何.*修復",
                r"怎麼.*解決",
                r"suggest.*fix",
                r"how.*fix",
            ],
            IntentType.OPTIMIZE_CODE: [
                r"如何.*優化",
                r"優化.*程式碼",
                r"optimize",
                r"improve",
            ],
            IntentType.STOP_DEBUG: [
                r"停止.*偵錯",
                r"結束.*debug",
                r"stop.*debug",
            ],
            IntentType.HELP: [
                r"幫助",
                r"help",
                r"怎麼用",
                r"如何使用",
            ],
        }
    
    def parse(self, text: str) -> Intent:
        """解析自然語言輸入"""
        text = text.strip().lower()
        
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {}
                    
                    # 提取實體
                    if intent_type == IntentType.SET_BREAKPOINT:
                        if match.groups():
                            entities['line'] = int(match.group(1))
                    elif intent_type == IntentType.REMOVE_BREAKPOINT:
                        if match.groups():
                            entities['breakpoint_id'] = int(match.group(1))
                    elif intent_type == IntentType.EVALUATE:
                        if match.groups():
                            entities['expression'] = match.group(1).strip()
                    
                    return Intent(
                        type=intent_type,
                        confidence=0.9,
                        entities=entities,
                        original_text=text
                    )
        
        return Intent(
            type=IntentType.UNKNOWN,
            confidence=0.0,
            entities={},
            original_text=text
        )


class ErrorAnalyzer:
    """錯誤分析器"""
    
    def __init__(self):
        self.common_errors = {
            'ZeroDivisionError': {
                'explanation': '除以零錯誤：嘗試將數字除以零。',
                'causes': [
                    '變數值為 0',
                    '計算結果為 0',
                    '未初始化的變數',
                ],
                'fixes': [
                    '在除法前檢查除數是否為 0',
                    '使用 try-except 捕獲異常',
                    '確保變數正確初始化',
                ]
            },
            'NameError': {
                'explanation': '名稱錯誤：使用了未定義的變數或函數。',
                'causes': [
                    '變數名拼寫錯誤',
                    '變數未定義',
                    '作用域問題',
                ],
                'fixes': [
                    '檢查變數名拼寫',
                    '確保變數已定義',
                    '檢查變數作用域',
                ]
            },
            'TypeError': {
                'explanation': '類型錯誤：對不支援的類型執行操作。',
                'causes': [
                    '類型不匹配',
                    '參數數量錯誤',
                    '不支援的操作',
                ],
                'fixes': [
                    '檢查變數類型',
                    '使用類型轉換',
                    '檢查函數參數',
                ]
            },
            'IndexError': {
                'explanation': '索引錯誤：訪問了不存在的索引。',
                'causes': [
                    '索引超出範圍',
                    '列表為空',
                    '索引計算錯誤',
                ],
                'fixes': [
                    '檢查列表長度',
                    '使用 try-except',
                    '驗證索引範圍',
                ]
            },
            'KeyError': {
                'explanation': '鍵錯誤：訪問了不存在的字典鍵。',
                'causes': [
                    '鍵不存在',
                    '鍵名拼寫錯誤',
                    '字典未初始化',
                ],
                'fixes': [
                    '使用 dict.get() 方法',
                    '檢查鍵是否存在',
                    '使用 defaultdict',
                ]
            },
            'AttributeError': {
                'explanation': '屬性錯誤：對象沒有該屬性。',
                'causes': [
                    '屬性名錯誤',
                    '對象類型錯誤',
                    '屬性未定義',
                ],
                'fixes': [
                    '檢查屬性名',
                    '使用 hasattr() 檢查',
                    '確認對象類型',
                ]
            },
        }
    
    def analyze(self, error_type: str, error_message: str, 
                stack_trace: List[str]) -> Dict[str, Any]:
        """分析錯誤"""
        analysis = {
            'error_type': error_type,
            'error_message': error_message,
            'explanation': '',
            'possible_causes': [],
            'suggested_fixes': [],
            'related_code': [],
        }
        
        # 查找已知錯誤
        if error_type in self.common_errors:
            error_info = self.common_errors[error_type]
            analysis['explanation'] = error_info['explanation']
            analysis['possible_causes'] = error_info['causes']
            analysis['suggested_fixes'] = error_info['fixes']
        else:
            analysis['explanation'] = f'發生了 {error_type} 錯誤。'
            analysis['suggested_fixes'] = ['檢查錯誤訊息', '查看堆疊追蹤', '檢查相關程式碼']
        
        return analysis


class CodeOptimizer:
    """程式碼優化器"""
    
    def __init__(self):
        self.optimization_patterns = [
            {
                'name': '列表推導式',
                'pattern': r'for .+ in .+:\s+.+\.append',
                'suggestion': '考慮使用列表推導式來簡化程式碼並提升效能',
                'example': '[x for x in items if condition]'
            },
            {
                'name': 'f-string',
                'pattern': r'["\'].+["\']\.format\(',
                'suggestion': '使用 f-string 可以提升可讀性和效能',
                'example': 'f"Hello {name}"'
            },
            {
                'name': '生成器表達式',
                'pattern': r'sum\(\[.+\]\)',
                'suggestion': '對於大型數據集，使用生成器表達式可以節省記憶體',
                'example': 'sum(x for x in items)'
            },
        ]
    
    def analyze_code(self, code: str) -> List[Dict[str, str]]:
        """分析程式碼並提供優化建議"""
        suggestions = []
        
        for pattern_info in self.optimization_patterns:
            if re.search(pattern_info['pattern'], code):
                suggestions.append({
                    'name': pattern_info['name'],
                    'suggestion': pattern_info['suggestion'],
                    'example': pattern_info['example']
                })
        
        return suggestions


class ChatDebugInterface:
    """聊天式偵錯介面"""
    
    def __init__(self):
        self.cli = DebugCLI()
        self.nlp = NaturalLanguageProcessor()
        self.error_analyzer = ErrorAnalyzer()
        self.code_optimizer = CodeOptimizer()
        self.conversation_history: List[Dict[str, str]] = []
    
    async def process_message(self, message: str) -> str:
        """處理使用者訊息"""
        # 記錄對話
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # 解析意圖
        intent = self.nlp.parse(message)
        
        # 根據意圖執行動作
        response = await self._handle_intent(intent)
        
        # 記錄回應
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        return response
    
    async def _handle_intent(self, intent: Intent) -> str:
        """處理意圖"""
        if intent.type == IntentType.START_DEBUG:
            return await self._handle_start_debug(intent)
        
        elif intent.type == IntentType.SET_BREAKPOINT:
            return await self._handle_set_breakpoint(intent)
        
        elif intent.type == IntentType.REMOVE_BREAKPOINT:
            return await self._handle_remove_breakpoint(intent)
        
        elif intent.type == IntentType.CONTINUE:
            return await self._handle_continue(intent)
        
        elif intent.type == IntentType.STEP_OVER:
            return await self._handle_step_over(intent)
        
        elif intent.type == IntentType.STEP_INTO:
            return await self._handle_step_into(intent)
        
        elif intent.type == IntentType.STEP_OUT:
            return await self._handle_step_out(intent)
        
        elif intent.type == IntentType.SHOW_VARIABLES:
            return await self._handle_show_variables(intent)
        
        elif intent.type == IntentType.EVALUATE:
            return await self._handle_evaluate(intent)
        
        elif intent.type == IntentType.SHOW_STACK:
            return await self._handle_show_stack(intent)
        
        elif intent.type == IntentType.EXPLAIN_ERROR:
            return await self._handle_explain_error(intent)
        
        elif intent.type == IntentType.SUGGEST_FIX:
            return await self._handle_suggest_fix(intent)
        
        elif intent.type == IntentType.OPTIMIZE_CODE:
            return await self._handle_optimize_code(intent)
        
        elif intent.type == IntentType.STOP_DEBUG:
            return await self._handle_stop_debug(intent)
        
        elif intent.type == IntentType.HELP:
            return self._handle_help()
        
        else:
            return self._handle_unknown(intent)
    
    async def _handle_start_debug(self, intent: Intent) -> str:
        """處理啟動偵錯"""
        # 載入配置
        configs = self.cli.config_manager.load_configurations()
        
        if not configs:
            return "❌ 找不到偵錯配置。請先建立 .vscode/launch.json 檔案。"
        
        # 如果只有一個配置，直接使用
        if len(configs) == 1:
            config_name = configs[0].name
        else:
            # 列出可用配置
            config_list = "\n".join([f"  {i+1}. {c.name}" for i, c in enumerate(configs)])
            return f"請選擇要使用的配置：\n{config_list}\n\n請說「使用配置 1」或直接說配置名稱。"
        
        success = await self.cli.start_debug(config_name)
        if success:
            return f"✅ 已啟動偵錯會話：{config_name}\n\n您可以：\n- 設定斷點\n- 開始執行\n- 檢視變數"
        else:
            return "❌ 啟動偵錯會話失敗。請檢查配置是否正確。"
    
    async def _handle_set_breakpoint(self, intent: Intent) -> str:
        """處理設定斷點"""
        line = intent.entities.get('line')
        if not line:
            return "請指定要設定斷點的行號，例如：「在第 10 行設定斷點」"
        
        # 取得當前檔案（簡化版，實際應該從上下文獲取）
        if not self.cli.current_session_id:
            return "❌ 請先啟動偵錯會話"
        
        session = self.cli.engine.get_session(self.cli.current_session_id)
        if not session or not session.config.program:
            return "❌ 無法確定目標檔案"
        
        file = session.config.program
        success = await self.cli.set_breakpoint(file, line)
        
        if success:
            return f"✅ 已在 {file} 的第 {line} 行設定斷點。\n\n要繼續執行嗎？"
        else:
            return "❌ 設定斷點失敗"
    
    async def _handle_remove_breakpoint(self, intent: Intent) -> str:
        """處理移除斷點"""
        bp_id = intent.entities.get('breakpoint_id')
        if not bp_id:
            return "請指定要移除的斷點編號"
        
        success = await self.cli.remove_breakpoint(bp_id)
        if success:
            return f"✅ 已移除斷點 {bp_id}"
        else:
            return f"❌ 找不到斷點 {bp_id}"
    
    async def _handle_continue(self, intent: Intent) -> str:
        """處理繼續執行"""
        success = await self.cli.continue_execution()
        if success:
            return "▶️ 程式繼續執行中..."
        else:
            return "❌ 無法繼續執行。請確認偵錯會話是否處於暫停狀態。"
    
    async def _handle_step_over(self, intent: Intent) -> str:
        """處理單步執行（跳過）"""
        success = await self.cli.step_over()
        if success:
            # 顯示當前位置
            frames = await self.cli.engine.get_stack_trace(self.cli.current_session_id)
            if frames:
                frame = frames[0]
                return f"⏭️ 已執行到下一行\n\n📍 當前位置：{frame.file}:{frame.line}\n   {frame.name}"
            return "⏭️ 已執行到下一行"
        else:
            return "❌ 無法執行單步操作"
    
    async def _handle_step_into(self, intent: Intent) -> str:
        """處理單步執行（進入）"""
        success = await self.cli.step_into()
        if success:
            frames = await self.cli.engine.get_stack_trace(self.cli.current_session_id)
            if frames:
                frame = frames[0]
                return f"⤵️ 已進入函數\n\n📍 當前位置：{frame.file}:{frame.line}\n   {frame.name}"
            return "⤵️ 已進入函數"
        else:
            return "❌ 無法執行單步操作"
    
    async def _handle_step_out(self, intent: Intent) -> str:
        """處理單步執行（跳出）"""
        success = await self.cli.step_out()
        if success:
            frames = await self.cli.engine.get_stack_trace(self.cli.current_session_id)
            if frames:
                frame = frames[0]
                return f"⤴️ 已跳出函數\n\n📍 當前位置：{frame.file}:{frame.line}\n   {frame.name}"
            return "⤴️ 已跳出函數"
        else:
            return "❌ 無法執行單步操作"
    
    async def _handle_show_variables(self, intent: Intent) -> str:
        """處理顯示變數"""
        if not self.cli.current_session_id:
            return "❌ 請先啟動偵錯會話"
        
        variables = await self.cli.engine.get_variables(self.cli.current_session_id)
        if not variables:
            return "目前沒有可用的變數資訊"
        
        var_list = "\n".join([f"  • {var.name} = {var.value} ({var.type})" 
                             for var in variables[:10]])  # 限制顯示數量
        
        if len(variables) > 10:
            var_list += f"\n  ... 還有 {len(variables) - 10} 個變數"
        
        return f"📊 當前變數：\n{var_list}\n\n要查看特定變數的值，請說「x 的值是多少」"
    
    async def _handle_evaluate(self, intent: Intent) -> str:
        """處理評估表達式"""
        expression = intent.entities.get('expression')
        if not expression:
            return "請指定要評估的表達式"
        
        result = await self.cli.engine.evaluate_expression(
            self.cli.current_session_id, expression
        )
        
        if result:
            return f"💡 {result.name} = {result.value}\n   類型：{result.type}"
        else:
            return f"❌ 無法評估表達式「{expression}」"
    
    async def _handle_show_stack(self, intent: Intent) -> str:
        """處理顯示堆疊追蹤"""
        if not self.cli.current_session_id:
            return "❌ 請先啟動偵錯會話"
        
        frames = await self.cli.engine.get_stack_trace(self.cli.current_session_id)
        if not frames:
            return "目前沒有堆疊追蹤資訊"
        
        stack_list = []
        for i, frame in enumerate(frames):
            marker = "→" if i == 0 else " "
            stack_list.append(f"  {marker} {frame.name}")
            stack_list.append(f"    {frame.file}:{frame.line}")
        
        return f"📚 堆疊追蹤：\n" + "\n".join(stack_list)
    
    async def _handle_explain_error(self, intent: Intent) -> str:
        """處理解釋錯誤"""
        # 這裡應該從實際的錯誤資訊中提取
        # 簡化版本，假設有錯誤資訊
        error_type = "ZeroDivisionError"  # 示例
        error_message = "division by zero"
        
        analysis = self.error_analyzer.analyze(error_type, error_message, [])
        
        response = f"🔍 錯誤分析：\n\n"
        response += f"**錯誤類型**：{error_type}\n"
        response += f"**說明**：{analysis['explanation']}\n\n"
        response += f"**可能原因**：\n"
        for cause in analysis['possible_causes']:
            response += f"  • {cause}\n"
        response += f"\n**建議修復方法**：\n"
        for fix in analysis['suggested_fixes']:
            response += f"  • {fix}\n"
        
        return response
    
    async def _handle_suggest_fix(self, intent: Intent) -> str:
        """處理建議修復"""
        return """💡 修復建議：

1. **檢查變數值**
   在出錯的地方前加入檢查：
   ```python
   if divisor != 0:
       result = numerator / divisor
   ```

2. **使用異常處理**
   ```python
   try:
       result = numerator / divisor
   except ZeroDivisionError:
       result = 0  # 或其他預設值
   ```

3. **驗證輸入**
   確保輸入值符合預期範圍

要我幫您自動應用修復嗎？"""
    
    async def _handle_optimize_code(self, intent: Intent) -> str:
        """處理優化程式碼"""
        # 這裡應該分析實際的程式碼
        # 簡化版本
        suggestions = [
            {
                'name': '使用列表推導式',
                'suggestion': '第 15-20 行的迴圈可以用列表推導式簡化',
                'example': 'result = [x * 2 for x in items if x > 0]'
            }
        ]
        
        response = "🚀 優化建議：\n\n"
        for i, sugg in enumerate(suggestions, 1):
            response += f"{i}. **{sugg['name']}**\n"
            response += f"   {sugg['suggestion']}\n"
            response += f"   範例：`{sugg['example']}`\n\n"
        
        return response
    
    async def _handle_stop_debug(self, intent: Intent) -> str:
        """處理停止偵錯"""
        success = await self.cli.stop_debug()
        if success:
            return "⏹️ 偵錯會話已停止"
        else:
            return "❌ 停止偵錯會話失敗"
    
    def _handle_help(self) -> str:
        """處理幫助"""
        return """🔧 MachineNativeOps 聊天式偵錯

**可用命令**：

**基本操作**：
  • 「啟動偵錯」- 開始偵錯會話
  • 「在第 10 行設定斷點」- 設定斷點
  • 「繼續執行」- 繼續程式執行
  • 「下一行」- 單步執行（跳過）
  • 「進入函數」- 單步執行（進入）
  • 「停止偵錯」- 結束偵錯會話

**檢視資訊**：
  • 「顯示變數」- 查看所有變數
  • 「x 的值是多少」- 查看特定變數
  • 「堆疊追蹤」- 顯示呼叫堆疊

**智能診斷**：
  • 「為什麼會錯誤」- 解釋錯誤原因
  • 「如何修復」- 獲取修復建議
  • 「如何優化」- 獲取優化建議

直接用自然語言描述您的需求即可！"""
    
    def _handle_unknown(self, intent: Intent) -> str:
        """處理未知意圖"""
        return f"""抱歉，我不太理解「{intent.original_text}」的意思。

您可以：
  • 說「幫助」查看可用命令
  • 用更具體的方式描述您的需求
  • 使用常見的偵錯術語

例如：「在第 10 行設定斷點」、「顯示變數」、「為什麼會錯誤」"""


# 簡單的聊天介面測試
async def chat_loop():
    """聊天循環"""
    interface = ChatDebugInterface()
    
    print("🔧 MachineNativeOps 聊天式偵錯")
    print("輸入 'exit' 結束對話\n")
    
    while True:
        try:
            user_input = input("您: ").strip()
            
            if user_input.lower() in ['exit', 'quit', '退出']:
                print("再見！")
                break
            
            if not user_input:
                continue
            
            response = await interface.process_message(user_input)
            print(f"\nAI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n再見！")
            break
        except Exception as e:
            print(f"錯誤：{e}")


if __name__ == '__main__':
    asyncio.run(chat_loop())