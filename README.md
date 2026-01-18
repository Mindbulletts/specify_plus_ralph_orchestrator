# Specify + Ralph Orchestrator

A Claude Code plugin that bridges the `/start:specify` specification workflow with [Ralph Claude Code](https://github.com/frankbria/ralph-claude-code) autonomous orchestration.

## Problem

Developers using Claude Code face two disconnected workflows:

1. **Specification Creation**: Using `/start:specify` to create structured PRD, SDD, and PLAN documents
2. **Autonomous Execution**: Using Ralph to run iterative Claude Code sessions

Ralph expects specific file formats (`PROMPT.md`, `@fix_plan.md`, `@AGENT.md`, `specs/`) that don't match the specification output (`product-requirements.md`, `solution-design.md`, `implementation-plan.md`). This forces manual translation, loses traceability, and risks specification drift.

## Solution

The `export-to-ralph` skill automatically transforms completed specifications into Ralph's format:

| Specification Input | Ralph Output |
|---------------------|--------------|
| product-requirements.md | PROMPT.md, specs/features/ |
| solution-design.md | @AGENT.md |
| implementation-plan.md | @fix_plan.md |

## Quick Start

### 1. Create a specification

```bash
/start:specify "Add user authentication with OAuth"
```

Follow the guided workflow through PRD → SDD → PLAN phases.

### 2. Export to Ralph format

```bash
python skills/export-to-ralph/export.py 002
```

Or with options:
```bash
python skills/export-to-ralph/export.py 002 --dry-run    # Preview without writing
python skills/export-to-ralph/export.py 002 --force      # Overwrite existing files
python skills/export-to-ralph/export.py 002 --output-dir ./build
```

### 3. Run Ralph

```bash
ralph start
```

## Features

- **Automatic EARS-to-Gherkin conversion**: Acceptance criteria become test scenarios
- **Priority mapping**: PLAN phases → High/Medium/Low priority tasks
- **Traceability preservation**: PRD references maintained in task list
- **Partial export support**: Missing documents produce warnings, not failures
- **Cross-platform**: Works on Windows, macOS, and Linux

## Project Structure

```
skills/
├── export-to-ralph/           # Export skill
│   ├── SKILL.md               # Skill definition
│   ├── export.py              # Python export script
│   ├── reference.md           # Transformation rules & ADRs
│   └── templates/             # Output file templates
├── specification-management/  # Spec directory management
├── requirements-analysis/     # PRD creation
├── architecture-design/       # SDD creation
└── implementation-planning/   # PLAN creation

commands/
└── specify.md                 # /start:specify command

docs/specs/                    # Specification storage (auto-numbered)
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Transformation engine | Python script | Deterministic output; no AI calls needed |
| Output location | Project root | Direct Ralph consumption |
| Missing documents | Warn, don't block | Enables iterative workflow |
| Criteria format | Regex-based | Reproducible; fast execution |

## Requirements

- Python 3.x (standard library only)
- Claude Code CLI
- Ralph Claude Code (for autonomous execution)

## Documentation

- [Transformation Rules](skills/export-to-ralph/reference.md) - Detailed field mappings and conversion logic
- [Skill Usage](skills/export-to-ralph/SKILL.md) - When and how to use the export skill

## License

MIT
