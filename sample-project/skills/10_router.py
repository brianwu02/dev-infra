"""Skill 10: Multi-Model Router

Demonstrates:
- Routing prompts to different model tiers based on complexity
- Using Haiku for fast/cheap tasks, Sonnet for balanced, Opus for complex
- Automatic complexity classification
- Cost-aware model selection
"""

import anthropic

client = anthropic.Anthropic()

MODELS = {
    "simple": "claude-haiku-4-5-20251001",
    "moderate": "claude-sonnet-4-6",
    "complex": "claude-opus-4-6",
}

CLASSIFIER_PROMPT = """\
Classify the complexity of the following user request as exactly one of: simple, moderate, complex.

Rules:
- simple: factual lookups, format conversions, basic questions, one-step tasks
- moderate: explanations, summaries, multi-step reasoning, code generation
- complex: architecture design, nuanced analysis, long-form writing, multi-constraint optimization

Respond with ONLY the word: simple, moderate, or complex.

Request: {prompt}
"""


def classify_complexity(prompt: str) -> str:
    """Use Haiku to quickly classify prompt complexity."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": CLASSIFIER_PROMPT.format(prompt=prompt)}],
    )
    label = response.content[0].text.strip().lower()
    return label if label in MODELS else "moderate"


def route_and_respond(prompt: str) -> tuple[str, str, str]:
    """Classify, route to the right model, and get the response."""
    complexity = classify_complexity(prompt)
    model = MODELS[complexity]

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return complexity, model, response.content[0].text


def main():
    prompts = [
        "What's 42 in hexadecimal?",
        "Explain the difference between Docker volumes and bind mounts with examples.",
        "Design a fault-tolerant event processing pipeline that handles at-least-once delivery, "
        "deduplication, dead-letter queues, and backpressure. Consider trade-offs between latency, "
        "throughput, and consistency. Provide the architecture for both a small team and a large-scale deployment.",
    ]

    for prompt in prompts:
        print(f"Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        complexity, model, response = route_and_respond(prompt)
        print(f"  Complexity: {complexity} → Model: {model}")
        print(f"  Response: {response[:150]}...\n")


if __name__ == "__main__":
    main()
