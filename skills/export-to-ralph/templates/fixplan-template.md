# {project_name} Fix Plan

## High Priority

{high_priority_tasks}

## Medium Priority

{medium_priority_tasks}

## Low Priority

{low_priority_tasks}

## Completed

{completed_tasks}

## Notes

### Parallelization
{parallel_notes}

### Dependencies
{dependency_notes}

### Traceability
{traceability_notes}

---

**Task Format:** `- [ ] TX.Y: Description (file_path) [ref: PRD/AC-X.Y]`

**Priority Guidelines:**
- High: Core functionality, blocking dependencies (Phase 1)
- Medium: Important features, non-blocking (Phase 2)
- Low: Nice-to-haves, optimizations (Phase 3+)

**Marking Complete:** Change `- [ ]` to `- [x]` when task is done

**Ralph Integration:**
- Ralph tracks task completion via checkbox state
- EXIT_SIGNAL should be `true` only when ALL tasks are `[x]`
- Use `[ref: PRD/AC-X.Y]` to trace back to requirements
