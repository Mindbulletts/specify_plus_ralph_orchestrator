# Agent Build Instructions

## Project Setup

### Install
```bash
# TODO: Add install command
```

### Development Server
```bash
# TODO: Add dev command
```

### Running Tests
```bash
python -m pytest tests/  # If tests created
```

### Build
```bash
# TODO: Add build command
```

## Architecture

- **Architecture Pattern**: Single-responsibility skill with Python export script
- **Integration Approach**: New skill `export-to-ralph` invoked after specification completion; reads spec documents, transforms content, writes Ralph files to project root
- **Justification**: Follows established skill pattern; Python handles file I/O and transformation logic cleanly; deterministic output ensures reproducibility
- **Key Decisions**:
  1. Python script for complex transformation logic (like spec.py pattern)
  2. Skill provides methodology/guidance; script executes transformation
  3. Export to project root for direct Ralph consumption
  4. Partial export with warnings rather than blocking

## Key Files

- `SKILL.md` - NEW: Skill definition and methodology
- `export.py` - NEW: Python export script
- `reference.md` - NEW: Transformation rules reference
- `prompt-template.md` - NEW: PROMPT.md structure
- `fixplan-template.md` - NEW: @fix_plan.md structure
- `agent-template.md` - NEW: @AGENT.md structure
- `PROMPT.md`
- `fix_plan.md`
- `AGENT.md`
- `error-handling.md`
- `api.md`

## Integration Points

```yaml
# Inter-Component Communication
- from: SKILL.md
  to: export.py
    - protocol: Bash execution
    - endpoints: CLI arguments
    - data_flow: "Skill invokes script with spec ID; script returns success/failure"

- from: export.py
  to: Specification files
    - protocol: File read
    - endpoints: docs/specs/[id]-[name]/*.md
    - data_flow: "Read PRD, SDD, PLAN documents"

- from: export.py
  to: Ralph output files
    - protocol: File write
    - endpoints: PROMPT.md, @fix_plan.md, @AGENT.md, specs/
    - data_flow: "Write transformed content"
```

## Quality Requirements

| Requirement | Metric | Target |
|-------------|--------|--------|
| **Transformation Accuracy** | Fields correctly mapped | 100% for documented fields |
| **Execution Time** | Time to export | < 2 seconds for typical spec |
| **Error Detection** | [NEEDS CLARIFICATION] markers caught | 100% detection rate |
| **Cross-Platform** | Works on Windows/macOS/Linux | All three platforms |
| **Partial Export** | Handles missing optional sections | No crashes; clear warnings |

## Decision Rationale

- **ADR-1 Python Script for Transformation****: Use Python script (export.py) for complex transformation logic
- **ADR-2 Export to Project Root****: Write Ralph files to project root by default
- **ADR-3 Partial Export with Warnings****: Allow export when optional sections missing
- **ADR-4 Deterministic Transformation****: Use regex-based transformation, not AI-mediated
- **ADR-5 SKILL.md + Python Script Architecture****: Skill provides methodology; script executes

## Error Handling

| Error Type | Detection | Response |
|------------|-----------|----------|
| **Spec not found** | Spec ID doesn't exist | Exit with error: "Spec [ID] not found in docs/specs/" |
| **[NEEDS CLARIFICATION] markers** | Regex search in documents | Exit with error: "Cannot export - resolve clarification markers first" + list markers |
| **Missing PRD** | File not exists | Warning: "PRD not found - PROMPT.md will lack context" |
| **Missing SDD** | File not exists | Warning: "SDD not found - @AGENT.md will have minimal config" |
| **Missing PLAN** | File not exists | Warning: "PLAN not found - @fix_plan.md will only have PRD features" |
| **Missing Must-Have features** | No features extracted | Exit with error: "No Must-Have features found - cannot generate task list" |
| **Output collision** | Files exist at target | Prompt: "Files exist. Overwrite? (use --force to skip)" |
| **Write permission denied** | OS permission error | Exit with error: "Cannot write to [path]: Permission denied" |

---

## Feature Development Quality Standards

### Testing Requirements
- Minimum 85% code coverage for new code
- 100% test pass rate required
- Unit tests for all business logic
- Integration tests for API endpoints

### Git Workflow Requirements
- Use conventional commit format
- Work on feature branches
- Never commit directly to main

### Feature Completion Checklist
- [ ] All tests passing
- [ ] Coverage meets threshold
- [ ] Documentation updated
- [ ] @fix_plan.md task marked complete
