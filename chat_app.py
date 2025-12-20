from typing import Dict, List

from guardrails_client import chat_completion, client_available, get_api_key

SYSTEM_PROMPT = (
    "You are an AI assistant who can chat with users about the project and its codebase."
)


def initial_messages() -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def chat_turn(user_input: str, messages: List[Dict[str, str]]) -> str:
    messages.append({"role": "user", "content": user_input})
    try:
        response = chat_completion(model="gpt-4o-mini", messages=messages)
    except ValueError as exc:
        print(f"[chat_app] configuration error: {exc}")
        reply = "設定錯誤：請確認 AI_INTEGRATIONS_OPENAI_API_KEY 或 OPENAI_API_KEY 是否已設置。"
        messages.append({"role": "assistant", "content": reply})
        return reply
    except Exception as exc:
        print(f"[chat_app] AI runtime error: {exc}")
        reply = "對不起，AI 目前無法回應。"
        messages.append({"role": "assistant", "content": reply})
        return reply
    else:
        reply = "對不起，我目前無法回應。"
        choices = getattr(response, "choices", [])
        if choices:
            first_choice = choices[0]
            message = getattr(first_choice, "message", None)
            content = getattr(message, "content", None)
            if content:
                reply = content
        messages.append({"role": "assistant", "content": reply})
        return reply


def run_chat() -> None:
    configured_key = get_api_key()
    if not client_available():
        if not configured_key:
            print("AI client not configured. Set AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY.")
        else:
            print("AI client dependencies missing. Please install guardrails or openai packages.")
        return

    messages = initial_messages()

    print("=== AI Assistant Chat ===")
    print("Type 'exit' or 'quit' to leave.")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        reply = chat_turn(user_input, messages)
        print(f"AI: {reply}")


if __name__ == "__main__":
    run_chat()
