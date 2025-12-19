import os
from typing import Dict, List

from openai import OpenAI

SYSTEM_PROMPT = (
    "You are an AI assistant who can chat with users about the project and its codebase."
)


def build_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
        base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
    )


def initial_messages() -> List[Dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def chat_turn(client: OpenAI, user_input: str, messages: List[Dict[str, str]]) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
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
    client = build_client()
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

        reply = chat_turn(client, user_input, messages)
        print(f"AI: {reply}")


if __name__ == "__main__":
    run_chat()
