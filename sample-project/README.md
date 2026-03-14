# AI Skills Sample Project

A template full-stack project demonstrating two things:
1. **AI API patterns** — standalone Python scripts covering 10 common LLM integration skills
2. **AI CLI configurations** — `.claude/` and `.gemini/` skill directories that teach Claude Code and Gemini CLI how to work with your codebase

## Setup

```bash
cd /workspace/.dev-infra/sample-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Skills

| # | Skill | File | Description |
|---|-------|------|-------------|
| 1 | **Chat** | `skills/01_chat.py` | Basic conversation with message history |
| 2 | **Streaming** | `skills/02_streaming.py` | Real-time token streaming |
| 3 | **Structured Output** | `skills/03_structured_output.py` | Extract typed data from unstructured text |
| 4 | **Tool Use** | `skills/04_tool_use.py` | Give the model functions to call (weather, calculator, DB query) |
| 5 | **RAG** | `skills/05_rag.py` | Retrieval-augmented generation with local documents |
| 6 | **Summarization** | `skills/06_summarize.py` | Multi-strategy summarization (bullets, TL;DR, progressive) |
| 7 | **Code Generation** | `skills/07_codegen.py` | Generate, explain, and review code |
| 8 | **Image Analysis** | `skills/08_vision.py` | Analyze images with multimodal input |
| 9 | **Agentic Loop** | `skills/09_agent_loop.py` | Autonomous tool-calling agent with a task loop |
| 10 | **Multi-Model Router** | `skills/10_router.py` | Route prompts to the right model tier by complexity |

## Tools

| File | Description |
|------|-------------|
| `tools/db_assistant.py` | Natural-language SQL against TimescaleDB |
| `tools/file_qa.py` | Ask questions about local files |
| `tools/git_summary.py` | Summarize git diffs and generate commit messages |

## Running

```bash
# Run any skill
python skills/01_chat.py

# Run a tool
python tools/git_summary.py
```

## AI CLI Configurations

This project includes pre-configured skill directories for both Claude Code and Gemini CLI.

### `.claude/` — Claude Code Skills

```
.claude/
├── settings.json                          # Permission allowlist (read-only commands)
└── skills/
    ├── coding-standards/SKILL.md          # Naming, imports, type safety rules
    ├── verification-loop/SKILL.md         # Post-change quality gate (/verification-loop)
    ├── tdd-workflow/SKILL.md              # Test-driven development process
    ├── add-endpoint/SKILL.md              # Full-stack endpoint checklist (/add-endpoint)
    ├── add-component/SKILL.md             # React component scaffold (/add-component)
    ├── add-migration/SKILL.md             # DB migration creation (/add-migration)
    ├── db-schema/SKILL.md                 # Database schema reference
    ├── project-structure/SKILL.md         # File tree and conventions
    ├── deploy/SKILL.md                    # Deployment guide (/deploy)
    └── docker-patterns/SKILL.md           # DooD, compose, container patterns
```

Skills marked with `/command` are user-invokable — type the command in Claude Code to trigger them.

### `.gemini/` — Gemini CLI Skills

Same skill set, same format. Gemini CLI reads `GEMINI.md` for project context and `.gemini/skills/` for invokable skills.

### `CLAUDE.md` / `GEMINI.md` — Project Context

These are the root-level files that each AI CLI loads automatically. They contain:
- What the project is
- Tech stack and architecture
- Key commands (start, test, deploy)
- Non-negotiable conventions
- References to skills that auto-activate

### How to Customize

1. **Edit `CLAUDE.md`/`GEMINI.md`** with your actual project details
2. **Add domain-specific skills** — copy a skill directory and modify
3. **Update `settings.json`** — add commands you want auto-approved
4. **Skill frontmatter** — set `user-invokable: true` and `argument-hint` for slash commands
