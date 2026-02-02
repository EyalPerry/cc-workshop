# Claude Code Workshop: Automating Development with Claude Code

A hands-on workshop that teaches you how to automate software development using [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Anthropic's CLI tool for AI-assisted engineering.

## What You'll Build

**TaskFlow Scheduler** — a job scheduling API with dependency resolution, retry policies, and priority-based execution. Built with FastAPI, asyncpg, Pydantic v2, and Alembic.

You won't write this by hand. You'll direct Claude Code to build it for you, learning how to structure prompts, rules, and project configuration so that an AI agent produces production-quality code.

## What You'll Learn

- **Project rules (`.claude/rules/`)** — How to encode coding standards, testing conventions, and architectural decisions so Claude Code follows them automatically
- **Skills & workflows (`.claude/skills/`)** — Custom slash commands for repeatable tasks like committing, linting, and aligning code
- **Specs-driven development (`specs/`)** — Writing PRDs and SRS documents that Claude Code reads before generating implementation plans
- **Paced implementation** — Breaking work into small, testable phases and iterating with Claude Code step by step
- **Settings & permissions (`.claude/settings.json`)** — Configuring which scripts Claude Code can run without prompting

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for integration/E2E tests with testcontainers)
- A Claude Code installation with an active API key

## Getting Started

```bash
# Clone the repository
git clone <repo-url> && cd workshop

# Install dependencies
./scripts/setup

# Run tests
./scripts/test.py

# Run linting
./scripts/lint.py
```

## Project Structure

```
├── .claude/
│   ├── rules/          # Coding standards & conventions Claude Code follows
│   │   ├── system.md   # Global workflow rules (planning, pacing, context7)
│   │   ├── project.md  # Project scripts, tech stack, test mapping
│   │   └── eng/        # Language-specific dev & test guidelines
│   ├── skills/         # Custom slash commands (align, flow)
│   ├── agents/         # Agent configurations (doc)
│   └── settings.json   # Permissions for script execution
├── specs/
│   ├── PRD.md          # Product requirements
│   └── SRS.md          # Technical specification
├── src/                # Application source code
├── test/               # Test suites (unit, integration, e2e)
├── scripts/            # Build, test, lint, and setup scripts
├── Dockerfile          # Container build
├── pyproject.toml      # Python project config
└── alembic.ini         # Database migration config
```

## Workshop Flow

1. **Read the specs** — Start with `specs/PRD.md` and `specs/SRS.md` to understand what TaskFlow does
2. **Explore the rules** — Read `.claude/rules/` to see how coding standards are encoded
3. **Ask Claude Code to plan** — It will produce a phased `PLAN.md` with testable steps
4. **Implement phase by phase** — Claude Code builds each phase, runs tests, and waits for your approval before continuing
5. **Commit with `/flow`** — Use the custom skill to checkpoint and commit progress

## Key Concepts

### Rules as Code

The `.claude/rules/` directory contains markdown files that act as persistent instructions. Claude Code reads these on every interaction, ensuring consistent adherence to:

- Function size limits, naming conventions, and type safety requirements
- Test anatomy (AAA pattern, BDD naming, comprehensive assertions)
- Import conventions and module structure
- Dependency management policies

### Specs-Driven Development

Instead of describing features in chat, you write formal specifications in `specs/`. Claude Code reads these before planning, producing implementations that match the documented requirements rather than ad-hoc interpretations.

### Paced Implementation

Work is broken into phases where each phase is self-contained, testable, and under 100 lines of changes. This prevents large, unreviewed code dumps and keeps you in control of the development process.
