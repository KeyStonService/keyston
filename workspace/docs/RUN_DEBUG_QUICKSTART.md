# 執行與偵錯系統 - 快速入門

## 🚀 5 分鐘快速開始

### 步驟 1：安裝依賴

```bash
cd MachineNativeOps
pip install -r requirements.txt
```

### 步驟 2：建立 launch.json

在專案根目錄建立 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Debug Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### 步驟 3：使用終端機偵錯

```bash
# 啟動偵錯會話
python -m src.core.run-debug.cli start --config "Python: Debug Current File"

# 設定斷點
python -m src.core.run-debug.cli breakpoint src/main.py 10

# 繼續執行
python -m src.core.run-debug.cli continue

# 查看變數
python -m src.core.run-debug.cli variables

# 停止偵錯
python -m src.core.run-debug.cli stop
```

### 步驟 4：使用互動式 REPL

```bash
python -m src.core.run-debug.cli repl
```

在 REPL 中：

```
(mno-debug) start Python: Debug Current File
(mno-debug) break src/main.py 10
(mno-debug) continue
(mno-debug) vars
(mno-debug) next
(mno-debug) exit
```

### 步驟 5：使用聊天式偵錯

```python
from src.core.run_debug.chat_interface import ChatDebugInterface
import asyncio

async def main():
    interface = ChatDebugInterface()
    
    # 啟動偵錯
    response = await interface.process_message("啟動偵錯")
    print(response)
    
    # 設定斷點
    response = await interface.process_message("在第 10 行設定斷點")
    print(response)
    
    # 查看變數
    response = await interface.process_message("顯示變數")
    print(response)

asyncio.run(main())
```

## 📝 常見使用場景

### 場景 1：Python 應用程式偵錯

**launch.json**

```json
{
  "name": "Python: Flask App",
  "type": "python",
  "request": "launch",
  "module": "flask",
  "env": {
    "FLASK_APP": "app.py",
    "FLASK_ENV": "development"
  },
  "args": ["run", "--no-debugger", "--no-reload"],
  "jinja": true
}
```

**使用方式**

```bash
# 終端機
mno debug start --config "Python: Flask App"
mno debug break app.py 25
mno debug continue

# 聊天式
"啟動 Flask 應用程式偵錯"
"在處理請求的地方設定斷點"
"顯示 request 變數"
```

### 場景 2：條件斷點

```bash
# 終端機
mno debug breakpoint src/calculator.py 15 --condition "x > 100"

# 聊天式
"在第 15 行設定斷點，條件是 x 大於 100"
```

### 場景 3：日誌點

```bash
# 終端機
mno debug breakpoint src/main.py 20 --log "Value of x: {x}"

# 聊天式
"在第 20 行設定日誌點，記錄 x 的值"
```

### 場景 4：錯誤診斷

```bash
# 聊天式
"為什麼程式在第 10 行崩潰？"
"如何修復這個錯誤？"
"這段程式碼有什麼問題？"
```

### 場景 5：程式碼優化

```bash
# 聊天式
"如何優化這段程式碼？"
"這個迴圈可以改進嗎？"
"有更好的寫法嗎？"
```

## 🎯 進階功能

### 多語言支援

**Node.js 偵錯**

```json
{
  "name": "Node: Debug Server",
  "type": "node",
  "request": "launch",
  "program": "${workspaceFolder}/server.js",
  "skipFiles": ["<node_internals>/**"]
}
```

**複合配置（同時偵錯前後端）**

```json
{
  "name": "Full Stack",
  "type": "compound",
  "configurations": ["Python: Backend", "Node: Frontend"]
}
```

### 遠端偵錯

```json
{
  "name": "Python: Remote Attach",
  "type": "python",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  }
}
```

### 自訂偵錯適配器

```python
from src.core.run_debug.engine import DebugAdapter, get_engine

class MyLanguageAdapter(DebugAdapter):
    def __init__(self):
        super().__init__("mylang")
    
    async def launch(self, session):
        # 實作啟動邏輯
        pass
    
    # 實作其他方法...

# 註冊適配器
engine = get_engine()
engine.register_adapter("mylang", MyLanguageAdapter())
```

## 🔧 故障排除

### 問題 1：無法連接到偵錯器

**解決方案**：

```bash
# 檢查 debugpy 是否已安裝
pip install debugpy

# 檢查端口是否被佔用
lsof -i :5678
```

### 問題 2：斷點未觸發

**解決方案**：

- 確認檔案路徑正確
- 檢查程式碼是否被執行到
- 確認斷點已驗證（verified）

### 問題 3：變數顯示不正確

**解決方案**：

- 確認程式在斷點處暫停
- 檢查變數作用域
- 使用 `eval` 命令手動評估

## 📚 更多資源

- [完整文檔](./RUN_DEBUG_SYSTEM.md)
- [API 參考](./RUN_DEBUG_API.md)
- [範例專案](../examples/debug-examples/)
- [影片教學](https://example.com/tutorials)

## 💡 提示與技巧

1. **使用快捷鍵**：在 REPL 中使用 Tab 自動完成
2. **保存配置**：將常用配置保存到 launch.json
3. **使用別名**：為常用命令建立別名
4. **記錄會話**：使用 `--log` 參數記錄偵錯會話
5. **團隊協作**：共享 launch.json 配置

## 🎓 學習路徑

1. **初學者**：從基本的斷點和單步執行開始
2. **中級**：學習條件斷點和表達式評估
3. **進階**：掌握遠端偵錯和自訂適配器
4. **專家**：使用聊天式介面進行智能診斷

## 🤝 獲取幫助

- 在 REPL 中輸入 `help`
- 在聊天介面中說「幫助」
- 查看 [故障排除指南](./RUN_DEBUG_TROUBLESHOOTING.md)
- 提交 [Issue](https://github.com/MachineNativeOps/issues)
