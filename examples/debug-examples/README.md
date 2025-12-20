# 執行與偵錯系統 - 範例與示範

這個目錄包含了 MachineNativeOps 執行與偵錯系統的完整範例和示範。

## 📁 檔案說明

- **launch.json** - 各種語言和場景的偵錯配置範例
- **sample_app.py** - 示範用的 Python 應用程式
- **demo.py** - 完整的功能示範腳本
- **README.md** - 本檔案

## 🚀 快速開始

### 1. 安裝依賴

```bash
cd ../../  # 回到專案根目錄
pip install -r requirements.txt
```

### 2. 執行完整示範

```bash
python examples/debug-examples/demo.py
```

這將展示：
- ✅ 基本偵錯功能
- ✅ 聊天式偵錯介面
- ✅ 進階功能
- ✅ 智能錯誤分析
- ✅ 程式碼優化建議
- ✅ 互動式示範

### 3. 使用範例應用程式

```bash
# 直接執行
python examples/debug-examples/sample_app.py

# 使用偵錯器執行
python -m src.core.run-debug.cli start --config "Python: Current File"
```

## 📚 範例場景

### 場景 1：基本偵錯

```bash
# 啟動 REPL
python -m src.core.run-debug.cli repl

# 在 REPL 中
(mno-debug) start Python: Current File
(mno-debug) break examples/debug-examples/sample_app.py 25
(mno-debug) continue
(mno-debug) vars
(mno-debug) next
(mno-debug) exit
```

### 場景 2：聊天式偵錯

```python
from src.core.run_debug.chat_interface import ChatDebugInterface
import asyncio

async def main():
    interface = ChatDebugInterface()
    
    # 自然語言互動
    print(await interface.process_message("啟動偵錯"))
    print(await interface.process_message("在第 25 行設定斷點"))
    print(await interface.process_message("顯示變數"))
    print(await interface.process_message("為什麼會錯誤？"))

asyncio.run(main())
```

### 場景 3：條件斷點

```bash
# 設定條件斷點
python -m src.core.run-debug.cli breakpoint \
  examples/debug-examples/sample_app.py 50 \
  --condition "average > 50"
```

### 場景 4：日誌點

```bash
# 設定日誌點
python -m src.core.run-debug.cli breakpoint \
  examples/debug-examples/sample_app.py 30 \
  --log "計算結果: {result}"
```

## 🎯 學習路徑

### 初學者

1. **執行示範腳本**
   ```bash
   python examples/debug-examples/demo.py
   ```

2. **嘗試基本命令**
   ```bash
   python -m src.core.run-debug.cli --help
   ```

3. **使用 REPL**
   ```bash
   python -m src.core.run-debug.cli repl
   ```

### 中級使用者

1. **建立自訂配置**
   - 複製 `launch.json` 到您的專案
   - 修改配置以符合需求

2. **使用條件斷點**
   - 學習何時使用條件斷點
   - 練習編寫條件表達式

3. **探索聊天介面**
   - 嘗試不同的自然語言命令
   - 學習錯誤診斷功能

### 進階使用者

1. **建立自訂適配器**
   - 為新語言建立適配器
   - 實作 DAP 協議

2. **整合到工作流程**
   - 將偵錯整合到 CI/CD
   - 建立自動化偵錯腳本

3. **擴充功能**
   - 新增自訂診斷規則
   - 建立優化建議

## 💡 實用技巧

### 技巧 1：快速設定多個斷點

```python
# 使用 Python API
from src.core.run_debug.engine import get_engine

engine = get_engine()
session = engine.get_session(session_id)

# 批次設定斷點
breakpoints = [
    (file, 10),
    (file, 25),
    (file, 50),
]

for file, line in breakpoints:
    session.add_breakpoint(file, line)
```

### 技巧 2：儲存偵錯會話

```python
# 匯出會話資訊
import json

session_data = {
    'breakpoints': [
        {'file': bp.file, 'line': bp.line}
        for bp in session.get_breakpoints()
    ],
    'config': session.config.name
}

with open('debug_session.json', 'w') as f:
    json.dump(session_data, f, indent=2)
```

### 技巧 3：自動化錯誤診斷

```python
from src.core.run_debug.chat_interface import ErrorAnalyzer

analyzer = ErrorAnalyzer()

# 分析錯誤
try:
    # 您的程式碼
    pass
except Exception as e:
    analysis = analyzer.analyze(
        type(e).__name__,
        str(e),
        []
    )
    print(analysis['explanation'])
    print(analysis['suggested_fixes'])
```

## 🔧 常見問題

### Q1: 如何偵錯遠端應用程式？

**A:** 使用遠端附加配置：

```json
{
  "name": "Python: Remote Attach",
  "type": "python",
  "request": "attach",
  "connect": {
    "host": "remote-server.com",
    "port": 5678
  }
}
```

### Q2: 如何偵錯 Docker 容器中的應用程式？

**A:**
1. 在容器中安裝 debugpy
2. 暴露偵錯端口
3. 使用附加配置連接

```dockerfile
# Dockerfile
RUN pip install debugpy
EXPOSE 5678
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "app.py"]
```

### Q3: 如何同時偵錯前後端？

**A:** 使用複合配置：

```json
{
  "name": "Full Stack",
  "type": "compound",
  "configurations": [
    "Python: Backend",
    "Node: Frontend"
  ]
}
```

## 📖 更多資源

- [完整文檔](../../docs/RUN_DEBUG_SYSTEM.md)
- [快速入門](../../docs/RUN_DEBUG_QUICKSTART.md)
- [API 參考](../../docs/RUN_DEBUG_API.md)
- [故障排除](../../docs/RUN_DEBUG_TROUBLESHOOTING.md)

## 🤝 貢獻

歡迎提交新的範例和改進建議！

1. Fork 專案
2. 建立功能分支
3. 提交變更
4. 發送 Pull Request

## 📝 授權

MIT License - 詳見 [LICENSE](../../LICENSE)