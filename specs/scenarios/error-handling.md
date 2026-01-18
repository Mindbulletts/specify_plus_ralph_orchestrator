# Error Handling Scenarios

Based on SDD error handling patterns.

```
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
```