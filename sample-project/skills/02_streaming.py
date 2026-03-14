"""Skill 2: Streaming Responses

Demonstrates:
- Token-by-token streaming for real-time UX
- Handling stream events (text deltas, stop reason, usage)
"""

import sys
import anthropic

client = anthropic.Anthropic()


def stream_response(prompt: str):
    """Stream a response token by token."""
    print("Claude: ", end="", flush=True)

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("\n")


def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Explain Docker-outside-of-Docker in 3 sentences."

    stream_response(prompt)


if __name__ == "__main__":
    main()
