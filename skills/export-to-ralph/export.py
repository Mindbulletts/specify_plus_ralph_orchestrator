#!/usr/bin/env python3
"""
Export to Ralph - Specification to Ralph Format Converter

Exports completed PRD/SDD/PLAN specifications for Ralph execution. Assumes the
project already has an established Ralph structure (PROMPT.md, @AGENT.md, etc.).

What this script does:
- Copies PRD/SDD/PLAN to specs/new-features/
- Creates @fix_plan.md with prioritized tasks from the implementation plan
- Updates PROMPT.md "Current Focus" line (line 16)
- Deletes source docs/specs/NNN-*/ after successful conversion

What this script does NOT do:
- Create new PROMPT.md (use existing, customized version)
- Create new @AGENT.md (use existing, customized version)
- Create specs/requirements.md or specs/features/ (use project-overview.md)

Usage:
    python export.py <spec-id> [--output-dir DIR] [--dry-run] [--force] [--no-cleanup]

Examples:
    python export.py 002
    python export.py 002 --dry-run
    python export.py 002 --output-dir /path/to/project --force
    python export.py 002 --no-cleanup  # Keep source docs/specs/NNN-*/
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# =============================================================================
# Configuration
# =============================================================================

SPECS_DIR = Path("docs/specs")
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Target paths in project
NEW_FEATURES_DIR = Path("specs/new-features")
FIX_PLAN_FILE = Path("@fix_plan.md")
PROMPT_FILE = Path("PROMPT.md")

# Regex patterns
NEEDS_CLARIFICATION_PATTERN = re.compile(r'\[NEEDS CLARIFICATION[^\]]*\]', re.IGNORECASE)
CURRENT_FOCUS_PATTERN = re.compile(r'^(\*\*Current Focus:\*\*)\s*.*$', re.MULTILINE)


# =============================================================================
# CLI Interface
# =============================================================================

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Export specification to Ralph format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python export.py 002                    # Export spec 002 to current directory
    python export.py 002 --dry-run          # Show what would be created
    python export.py 002 --output-dir ./    # Export to specific directory
    python export.py 002 --force            # Overwrite existing files
    python export.py 002 --no-cleanup       # Keep source docs/specs/NNN-*/
        """
    )
    parser.add_argument(
        "spec",
        help="Spec ID (e.g., '002') or full path to spec directory"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory for Ralph files (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't delete source docs/specs/NNN-*/ after conversion"
    )
    return parser.parse_args()


# =============================================================================
# Spec Resolution and Validation
# =============================================================================

def resolve_spec_path(spec: str) -> Optional[Path]:
    """
    Resolve spec ID or path to actual spec directory.

    Args:
        spec: Spec ID (e.g., "002") or full path

    Returns:
        Path to spec directory or None if not found
    """
    # If it's already a path
    if os.path.isdir(spec):
        return Path(spec)

    # If it's a spec ID (3 digits), find matching directory
    if re.match(r'^\d{3}$', spec):
        if SPECS_DIR.exists():
            for dir_path in SPECS_DIR.iterdir():
                if dir_path.is_dir() and dir_path.name.startswith(f"{spec}-"):
                    return dir_path

    # Try as direct path
    spec_path = Path(spec)
    if spec_path.exists() and spec_path.is_dir():
        return spec_path

    return None


def find_clarification_markers(content: str) -> List[str]:
    """
    Find all [NEEDS CLARIFICATION] markers in content.

    Excludes markers that are:
    - In code blocks (backticks)
    - In validation checklist items
    - In documentation describing the marker itself
    - In Gherkin scenarios, Mermaid diagrams, or table cells
    """
    markers = []

    # Split into lines for context-aware checking
    lines = content.split('\n')
    in_code_block = False

    for i, line in enumerate(lines):
        # Track code block state
        if '```' in line:
            in_code_block = not in_code_block
            continue

        # Skip if inside a code block
        if in_code_block:
            continue

        # Skip inline code (backticks)
        if line.strip().startswith('`'):
            continue

        # Skip validation checklist lines
        if '- [x]' in line.lower() or '- [ ]' in line.lower():
            if any(kw in line.lower() for kw in ['no [needs clarification]', 'markers', 'addressed']):
                continue

        # Skip documentation lines describing the marker
        doc_keywords = [
            'exit with error', 'blocks export', 'detects', 'finds',
            'check for', 'regex', 'rule 1:', 'rule 2:', 'export shall',
            'script checks', 'error detection', 'caught', 'markers block'
        ]
        if any(kw in line.lower() for kw in doc_keywords):
            continue

        # Skip lines where marker is immediately followed by "markers" (meta-documentation)
        if '[needs clarification] markers' in line.lower():
            continue

        # Skip Gherkin scenario lines
        gherkin_prefixes = ['given:', 'when:', 'then:', 'and:', 'but:']
        stripped = line.strip().lower()
        if any(stripped.startswith(prefix) for prefix in gherkin_prefixes):
            continue

        # Skip Mermaid diagram lines
        if '-->' in line or '-->>' in line:
            continue

        # Skip table cells (lines starting with |)
        if stripped.startswith('|'):
            continue

        # Skip numbered steps (e.g., "5. Script checks...")
        if re.match(r'^\s*\d+\.', line):
            continue

        # Find actual markers on this line
        found = NEEDS_CLARIFICATION_PATTERN.findall(line)
        for marker in found:
            # Skip if marker is in backticks (inline code)
            if f'`{marker}`' in line or '`[NEEDS CLARIFICATION' in line:
                continue
            markers.append(marker)

    return markers


def validate_spec(spec_dir: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate specification for export readiness.

    Args:
        spec_dir: Path to specification directory

    Returns:
        Tuple of (can_proceed, blocking_errors, warnings)
    """
    errors = []
    warnings = []

    prd_path = spec_dir / "product-requirements.md"
    sdd_path = spec_dir / "solution-design.md"
    plan_path = spec_dir / "implementation-plan.md"

    # Check PRD exists (required)
    if not prd_path.exists():
        errors.append(f"PRD not found: {prd_path}")
    else:
        prd_content = prd_path.read_text(encoding='utf-8')

        # Check for clarification markers
        markers = find_clarification_markers(prd_content)
        if markers:
            errors.append(f"PRD has {len(markers)} [NEEDS CLARIFICATION] markers")

        # Check for Must-Have features
        if "### Must Have Features" not in prd_content and "### Must Have" not in prd_content:
            errors.append("PRD has no Must-Have features section")

    # Check SDD (optional but recommended)
    if not sdd_path.exists():
        warnings.append("SDD not found - specs/new-features/ will be incomplete")
    else:
        sdd_content = sdd_path.read_text(encoding='utf-8')
        markers = find_clarification_markers(sdd_content)
        if markers:
            errors.append(f"SDD has {len(markers)} [NEEDS CLARIFICATION] markers")

    # Check PLAN (required for task list)
    if not plan_path.exists():
        errors.append("PLAN not found - required for @fix_plan.md generation")
    else:
        plan_content = plan_path.read_text(encoding='utf-8')
        markers = find_clarification_markers(plan_content)
        if markers:
            errors.append(f"PLAN has {len(markers)} [NEEDS CLARIFICATION] markers")

        # Check for Phase 1
        if "### Phase 1" not in plan_content:
            errors.append("PLAN has no Phase 1 section")

    can_proceed = len(errors) == 0
    return can_proceed, errors, warnings


def validate_project_structure(output_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validate that the target project has the expected Ralph structure.

    Args:
        output_dir: Path to project directory

    Returns:
        Tuple of (can_proceed, missing_items)
    """
    missing = []

    # Required files/directories for project-specific mode
    required = [
        (output_dir / "PROMPT.md", "PROMPT.md"),
        (output_dir / "@AGENT.md", "@AGENT.md"),
        (output_dir / "specs", "specs/"),
    ]

    for path, name in required:
        if not path.exists():
            missing.append(name)

    return len(missing) == 0, missing


# =============================================================================
# Document Readers
# =============================================================================

def read_prd(prd_path: Path) -> Dict:
    """
    Read and parse PRD document.

    Returns dict with extracted sections.
    """
    if not prd_path.exists():
        return {}

    content = prd_path.read_text(encoding='utf-8')

    def extract_subsection(header: str) -> str:
        """Extract content under a subsection header."""
        pattern = rf'###\s*{re.escape(header)}\s*\n(.*?)(?=\n###|\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    return {
        'title': extract_prd_title(content),
        'vision': extract_subsection("Vision"),
        'raw_content': content
    }


def extract_prd_title(content: str) -> str:
    """Extract title from PRD frontmatter or first heading."""
    # Try frontmatter
    match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', content)
    if match:
        return match.group(1).strip()

    # Try first H1
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return "Project"


def read_plan(plan_path: Path) -> Dict:
    """
    Read and parse PLAN document.

    Returns dict with extracted phases and tasks.
    """
    if not plan_path.exists():
        return {}

    content = plan_path.read_text(encoding='utf-8')

    def extract_phases() -> Dict[str, List[Dict]]:
        """Extract all phases and their tasks."""
        phases = {}

        # Find phase sections
        phase_pattern = r'###\s*Phase\s*(\d+)[:\s]*([^\n]*)\n(.*?)(?=###\s*Phase|\Z)'
        for match in re.finditer(phase_pattern, content, re.DOTALL):
            phase_num = match.group(1)
            phase_name = match.group(2).strip()
            phase_content = match.group(3)

            tasks = []

            # Find task blocks
            task_pattern = r'-\s*\[\s*[x ]?\s*\]\s*\*\*([^\*]+)\*\*([^\n]*)\n(.*?)(?=-\s*\[\s*[x ]?\s*\]\s*\*\*|\Z)'
            for task_match in re.finditer(task_pattern, phase_content, re.DOTALL):
                task_id_name = task_match.group(1).strip()
                task_meta = task_match.group(2).strip()
                task_body = task_match.group(3).strip()

                # Parse task ID and name
                id_match = re.match(r'(T\d+\.\d+)\s+(.+)', task_id_name)
                if id_match:
                    task_id = id_match.group(1)
                    task_name = id_match.group(2)
                else:
                    task_id = task_id_name
                    task_name = task_id_name

                # Extract metadata
                parallel = '[parallel: true]' in task_meta.lower()
                component_match = re.search(r'\[component:\s*([^\]]+)\]', task_meta, re.IGNORECASE)
                component = component_match.group(1) if component_match else None

                # Extract key lines
                implement_match = re.search(r'Implement:\s*(.+?)(?=\n|$)', task_body)
                test_match = re.search(r'Test:\s*(.+?)(?=\n|$)', task_body)
                success_match = re.search(r'Success:\s*(.+?)(?=\n|$)', task_body)

                # Extract file path from Implement line
                file_path = ""
                if implement_match:
                    impl_text = implement_match.group(1)
                    path_match = re.search(r'`([^`]+)`|Create\s+(\S+)', impl_text)
                    if path_match:
                        file_path = path_match.group(1) or path_match.group(2) or ""

                # Extract PRD reference
                ref_match = re.search(r'\[ref:\s*(PRD/AC-[\d\.]+)\]', task_body)
                prd_ref = ref_match.group(1) if ref_match else ""

                tasks.append({
                    'id': task_id,
                    'name': task_name,
                    'parallel': parallel,
                    'component': component,
                    'file_path': file_path,
                    'test_desc': test_match.group(1).strip() if test_match else "",
                    'success': success_match.group(1).strip() if success_match else "",
                    'prd_ref': prd_ref
                })

            phases[phase_num] = {
                'name': phase_name,
                'tasks': tasks
            }

        return phases

    return {
        'phases': extract_phases(),
        'raw_content': content
    }


# =============================================================================
# Transformers
# =============================================================================

def flatten_plan_task(task: Dict) -> str:
    """
    Flatten a PLAN task into a @fix_plan.md checkbox item.

    Input task dict with: id, name, file_path, test_desc, prd_ref
    Output: "- [ ] T1.1: Description (file_path) [ref: PRD/AC-X.Y]"
    """
    task_id = task.get('id', 'T?.?')
    task_name = task.get('name', 'Unknown')
    file_path = task.get('file_path', '')
    test_desc = task.get('test_desc', '')
    prd_ref = task.get('prd_ref', '')

    # Build description
    desc_parts = [task_name]
    if test_desc:
        desc_parts.append(f"with {test_desc}")

    description = ' '.join(desc_parts)

    # Add file path if present
    file_note = f" ({file_path})" if file_path else ""

    # Add PRD reference if present
    ref_note = f" [ref: {prd_ref}]" if prd_ref else ""

    return f"- [ ] {task_id}: {description}{file_note}{ref_note}"


def transform_fixplan(plan: Dict, project_name: str) -> str:
    """
    Transform PLAN into @fix_plan.md content.
    """
    template_path = TEMPLATES_DIR / "fixplan-template.md"
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        template = "# {project_name} Fix Plan\n\n## High Priority\n\n{high_priority_tasks}"

    high_tasks = []
    medium_tasks = []
    low_tasks = []
    parallel_notes = []
    dependency_notes = []
    traceability_notes = []

    if plan and plan.get('phases'):
        phases = plan['phases']

        # Track tasks with PRD refs for traceability
        prd_refs = {}

        # Phase 1 -> High
        if '1' in phases:
            phase_name = phases['1'].get('name', 'Phase 1')
            dependency_notes.append(f"- **Phase 1 ({phase_name})**: Must complete before Phase 2")
            for task in phases['1'].get('tasks', []):
                high_tasks.append(flatten_plan_task(task))
                if task.get('parallel'):
                    parallel_notes.append(f"- {task.get('id')} can run in parallel with other parallel tasks")
                if task.get('prd_ref'):
                    ref = task.get('prd_ref')
                    if ref not in prd_refs:
                        prd_refs[ref] = []
                    prd_refs[ref].append(task.get('id'))

        # Phase 2 -> Medium
        if '2' in phases:
            phase_name = phases['2'].get('name', 'Phase 2')
            dependency_notes.append(f"- **Phase 2 ({phase_name})**: Depends on Phase 1 completion")
            for task in phases['2'].get('tasks', []):
                medium_tasks.append(flatten_plan_task(task))
                if task.get('parallel'):
                    parallel_notes.append(f"- {task.get('id')} can run in parallel with other parallel tasks")
                if task.get('prd_ref'):
                    ref = task.get('prd_ref')
                    if ref not in prd_refs:
                        prd_refs[ref] = []
                    prd_refs[ref].append(task.get('id'))

        # Phase 3+ -> Low
        for phase_num in sorted(phases.keys()):
            if int(phase_num) >= 3:
                phase_name = phases[phase_num].get('name', f'Phase {phase_num}')
                dependency_notes.append(f"- **Phase {phase_num} ({phase_name})**: Lower priority, implement after core features")
                for task in phases[phase_num].get('tasks', []):
                    low_tasks.append(flatten_plan_task(task))
                    if task.get('prd_ref'):
                        ref = task.get('prd_ref')
                        if ref not in prd_refs:
                            prd_refs[ref] = []
                        prd_refs[ref].append(task.get('id'))

        # Build traceability notes
        for ref, task_ids in prd_refs.items():
            traceability_notes.append(f"- {ref} -> {', '.join(task_ids)}")

    # Format task lists
    high_str = '\n'.join(high_tasks) if high_tasks else "- [ ] No high priority tasks defined"
    medium_str = '\n'.join(medium_tasks) if medium_tasks else "- [ ] No medium priority tasks defined"
    low_str = '\n'.join(low_tasks) if low_tasks else "- [ ] No low priority tasks defined"

    parallel_str = '\n'.join(parallel_notes) if parallel_notes else "- No parallel tasks identified"
    dependency_str = '\n'.join(dependency_notes) if dependency_notes else "- Execute tasks in order listed"
    traceability_str = '\n'.join(traceability_notes) if traceability_notes else "- All tasks trace to PRD requirements"

    # Replace template placeholders
    result = template.replace('{project_name}', project_name)
    result = result.replace('{high_priority_tasks}', high_str)
    result = result.replace('{medium_priority_tasks}', medium_str)
    result = result.replace('{low_priority_tasks}', low_str)
    result = result.replace('{completed_tasks}', "- [x] Project initialization")
    result = result.replace('{parallel_notes}', parallel_str)
    result = result.replace('{dependency_notes}', dependency_str)
    result = result.replace('{traceability_notes}', traceability_str)
    # Legacy support for old template format
    result = result.replace('{notes}', dependency_str)

    return result


def update_prompt_current_focus(prompt_path: Path, feature_name: str, description: str) -> str:
    """
    Update the "Current Focus" line in PROMPT.md.

    Args:
        prompt_path: Path to PROMPT.md
        feature_name: Name of the new feature
        description: Brief description from PRD vision

    Returns:
        Updated content
    """
    if not prompt_path.exists():
        return ""

    content = prompt_path.read_text(encoding='utf-8')

    # Build new current focus line
    # Truncate description if too long
    if len(description) > 100:
        description = description[:97] + "..."

    new_focus = f"**Current Focus:** {feature_name} - {description}"

    # Replace the Current Focus line
    updated = CURRENT_FOCUS_PATTERN.sub(new_focus, content)

    return updated


# =============================================================================
# File Operations
# =============================================================================

def copy_spec_files(
    spec_dir: Path,
    output_dir: Path,
    dry_run: bool = False
) -> List[str]:
    """
    Copy PRD/SDD/PLAN to specs/new-features/.

    Returns list of copied files.
    """
    copied = []
    target_dir = output_dir / NEW_FEATURES_DIR

    files_to_copy = [
        "product-requirements.md",
        "solution-design.md",
        "implementation-plan.md"
    ]

    for filename in files_to_copy:
        src = spec_dir / filename
        dst = target_dir / filename

        if not src.exists():
            continue

        if dry_run:
            print(f"  [DRY RUN] Would copy: {src} -> {dst}")
            copied.append(filename)
            continue

        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(src, dst)
        copied.append(filename)
        print(f"  Copied: {filename}")

    return copied


def write_fixplan(
    output_dir: Path,
    content: str,
    dry_run: bool = False,
    force: bool = False
) -> bool:
    """
    Write @fix_plan.md to project root.

    Returns True if written successfully.
    """
    target = output_dir / FIX_PLAN_FILE

    if dry_run:
        print(f"  [DRY RUN] Would create: {target}")
        return True

    # Check for existing file
    if target.exists() and not force:
        response = input(f"  File exists: {target}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print(f"  Skipped: {target}")
            return False

    target.write_text(content, encoding='utf-8')
    print(f"  Created: {target}")
    return True


def update_prompt(
    output_dir: Path,
    feature_name: str,
    description: str,
    dry_run: bool = False
) -> bool:
    """
    Update PROMPT.md "Current Focus" line.

    Returns True if updated successfully.
    """
    prompt_path = output_dir / PROMPT_FILE

    if not prompt_path.exists():
        print(f"  Warning: {prompt_path} not found, skipping update")
        return False

    updated_content = update_prompt_current_focus(prompt_path, feature_name, description)

    if dry_run:
        print(f"  [DRY RUN] Would update Current Focus in: {prompt_path}")
        return True

    prompt_path.write_text(updated_content, encoding='utf-8')
    print(f"  Updated: {prompt_path} (Current Focus line)")
    return True


def cleanup_source(spec_dir: Path, dry_run: bool = False) -> bool:
    """
    Delete source docs/specs/NNN-*/ directory after successful conversion.

    Returns True if deleted successfully.
    """
    if dry_run:
        print(f"  [DRY RUN] Would delete: {spec_dir}")
        return True

    if spec_dir.exists():
        shutil.rmtree(spec_dir)
        print(f"  Deleted: {spec_dir}")
        return True

    return False


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point."""
    args = parse_args()

    print(f"\n{'='*60}")
    print("Export to Ralph")
    print(f"{'='*60}\n")

    # Step 1: Resolve spec path
    print(f"Resolving spec: {args.spec}")
    spec_dir = resolve_spec_path(args.spec)

    if not spec_dir:
        print(f"ERROR: Spec not found: {args.spec}")
        print(f"  Looked in: {SPECS_DIR}")
        sys.exit(1)

    print(f"  Found: {spec_dir}")

    # Step 2: Validate project structure
    print("\nValidating project structure...")
    structure_ok, missing = validate_project_structure(args.output_dir)

    if not structure_ok:
        print("\nERROR: Project missing required Ralph files:")
        for item in missing:
            print(f"  - {item}")
        print("\nThis export mode requires an existing Ralph project structure.")
        print("Ensure PROMPT.md, @AGENT.md, and specs/ directory exist.")
        sys.exit(1)

    print("  Project structure validated!")

    # Step 3: Validate specification
    print("\nValidating specification...")
    can_proceed, errors, warnings = validate_spec(spec_dir)

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\nBlocking Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nExport blocked. Resolve errors and try again.")
        sys.exit(1)

    print("  Validation passed!")

    # Step 4: Read documents
    print("\nReading documents...")
    prd = read_prd(spec_dir / "product-requirements.md")
    plan = read_plan(spec_dir / "implementation-plan.md")

    print(f"  PRD: {'Found' if prd else 'Not found'}")
    print(f"  PLAN: {'Found' if plan else 'Not found'}")

    # Determine project name and description
    project_name = prd.get('title', 'Project')
    project_desc = prd.get('vision', 'No description available')
    print(f"\nProject: {project_name}")

    # Step 5: Copy spec files to specs/new-features/
    print(f"\nCopying spec files to {NEW_FEATURES_DIR}/...")
    if args.dry_run:
        print("  (DRY RUN - no files will be created)")

    copied = copy_spec_files(spec_dir, args.output_dir, dry_run=args.dry_run)
    print(f"  Copied {len(copied)} files")

    # Step 6: Generate and write @fix_plan.md
    print("\nGenerating @fix_plan.md...")
    fixplan_content = transform_fixplan(plan, project_name)
    print(f"  Generated: {len(fixplan_content)} bytes")

    write_fixplan(args.output_dir, fixplan_content, dry_run=args.dry_run, force=args.force)

    # Step 7: Update PROMPT.md Current Focus
    print("\nUpdating PROMPT.md Current Focus...")
    update_prompt(args.output_dir, project_name, project_desc, dry_run=args.dry_run)

    # Step 8: Cleanup source (unless --no-cleanup)
    if not args.no_cleanup:
        print("\nCleaning up source...")
        cleanup_source(spec_dir, dry_run=args.dry_run)
    else:
        print("\nSkipping cleanup (--no-cleanup specified)")

    # Step 9: Summary
    print(f"\n{'='*60}")
    print("Export Complete!")
    print(f"{'='*60}")

    print(f"\nFiles in specs/new-features/:")
    for f in copied:
        print(f"  - {f}")

    print(f"\nFiles updated/created:")
    print(f"  - @fix_plan.md")
    print(f"  - PROMPT.md (Current Focus line)")

    if not args.no_cleanup and not args.dry_run:
        print(f"\nCleaned up:")
        print(f"  - {spec_dir}")

    if warnings:
        print(f"\nWarnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")

    print("\nNext Steps:")
    print("  1. Review @fix_plan.md for task list")
    print("  2. Review specs/new-features/ for full specifications")
    print("  3. Run: ralph start")
    print("")


if __name__ == "__main__":
    main()
