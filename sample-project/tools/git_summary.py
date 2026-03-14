"""Tool: Git Diff Summarizer & Commit Message Generator

Summarizes git changes and generates commit messages.

Usage:
    python tools/git_summary.py              # summarize staged changes
    python tools/git_summary.py --all        # summarize all uncommitted changes
    python tools/git_summary.py --log 5      # summarize last 5 commits
"""

import subprocess
import sys
import anthropic

client = anthropic.Anthropic()


def run_git(args: list[str]) -> str:
    """Run a git command and return output."""
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    return result.stdout


def summarize_diff(diff: str) -> str:
    """Summarize a git diff and suggest a commit message."""
    if not diff.strip():
        return "No changes to summarize."

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=(
            "You are a git expert. Given a diff, provide:\n"
            "1. A brief summary of what changed (2-3 sentences)\n"
            "2. A suggested commit message (conventional commits format: type(scope): description)\n\n"
            "Be concise. Focus on the 'what' and 'why', not the 'how'."
        ),
        messages=[{"role": "user", "content": f"```diff\n{diff[:15000]}\n```"}],
    )
    return response.content[0].text


def summarize_log(count: int) -> str:
    """Summarize recent git commits."""
    log = run_git(["log", f"-{count}", "--pretty=format:%h %s", "--stat"])
    if not log.strip():
        return "No commits found."

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"Summarize these git commits in 3-5 bullet points:\n\n{log[:15000]}",
        }],
    )
    return response.content[0].text


def main():
    if "--log" in sys.argv:
        idx = sys.argv.index("--log")
        count = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 5
        print(f"Summarizing last {count} commits:\n")
        print(summarize_log(count))

    elif "--all" in sys.argv:
        diff = run_git(["diff", "HEAD"])
        print("Summarizing all uncommitted changes:\n")
        print(summarize_diff(diff))

    else:
        diff = run_git(["diff", "--cached"])
        if not diff.strip():
            print("No staged changes. Use --all for all uncommitted changes, or stage with git add.")
            return
        print("Summarizing staged changes:\n")
        print(summarize_diff(diff))


if __name__ == "__main__":
    main()
