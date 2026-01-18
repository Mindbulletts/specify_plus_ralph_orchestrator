# {project_name}

## Overview

{vision}

## Problem & Context

{problem_statement}

## Objectives

{value_proposition}

## Scope Boundaries

**In Scope:**
{in_scope}

**Out of Scope:**
{out_of_scope}

## Key Constraints

{constraints}

## Assumptions

{assumptions}

## Success Criteria

{success_criteria}

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
