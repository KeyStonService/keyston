import os
import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("AI_INTEGRATIONS_OPENAI_API_KEY", "test-key")

import chat_app  # noqa: E402
import code_assistant  # noqa: E402


def test_code_assistant_read_write_and_list(monkeypatch, tmp_path):
    monkeypatch.setattr(code_assistant, "WORKSPACE", str(tmp_path))

    write_result = code_assistant.execute_tool(
        "write_file", {"file_path": "notes.txt", "content": "hello ai"}
    )
    assert "Successfully wrote" in write_result

    read_result = code_assistant.execute_tool(
        "read_file", {"file_path": "notes.txt"}
    )
    assert "hello ai" in read_result

    listing = code_assistant.execute_tool("list_files", {"path": "."})
    assert "[FILE] notes.txt" in listing


def test_code_assistant_run_command_safety(monkeypatch, tmp_path):
    monkeypatch.setattr(code_assistant, "WORKSPACE", str(tmp_path))
    (tmp_path / "example.txt").write_text("content")

    allowed_output = code_assistant.execute_tool("run_command", {"command": "ls"})
    assert "example.txt" in allowed_output

    blocked_output = code_assistant.execute_tool(
        "run_command", {"command": "rm -rf /"}
    )
    assert "Command not allowed" in blocked_output


def test_chat_app_chat_turn_uses_stubbed_completion(monkeypatch):
    stub_response = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content="hello back", tool_calls=None))
        ]
    )

    def _fake_completion(**kwargs):
        return stub_response

    monkeypatch.setattr(chat_app, "chat_completion", _fake_completion)

    messages = chat_app.initial_messages()
    reply = chat_app.chat_turn("hello", messages)

    assert reply == "hello back"
    assert messages[-2]["content"] == "hello"
    assert messages[-1]["content"] == "hello back"


def test_chat_app_run_chat_missing_client(monkeypatch, capsys):
    monkeypatch.setattr(chat_app, "client_available", lambda: False)
    chat_app.run_chat()
    captured = capsys.readouterr()
    assert "AI client not configured" in captured.out
