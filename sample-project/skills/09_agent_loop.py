"""Skill 9: Agentic Tool-Calling Loop

Demonstrates:
- Autonomous agent that plans and executes multi-step tasks
- Tool loop: model calls tools → we execute → feed results back → repeat
- File system tools (read, list, search)
- Self-terminating agent (decides when it's done)
"""

import json
import os
import subprocess
import anthropic

client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "list_files",
        "description": "List files in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current directory)"}
            },
            "required": [],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return output. Only for safe, read-only commands.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"],
        },
    },
    {
        "name": "done",
        "description": "Signal that the task is complete. Call this when you have the final answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "Final answer or summary"}
            },
            "required": ["result"],
        },
    },
]

# Commands allowed for safety
SAFE_PREFIXES = ("ls", "cat", "head", "tail", "wc", "grep", "find", "du", "df", "date", "whoami", "uname", "docker ps", "git log", "git status", "git diff")


def execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool call."""
    if name == "list_files":
        path = input_data.get("path", ".")
        try:
            entries = os.listdir(path)
            return "\n".join(sorted(entries))
        except Exception as e:
            return f"Error: {e}"

    elif name == "read_file":
        try:
            with open(input_data["path"]) as f:
                content = f.read(10000)  # Cap at 10k chars
            return content
        except Exception as e:
            return f"Error: {e}"

    elif name == "run_command":
        cmd = input_data["command"]
        if not any(cmd.strip().startswith(p) for p in SAFE_PREFIXES):
            return f"Blocked: only safe read-only commands allowed. Got: {cmd}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Error: command timed out"

    elif name == "done":
        return input_data["result"]

    return f"Unknown tool: {name}"


def run_agent(task: str, max_turns: int = 10) -> str:
    """Run an agentic loop until the model calls 'done' or max turns reached."""
    messages = [{"role": "user", "content": task}]
    system = (
        "You are an autonomous agent. You have tools to explore the file system and run commands. "
        "Plan your approach, use tools step by step, and call 'done' with your final answer when finished. "
        "Be efficient — don't read files you don't need."
    )

    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        # Print any text the model outputs
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"  [think] {block.text[:200]}")

        # Check for tool calls
        if response.stop_reason == "end_turn":
            text_parts = [b.text for b in response.content if b.type == "text"]
            return " ".join(text_parts) if text_parts else "(no response)"

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}({json.dumps(block.input)[:100]})")
                result = execute_tool(block.name, block.input)
                if block.name == "done":
                    return result
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result[:5000],
                })
        messages.append({"role": "user", "content": tool_results})

    return "(max turns reached)"


def main():
    task = "Explore the current directory. Find all Python files, count them, and summarize what this project does based on the file structure and any README."
    print(f"Task: {task}\n")
    result = run_agent(task)
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
