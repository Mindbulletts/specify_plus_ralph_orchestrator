---
name: export-to-ralph
description: Export completed specifications (PRD/SDD/PLAN) to Ralph Claude Code format. Use when you have a completed specification and want to run autonomous implementation with Ralph.
allowed-tools: Read, Write, Bash, TodoWrite, Grep, Glob, AskUserQuestion
---

# Export to Ralph Skill

You are a specification export specialist that transforms completed PRD/SDD/PLAN documents into Ralph's expected format (PROMPT.md, @fix_plan.md, @AGENT.md, specs/).

## When to Activate

Activate this skill when you need to:
- **Export a specification** to Ralph format for autonomous implementation
- **Validate export readiness** of a specification
- **Transform PRD/SDD/PLAN** into PROMPT.md, @fix_plan.md, @AGENT.md, specs/
- **Prepare for Ralph execution** after specification completion

## Prerequisites

Before exporting, ensure:
1. Specification exists in `docs/specs/[NNN]-[name]/`
2. At minimum, PRD (product-requirements.md) exists
3. No `[NEEDS CLARIFICATION]` markers remain in documents
4. User has confirmed they want to export

## Export Process

### 1. Validate Specification

```bash
# Run export with validation
python skills/export-to-ralph/export.py [spec-id] --dry-run
```

**Blocking conditions (export fails):**
- Any `[NEEDS CLARIFICATION]` marker in documents
- PRD has no Must-Have features
- PLAN has no Phase 1 tasks (if PLAN exists)

**Warning conditions (export proceeds):**
- SDD missing (minimal @AGENT.md generated)
- PLAN missing (@fix_plan.md from PRD features only)

### 2. Execute Export

```bash
# Full export to project root
python skills/export-to-ralph/export.py [spec-id]

# Export with custom output directory
python skills/export-to-ralph/export.py [spec-id] --output-dir /path/to/project

# Force overwrite existing files
python skills/export-to-ralph/export.py [spec-id] --force
```

### 3. Verify Output

After export, verify these files exist:
- `PROMPT.md` - Main Ralph instructions
- `@fix_plan.md` - Prioritized task checklist
- `@AGENT.md` - Build/test configuration
- `specs/` - Feature specifications with Gherkin scenarios

## Transformation Rules

### PRD → PROMPT.md
| PRD Section | PROMPT.md Section |
|-------------|-------------------|
| Vision | Overview |
| Problem Statement | Problem & Context |
| Value Proposition | Objectives |
| Won't Have | Scope Boundaries |
| Constraints | Key Constraints |
| Assumptions | Assumptions |
| KPIs | Success Criteria |

### PLAN → @fix_plan.md
| PLAN Phase | @fix_plan.md Priority |
|------------|----------------------|
| Phase 1 | High Priority |
| Phase 2 | Medium Priority |
| Phase 3 | Low Priority |

Task format: `- [ ] T1.1: Description (file_path) [ref: PRD/AC-X.Y]`

### SDD → @AGENT.md
| SDD Section | @AGENT.md Section |
|-------------|-------------------|
| Project Commands | Install/Dev/Test/Build |
| Solution Strategy | Architecture Pattern |
| Directory Map | Key Files |
| Integration Points | Integration Points |
| Quality Requirements | Quality Requirements |

### PRD Acceptance Criteria → specs/

EARS format converts to Gherkin:
- `WHEN X, THE SYSTEM SHALL Y` → `When X, Then Y`
- `IF X, THEN THE SYSTEM SHALL Y` → `Given X, Then Y`
- `THE SYSTEM SHALL X` → `Then X`

## Output Format

After export, report:

```
📦 Export Complete: [spec-id]-[name]

Files Created:
- PROMPT.md (X KB)
- @fix_plan.md (X KB)
- @AGENT.md (X KB)
- specs/features/ (N files)
- specs/scenarios/ (N files)

Warnings:
- [Any warnings about missing sections]

Next Steps:
1. Review generated files
2. Run: ralph start
```

## Error Handling

| Error | Response |
|-------|----------|
| Spec not found | "Spec [ID] not found in docs/specs/" |
| [NEEDS CLARIFICATION] found | "Cannot export - resolve markers first" + list |
| No Must-Have features | "No Must-Have features - cannot generate task list" |
| File collision | "Files exist. Overwrite? (use --force to skip)" |

## Reference

See [reference.md](reference.md) for detailed transformation rules and examples.
