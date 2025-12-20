import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tools.ai_auto_fix as ai_auto_fix  # noqa: E402
import tools.ai_refactor_review as ai_refactor_review  # noqa: E402


def test_ai_auto_fix_init_warns_when_unavailable(monkeypatch, capsys):
    monkeypatch.setenv("AI_INTEGRATIONS_OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(ai_auto_fix, "client_available", lambda api_key=None: False)
    monkeypatch.setattr(ai_auto_fix, "get_api_key", lambda: None)

    generator = ai_auto_fix.AIFixGenerator()
    captured = capsys.readouterr()

    assert generator.available is False
    assert "AI client not available" in captured.out


def test_ai_refactor_review_init_warns_when_unavailable(monkeypatch, capsys):
    monkeypatch.setenv("AI_INTEGRATIONS_OPENAI_API_KEY", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setattr(ai_refactor_review, "client_available", lambda api_key=None: False)
    monkeypatch.setattr(ai_refactor_review, "get_api_key", lambda: None)

    generator = ai_refactor_review.AISuggestionGenerator()
    captured = capsys.readouterr()

    assert generator.available is False
    assert "AI suggestions not available" in captured.out
