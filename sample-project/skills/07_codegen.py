"""Skill 7: Code Generation, Explanation, and Review

Demonstrates:
- Generating code from natural language
- Explaining existing code
- Code review with actionable feedback
"""

import sys
import anthropic

client = anthropic.Anthropic()


def generate_code(description: str, language: str = "python") -> str:
    """Generate code from a natural language description."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            f"You are a senior {language} developer. Generate clean, well-structured code. "
            "Include brief inline comments. No markdown fences — output only the code."
        ),
        messages=[{"role": "user", "content": description}],
    )
    return response.content[0].text


def explain_code(code: str) -> str:
    """Explain what a piece of code does."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Explain this code clearly and concisely. What does it do, and how?\n\n```\n{code}\n```",
        }],
    )
    return response.content[0].text


def review_code(code: str) -> str:
    """Review code for bugs, style issues, and improvements."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are a thorough code reviewer. For each issue found, state: "
            "1) the problem, 2) severity (bug/style/perf), 3) suggested fix. "
            "If the code is solid, say so."
        ),
        messages=[{
            "role": "user",
            "content": f"Review this code:\n\n```\n{code}\n```",
        }],
    )
    return response.content[0].text


def main():
    # Generate
    print("=== Code Generation ===")
    desc = "A Python function that retries an async HTTP request with exponential backoff, max 3 retries, using aiohttp."
    print(f"Prompt: {desc}\n")
    code = generate_code(desc)
    print(code)

    # Explain
    print("\n=== Code Explanation ===")
    sample = """
def memoize(fn):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper
"""
    print(explain_code(sample))

    # Review
    print("\n=== Code Review ===")
    buggy = """
import sqlite3

def get_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.execute(f"SELECT * FROM users WHERE name = '{username}'")
    return cursor.fetchone()

def process_items(items):
    results = []
    for i in range(len(items)):
        if items[i] != None:
            results.append(items[i] * 2)
    return results
"""
    print(review_code(buggy))


if __name__ == "__main__":
    main()
