"""Skill 6: Multi-Strategy Summarization

Demonstrates:
- Bullet-point summaries
- TL;DR one-liners
- Progressive summarization (map-reduce for long texts)
- Custom summary formats
"""

import sys
import anthropic

client = anthropic.Anthropic()

SAMPLE_TEXT = """\
Docker containers have revolutionized software deployment by providing lightweight,
portable environments. Unlike virtual machines, containers share the host kernel,
making them faster to start and more resource-efficient. Docker uses namespaces for
process isolation and cgroups for resource limiting. Images are built in layers using
Dockerfiles, where each instruction creates a new layer. Docker Compose allows defining
multi-container applications in a single YAML file, managing networking and volumes
between services. The Docker socket (/var/run/docker.sock) provides the API endpoint
for controlling the Docker daemon. Docker-outside-of-Docker (DooD) is a pattern where
a container mounts the host's Docker socket to manage sibling containers rather than
running a Docker daemon inside the container. This avoids the complexity and security
issues of Docker-in-Docker (DinD) while still allowing containerized CI/CD agents and
dev environments to build and manage containers. Named volumes persist data across
container restarts, while bind mounts map host directories directly. Health checks in
compose files let orchestrators monitor container readiness. Watchtower can monitor
running containers and notify when new images are available. For monitoring, Netdata
provides real-time metrics, Dozzle shows container logs, and Uptime Kuma tracks service
availability.
"""


def summarize(text: str, strategy: str = "bullets") -> str:
    """Summarize text using the specified strategy."""
    prompts = {
        "bullets": "Summarize the following text as 3-5 concise bullet points:\n\n{text}",
        "tldr": "Give a single-sentence TL;DR of the following text:\n\n{text}",
        "eli5": "Explain the following text like I'm 5 years old, in 2-3 simple sentences:\n\n{text}",
        "technical": "Summarize the following for a senior engineer — focus on architecture decisions and trade-offs:\n\n{text}",
    }
    prompt = prompts.get(strategy, prompts["bullets"]).format(text=text)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def progressive_summarize(text: str, chunk_size: int = 2000) -> str:
    """Map-reduce summarization for long texts: summarize chunks, then summarize summaries."""
    # Map: summarize each chunk
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    if len(chunks) <= 1:
        return summarize(text, "bullets")

    print(f"  [progressive] Summarizing {len(chunks)} chunks...")
    summaries = [summarize(chunk, "bullets") for chunk in chunks]

    # Reduce: summarize the summaries
    combined = "\n\n".join(f"Chunk {i+1}:\n{s}" for i, s in enumerate(summaries))
    return summarize(combined, "bullets")


def main():
    text = sys.stdin.read() if not sys.stdin.isatty() else SAMPLE_TEXT

    for strategy in ["tldr", "bullets", "eli5", "technical"]:
        print(f"\n{'=' * 40}")
        print(f"Strategy: {strategy}")
        print('=' * 40)
        print(summarize(text, strategy))


if __name__ == "__main__":
    main()
