---
name: export-to-ralph
description: Export completed specifications (PRD/SDD/PLAN) to Ralph format. Copies specs to specs/new-features/, creates @fix_plan.md, updates PROMPT.md "Current Focus", and cleans up source.
allowed-tools: Read, Write, Bash, TodoWrite, Grep, Glob, AskUserQuestion
---

# Export to Ralph Skill

You are a specification export specialist that prepares completed PRD/SDD/PLAN documents for Ralph execution.

## When to Activate

Activate this skill when you need to:
- **Export a specification** to Ralph format after completing `/start:specify`
- **Prepare for Ralph execution** with fresh specifications
- **Update project focus** for a new development cycle

## Prerequisites

Before exporting, ensure:
1. Specification exists in `docs/specs/[NNN]-[name]/`
2. PRD (product-requirements.md) exists with Must-Have features
3. PLAN (implementation-plan.md) exists with Phase 1 tasks
4. No `[NEEDS CLARIFICATION]` markers remain in documents
5. **Project has existing Ralph structure** (PROMPT.md, @AGENT.md, specs/)

## What This Skill Does

| Action | Details |
|--------|---------|
| **Copy PRD** | `docs/specs/NNN-*/product-requirements.md` -> `specs/new-features/` |
| **Copy SDD** | `docs/specs/NNN-*/solution-design.md` -> `specs/new-features/` |
| **Copy PLAN** | `docs/specs/NNN-*/implementation-plan.md` -> `specs/new-features/` |
| **Create @fix_plan.md** | Transform PLAN phases to prioritized task list |
| **Update PROMPT.md** | Update "Current Focus" line with new feature name |
| **Delete source** | Remove `docs/specs/NNN-*/` after successful conversion |

## What This Skill Does NOT Do

| Skip | Reason |
|------|--------|
| Create new PROMPT.md | Use existing, customized version |
| Create new @AGENT.md | Use existing, customized version |
| Create specs/requirements.md | Use project-overview.md instead |
| Create specs/features/*.md | Use specs/new-features/ instead |

## Export Process

### 1. Validate with Dry Run

```bash
python skills/export-to-ralph/export.py [spec-id] --dry-run
```

**Blocking conditions (export fails):**
- Project missing PROMPT.md, @AGENT.md, or specs/
- Any `[NEEDS CLARIFICATION]` marker in documents
- PRD has no Must-Have features section
- PLAN has no Phase 1 tasks

**Warning conditions (export proceeds):**
- SDD missing (specs/new-features/ will be incomplete)

### 2. Execute Export

```bash
# Full export to project root
python skills/export-to-ralph/export.py [spec-id]

# Export with custom output directory
python skills/export-to-ralph/export.py [spec-id] --output-dir /path/to/project

# Force overwrite existing @fix_plan.md
python skills/export-to-ralph/export.py [spec-id] --force

# Keep source docs/specs/NNN-*/ (don't delete)
python skills/export-to-ralph/export.py [spec-id] --no-cleanup
```

### 3. Verify Output

After export, verify:
- `specs/new-features/product-requirements.md` - Full PRD
- `specs/new-features/solution-design.md` - Full SDD (if provided)
- `specs/new-features/implementation-plan.md` - Full PLAN
- `@fix_plan.md` - Prioritized task checklist
- `PROMPT.md` - Updated "Current Focus" line
- `docs/specs/NNN-*/` - Deleted (unless --no-cleanup)

## Transformation Rules

### PLAN -> @fix_plan.md

| PLAN Phase | @fix_plan.md Priority |
|------------|----------------------|
| Phase 1 | High Priority |
| Phase 2 | Medium Priority |
| Phase 3+ | Low Priority |

Task format: `- [ ] T1.1: Description (file_path) [ref: PRD/AC-X.Y]`

### PRD -> PROMPT.md Current Focus

The script extracts the PRD title and vision to update line 16:

**Before:**
```markdown
**Current Focus:** Previous Feature - Previous description...
```

**After:**
```markdown
**Current Focus:** New Feature Name - Vision statement from PRD...
```

## Output Format

After export, report:

```
Export Complete!

Files in specs/new-features/:
  - product-requirements.md
  - solution-design.md
  - implementation-plan.md

Files updated/created:
  - @fix_plan.md
  - PROMPT.md (Current Focus line)

Cleaned up:
  - docs/specs/003-feature-name

Next Steps:
  1. Review @fix_plan.md for task list
  2. Review specs/new-features/ for full specifications
  3. Run: ralph start
```

## Error Handling

| Error | Response |
|-------|----------|
| Project missing PROMPT.md | "Project missing required Ralph files" - create PROMPT.md first |
| Project missing @AGENT.md | "Project missing required Ralph files" - create @AGENT.md first |
| Project missing specs/ | "Project missing required Ralph files" - create specs/ directory first |
| Spec not found | "Spec [ID] not found in docs/specs/" |
| [NEEDS CLARIFICATION] found | "Cannot export - resolve markers first" + list |
| No Must-Have features | "PRD has no Must-Have features section" |
| No Phase 1 | "PLAN has no Phase 1 section" |
| @fix_plan.md exists | "File exists. Overwrite? (use --force to skip)" |

## Workflow Integration

```
start:specify (creates docs/specs/NNN-*/)
       |
       v
start:export-to-ralph
       |
       +-- Copy PRD/SDD/PLAN -> specs/new-features/
       +-- Transform PLAN -> @fix_plan.md
       +-- Update PROMPT.md "Current Focus" line
       +-- Delete docs/specs/NNN-*/
       |
       v
ralph start
       |
       v
finalize-ralph.sh
       +-- Archive @fix_plan.md
       +-- Reset specs/new-features/
       +-- Cleanup runtime files
```

## Reference

See [reference.md](reference.md) for detailed transformation rules and examples.
