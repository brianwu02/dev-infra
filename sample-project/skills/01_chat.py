"""Skill 1: Basic Chat with Message History

Demonstrates:
- Creating a client and sending messages
- Maintaining conversation history
- System prompts
- Interactive REPL loop
"""

import anthropic

client = anthropic.Anthropic()

SYSTEM = "You are a helpful assistant. Be concise."


def chat(messages: list[dict]) -> str:
    """Send messages and return the assistant's reply."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM,
        messages=messages,
    )
    return response.content[0].text


def main():
    print("Chat with Claude (type 'quit' to exit)\n")
    messages = []

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        messages.append({"role": "user", "content": user_input})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"Claude: {reply}\n")


if __name__ == "__main__":
    main()
