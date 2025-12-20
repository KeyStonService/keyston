#!/usr/bin/env python3

"""
Semantic Commit Message Generator
----------------------------------
使用 AI 生成符合 Conventional Commits 規範的 commit message

支援的 commit 類型：
- fix: 修復 bug
- feat: 新功能
- refactor: 重構代碼
- docs: 文檔更新
- style: 代碼格式調整
- test: 測試相關
- chore: 構建/工具相關
- perf: 性能優化
- ci: CI/CD 相關

使用：
    python tools/semantic-commit-generator.py \
        --files "services/api/legacy.php" \
        --action "removed" \
        --reason "PHP forbidden in services directory" \
        --violation-type "language-governance"
"""

import argparse
import os

from guardrails_client import chat_completion, get_api_key, is_client_available
from rich import print
from rich.console import Console

console = Console()


def generate_semantic_commit_ai(
    files: list[str],
    action: str,
    reason: str,
    violation_type: str,
    api_key: str = None
) -> str:
    """使用 AI 生成 semantic commit message"""
    
    if not api_key:
        api_key = get_api_key()
    
    if not is_client_available(api_key):
        console.print("[yellow]Warning: No OpenAI/Guardrails client, using rule-based generation[/yellow]")
        return generate_semantic_commit_rules(files, action, reason, violation_type)
    
    # 準備 prompt
    prompt = f"""Generate a semantic commit message following Conventional Commits specification.

Files changed: {', '.join(files)}
Action taken: {action}
Reason: {reason}
Violation type: {violation_type}

The commit message should:
1. Start with a type (fix, feat, refactor, docs, style, test, chore, perf, ci)
2. Optionally include a scope in parentheses
3. Have a brief description (max 50 chars)
4. Optionally include a body with more details
5. Optionally include a footer with breaking changes or issue references

Format:
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Generate the commit message:"""
    
    try:
        response = chat_completion(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at writing semantic commit messages following Conventional Commits specification. Generate concise, clear commit messages."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.7,
            api_key=api_key,
        )
        
        commit_msg = response.choices[0].message.content.strip()
        return commit_msg
        
    except Exception as e:
        console.print(f"[yellow]AI generation failed: {e}. Using rule-based generation[/yellow]")
        return generate_semantic_commit_rules(files, action, reason, violation_type)


def generate_semantic_commit_rules(
    files: list[str],
    action: str,
    reason: str,
    violation_type: str
) -> str:
    """使用規則生成 semantic commit message"""
    
    # 決定 commit type
    commit_type = "fix"
    scope = "governance"
    
    if "security" in violation_type.lower() or "vulnerability" in violation_type.lower():
        commit_type = "fix"
        scope = "security"
    elif "language" in violation_type.lower() or "governance" in violation_type.lower():
        commit_type = "refactor"
        scope = "language"
    elif "architecture" in violation_type.lower():
        commit_type = "refactor"
        scope = "architecture"
    elif "documentation" in violation_type.lower() or "docs" in violation_type.lower():
        commit_type = "docs"
        scope = None
    
    # 決定 action 描述
    action_map = {
        "removed": "remove",
        "moved": "move",
        "migrated": "migrate",
        "refactored": "refactor",
        "fixed": "fix",
        "updated": "update"
    }
    
    action_verb = action_map.get(action.lower(), action.lower())
    
    # 生成描述
    if len(files) == 1:
        file_desc = os.path.basename(files[0])
    elif len(files) <= 3:
        file_desc = f"{len(files)} files"
    else:
        file_desc = f"{len(files)} files"
    
    # 構建 commit message
    if scope:
        description = f"{commit_type}({scope}): {action_verb} {file_desc}"
    else:
        description = f"{commit_type}: {action_verb} {file_desc}"
    
    # 限制描述長度為 50 字符
    if len(description) > 50:
        if len(files) > 1:
            description = f"{commit_type}({scope}): {action_verb} {len(files)} files" if scope else f"{commit_type}: {action_verb} {len(files)} files"
        else:
            description = description[:47] + "..."
    
    # 添加 body
    body = f"\n{reason}\n"
    
    # 添加文件列表（如果超過 3 個只列前幾個）
    if len(files) > 1:
        body += "\nFiles affected:\n"
        for f in files[:5]:
            body += f"- {f}\n"
        if len(files) > 5:
            body += f"- ... and {len(files) - 5} more files\n"
    
    # 添加 footer
    footer = f"\nType: {violation_type}\nAction: {action}\n"
    
    commit_msg = description + "\n" + body + footer
    
    return commit_msg


def validate_commit_message(commit_msg: str) -> bool:
    """驗證 commit message 格式"""
    
    lines = commit_msg.split("\n")
    if not lines:
        return False
    
    # 檢查第一行格式
    first_line = lines[0]
    
    # 檢查是否包含類型
    valid_types = ["fix", "feat", "refactor", "docs", "style", "test", "chore", "perf", "ci", "build", "revert"]
    
    has_valid_type = any(first_line.startswith(t) for t in valid_types)
    
    if not has_valid_type:
        return False
    
    # 檢查是否有冒號
    if ":" not in first_line:
        return False
    
    # 檢查長度（建議不超過 50 字符）
    if len(first_line) > 72:  # 允許一些彈性
        console.print("[yellow]Warning: First line exceeds recommended length[/yellow]")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate semantic commit message")
    parser.add_argument("--files", nargs="+", required=True, help="List of files changed")
    parser.add_argument("--action", required=True, help="Action taken (e.g., 'removed', 'moved', 'refactored')")
    parser.add_argument("--reason", required=True, help="Reason for the change")
    parser.add_argument("--violation-type", required=True, help="Type of violation (e.g., 'language-governance', 'security')")
    parser.add_argument("--use-ai", action="store_true", help="Use AI to generate commit message")
    parser.add_argument("--api-key", help="OpenAI API key (or use OPENAI_API_KEY env var)")
    parser.add_argument("--output", help="Output file for commit message")
    
    args = parser.parse_args()
    
    console.print("[cyan]🤖 Generating semantic commit message...[/cyan]")
    
    # 生成 commit message
    if args.use_ai:
        commit_msg = generate_semantic_commit_ai(
            args.files,
            args.action,
            args.reason,
            args.violation_type,
            args.api_key
        )
    else:
        commit_msg = generate_semantic_commit_rules(
            args.files,
            args.action,
            args.reason,
            args.violation_type
        )
    
    # 驗證
    if validate_commit_message(commit_msg):
        console.print("[green]✓ Valid semantic commit message generated[/green]")
    else:
        console.print("[yellow]⚠ Commit message may not follow Conventional Commits format[/yellow]")
    
    # 顯示結果
    console.print("\n[bold]Generated Commit Message:[/bold]")
    console.print("─" * 60)
    print(commit_msg)
    console.print("─" * 60)
    
    # 儲存到檔案
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(commit_msg)
        console.print(f"\n[green]✓ Commit message saved to {args.output}[/green]")
    
    console.print("\n[green]✅ Commit message generation complete![/green]")
    
    return commit_msg


if __name__ == "__main__":
    main()
