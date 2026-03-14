"""Tool: File Q&A

Point it at any file and ask questions about it.

Usage:
    python tools/file_qa.py /path/to/file.py "What does the main function do?"
    python tools/file_qa.py docker-compose.yml "What ports are exposed?"
"""

import sys
import anthropic

client = anthropic.Anthropic()


def ask_about_file(file_path: str, question: str) -> str:
    """Read a file and answer a question about its contents."""
    with open(file_path) as f:
        content = f.read(50000)  # Cap at 50k chars

    # Detect file type for context
    ext = file_path.rsplit(".", 1)[-1] if "." in file_path else "txt"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="Answer questions about the provided file. Be concise and specific.",
        messages=[{
            "role": "user",
            "content": (
                f"File: {file_path} (type: .{ext})\n"
                f"Contents:\n```\n{content}\n```\n\n"
                f"Question: {question}"
            ),
        }],
    )
    return response.content[0].text


def main():
    if len(sys.argv) < 3:
        print("Usage: python file_qa.py <file_path> <question>")
        print("Example: python file_qa.py Makefile 'What targets are available?'")
        sys.exit(1)

    file_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    print(f"File: {file_path}")
    print(f"Question: {question}\n")
    print(ask_about_file(file_path, question))


if __name__ == "__main__":
    main()
