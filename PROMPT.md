# Ralph Claude Code Integration

## Overview

Enable developers to create structured specifications (PRD/SDD/PLAN) using `/start:specify` that can be directly consumed by Ralph's autonomous AI orchestration loop for hands-off implementation.

## Problem & Context

Developers using Claude Code for AI-assisted development face two disconnected workflows:

1. **Specification Creation**: Using `/start:specify` to create structured PRD, SDD, and PLAN documents
2. **Autonomous Execution**: Using Ralph to run iterative Claude Code sessions

Currently, there is no bridge between these systems. Ralph expects specific file formats (PROMPT.md, @fix_plan.md, @AGENT.md, specs/) that don't match the output of the specification workflow (product-requirements.md, solution-design.md, implementation-plan.md). This forces developers to:

- Manually translate specifications into Ralph's format
- Lose traceability between requirements and implementation
- Duplicate effort describing the same feature in two formats
- Risk specification drift during manual translation

**Impact**: Developers spend 30-60 minutes per feature manually converting specifications, with no guarantee of accurate translation.

## Objectives

An integrated workflow that:

1. **Eliminates manual translation**: Specifications created with `/start:specify` are automatically consumable by Ralph
2. **Maintains traceability**: Every Ralph task traces back to PRD acceptance criteria
3. **Preserves context**: Architecture decisions from SDD inform Ralph's implementation
4. **Enables hands-off execution**: Single command transitions from completed specification to autonomous implementation

## Scope Boundaries

**In Scope:**
- Specification Export to Ralph Format

**Out of Scope:**
- **Ralph execution monitoring dashboard**: Out of scope; use Ralph's built-in `ralph-monitor` command
- **Automatic specification updates from implementation**: Would require reverse-engineering implementation changes
- **Multi-specification orchestration**: Running multiple specs in parallel with Ralph; focus on single-spec workflow first
- **Ralph installation automation for all platforms**: Initial focus on environments where Ralph is already functional
- **IDE integration**: Focus on CLI workflow; IDE plugins are future consideration

## Key Constraints

- Ralph repository (frankbria/ralph-claude-code) must remain accessible for initial setup
- Users must have Claude Code CLI installed and configured
- Export targets local filesystem (no cloud/remote export in this phase)
- Windows, macOS, and Linux must all be supported for export functionality

CON-1: **Plugin Architecture** - Must follow existing skill structure pattern (SKILL.md, template.md, reference.md in dedicated directory)

CON-2: **Tool Availability** - Limited to tools available in Claude Code: Read, Write, Edit, Bash, TodoWrite, Grep, Glob, Task, AskUserQuestion

CON-3: **No External Dependencies** - Cannot require npm/pip packages; Python scripts only use standard library

CON-4: **Cross-Platform** - Must work on Windows, macOS, and Linux (Ralph uses Bash scripts)

CON-5: **Deterministic Output** - Transformation must be predictable and reproducible (no AI-mediated conversion)

CON-6: **Partial Export Support** - Must handle incomplete specifications with warnings (user-confirmed decision)

## Assumptions

- Users are familiar with the `/start:specify` workflow and have completed at least one specification
- Ralph's file format expectations (PROMPT.md, @fix_plan.md, @AGENT.md, specs/) will remain stable
- Users have git installed for Ralph repository cloning
- Claude Code CLI version is compatible with Ralph's expected command syntax

## Success Criteria

- **Adoption:** 80% of specifications completed with `/start:specify` are exported to Ralph within one week of completion
- **Engagement:** Average of 3+ specification-to-Ralph exports per active user per month
- **Quality:** 95% of exported specifications result in successful Ralph execution (no early circuit breaker trips)
- **Business Impact:** 50% reduction in time-to-first-commit for features using integrated workflow vs. manual translation

---

## Development Guidelines

1. Study specs/* to understand project specifications
2. Review @fix_plan.md for current priorities
3. Implement the highest priority item
4. Run tests after each implementation
5. Update @fix_plan.md with progress

## Testing Guidelines

- Focus on implementation over testing (~20% testing effort)
- Write tests for NEW functionality only
- Do NOT refactor existing tests unless broken
- Run essential tests for modified code

---

## Status Reporting

At the end of your response, ALWAYS include:

---RALPH_STATUS---
STATUS: IN_PROGRESS | COMPLETE | BLOCKED
TASKS_COMPLETED_THIS_LOOP: <number>
FILES_MODIFIED: <number>
TESTS_STATUS: PASSING | FAILING | NOT_RUN
WORK_TYPE: IMPLEMENTATION | TESTING | DOCUMENTATION | REFACTORING
EXIT_SIGNAL: false | true
RECOMMENDATION: <one line summary of what to do next>
---END_RALPH_STATUS---

### When to set EXIT_SIGNAL: true

Set EXIT_SIGNAL to **true** when ALL conditions are met:
1. All items in @fix_plan.md are marked [x]
2. All tests are passing
3. No errors or warnings in last execution
4. All requirements from specs/ are implemented
