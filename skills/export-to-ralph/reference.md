# Export to Ralph - Transformation Reference

This document provides detailed transformation rules for converting specification documents (PRD, SDD, PLAN) to Ralph's expected format.

## File Mappings Overview

```
docs/specs/[NNN]-[name]/
├── product-requirements.md  ──┬──► PROMPT.md
├── solution-design.md       ──┼──► @fix_plan.md
└── implementation-plan.md   ──┴──► @AGENT.md
                                    specs/
```

---

## PROMPT.md Generation

### Source: PRD + SDD
### Target: Project root PROMPT.md

### Section Mappings

| PROMPT.md Section | Source Document | Source Section | Transformation |
|-------------------|-----------------|----------------|----------------|
| Overview | PRD | Vision | Direct copy |
| Problem & Context | PRD | Problem Statement | Direct copy |
| Objectives | PRD | Value Proposition | Convert to bullet list |
| Scope Boundaries | PRD + SDD | Won't Have + Implementation Boundaries | Merge, prefix with "Will NOT:" |
| Key Constraints | SDD + PRD | Constraints (both) | Merge, deduplicate |
| Assumptions | PRD | Assumptions | Direct copy as bullets |
| Success Criteria | PRD | Success Metrics > KPIs | Convert to pass/fail criteria |

### RALPH_STATUS Block

Always append this block at the end of PROMPT.md:

```markdown
---

## Status Reporting

At the end of your response, include:

---RALPH_STATUS---
STATUS: IN_PROGRESS | COMPLETE | BLOCKED
TASKS_COMPLETED_THIS_LOOP: <number>
FILES_MODIFIED: <number>
TESTS_STATUS: PASSING | FAILING | NOT_RUN
WORK_TYPE: IMPLEMENTATION | TESTING | DOCUMENTATION | REFACTORING
EXIT_SIGNAL: false | true
RECOMMENDATION: <one line summary>
---END_RALPH_STATUS---
```

---

## @fix_plan.md Generation

### Source: PLAN (primary) or PRD (fallback)
### Target: Project root @fix_plan.md

### Priority Mapping

| Source | Target Priority |
|--------|-----------------|
| PLAN Phase 1 | High Priority |
| PLAN Phase 2 | Medium Priority |
| PLAN Phase 3+ | Low Priority |
| PRD Must-Have (no PLAN) | High Priority |
| PRD Should-Have (no PLAN) | Medium Priority |
| PRD Could-Have (no PLAN) | Low Priority |

### Task Flattening Rules

**Input (PLAN format):**
```markdown
- [ ] **T1.1 Payment Entity** `[activity: domain-modeling]`
  - Prime: Read payment interface contracts `[ref: SDD/Section 4.2]`
  - Test: Validation rejects negative amounts
  - Implement: Create `src/domain/Payment.ts`
  - Validate: Unit tests pass
  - Success: Works correctly `[ref: PRD/AC-1.1]`
```

**Output (@fix_plan.md format):**
```markdown
- [ ] T1.1: Create Payment entity with validation (src/domain/Payment.ts) [ref: PRD/AC-1.1]
```

### Extraction Rules

1. **Task ID**: Extract from `**T\d+\.\d+` pattern
2. **Task Name**: Extract text after task ID, before `**`
3. **File Path**: Extract from Implement line, look for backticks or "Create" keyword
4. **Test Summary**: Extract key behavior from Test line
5. **PRD Reference**: Preserve `[ref: PRD/AC-X.Y]` tags

### Metadata Preservation

| PLAN Metadata | @fix_plan.md Handling |
|---------------|----------------------|
| `[ref: PRD/AC-X.Y]` | Preserve as inline comment |
| `[parallel: true]` | Add to Notes section |
| `[component: name]` | Add to Notes section |
| `[activity: type]` | Omit (used for agent selection) |

### Notes Section

Add notes for:
- Tasks marked `[parallel: true]`: "T2.1 and T2.2 can run in parallel"
- Component groupings: "Backend component: T2.1, T2.3"
- Critical dependencies: "T2.4 requires T2.1 completion"

---

## @AGENT.md Generation

### Source: SDD
### Target: Project root @AGENT.md

### Section Mappings

| @AGENT.md Section | SDD Section | Extraction |
|-------------------|-------------|------------|
| Install | Project Commands > Install | Exact command |
| Dev | Project Commands > Dev | Exact command |
| Test | Project Commands > Test | Exact command |
| Build | Project Commands > Build | Exact command |
| Architecture Pattern | Solution Strategy | First paragraph |
| Key Files | Directory Map | Extract paths with NEW/MODIFY |
| Integration Points | Integration Points | Format as list |
| Quality Requirements | Quality Requirements | Copy table |
| Decision Rationale | Architecture Decisions | ADR name + rationale |
| Error Handling | Runtime View > Error Handling | Copy error patterns |

### Command Extraction

Look for bash code blocks in SDD Project Commands section:

```bash
Install: [command]
Dev:     [command]
Test:    [command]
Build:   [command]
```

If missing, generate placeholder:
```bash
# TODO: Add [section] command
echo "No [section] command configured"
```

### Key Files Format

**Input (SDD Directory Map):**
```
src/
├── payments/
│   ├── controllers/
│   │   └── PaymentController.ts  # NEW: REST API endpoints
│   └── services/
│       └── PaymentService.ts     # MODIFY: Add retry logic
```

**Output (@AGENT.md):**
```markdown
### Key Files
- `src/payments/controllers/PaymentController.ts` - NEW: REST API endpoints
- `src/payments/services/PaymentService.ts` - MODIFY: Add retry logic
```

---

## specs/ Directory Generation

### Source: PRD (acceptance criteria) + SDD (scenarios)
### Target: Project root specs/

### Directory Structure

```
specs/
├── features/
│   ├── [feature-1-name].md
│   └── [feature-2-name].md
├── scenarios/
│   ├── error-handling.md
│   └── edge-cases.md
└── interfaces/
    └── api.md
```

### EARS to Gherkin Conversion

| EARS Pattern | Example | Gherkin Output |
|--------------|---------|----------------|
| EVENT-DRIVEN | `WHEN user submits, THE SYSTEM SHALL validate` | `Given system ready`<br>`When user submits`<br>`Then system validates` |
| UBIQUITOUS | `THE SYSTEM SHALL encrypt data` | `Then system encrypts data` |
| STATE-DRIVEN | `WHILE processing, THE SYSTEM SHALL show spinner` | `Given system is processing`<br>`Then spinner is shown` |
| OPTIONAL | `WHERE feature enabled, THE SYSTEM SHALL log` | `Given feature is enabled`<br>`Then system logs` |
| COMPLEX | `IF amount > 1000, THEN require approval` | `Given amount exceeds 1000`<br>`Then approval is required` |

### Regex Patterns

```python
# EVENT-DRIVEN: WHEN X, THE SYSTEM SHALL Y
r'WHEN\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)'

# COMPLEX: IF X, THEN THE SYSTEM SHALL Y
r'IF\s+(.+?),\s*THEN THE SYSTEM SHALL\s+(.+)'

# UBIQUITOUS: THE SYSTEM SHALL X
r'THE SYSTEM SHALL\s+(.+)'

# STATE-DRIVEN: WHILE X, THE SYSTEM SHALL Y
r'WHILE\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)'

# OPTIONAL: WHERE X, THE SYSTEM SHALL Y
r'WHERE\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)'
```

### Feature File Template

```markdown
# Feature: [Feature Name]

**User Story:** [From PRD user story]

## Scenario: [AC-X.Y Name]

```gherkin
Given [precondition]
When [trigger action]
Then [expected outcome]
And [additional verification]
```

**Original EARS:** [Original criterion text]

---

## Scenario: [AC-X.Y+1 Name]
...
```

---

## Validation Rules

### Blocking Conditions

Export MUST fail if:

1. **[NEEDS CLARIFICATION] markers exist**
   - Regex: `\[NEEDS CLARIFICATION[^\]]*\]`
   - Error: List all locations

2. **PRD has no Must-Have features**
   - Check: `### Must Have Features` section exists and has content
   - Error: "No Must-Have features found"

3. **PLAN has no Phase 1 tasks (if PLAN exists)**
   - Check: `### Phase 1:` section has task items
   - Error: "PLAN Phase 1 is empty"

### Warning Conditions

Export proceeds with warnings if:

1. **SDD missing**
   - Warning: "SDD not found - @AGENT.md will have minimal config"
   - Action: Generate placeholder @AGENT.md

2. **PLAN missing**
   - Warning: "PLAN not found - using PRD features for task list"
   - Action: Generate @fix_plan.md from PRD features

3. **Optional sections empty**
   - Warning: "[Section] empty - corresponding output may be incomplete"

---

## Output File Locations

| File | Location | Collision Handling |
|------|----------|-------------------|
| PROMPT.md | `{output_dir}/PROMPT.md` | Prompt or --force |
| @fix_plan.md | `{output_dir}/@fix_plan.md` | Prompt or --force |
| @AGENT.md | `{output_dir}/@AGENT.md` | Prompt or --force |
| specs/ | `{output_dir}/specs/` | Merge or --force |

Default `output_dir`: Project root (current working directory)

---

## Examples

### Complete PRD Feature → specs/features/

**PRD Input:**
```markdown
#### Feature 1: User Authentication

- **User Story:** As a user, I want to log in securely so that my data is protected

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN the user submits valid credentials, THE SYSTEM SHALL redirect to dashboard within 2 seconds
  - [ ] IF the password is incorrect 3 times, THEN THE SYSTEM SHALL lock the account
  - [ ] THE SYSTEM SHALL encrypt all passwords using bcrypt
```

**specs/features/user-authentication.md Output:**
```markdown
# Feature: User Authentication

**User Story:** As a user, I want to log in securely so that my data is protected

## Scenario: AC-1.1 Valid Login Redirect

```gherkin
Given the login page is displayed
And the system is ready
When the user submits valid credentials
Then the system redirects to dashboard within 2 seconds
```

**Original EARS:** WHEN the user submits valid credentials, THE SYSTEM SHALL redirect to dashboard within 2 seconds

---

## Scenario: AC-1.2 Account Lockout

```gherkin
Given the user has entered incorrect password
And the incorrect attempt count is 3
When the system processes the login attempt
Then the account is locked
```

**Original EARS:** IF the password is incorrect 3 times, THEN THE SYSTEM SHALL lock the account

---

## Scenario: AC-1.3 Password Encryption

```gherkin
Given a password is provided
When the system stores the password
Then the password is encrypted using bcrypt
```

**Original EARS:** THE SYSTEM SHALL encrypt all passwords using bcrypt
```
