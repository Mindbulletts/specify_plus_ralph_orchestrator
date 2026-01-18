# Ralph Claude Code Integration Fix Plan

## High Priority

- [ ] T1.1: Create Skill Directory Structure with Directory structure matches SDD specification (`skills/export-to-ralph/`)
- [ ] T1.2: Create SKILL.md Definition with SKILL.md has required frontmatter (name, description, allowed-tools) (`skills/export-to-ralph/SKILL.md`)
- [ ] T1.3: Create Reference Documentation with Reference.md documents all transformation rules (`skills/export-to-ralph/reference.md`)
- [ ] T1.4: Create Ralph File Templates with Templates produce valid Ralph files (`templates/prompt-template.md`,) [ref: PRD/AC-1.1]
- [ ] T1.5: Phase Validation

## Medium Priority

- [ ] T2.1: Create Script Skeleton with CLI with CLI parses arguments correctly; --help works; --dry-run flag recognized (`export.py`)
- [ ] T2.2: Implement Spec Resolution and Validation with Resolves spec ID to directory; detects missing documents; finds [NEEDS CLARIFICATION] markers [ref: PRD/AC-1.2]
- [ ] T2.3: Implement Document Readers with Extracts all required sections from each document type
- [ ] T2.4: Implement PROMPT.md Transformer with Generates valid PROMPT.md with all sections; includes RALPH_STATUS block [ref: PRD/AC-1.1]
- [ ] T2.5: Implement @fix_plan.md Transformer with Generates checkbox items; groups by priority; flattens PLAN tasks [ref: PRD/AC-2.1]
- [ ] T2.6: Implement @AGENT.md Transformer with Extracts commands from SDD; includes architecture notes; adds quality requirements [ref: PRD/AC-1.1]
- [ ] T2.7: Implement specs/ Generator with Creates feature files; converts EARS to Gherkin; creates scenario files [ref: PRD/AC-3.1]
- [ ] T2.8: Implement File Writer with Collision Handling with Creates files; prompts on collision (unless --force); respects --dry-run
- [ ] T2.9: Phase Validation

## Low Priority

- [ ] T3.1: End-to-End Export Test with Export complete spec 002; verify all four output files created [ref: PRD/AC-1.1]
- [ ] T3.2: Partial Export Test with Export with missing SDD produces warnings but completes [ref: PRD/AC-1.3]
- [ ] T3.3: Error Handling Test with Invalid spec ID returns error; [NEEDS CLARIFICATION] blocks export [ref: PRD/AC-1.2]
- [ ] T3.4: Cross-Platform Validation with Script runs on Windows paths; uses Path objects throughout
- [ ] T3.5: Quality Gates
- [ ] T3.6: Specification Compliance

## Completed

- [x] Project initialization

## Notes

- T2.4 can run in parallel
- T2.5 can run in parallel
- T2.6 can run in parallel
- T2.7 can run in parallel

---

**Task Format:** `- [ ] TX.Y: Description (file_path) [ref: PRD/AC-X.Y]`

**Priority Guidelines:**
- High: Core functionality, blocking dependencies
- Medium: Important features, non-blocking
- Low: Nice-to-haves, optimizations

**Marking Complete:** Change `- [ ]` to `- [x]` when task is done
