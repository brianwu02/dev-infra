"""Skill 4: Tool Use (Function Calling)

Demonstrates:
- Defining tools with JSON schemas
- Handling tool_use responses
- Executing tools and returning results
- Multi-turn tool conversations
"""

import json
import math
import anthropic

client = anthropic.Anthropic()

# Define tools the model can call
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression. Supports +, -, *, /, **, sqrt, sin, cos, log.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate, e.g. '2 ** 10' or 'sqrt(144)'"
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"],
        },
    },
]

# Allowed math functions for safe eval
SAFE_MATH = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
    "tan": math.tan, "log": math.log, "log10": math.log10,
    "pi": math.pi, "e": math.e, "abs": abs, "round": round,
}


def execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool and return the result as a string."""
    if name == "calculator":
        try:
            result = eval(input_data["expression"], {"__builtins__": {}}, SAFE_MATH)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    elif name == "get_weather":
        # Simulated — replace with a real API call
        city = input_data["city"]
        return json.dumps({"city": city, "temp_f": 72, "condition": "Partly cloudy", "humidity": 45})

    return f"Unknown tool: {name}"


def chat_with_tools(user_message: str) -> str:
    """Send a message, handle any tool calls, and return the final response."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # If no tool use, return the text
        if response.stop_reason == "end_turn":
            return "".join(b.text for b in response.content if b.type == "text")

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  [tool] {block.name}({json.dumps(block.input)})")
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})


def main():
    queries = [
        "What is 2^16 + sqrt(625)?",
        "What's the weather in Austin and what's 98.6 Fahrenheit in Celsius? (formula: (F-32)*5/9)",
    ]
    for q in queries:
        print(f"Q: {q}")
        answer = chat_with_tools(q)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
