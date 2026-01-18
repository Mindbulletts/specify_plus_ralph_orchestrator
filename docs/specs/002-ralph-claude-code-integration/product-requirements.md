---
title: "Ralph Claude Code Integration"
status: draft
version: "1.0"
---

# Product Requirements Document

## Validation Checklist

### CRITICAL GATES (Must Pass)

- [x] All required sections are complete
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Problem statement is specific and measurable
- [x] Every feature has testable acceptance criteria (EARS format)
- [x] No contradictions between sections

### QUALITY CHECKS (Should Pass)

- [x] Problem is validated by evidence (not assumptions)
- [x] Context → Problem → Solution flow makes sense
- [x] Every persona has at least one user journey
- [x] All MoSCoW categories addressed (Must/Should/Could/Won't)
- [x] Every metric has corresponding tracking events
- [x] No feature redundancy (check for duplicates)
- [x] No technical implementation details included
- [x] A new team member could understand this PRD

---

## Product Overview

### Vision

Enable developers to create structured specifications (PRD/SDD/PLAN) using `/start:specify` that can be directly consumed by Ralph's autonomous AI orchestration loop for hands-off implementation.

### Problem Statement

Developers using Claude Code for AI-assisted development face two disconnected workflows:

1. **Specification Creation**: Using `/start:specify` to create structured PRD, SDD, and PLAN documents
2. **Autonomous Execution**: Using Ralph to run iterative Claude Code sessions

Currently, there is no bridge between these systems. Ralph expects specific file formats (PROMPT.md, @fix_plan.md, @AGENT.md, specs/) that don't match the output of the specification workflow (product-requirements.md, solution-design.md, implementation-plan.md). This forces developers to:

- Manually translate specifications into Ralph's format
- Lose traceability between requirements and implementation
- Duplicate effort describing the same feature in two formats
- Risk specification drift during manual translation

**Impact**: Developers spend 30-60 minutes per feature manually converting specifications, with no guarantee of accurate translation.

### Value Proposition

An integrated workflow that:

1. **Eliminates manual translation**: Specifications created with `/start:specify` are automatically consumable by Ralph
2. **Maintains traceability**: Every Ralph task traces back to PRD acceptance criteria
3. **Preserves context**: Architecture decisions from SDD inform Ralph's implementation
4. **Enables hands-off execution**: Single command transitions from completed specification to autonomous implementation

## User Personas

### Primary Persona: Solo Technical Founder

- **Demographics:** Age 28-40, strong technical background, wearing all hats (product, engineering, operations)
- **Goals:** Maximize output velocity; ship features faster than traditionally possible solo; maintain quality without dedicated QA; reduce context switching between product thinking and implementation
- **Pain Points:** Scope creep during AI sessions; context loss between sessions; no systematic requirement capture leading to late-discovered edge cases; decision fatigue from constant architecture choices mid-implementation

### Secondary Persona: Staff Engineer at Mid-Size Company

- **Demographics:** Age 32-50, 10+ years engineering experience, manages 2-3 engineers
- **Goals:** Scale team output without proportional hiring; ensure AI-generated code follows established patterns; reduce code review burden; capture knowledge from AI-assisted development
- **Pain Points:** AI ignores existing codebase patterns; architecture decisions made during AI sessions are lost; AI-generated code requires 2-3x review time; no standards enforcement

### Tertiary Persona: Product Manager at AI-Forward Startup

- **Demographics:** Age 30-45, non-technical but technically literate, owns product roadmap
- **Goals:** Bridge product-engineering gap; ensure engineers build exactly what users need; accelerate roadmap delivery; maintain product vision across AI-generated implementations
- **Pain Points:** Specification-to-code translation loss; no visibility into AI implementation progress; PRD format incompatible with AI consumption; difficult to verify AI-generated code meets acceptance criteria

## User Journey Maps

### Primary User Journey: Specification-to-Autonomous-Implementation

1. **Awareness:** Developer realizes they have a feature to implement that would benefit from structured specification followed by autonomous AI execution
2. **Consideration:** Developer evaluates whether to use integrated workflow vs. manual specification + manual Ralph setup vs. direct Claude Code iteration
3. **Adoption:** Developer runs `/start:specify "feature description"` knowing it will produce Ralph-compatible output
4. **Usage:**
   - Complete PRD phase (define WHAT and WHY)
   - Complete SDD phase (define HOW)
   - Complete PLAN phase (define execution sequence)
   - Run single command to hand off to Ralph: `ralph start --spec 002-feature-name`
   - Monitor autonomous implementation progress
   - Review and merge completed implementation
5. **Retention:** Developer uses integrated workflow for all medium-to-large features; builds library of reusable specifications

### Secondary User Journey: Existing Ralph User Adopting Specifications

1. **Awareness:** Ralph user discovers `/start:specify` creates compatible specifications
2. **Consideration:** Evaluates if structured specification improves Ralph's output quality
3. **Adoption:** Uses `/start:specify` for next feature instead of manual PROMPT.md creation
4. **Usage:**
   - Experiences guided requirement gathering
   - Appreciates automatic priority mapping
   - Values acceptance criteria → task traceability
5. **Retention:** Standardizes on specification-first workflow for complex features

## Feature Requirements

### Must Have Features

#### Feature 1: Specification Export to Ralph Format

- **User Story:** As a developer who has completed a specification, I want to export it to Ralph's expected format so that I can run autonomous implementation without manual translation

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN a user runs export command on a completed specification, THE SYSTEM SHALL generate PROMPT.md containing project vision, objectives, scope boundaries, and constraints from PRD
  - [ ] WHEN exporting, THE SYSTEM SHALL generate @fix_plan.md with PRD Must-Have features as High Priority items, Should-Have as Medium, and Could-Have as Low Priority
  - [ ] WHEN exporting, THE SYSTEM SHALL generate @AGENT.md with build/test commands from SDD Project Commands section
  - [ ] WHEN exporting, THE SYSTEM SHALL generate specs/ directory with feature specifications derived from PRD acceptance criteria and SDD acceptance scenarios
  - [ ] IF the specification is incomplete (has [NEEDS CLARIFICATION] markers), THEN THE SYSTEM SHALL refuse export and list incomplete sections
  - [ ] WHEN export completes successfully, THE SYSTEM SHALL display the path to exported files and the command to start Ralph

#### Feature 2: PLAN-to-Fix-Plan Task Mapping

- **User Story:** As a developer, I want my PLAN tasks to become Ralph @fix_plan.md items so that Ralph implements exactly what I specified

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN converting PLAN tasks, THE SYSTEM SHALL transform each task (T1.1, T2.1, etc.) into a checkbox item (`- [ ] description`)
  - [ ] WHEN converting, THE SYSTEM SHALL strip TDD metadata (Prime/Test/Implement/Validate structure) into a single action description
  - [ ] WHEN converting, THE SYSTEM SHALL preserve task references (`[ref: PRD/AC-1.1]`) as inline notes
  - [ ] WHEN converting, THE SYSTEM SHALL group Phase 1 tasks as High Priority, Phase 2 as Medium, Phase 3 as Low Priority
  - [ ] WHEN converting parallel tasks (`[parallel: true]`), THE SYSTEM SHALL add a note indicating parallelization opportunity

#### Feature 3: Acceptance Criteria to Gherkin Conversion

- **User Story:** As a developer, I want my EARS-format acceptance criteria converted to Gherkin scenarios so that Ralph's specs directory is properly structured

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN converting EARS EVENT-DRIVEN criteria (`WHEN X, THE SYSTEM SHALL Y`), THE SYSTEM SHALL produce `When X, Then Y` Gherkin format
  - [ ] WHEN converting EARS UBIQUITOUS criteria (`THE SYSTEM SHALL X`), THE SYSTEM SHALL produce `Then X` without trigger condition
  - [ ] WHEN converting EARS COMPLEX criteria (`IF X, THEN THE SYSTEM SHALL Y`), THE SYSTEM SHALL produce `Given X, Then Y` format
  - [ ] WHEN converting, THE SYSTEM SHALL group related criteria into Scenario blocks with descriptive names
  - [ ] THE SYSTEM SHALL preserve original EARS criterion as comment above each converted scenario for traceability

### Should Have Features

#### Feature 4: Ralph Project Initialization

- **User Story:** As a developer starting a new Ralph project, I want to clone ralph-claude-code and set up my project directory so that I'm ready to use the integrated workflow

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN user runs initialization command, THE SYSTEM SHALL clone ralph-claude-code repository to specified location
  - [ ] WHEN initializing, THE SYSTEM SHALL install Ralph scripts to ~/.ralph/ if not already present
  - [ ] WHEN initializing, THE SYSTEM SHALL create project structure with required directories (specs/, src/, logs/)
  - [ ] WHEN initialization completes, THE SYSTEM SHALL verify Ralph is operational by running `ralph --version`
  - [ ] IF Ralph is already installed, THEN THE SYSTEM SHALL skip installation and report existing version

#### Feature 5: Bidirectional Traceability Report

- **User Story:** As a developer reviewing implementation, I want to see which PRD acceptance criteria map to which Ralph tasks so that I can verify complete coverage

- **Acceptance Criteria (EARS Format):**
  - [ ] WHEN user runs traceability report, THE SYSTEM SHALL display matrix of PRD acceptance criteria vs @fix_plan.md tasks
  - [ ] THE SYSTEM SHALL highlight acceptance criteria with no corresponding tasks
  - [ ] THE SYSTEM SHALL highlight tasks with no acceptance criteria reference
  - [ ] WHEN displaying matrix, THE SYSTEM SHALL show task completion status from @fix_plan.md checkboxes
  - [ ] WHEN exporting report, THE SYSTEM SHALL generate markdown file in spec directory

### Could Have Features

#### Feature 6: Real-Time Progress Sync

- **User Story:** As a developer monitoring Ralph execution, I want to see PLAN tasks update in real-time so that I know which specification items are complete

- **Acceptance Criteria (EARS Format):**
  - [ ] WHILE Ralph is executing, THE SYSTEM SHALL monitor @fix_plan.md for checkbox changes
  - [ ] WHEN a @fix_plan.md item is checked, THE SYSTEM SHALL update corresponding PLAN task status
  - [ ] WHEN progress changes, THE SYSTEM SHALL update implementation-plan.md in spec directory
  - [ ] THE SYSTEM SHALL display completion percentage based on checked vs total tasks

#### Feature 7: Constitution Enforcement During Export

- **User Story:** As a staff engineer, I want the export to validate against my project's CONSTITUTION.md so that generated Ralph files follow our standards

- **Acceptance Criteria (EARS Format):**
  - [ ] IF CONSTITUTION.md exists in project root, THEN THE SYSTEM SHALL validate exported files against L1/L2 rules
  - [ ] WHEN validation fails, THE SYSTEM SHALL display specific rule violations
  - [ ] WHERE constitution validation is enabled, THE SYSTEM SHALL add quality standards from constitution to @AGENT.md

### Won't Have (This Phase)

- **Ralph execution monitoring dashboard**: Out of scope; use Ralph's built-in `ralph-monitor` command
- **Automatic specification updates from implementation**: Would require reverse-engineering implementation changes
- **Multi-specification orchestration**: Running multiple specs in parallel with Ralph; focus on single-spec workflow first
- **Ralph installation automation for all platforms**: Initial focus on environments where Ralph is already functional
- **IDE integration**: Focus on CLI workflow; IDE plugins are future consideration

## Detailed Feature Specifications

### Feature: Specification Export to Ralph Format

**Description:** This is the core integration feature that transforms completed specifications from the `/start:specify` workflow into files consumable by Ralph's autonomous execution loop. The export reads all three specification documents (PRD, SDD, PLAN) and generates four Ralph-compatible files (PROMPT.md, @fix_plan.md, @AGENT.md, specs/).

**User Flow:**
1. User completes specification using `/start:specify` workflow
2. User runs `/start:export-to-ralph 002-feature-name` or equivalent command
3. System validates specification completeness
4. System reads product-requirements.md, solution-design.md, implementation-plan.md
5. System transforms content according to mapping rules
6. System writes PROMPT.md, @fix_plan.md, @AGENT.md, specs/ to target directory
7. System displays success message with next steps

**Business Rules:**
- Rule 1: Export SHALL fail if any specification document contains `[NEEDS CLARIFICATION]` markers
- Rule 2: Export SHALL fail if implementation-plan.md is missing or empty
- Rule 3: PROMPT.md SHALL include Ralph's required RALPH_STATUS block template at the end
- Rule 4: @fix_plan.md SHALL have at least one item in High Priority section
- Rule 5: @AGENT.md SHALL include all commands from SDD Project Commands section
- Rule 6: specs/ files SHALL use Three Amigos format with Gherkin scenarios

**Edge Cases:**
- Scenario 1: User attempts export before SDD is complete → Expected: Warn user that SDD provides build commands; offer to export with placeholder @AGENT.md
- Scenario 2: PRD has no Must-Have features → Expected: Error with message "No Must-Have features found; at least one is required for Ralph task list"
- Scenario 3: Target directory already contains Ralph files → Expected: Prompt user to confirm overwrite or specify different directory
- Scenario 4: PLAN has no phases → Expected: Error with message "Implementation plan has no phases; cannot generate fix_plan.md"

## Success Metrics

### Key Performance Indicators

- **Adoption:** 80% of specifications completed with `/start:specify` are exported to Ralph within one week of completion
- **Engagement:** Average of 3+ specification-to-Ralph exports per active user per month
- **Quality:** 95% of exported specifications result in successful Ralph execution (no early circuit breaker trips)
- **Business Impact:** 50% reduction in time-to-first-commit for features using integrated workflow vs. manual translation

### Tracking Requirements

| Event | Properties | Purpose |
|-------|------------|---------|
| export_initiated | spec_id, spec_name, documents_present[] | Track which specs are exported |
| export_completed | spec_id, duration_ms, files_generated[] | Measure export success and performance |
| export_failed | spec_id, failure_reason, incomplete_sections[] | Identify common failure patterns |
| ralph_started_from_export | spec_id, ralph_version | Track adoption of integrated workflow |
| ralph_completed_from_export | spec_id, tasks_completed, tasks_total, duration_minutes | Measure end-to-end success |

---

## Constraints and Assumptions

### Constraints
- Ralph repository (frankbria/ralph-claude-code) must remain accessible for initial setup
- Users must have Claude Code CLI installed and configured
- Export targets local filesystem (no cloud/remote export in this phase)
- Windows, macOS, and Linux must all be supported for export functionality

### Assumptions
- Users are familiar with the `/start:specify` workflow and have completed at least one specification
- Ralph's file format expectations (PROMPT.md, @fix_plan.md, @AGENT.md, specs/) will remain stable
- Users have git installed for Ralph repository cloning
- Claude Code CLI version is compatible with Ralph's expected command syntax

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Ralph file format changes | High | Low | Version-lock Ralph integration; monitor upstream for breaking changes |
| Incomplete mapping loses specification detail | Medium | Medium | Comprehensive test coverage; user review of exported files before Ralph execution |
| Export performance slow for large specifications | Low | Low | Implement streaming writes; provide progress indicators |
| Users expect real-time Ralph monitoring | Medium | Medium | Clear documentation that monitoring uses Ralph's built-in tools |
| Specification drift after export | Medium | High | Add warning when specs modified after export; suggest re-export |

## Open Questions

- [x] What is Ralph's exact expected file format? → Documented in research findings
- [x] How does ralph-import work and can we leverage it? → It uses Claude to convert; we'll do direct mapping
- [x] Should export be a new skill or extend existing specification-management skill? → **New skill: `start:export-to-ralph`** - dedicated skill focused on Ralph integration
- [x] What is the preferred target directory for exported Ralph files? → **Project root** - simplest and most direct for Ralph workflow integration
- [x] Should we support partial exports? → **Yes, allow partial exports** with warnings about missing sections

---

## Supporting Research

### Competitive Analysis

**Direct Alternative: ralph-import command**
- Strengths: Already exists; converts any PRD format to Ralph structure
- Weaknesses: Requires Claude API call for conversion; less predictable output; no guarantee of structure preservation
- Learning: Our integration should be deterministic transformation, not AI-mediated conversion

**Alternative Workflow: Manual Translation**
- Current state for most users
- Time cost: 30-60 minutes per feature
- Error-prone: Format details easily missed
- No traceability maintained

### User Research

Based on persona analysis and workflow examination:
- Solo founders value time multiplication above all
- Staff engineers prioritize pattern compliance and review efficiency
- Product managers need visibility into specification-to-implementation mapping
- All personas cite "context loss" as major pain point

### Market Data

- Claude Code adoption growing rapidly in developer community
- Autonomous AI development tools (like Ralph) emerging as next evolution
- Specification-driven development regaining interest as AI makes implementation cheaper
- Integration between planning tools and execution tools identified as gap by multiple tool creators
