# Specify + Ralph Orchestrator

A Claude Code skill that bridges the `/start:specify` specification workflow ([the-startup](https://github.com/rsmdt/the-startup) plugin) with [Ralph Claude Code](https://github.com/frankbria/ralph-claude-code) autonomous orchestration.

## Problem

Developers using Claude Code face two disconnected workflows:

1. **Specification Creation**: Using `/start:specify` to create structured PRD, SDD, and PLAN documents
2. **Autonomous Execution**: Using Ralph to run iterative Claude Code sessions

Ralph expects specific file formats (`PROMPT.md`, `@fix_plan.md`, `@AGENT.md`, `specs/`) that don't match the specification output (`product-requirements.md`, `solution-design.md`, `implementation-plan.md`). This forces manual translation, loses traceability, and risks specification drift.

## Solution

The `export-to-ralph` skill automatically transforms completed specifications into Ralph's format:

| Specification Input | Ralph Output |
|---------------------|--------------|
| product-requirements.md | PROMPT.md, specs/features/, specs/requirements.md |
| solution-design.md | @AGENT.md |
| implementation-plan.md | @fix_plan.md |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code                          │
│  ┌─────────────────┐    ┌─────────────────────────┐    │
│  │ /start:specify  │───▶│ /start:export-to-ralph  │    │
│  │ (the-startup)   │    │ (this skill)            │    │
│  └─────────────────┘    └───────────┬─────────────┘    │
│         │                           │                   │
│         ▼                           ▼                   │
│   docs/specs/NNN-*/           ralph-export NNN          │
│   ├── product-requirements.md       │                   │
│   ├── solution-design.md            ▼                   │
│   └── implementation-plan.md  PROMPT.md                 │
│                               @fix_plan.md              │
│                               @AGENT.md                 │
│                               specs/                    │
└─────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │  ralph start    │
                            │  (CLI tool)     │
                            └─────────────────┘
```

## Prerequisites

Before installing this skill, ensure you have:

1. **Claude Code CLI** - Installed and configured
2. **the-startup plugin** - Provides `/start:specify` command
   ```bash
   # In Claude Code, use /plugin to install from the-startup marketplace
   /plugin
   ```
3. **Ralph Claude Code** - Installed globally
   ```bash
   git clone https://github.com/frankbria/ralph-claude-code.git
   cd ralph-claude-code
   ./install.sh
   ```

## Installation

### Option A: Add to the-startup Plugin (Recommended)

Copy the `export-to-ralph` skill into your existing the-startup plugin installation:

```bash
# Find your the-startup plugin location
# Typically: ~/.claude/plugins/cache/the-startup/start/<version>/

# Copy the skill
cp -r skills/export-to-ralph ~/.claude/plugins/cache/the-startup/start/2.13.0/skills/
```

This makes `/start:export-to-ralph` available as a Claude Code skill alongside other `start:*` commands.

### Option B: Shell Alias (For CLI Usage)

Add an alias to your shell configuration for direct command-line access:

**Bash/Zsh** (`~/.bashrc` or `~/.zshrc`):
```bash
# Ralph Export Alias
alias ralph-export='python ~/.claude/plugins/cache/the-startup/start/2.13.0/skills/export-to-ralph/export.py'
```

**PowerShell** (`$PROFILE`):
```powershell
# Ralph Export Alias
function ralph-export { python "$env:USERPROFILE\.claude\plugins\cache\the-startup\start\2.13.0\skills\export-to-ralph\export.py" $args }
```

After adding, reload your shell:
```bash
source ~/.bashrc  # or restart terminal
```

### Option C: Both (Recommended for Full Integration)

Install both Option A and Option B for maximum flexibility:
- Use `/start:export-to-ralph` within Claude Code sessions
- Use `ralph-export` from the command line

## Quick Start

### 1. Create a Specification

```bash
# In Claude Code
/start:specify "Add user authentication with OAuth"
```

Follow the guided workflow through PRD → SDD → PLAN phases.

### 2. Export to Ralph Format

**Via Claude Code skill:**
```
/start:export-to-ralph
```

**Via command line:**
```bash
ralph-export 001                    # Export spec 001
ralph-export 001 --dry-run          # Preview without writing
ralph-export 001 --force            # Overwrite existing files
ralph-export 001 --output-dir ./    # Custom output directory
```

### 3. Run Ralph

```bash
ralph start
```

## Features

- **Automatic EARS-to-Gherkin conversion**: Acceptance criteria become test scenarios
- **Priority mapping**: PLAN phases → High/Medium/Low priority tasks
- **Traceability preservation**: PRD references maintained in task list (`[ref: PRD/AC-X.Y]`)
- **Consolidated requirements.md**: Single file for fast Ralph context loading
- **Partial export support**: Missing documents produce warnings, not failures
- **Cross-platform**: Works on Windows, macOS, and Linux

## Generated Output

### @fix_plan.md Structure

```markdown
## High Priority
- [ ] T1.1: Task description (file_path) [ref: PRD/AC-1.1]

## Notes

### Parallelization
- T2.1 can run in parallel with other parallel tasks

### Dependencies
- **Phase 1 (Core)**: Must complete before Phase 2
- **Phase 2 (Integration)**: Depends on Phase 1 completion

### Traceability
- PRD/AC-1.1 → T1.1, T1.3
- PRD/AC-2.1 → T2.1
```

### PROMPT.md Includes

- RALPH_STATUS block for exit detection
- EXIT_SIGNAL guidance
- Development and testing guidelines

## Project Structure

```
skills/
└── export-to-ralph/           # The export skill
    ├── SKILL.md               # Skill definition (for Claude Code)
    ├── export.py              # Python export script
    ├── reference.md           # Transformation rules & ADRs
    └── templates/             # Output file templates
        ├── prompt-template.md
        ├── fixplan-template.md
        └── agent-template.md

docs/specs/                    # Specification storage (auto-numbered)
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Transformation engine | Python script | Deterministic output; no AI calls needed |
| Output location | Project root | Direct Ralph consumption |
| Missing documents | Warn, don't block | Enables iterative workflow |
| Criteria format | Regex-based | Reproducible; fast execution |
| Plugin integration | Add to the-startup | Seamless `/start:*` workflow |

## Setup for Other Users/Environments

### New Environment Checklist

1. **Install prerequisites:**
   - Claude Code CLI
   - the-startup plugin (via `/plugin` command)
   - Ralph Claude Code (`./install.sh`)

2. **Install export-to-ralph skill:**
   ```bash
   # Clone this repo
   git clone https://github.com/Mindbulletts/specify_plus_ralph_orchestrator.git

   # Copy skill to the-startup (adjust version as needed)
   cp -r specify_plus_ralph_orchestrator/skills/export-to-ralph \
         ~/.claude/plugins/cache/the-startup/start/*/skills/
   ```

3. **Add shell alias (optional):**
   ```bash
   echo "alias ralph-export='python ~/.claude/plugins/cache/the-startup/start/2.13.0/skills/export-to-ralph/export.py'" >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Verify installation:**
   ```bash
   ralph-export --help
   ```

### Version Compatibility

| Component | Tested Version |
|-----------|---------------|
| the-startup plugin | 2.13.0 |
| Ralph Claude Code | 0.9.9 |
| Python | 3.x |
| Claude Code CLI | 2.x |

When the-startup plugin updates, re-copy the `export-to-ralph` skill to the new version directory.

## Long-Term Solutions

The current installation method (copying to the-startup plugin) works but requires re-copying after plugin updates. Consider these alternatives:

### Option 1: Contribute to the-startup (Recommended)

Submit a pull request to [the-startup repository](https://github.com/rsmdt/the-startup) to include `export-to-ralph` as an official skill.

**Pros:**
- Permanent solution
- Maintained with plugin updates
- Benefits all users

**Cons:**
- Requires maintainer approval
- May need to adapt to their standards

### Option 2: Separate Plugin

Publish `export-to-ralph` as a standalone Claude Code plugin.

**Pros:**
- Independent versioning
- Full control over updates
- Can add additional features

**Cons:**
- Two plugins to manage
- Need to set up marketplace or distribution

**To implement:**
1. Create `.claude-plugin/plugin.json` with plugin metadata
2. Publish to a marketplace (GitHub-based or custom)
3. Users install via `/plugin` command

### Option 3: User-Level Skill

Install as a user-level subagent in `~/.claude/agents/`.

**Pros:**
- Survives plugin updates
- User-controlled

**Cons:**
- Different invocation pattern
- Less integrated with `/start:*` workflow

## Requirements

- Python 3.x (standard library only)
- Claude Code CLI
- the-startup plugin (for `/start:specify`)
- Ralph Claude Code (for autonomous execution)

## Documentation

- [Transformation Rules](skills/export-to-ralph/reference.md) - Detailed field mappings, ADRs, and conversion logic
- [Skill Usage](skills/export-to-ralph/SKILL.md) - When and how to use the export skill
- [Ralph Documentation](https://github.com/frankbria/ralph-claude-code) - Ralph CLI usage

## Contributing

1. Fork this repository
2. Make changes to `skills/export-to-ralph/`
3. Test with `ralph-export <spec-id> --dry-run`
4. Submit a pull request

## License

MIT
