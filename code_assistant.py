import os
import json
import subprocess

from guardrails_client import chat_completion, client_available

WORKSPACE = "/home/runner/workspace"

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list (relative to workspace)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The file path to read (relative to workspace)"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a pattern in files using grep",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The search pattern"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (default: current directory)"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show the current git status",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Show recent git commits",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of commits to show (default: 5)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The file path to write (relative to workspace)"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a safe shell command (limited to: ls, cat, head, tail, wc, find, tree)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def list_files(path: str) -> str:
    full_path = os.path.join(WORKSPACE, path.lstrip("/"))
    try:
        items = os.listdir(full_path)
        result = []
        for item in sorted(items):
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                result.append(f"[DIR]  {item}/")
            else:
                result.append(f"[FILE] {item}")
        return "\n".join(result) if result else "Empty directory"
    except Exception as e:
        return f"Error: {e}"

def read_file(file_path: str) -> str:
    full_path = os.path.join(WORKSPACE, file_path.lstrip("/"))
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 5000:
                return content[:5000] + "\n\n... (truncated, file too large)"
            return content
    except Exception as e:
        return f"Error: {e}"

def search_code(pattern: str, path: str = ".") -> str:
    full_path = os.path.join(WORKSPACE, path.lstrip("/"))
    try:
        result = subprocess.run(
            ["grep", "-rn", "--include=*.py", "--include=*.js", "--include=*.ts", 
             "--include=*.yaml", "--include=*.yml", "--include=*.json", pattern, full_path],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout[:3000] if result.stdout else "No matches found"
        return output
    except Exception as e:
        return f"Error: {e}"

def git_status() -> str:
    try:
        result = subprocess.run(
            ["git", "status"], capture_output=True, text=True, cwd=WORKSPACE, timeout=10
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

def git_log(count: int = 5) -> str:
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline"], 
            capture_output=True, text=True, cwd=WORKSPACE, timeout=10
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

def write_file(file_path: str, content: str) -> str:
    full_path = os.path.join(WORKSPACE, file_path.lstrip("/"))
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error: {e}"

def run_command(command: str) -> str:
    safe_commands = ['ls', 'cat', 'head', 'tail', 'wc', 'find', 'tree', 'pwd', 'echo']
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        allowed = ', '.join(safe_commands)
        return f"Command not allowed. Only these are permitted: {allowed}"
    try:
        result = subprocess.run(
            cmd_parts, shell=False, capture_output=True, text=True, 
            cwd=WORKSPACE, timeout=10
        )
        output = result.stdout or result.stderr
        return output[:3000] if output else "Command executed (no output)"
    except Exception as e:
        return f"Error: {e}"

def execute_tool(name: str, args: dict) -> str:
    if name == "list_files":
        return list_files(args.get("path", "."))
    elif name == "read_file":
        return read_file(args["file_path"])
    elif name == "search_code":
        return search_code(args["pattern"], args.get("path", "."))
    elif name == "git_status":
        return git_status()
    elif name == "git_log":
        return git_log(args.get("count", 5))
    elif name == "write_file":
        return write_file(args["file_path"], args["content"])
    elif name == "run_command":
        return run_command(args["command"])
    return "Unknown tool"

def chat():
    print("=" * 60)
    print("加購分析師 - AI 高階程式碼顧問")
    print("我可以分析您的專案、提供優化建議、管理儲存庫")
    print("輸入 'quit' 或 'exit' 結束對話")
    print("=" * 60)
    if not client_available():
        print("⚠️  OpenAI/Guardrails client not configured. Please set AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY.")
        return
    
    messages = [
        {"role": "system", "content": """你是「加購分析師」- 一位高階程式碼顧問和專案分析師。

## 你的專業角色：
你是一位資深的軟體架構師和技術顧問，專門幫助開發者：
1. **專案分析** - 深入分析程式碼結構、架構和品質
2. **優化建議** - 提供效能優化、程式碼重構建議
3. **技術評估** - 評估技術債務、安全風險、可維護性
4. **功能擴展** - 建議可以加入的新功能和改進
5. **最佳實踐** - 分享業界最佳實踐和設計模式

## 你的工具能力：
- List files and directories
- Read file contents
- Search for code patterns
- Check git status and history
- Write/create files
- Run safe shell commands

Always respond in the same language the user uses (Chinese or English).
When using tools, explain what you're doing and summarize the results clearly."""}
    ]
    
    while True:
        user_input = input("\n您: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '結束', '退出']:
            print("\n再見！感謝使用加購分析師。")
            break
        
        if not user_input:
            continue
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = chat_completion(model="gpt-4o-mini", messages=messages, tools=tools)
            
            assistant_message = response.choices[0].message
            
            while assistant_message.tool_calls:
                messages.append(assistant_message)
                
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"\n[執行: {tool_name}]")
                    
                    result = execute_tool(tool_name, tool_args)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                
                response = chat_completion(model="gpt-4o-mini", messages=messages, tools=tools)
                assistant_message = response.choices[0].message
            
            final_content = assistant_message.content
            messages.append({"role": "assistant", "content": final_content})
            print(f"\nAI: {final_content}")
            
        except Exception as e:
            print(f"\n發生錯誤: {e}")

if __name__ == "__main__":
    chat()
