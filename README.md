# Specify + Ralph Orchestrator

A Claude Code skill that bridges the `/start:specify` specification workflow ([the-startup](https://github.com/rsmdt/the-startup) plugin) with [Ralph Claude Code](https://github.com/frankbria/ralph-claude-code) autonomous orchestration.

## Problem

Developers using Claude Code face two disconnected workflows:

1. **Specification Creation**: Using `/start:specify` to create structured PRD, SDD, and PLAN documents
2. **Autonomous Execution**: Using Ralph to run iterative Claude Code sessions

The specification output (`docs/specs/NNN-*/`) needs to be prepared for Ralph execution, including updating the project's task list and focus area.

## Solution

The `export-to-ralph` skill prepares completed specifications for Ralph execution:

| Action | Details |
|--------|---------|
| **Copy specs** | PRD/SDD/PLAN -> `specs/new-features/` |
| **Create @fix_plan.md** | Transform PLAN phases to prioritized task list |
| **Update PROMPT.md** | Update "Current Focus" line with new feature |
| **Cleanup** | Delete source `docs/specs/NNN-*/` after conversion |

**Note:** This skill assumes an existing Ralph project structure (PROMPT.md, @AGENT.md, specs/). It does not create these files from scratch.

## Architecture Overview

```
+------------------------------------------------------------+
|                    Claude Code                              |
|  +------------------+    +---------------------------+     |
|  | /start:specify   |--->| /start:export-to-ralph    |     |
|  | (the-startup)    |    | (this skill)              |     |
|  +------------------+    +-------------+-------------+     |
|         |                              |                    |
|         v                              v                    |
|   docs/specs/NNN-*/           Existing Ralph Project        |
|   +-- product-requirements.md         |                    |
|   +-- solution-design.md              v                    |
|   +-- implementation-plan.md   specs/new-features/         |
|                                +-- product-requirements.md |
|                                +-- solution-design.md      |
|                                +-- implementation-plan.md  |
|                                                            |
|                                @fix_plan.md (created)      |
|                                PROMPT.md (updated)         |
+------------------------------------------------------------+
                                      |
                                      v
                            +------------------+
                            |  ralph start     |
                            |  (CLI tool)      |
                            +------------------+
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
4. **Existing Ralph Project Structure** - Your project must have:
   - `PROMPT.md` - Ralph development instructions
   - `@AGENT.md` - Build/test configuration
   - `specs/` - Specifications directory (with `project-overview.md`, etc.)

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

Follow the guided workflow through PRD -> SDD -> PLAN phases.

### 2. Export to Ralph Format

**Via Claude Code skill:**
```
/start:export-to-ralph
```

**Via command line:**
```bash
ralph-export 001                    # Export spec 001
ralph-export 001 --dry-run          # Preview without writing
ralph-export 001 --force            # Overwrite existing @fix_plan.md
ralph-export 001 --no-cleanup       # Keep source docs/specs/NNN-*/
ralph-export 001 --output-dir ./    # Custom output directory
```

### 3. Run Ralph

```bash
ralph start
```

## Features

- **Direct spec copying**: PRD/SDD/PLAN copied to `specs/new-features/` without transformation
- **Priority mapping**: PLAN phases -> High/Medium/Low priority tasks in @fix_plan.md
- **Traceability preservation**: PRD references maintained in task list (`[ref: PRD/AC-X.Y]`)
- **Current Focus update**: PROMPT.md line 16 updated with new feature name and vision
- **Automatic cleanup**: Source `docs/specs/NNN-*/` deleted after successful conversion
- **Cross-platform**: Works on Windows, macOS, and Linux

## Generated Output

### @fix_plan.md Structure

```markdown
# Feature Name Fix Plan

## High Priority
- [ ] T1.1: Task description (file_path) [ref: PRD/AC-1.1]

## Medium Priority
- [ ] T2.1: Task description (file_path) [ref: PRD/AC-2.1]

## Low Priority
- [ ] T3.1: Task description [ref: PRD/AC-3.1]

## Completed
- [x] Project initialization

## Notes

### Parallelization
- T2.1 can run in parallel with other parallel tasks

### Dependencies
- **Phase 1 (Core)**: Must complete before Phase 2
- **Phase 2 (Integration)**: Depends on Phase 1 completion

### Traceability
- PRD/AC-1.1 -> T1.1, T1.3
- PRD/AC-2.1 -> T2.1
```

### PROMPT.md Update

Only line 16 is modified:

```markdown
**Current Focus:** New Feature Name - Vision statement from PRD (truncated to 100 chars)...
```

## Project Structure

```
skills/
+-- export-to-ralph/           # The export skill
    +-- SKILL.md               # Skill definition (for Claude Code)
    +-- export.py              # Python export script
    +-- reference.md           # Transformation rules & ADRs
    +-- templates/             # Output file templates
        +-- fixplan-template.md

docs/specs/                    # Specification storage (auto-numbered)
```

## Expected Ralph Project Structure

Your target project must have this structure:

```
your-project/
+-- PROMPT.md                  # PERMANENT - Ralph instructions (customized)
+-- @AGENT.md                  # PERMANENT - Build instructions (customized)
+-- @fix_plan.md               # PER-CYCLE - Task list from implementation-plan
+-- specs/
    +-- project-overview.md    # PERMANENT - Business context, features
    +-- technical-reference.md # PERMANENT - Tech stack, APIs, patterns
    +-- new-features/          # PER-CYCLE - Current feature specs
        +-- product-requirements.md
        +-- solution-design.md
        +-- implementation-plan.md
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Transformation engine | Python script | Deterministic output; no AI calls needed |
| Output location | `specs/new-features/` | Matches existing project structure |
| File creation | Copy, don't transform | Preserves full specification detail |
| PROMPT.md update | Single line only | Preserves customized instructions |
| Missing documents | PLAN required, SDD optional | @fix_plan.md needs PLAN phases |
| Source cleanup | Default on | Prevents stale specs accumulating |

## Setup for Other Users/Environments

### New Environment Checklist

1. **Install prerequisites:**
   - Claude Code CLI
   - the-startup plugin (via `/plugin` command)
   - Ralph Claude Code (`./install.sh`)

2. **Set up Ralph project structure:**
   ```bash
   # Create required files (one-time setup)
   touch PROMPT.md @AGENT.md
   mkdir -p specs/new-features
   ```

3. **Install export-to-ralph skill:**
   ```bash
   # Clone this repo
   git clone https://github.com/Mindbulletts/specify_plus_ralph_orchestrator.git

   # Copy skill to the-startup (adjust version as needed)
   cp -r specify_plus_ralph_orchestrator/skills/export-to-ralph \
         ~/.claude/plugins/cache/the-startup/start/*/skills/
   ```

4. **Add shell alias (optional):**
   ```bash
   echo "alias ralph-export='python ~/.claude/plugins/cache/the-startup/start/2.13.0/skills/export-to-ralph/export.py'" >> ~/.bashrc
   source ~/.bashrc
   ```

5. **Verify installation:**
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

## Workflow Summary

```
/start:specify "Feature description"
       |
       v
docs/specs/NNN-feature/
       |
       v
/start:export-to-ralph (or: ralph-export NNN)
       |
       +-- Copy PRD/SDD/PLAN -> specs/new-features/
       +-- Transform PLAN -> @fix_plan.md
       +-- Update PROMPT.md "Current Focus"
       +-- Delete docs/specs/NNN-*/
       |
       v
ralph start
       |
       v
finalize-ralph.sh
       +-- Archive @fix_plan.md
       +-- Reset specs/new-features/
       +-- Ready for next cycle
```

## Requirements

- Python 3.x (standard library only)
- Claude Code CLI
- the-startup plugin (for `/start:specify`)
- Ralph Claude Code (for autonomous execution)
- **Existing Ralph project structure**

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
