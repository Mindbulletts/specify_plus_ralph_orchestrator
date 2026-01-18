---
title: "Ralph Claude Code Integration"
status: draft
version: "1.0"
---

# Implementation Plan

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All `[NEEDS CLARIFICATION: ...]` markers have been addressed
- [x] All specification file paths are correct and exist
- [x] Each phase follows TDD: Prime → Test → Implement → Validate
- [x] Every task has verifiable success criteria
- [x] A developer could follow this plan independently

### QUALITY CHECKS (Should Pass)

- [x] Context priming section is complete
- [x] All implementation phases are defined
- [x] Dependencies between phases are clear (no circular dependencies)
- [x] Parallel work is properly tagged with `[parallel: true]`
- [x] Activity hints provided for specialist selection `[activity: type]`
- [x] Every phase references relevant SDD sections
- [x] Every test references PRD acceptance criteria
- [x] Integration & E2E tests defined in final phase
- [x] Project commands match actual project setup

---

## Specification Compliance Guidelines

### How to Ensure Specification Adherence

1. **Before Each Phase**: Complete the Pre-Implementation Specification Gate
2. **During Implementation**: Reference specific SDD sections in each task
3. **After Each Task**: Run Specification Compliance checks
4. **Phase Completion**: Verify all specification requirements are met

### Deviation Protocol

When implementation requires changes from the specification:
1. Document the deviation with clear rationale
2. Obtain approval before proceeding
3. Update SDD when the deviation improves the design
4. Record all deviations in this plan for traceability

## Metadata Reference

- `[parallel: true]` - Tasks that can run concurrently
- `[component: component-name]` - For multi-component features
- `[ref: document/section; lines: 1, 2-3]` - Links to specifications, patterns, or interfaces and (if applicable) line(s)
- `[activity: type]` - Activity hint for specialist agent selection

### Success Criteria

**Validate** = Process verification ("did we follow TDD?")
**Success** = Outcome verification ("does it work correctly?")

```markdown
# Single-line format
- Success: [Criterion] `[ref: PRD/AC-X.Y]`

# Multi-line format
- Success:
  - [ ] [Criterion 1] `[ref: PRD/AC-X.Y]`
  - [ ] [Criterion 2] `[ref: SDD/Section]`
```

---

## Context Priming

*GATE: Read all files in this section before starting any implementation.*

**Specification**:

- `docs/specs/002-ralph-claude-code-integration/product-requirements.md` - Product Requirements
- `docs/specs/002-ralph-claude-code-integration/solution-design.md` - Solution Design
- `skills/specification-management/SKILL.md` - Reference skill structure pattern
- `skills/specification-management/spec.py` - Reference Python script pattern

**Key Design Decisions**:

- **ADR-1**: Python Script for Transformation - Use export.py with regex-based transformation logic (follows spec.py pattern)
- **ADR-2**: Export to Project Root - Write Ralph files to project root for direct Ralph consumption
- **ADR-3**: Partial Export with Warnings - Allow export when optional sections missing with clear warnings
- **ADR-4**: Deterministic Transformation - Use regex-based transformation, not AI-mediated
- **ADR-5**: SKILL.md + Python Script Architecture - Skill provides methodology, script executes

**Implementation Context**:

```bash
# Testing (Python standard library only)
python -m py_compile skills/export-to-ralph/export.py  # Syntax check

# Quality
python -c "import ast; ast.parse(open('skills/export-to-ralph/export.py').read())"  # Parse check

# Manual validation
python skills/export-to-ralph/export.py --help  # CLI help
python skills/export-to-ralph/export.py 002 --dry-run  # Dry run test
```

---

## Implementation Phases

Each task follows red-green-refactor: **Prime** (understand context), **Test** (red), **Implement** (green), **Validate** (refactor + verify).

> **Tracking Principle**: Track logical units that produce verifiable outcomes. The TDD cycle is the method, not separate tracked items.

---

### Phase 1: Skill Infrastructure

Establishes the export-to-ralph skill directory structure and core files.

- [ ] **T1.1 Create Skill Directory Structure** `[activity: infrastructure]`

  - Prime: Read specification-management skill structure `[ref: SDD/Building Block View/Directory Map]`
  - Test: Directory structure matches SDD specification
  - Implement: Create `skills/export-to-ralph/` with SKILL.md, export.py, reference.md, templates/
  - Validate: Directory exists with all required files
  - Success: Skill directory structure matches SDD Directory Map `[ref: SDD/Building Block View]`

- [ ] **T1.2 Create SKILL.md Definition** `[activity: documentation]`

  - Prime: Read existing SKILL.md files for pattern `[ref: skills/specification-management/SKILL.md]`
  - Test: SKILL.md has required frontmatter (name, description, allowed-tools)
  - Implement: Create `skills/export-to-ralph/SKILL.md` with activation guidance, workflow, and output format
  - Validate: Frontmatter parses correctly; sections match skill pattern
  - Success: SKILL.md follows established pattern and can be invoked via `Skill(skill: "start:export-to-ralph")` `[ref: PRD/Feature 1]`

- [ ] **T1.3 Create Reference Documentation** `[activity: documentation]`

  - Prime: Read SDD transformation rules and field mappings `[ref: SDD/Runtime View/Complex Logic]`
  - Test: Reference.md documents all transformation rules
  - Implement: Create `skills/export-to-ralph/reference.md` with EARS→Gherkin rules, task flattening rules, field mappings
  - Validate: All transformation patterns from SDD are documented
  - Success: Developer can understand transformation rules from reference alone `[ref: SDD/Implementation Examples]`

- [ ] **T1.4 Create Ralph File Templates** `[activity: documentation]`

  - Prime: Read Ralph file format requirements `[ref: SDD/External Interfaces]`
  - Test: Templates produce valid Ralph files
  - Implement: Create `templates/prompt-template.md`, `templates/fixplan-template.md`, `templates/agent-template.md`
  - Validate: Templates match Ralph expected format
  - Success:
    - prompt-template.md includes RALPH_STATUS block `[ref: PRD/AC-1.1]`
    - fixplan-template.md has High/Medium/Low priority sections `[ref: PRD/AC-2.1]`
    - agent-template.md has Install/Dev/Test/Build sections `[ref: PRD/AC-1.1]`

- [ ] **T1.5 Phase Validation** `[activity: validate]`

  - Run syntax checks on all created files. Verify skill can be loaded. Confirm directory structure matches SDD.

---

### Phase 2: Core Export Script

Implements the Python export.py script with document reading, validation, and transformation logic.

- [ ] **T2.1 Create Script Skeleton with CLI** `[activity: backend-cli]`

  - Prime: Read spec.py CLI pattern `[ref: skills/specification-management/spec.py]`
  - Test: CLI parses arguments correctly; --help works; --dry-run flag recognized
  - Implement: Create `export.py` with argparse CLI: spec_id, --output-dir, --dry-run, --force
  - Validate: CLI responds to all arguments correctly
  - Success: Script accepts spec ID and options per SDD interface `[ref: SDD/Building Block View/Internal API Changes]`

- [ ] **T2.2 Implement Spec Resolution and Validation** `[activity: backend-core]`

  - Prime: Read spec.py path resolution logic `[ref: skills/specification-management/spec.py]`
  - Test: Resolves spec ID to directory; detects missing documents; finds [NEEDS CLARIFICATION] markers
  - Implement: Add spec resolution and validation functions to export.py
  - Validate: Correctly identifies valid, incomplete, and invalid specifications
  - Success:
    - Spec not found returns error `[ref: SDD/Runtime View/Error Handling]`
    - [NEEDS CLARIFICATION] markers block export `[ref: PRD/AC-1.2]`
    - Missing optional documents generate warnings `[ref: PRD/AC-1.3]`

- [ ] **T2.3 Implement Document Readers** `[activity: backend-core]`

  - Prime: Read PRD, SDD, PLAN template structures `[ref: skills/requirements-analysis/template.md]`
  - Test: Extracts all required sections from each document type
  - Implement: Add functions to parse PRD (vision, features, EARS criteria), SDD (commands, architecture), PLAN (tasks)
  - Validate: All documented fields are extractable
  - Success: Readers extract all fields per SDD field mapping `[ref: SDD/Runtime View/Complex Logic Step 3]`

- [ ] **T2.4 Implement PROMPT.md Transformer** `[parallel: true]` `[activity: transformation]`

  - Prime: Read PROMPT.md generation algorithm `[ref: SDD/Runtime View/Complex Logic Step 4]`
  - Test: Generates valid PROMPT.md with all sections; includes RALPH_STATUS block
  - Implement: Add transform_prompt() function using template
  - Validate: Output matches Ralph expected format
  - Success: PROMPT.md contains vision, problem, objectives, scope, constraints, assumptions, criteria `[ref: PRD/AC-1.1]`

- [ ] **T2.5 Implement @fix_plan.md Transformer** `[parallel: true]` `[activity: transformation]`

  - Prime: Read @fix_plan.md generation algorithm `[ref: SDD/Runtime View/Complex Logic Step 5]`
  - Test: Generates checkbox items; groups by priority; flattens PLAN tasks
  - Implement: Add transform_fixplan() and flatten_plan_task() functions
  - Validate: Output has High/Medium/Low sections with checkbox items
  - Success:
    - PLAN tasks become checkbox items `[ref: PRD/AC-2.1]`
    - PRD references preserved `[ref: PRD/AC-2.1]`
    - Phase 1→High, Phase 2→Medium, Phase 3→Low priority `[ref: PRD/AC-2.1]`

- [ ] **T2.6 Implement @AGENT.md Transformer** `[parallel: true]` `[activity: transformation]`

  - Prime: Read @AGENT.md generation algorithm `[ref: SDD/Runtime View/Complex Logic Step 6]`
  - Test: Extracts commands from SDD; includes architecture notes; adds quality requirements
  - Implement: Add transform_agent() function using template
  - Validate: Output has Install/Dev/Test/Build sections with actual commands
  - Success: @AGENT.md contains build commands from SDD `[ref: PRD/AC-1.1]`

- [ ] **T2.7 Implement specs/ Generator** `[parallel: true]` `[activity: transformation]`

  - Prime: Read specs/ generation algorithm and EARS→Gherkin rules `[ref: SDD/Runtime View/Complex Logic Step 7]`
  - Test: Creates feature files; converts EARS to Gherkin; creates scenario files
  - Implement: Add transform_specs() and transform_ears_to_gherkin() functions
  - Validate: Generated Gherkin is syntactically valid
  - Success:
    - EARS EVENT-DRIVEN converts to Given-When-Then `[ref: PRD/AC-3.1]`
    - Original EARS preserved as comment `[ref: PRD/AC-3.1]`
    - Feature files grouped in specs/features/ `[ref: PRD/AC-1.1]`

- [ ] **T2.8 Implement File Writer with Collision Handling** `[activity: backend-io]`

  - Prime: Read SDD collision handling requirements `[ref: SDD/Runtime View/Error Handling]`
  - Test: Creates files; prompts on collision (unless --force); respects --dry-run
  - Implement: Add write_output() function with collision detection
  - Validate: Files created at correct locations; no unintended overwrites
  - Success:
    - Dry-run shows files without writing `[ref: SDD/Building Block View/Internal API Changes]`
    - Collision prompts user `[ref: SDD/Runtime View/Error Handling]`
    - --force skips prompt `[ref: SDD/Building Block View/Internal API Changes]`

- [ ] **T2.9 Phase Validation** `[activity: validate]`

  - Run all Phase 2 functions with test data. Verify transformations match expected output. Syntax check passes.

---

### Phase 3: Integration and Testing

Full system validation ensuring export skill works end-to-end.

- [ ] **T3.1 End-to-End Export Test** `[activity: e2e-test]`

  - Prime: Read acceptance scenarios from SDD `[ref: SDD/Acceptance Scenarios]`
  - Test: Export complete spec 002; verify all four output files created
  - Implement: Run full export on current specification
  - Validate: PROMPT.md, @fix_plan.md, @AGENT.md, specs/ all present and valid
  - Success: Complete specification exports successfully `[ref: PRD/AC-1.1]`

- [ ] **T3.2 Partial Export Test** `[activity: integration-test]`

  - Prime: Read partial export requirements `[ref: PRD/Feature 1/AC Edge Case 1]`
  - Test: Export with missing SDD produces warnings but completes
  - Implement: Test with partial specifications
  - Validate: Warnings displayed; partial files created
  - Success: Partial export with warnings works `[ref: PRD/AC-1.3]`

- [ ] **T3.3 Error Handling Test** `[activity: integration-test]`

  - Prime: Read error handling requirements `[ref: SDD/Runtime View/Error Handling]`
  - Test: Invalid spec ID returns error; [NEEDS CLARIFICATION] blocks export
  - Implement: Test all error conditions
  - Validate: Appropriate error messages for each failure mode
  - Success:
    - Spec not found error is clear `[ref: SDD/Runtime View/Error Handling]`
    - Blocking markers listed `[ref: PRD/AC-1.2]`

- [ ] **T3.4 Cross-Platform Validation** `[activity: validate]`

  - Prime: Read cross-platform constraint `[ref: SDD/Constraints CON-4]`
  - Test: Script runs on Windows paths; uses Path objects throughout
  - Implement: Verify path handling in export.py
  - Validate: No hardcoded path separators; UTF-8 encoding used
  - Success: Works on Windows, macOS, Linux `[ref: SDD/Quality Requirements]`

- [ ] **T3.5 Quality Gates** `[activity: validate]`

  - Performance: Export completes in < 2 seconds for typical spec `[ref: SDD/Quality Requirements]`
  - Coverage: All documented transformation rules have tests
  - Documentation: reference.md is complete and accurate

- [ ] **T3.6 Specification Compliance** `[activity: business-acceptance]`

  - All PRD acceptance criteria verified (Features 1-3)
  - Implementation follows SDD design (ADRs 1-5)
  - SKILL.md documentation complete
  - Ready for integration with /start:specify workflow

---

## Plan Verification

Before this plan is ready for implementation, verify:

| Criterion | Status |
|-----------|--------|
| A developer can follow this plan without additional clarification | ✅ |
| Every task produces a verifiable deliverable | ✅ |
| All PRD acceptance criteria map to specific tasks | ✅ |
| All SDD components have implementation tasks | ✅ |
| Dependencies are explicit with no circular references | ✅ |
| Parallel opportunities are marked with `[parallel: true]` | ✅ |
| Each task has specification references `[ref: ...]` | ✅ |
| Project commands in Context Priming are accurate | ✅ |

---

## PRD-to-Task Traceability

| PRD Acceptance Criteria | Task |
|------------------------|------|
| PRD/AC-1.1: Export creates PROMPT.md | T2.4 |
| PRD/AC-1.1: Export creates @fix_plan.md | T2.5 |
| PRD/AC-1.1: Export creates @AGENT.md | T2.6 |
| PRD/AC-1.1: Export creates specs/ | T2.7 |
| PRD/AC-1.2: Incomplete spec blocks export | T2.2 |
| PRD/AC-1.3: Missing SDD shows warning | T2.2, T3.2 |
| PRD/AC-2.1: PLAN tasks become checkboxes | T2.5 |
| PRD/AC-2.1: PRD references preserved | T2.5 |
| PRD/AC-2.1: Phase→Priority mapping | T2.5 |
| PRD/AC-3.1: EARS→Gherkin conversion | T2.7 |
| PRD/AC-3.1: Original EARS as comment | T2.7 |

## SDD-to-Task Traceability

| SDD Component | Task |
|--------------|------|
| Skill Directory Structure | T1.1 |
| SKILL.md Definition | T1.2 |
| Reference Documentation | T1.3 |
| Ralph File Templates | T1.4 |
| CLI Interface | T2.1 |
| Spec Resolution | T2.2 |
| Document Readers | T2.3 |
| PROMPT.md Transformer | T2.4 |
| @fix_plan.md Transformer | T2.5 |
| @AGENT.md Transformer | T2.6 |
| specs/ Generator | T2.7 |
| File Writer | T2.8 |
| Error Handling | T2.2, T3.3 |
| Cross-Platform | T3.4 |
