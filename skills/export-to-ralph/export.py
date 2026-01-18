#!/usr/bin/env python3
"""
Export to Ralph - Specification to Ralph Format Converter

Transforms completed PRD/SDD/PLAN specifications into Ralph's expected format:
- PROMPT.md: Main development instructions
- @fix_plan.md: Prioritized task checklist
- @AGENT.md: Build/test configuration
- specs/: Feature specifications with Gherkin scenarios

Usage:
    python export.py <spec-id> [--output-dir DIR] [--dry-run] [--force]

Examples:
    python export.py 002
    python export.py 002 --dry-run
    python export.py 002 --output-dir /path/to/project --force
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# =============================================================================
# Configuration
# =============================================================================

SPECS_DIR = Path("docs/specs")
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Regex patterns
NEEDS_CLARIFICATION_PATTERN = re.compile(r'\[NEEDS CLARIFICATION[^\]]*\]', re.IGNORECASE)
TASK_PATTERN = re.compile(r'-\s*\[\s*[x ]?\s*\]\s*\*\*(T\d+\.\d+)\s+(.+?)\*\*', re.IGNORECASE)
EARS_EVENT_PATTERN = re.compile(r'WHEN\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)', re.IGNORECASE)
EARS_COMPLEX_PATTERN = re.compile(r'IF\s+(.+?),\s*(?:THEN\s+)?THE SYSTEM SHALL\s+(.+)', re.IGNORECASE)
EARS_UBIQUITOUS_PATTERN = re.compile(r'THE SYSTEM SHALL\s+(.+)', re.IGNORECASE)
EARS_STATE_PATTERN = re.compile(r'WHILE\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)', re.IGNORECASE)
EARS_OPTIONAL_PATTERN = re.compile(r'WHERE\s+(.+?),\s*THE SYSTEM SHALL\s+(.+)', re.IGNORECASE)


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
    python export.py 002 --force             # Overwrite existing files
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
        warnings.append("SDD not found - @AGENT.md will have minimal config")
    else:
        sdd_content = sdd_path.read_text(encoding='utf-8')
        markers = find_clarification_markers(sdd_content)
        if markers:
            errors.append(f"SDD has {len(markers)} [NEEDS CLARIFICATION] markers")

    # Check PLAN (optional)
    if not plan_path.exists():
        warnings.append("PLAN not found - using PRD features for task list")
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

    def extract_section(header: str, next_headers: List[str] = None) -> str:
        """Extract content under a header until next header."""
        pattern = rf'##\s*{re.escape(header)}\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def extract_subsection(header: str) -> str:
        """Extract content under a subsection header."""
        pattern = rf'###\s*{re.escape(header)}\s*\n(.*?)(?=\n###|\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    # Extract features by priority
    def extract_features(section_name: str) -> List[Dict]:
        """Extract features from a priority section."""
        features = []
        section_content = extract_subsection(section_name)

        # Find feature blocks (#### Feature N: Name)
        feature_pattern = r'####\s*Feature\s*\d+:\s*(.+?)\n(.*?)(?=####|\Z)'
        for match in re.finditer(feature_pattern, section_content, re.DOTALL):
            feature_name = match.group(1).strip()
            feature_content = match.group(2).strip()

            # Extract user story
            user_story = ""
            story_match = re.search(r'\*\*User Story:\*\*\s*(.+?)(?=\n\*\*|\n-|\Z)', feature_content, re.DOTALL)
            if story_match:
                user_story = story_match.group(1).strip()

            # Extract acceptance criteria
            criteria = []
            criteria_pattern = r'-\s*\[\s*[x ]?\s*\]\s*(.+?)(?=\n\s*-|\Z)'
            for crit_match in re.finditer(criteria_pattern, feature_content, re.DOTALL):
                criteria.append(crit_match.group(1).strip())

            features.append({
                'name': feature_name,
                'user_story': user_story,
                'criteria': criteria
            })

        return features

    return {
        'title': extract_prd_title(content),
        'vision': extract_subsection("Vision"),
        'problem_statement': extract_subsection("Problem Statement"),
        'value_proposition': extract_subsection("Value Proposition"),
        'must_have': extract_features("Must Have Features") or extract_features("Must Have"),
        'should_have': extract_features("Should Have Features") or extract_features("Should Have"),
        'could_have': extract_features("Could Have Features") or extract_features("Could Have"),
        'wont_have': extract_subsection("Won't Have") or extract_subsection("Won't Have (This Phase)"),
        'constraints': extract_section("Constraints"),
        'assumptions': extract_section("Assumptions"),
        'kpis': extract_subsection("Key Performance Indicators"),
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


def read_sdd(sdd_path: Path) -> Dict:
    """
    Read and parse SDD document.

    Returns dict with extracted sections.
    """
    if not sdd_path.exists():
        return {}

    content = sdd_path.read_text(encoding='utf-8')

    def extract_section(header: str) -> str:
        """Extract content under a header."""
        pattern = rf'##\s*{re.escape(header)}\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def extract_subsection(header: str) -> str:
        """Extract content under a subsection header."""
        pattern = rf'###\s*{re.escape(header)}\s*\n(.*?)(?=\n###|\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    # Extract project commands from code block
    def extract_commands() -> Dict[str, str]:
        commands = {}
        commands_section = extract_subsection("Project Commands")

        # Look for Install, Dev, Test, Build commands
        for cmd_type in ['Install', 'Dev', 'Test', 'Build', 'Lint']:
            pattern = rf'{cmd_type}:\s*\[?([^\]\n]+)\]?'
            match = re.search(pattern, commands_section, re.IGNORECASE)
            if match:
                commands[cmd_type.lower()] = match.group(1).strip()

        # Also check for bash code blocks
        bash_pattern = r'```bash\s*(.*?)```'
        for match in re.finditer(bash_pattern, commands_section, re.DOTALL):
            block = match.group(1)
            for line in block.split('\n'):
                for cmd_type in ['Install', 'Dev', 'Test', 'Build']:
                    if line.strip().lower().startswith(cmd_type.lower() + ':'):
                        cmd = line.split(':', 1)[1].strip()
                        cmd = cmd.strip('[]')
                        commands[cmd_type.lower()] = cmd

        return commands

    # Extract directory map
    def extract_directory_map() -> List[str]:
        dir_section = extract_subsection("Directory Map")
        files = []

        # Look for file paths with annotations
        pattern = r'[├└│─\s]*([a-zA-Z_/\.\-]+\.[a-zA-Z]+)\s*#?\s*(NEW|MODIFY)?:?\s*(.+)?'
        for match in re.finditer(pattern, dir_section):
            path = match.group(1).strip()
            action = match.group(2) or ""
            desc = match.group(3) or ""
            if action:
                files.append(f"`{path}` - {action}: {desc}".strip())
            else:
                files.append(f"`{path}`")

        return files

    # Extract ADRs
    def extract_adrs() -> List[Dict]:
        adrs = []
        adr_section = extract_section("Architecture Decisions")

        # Pattern: - [x] ADR-N Name: Decision
        pattern = r'-\s*\[[x ]\]\s*\*?\*?(ADR-\d+[^:]*):?\*?\*?\s*(.+?)(?=\n\s*-|\Z)'
        for match in re.finditer(pattern, adr_section, re.DOTALL):
            adr_id = match.group(1).strip()
            content = match.group(2).strip()

            # Extract rationale if present
            rationale = ""
            rat_match = re.search(r'Rationale:\s*(.+?)(?=\n\s*-|Trade-offs:|User confirmed:|\Z)', content, re.DOTALL)
            if rat_match:
                rationale = rat_match.group(1).strip()

            adrs.append({
                'id': adr_id,
                'content': content.split('\n')[0].strip(),
                'rationale': rationale
            })

        return adrs

    return {
        'constraints': extract_section("Constraints"),
        'solution_strategy': extract_section("Solution Strategy"),
        'commands': extract_commands(),
        'directory_map': extract_directory_map(),
        'integration_points': extract_subsection("Integration Points"),
        'quality_requirements': extract_section("Quality Requirements"),
        'adrs': extract_adrs(),
        'error_handling': extract_subsection("Error Handling"),
        'implementation_boundaries': extract_subsection("Implementation Boundaries"),
        'raw_content': content
    }


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

def transform_prompt(prd: Dict, sdd: Dict, project_name: str) -> str:
    """
    Transform PRD and SDD into PROMPT.md content.
    """
    template_path = TEMPLATES_DIR / "prompt-template.md"
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        template = "# {project_name}\n\n{vision}\n\n{problem_statement}"

    # Build sections
    vision = prd.get('vision', 'No vision defined')
    problem = prd.get('problem_statement', 'No problem statement defined')
    value_prop = prd.get('value_proposition', 'No value proposition defined')

    # In scope from must-have features
    in_scope_items = []
    for feature in prd.get('must_have', []):
        in_scope_items.append(f"- {feature.get('name', 'Unknown feature')}")
    in_scope = '\n'.join(in_scope_items) if in_scope_items else "- Core functionality as defined in PRD"

    # Out of scope
    out_of_scope = prd.get('wont_have', 'No explicit out-of-scope items')

    # Constraints (merge PRD and SDD)
    constraints_list = []
    if prd.get('constraints'):
        constraints_list.append(prd['constraints'])
    if sdd.get('constraints'):
        constraints_list.append(sdd['constraints'])
    constraints = '\n\n'.join(constraints_list) if constraints_list else "No constraints defined"

    # Assumptions
    assumptions = prd.get('assumptions', 'No assumptions documented')

    # Success criteria from KPIs
    success_criteria = prd.get('kpis', 'No success criteria defined')

    # Replace template placeholders
    result = template.replace('{project_name}', project_name)
    result = result.replace('{vision}', vision)
    result = result.replace('{problem_statement}', problem)
    result = result.replace('{value_proposition}', value_prop)
    result = result.replace('{in_scope}', in_scope)
    result = result.replace('{out_of_scope}', out_of_scope)
    result = result.replace('{constraints}', constraints)
    result = result.replace('{assumptions}', assumptions)
    result = result.replace('{success_criteria}', success_criteria)

    return result


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


def transform_fixplan(prd: Dict, plan: Dict, project_name: str) -> str:
    """
    Transform PLAN (or PRD features) into @fix_plan.md content.
    """
    template_path = TEMPLATES_DIR / "fixplan-template.md"
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        template = "# {project_name} Fix Plan\n\n## High Priority\n\n{high_priority_tasks}"

    high_tasks = []
    medium_tasks = []
    low_tasks = []
    notes = []

    # If we have a PLAN, use its phases
    if plan and plan.get('phases'):
        phases = plan['phases']

        # Phase 1 -> High
        if '1' in phases:
            for task in phases['1'].get('tasks', []):
                high_tasks.append(flatten_plan_task(task))
                if task.get('parallel'):
                    notes.append(f"- {task.get('id')} can run in parallel")

        # Phase 2 -> Medium
        if '2' in phases:
            for task in phases['2'].get('tasks', []):
                medium_tasks.append(flatten_plan_task(task))
                if task.get('parallel'):
                    notes.append(f"- {task.get('id')} can run in parallel")

        # Phase 3+ -> Low
        for phase_num in sorted(phases.keys()):
            if int(phase_num) >= 3:
                for task in phases[phase_num].get('tasks', []):
                    low_tasks.append(flatten_plan_task(task))

    # Fallback to PRD features if no PLAN
    else:
        # Must-Have -> High
        for i, feature in enumerate(prd.get('must_have', []), 1):
            high_tasks.append(f"- [ ] F{i}: {feature.get('name', 'Feature')}")

        # Should-Have -> Medium
        for i, feature in enumerate(prd.get('should_have', []), 1):
            medium_tasks.append(f"- [ ] S{i}: {feature.get('name', 'Feature')}")

        # Could-Have -> Low
        for i, feature in enumerate(prd.get('could_have', []), 1):
            low_tasks.append(f"- [ ] C{i}: {feature.get('name', 'Feature')}")

    # Format task lists
    high_str = '\n'.join(high_tasks) if high_tasks else "- [ ] No high priority tasks defined"
    medium_str = '\n'.join(medium_tasks) if medium_tasks else "- [ ] No medium priority tasks defined"
    low_str = '\n'.join(low_tasks) if low_tasks else "- [ ] No low priority tasks defined"
    notes_str = '\n'.join(notes) if notes else "No additional notes"

    # Replace template placeholders
    result = template.replace('{project_name}', project_name)
    result = result.replace('{high_priority_tasks}', high_str)
    result = result.replace('{medium_priority_tasks}', medium_str)
    result = result.replace('{low_priority_tasks}', low_str)
    result = result.replace('{completed_tasks}', "- [x] Project initialization")
    result = result.replace('{notes}', notes_str)

    return result


def transform_agent(sdd: Dict, project_name: str) -> str:
    """
    Transform SDD into @AGENT.md content.
    """
    template_path = TEMPLATES_DIR / "agent-template.md"
    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        template = "# Agent Build Instructions\n\n## Project Setup\n\n{install_command}"

    # Extract commands
    commands = sdd.get('commands', {})
    install_cmd = commands.get('install', '# TODO: Add install command')
    dev_cmd = commands.get('dev', '# TODO: Add dev command')
    test_cmd = commands.get('test', '# TODO: Add test command')
    build_cmd = commands.get('build', '# TODO: Add build command')

    # Architecture pattern
    strategy = sdd.get('solution_strategy', 'No architecture pattern defined')
    # Take first paragraph only
    arch_pattern = strategy.split('\n\n')[0] if strategy else "No architecture pattern defined"

    # Key files
    dir_map = sdd.get('directory_map', [])
    key_files = '\n'.join([f"- {f}" for f in dir_map]) if dir_map else "- No key files documented"

    # Integration points
    integration = sdd.get('integration_points', 'No integration points documented')

    # Quality requirements
    quality = sdd.get('quality_requirements', 'No quality requirements defined')

    # ADRs
    adrs = sdd.get('adrs', [])
    adr_text = '\n'.join([f"- **{a['id']}**: {a['content']}" for a in adrs]) if adrs else "No ADRs documented"

    # Error handling
    error_handling = sdd.get('error_handling', 'No error handling patterns documented')

    # Replace template placeholders
    result = template.replace('{install_command}', install_cmd)
    result = result.replace('{dev_command}', dev_cmd)
    result = result.replace('{test_command}', test_cmd)
    result = result.replace('{build_command}', build_cmd)
    result = result.replace('{architecture_pattern}', arch_pattern)
    result = result.replace('{key_files}', key_files)
    result = result.replace('{integration_points}', integration)
    result = result.replace('{quality_requirements}', quality)
    result = result.replace('{decision_rationale}', adr_text)
    result = result.replace('{error_handling}', error_handling)

    return result


def transform_ears_to_gherkin(ears_criterion: str) -> str:
    """
    Transform EARS-format acceptance criterion to Gherkin scenario.

    EARS patterns:
    - UBIQUITOUS: "THE SYSTEM SHALL X"
    - EVENT-DRIVEN: "WHEN X, THE SYSTEM SHALL Y"
    - STATE-DRIVEN: "WHILE X, THE SYSTEM SHALL Y"
    - OPTIONAL: "WHERE X, THE SYSTEM SHALL Y"
    - COMPLEX: "IF X, THEN THE SYSTEM SHALL Y"
    """
    criterion = ears_criterion.strip()

    # EVENT-DRIVEN: WHEN X, THE SYSTEM SHALL Y
    match = EARS_EVENT_PATTERN.match(criterion)
    if match:
        trigger, action = match.groups()
        return f"Given the system is ready\nWhen {trigger.lower()}\nThen the system {action.lower()}"

    # COMPLEX: IF X, THEN THE SYSTEM SHALL Y
    match = EARS_COMPLEX_PATTERN.match(criterion)
    if match:
        condition, action = match.groups()
        return f"Given {condition.lower()}\nWhen the operation is triggered\nThen the system {action.lower()}"

    # STATE-DRIVEN: WHILE X, THE SYSTEM SHALL Y
    match = EARS_STATE_PATTERN.match(criterion)
    if match:
        state, action = match.groups()
        return f"Given {state.lower()}\nThen the system {action.lower()}"

    # OPTIONAL: WHERE X, THE SYSTEM SHALL Y
    match = EARS_OPTIONAL_PATTERN.match(criterion)
    if match:
        condition, action = match.groups()
        return f"Given {condition.lower()}\nThen the system {action.lower()}"

    # UBIQUITOUS: THE SYSTEM SHALL X
    match = EARS_UBIQUITOUS_PATTERN.match(criterion)
    if match:
        action = match.group(1)
        return f"Then the system {action.lower()}"

    # Fallback: return as-is with comment
    return f"# TODO: Convert manually\n# Original: {criterion}"


def transform_specs(prd: Dict, sdd: Dict, output_dir: Path) -> Dict[str, str]:
    """
    Transform PRD and SDD into specs/ directory files.

    Returns dict of {relative_path: content}
    """
    specs = {}

    # Create feature files from PRD
    all_features = (
        prd.get('must_have', []) +
        prd.get('should_have', []) +
        prd.get('could_have', [])
    )

    for i, feature in enumerate(all_features, 1):
        feature_name = feature.get('name', f'feature-{i}')
        safe_name = re.sub(r'[^a-zA-Z0-9]+', '-', feature_name.lower()).strip('-')

        content_lines = [f"# Feature: {feature_name}", ""]

        # Add user story
        user_story = feature.get('user_story', '')
        if user_story:
            content_lines.append(f"**User Story:** {user_story}")
            content_lines.append("")

        # Convert acceptance criteria to scenarios
        criteria = feature.get('criteria', [])
        for j, criterion in enumerate(criteria, 1):
            content_lines.append(f"## Scenario: AC-{i}.{j}")
            content_lines.append("")
            content_lines.append("```gherkin")
            content_lines.append(transform_ears_to_gherkin(criterion))
            content_lines.append("```")
            content_lines.append("")
            content_lines.append(f"**Original EARS:** {criterion}")
            content_lines.append("")
            content_lines.append("---")
            content_lines.append("")

        if criteria:
            specs[f"specs/features/{safe_name}.md"] = '\n'.join(content_lines)

    # Create error handling scenarios if SDD has error handling
    if sdd.get('error_handling'):
        error_content = [
            "# Error Handling Scenarios",
            "",
            "Based on SDD error handling patterns.",
            "",
            "```",
            sdd['error_handling'],
            "```"
        ]
        specs["specs/scenarios/error-handling.md"] = '\n'.join(error_content)

    return specs


# =============================================================================
# File Writer
# =============================================================================

def write_output(
    output_dir: Path,
    prompt_content: str,
    fixplan_content: str,
    agent_content: str,
    specs_files: Dict[str, str],
    dry_run: bool = False,
    force: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Write all output files.

    Returns tuple of (created_files, skipped_files)
    """
    created = []
    skipped = []

    files_to_write = {
        "PROMPT.md": prompt_content,
        "@fix_plan.md": fixplan_content,
        "@AGENT.md": agent_content,
    }

    # Add specs files
    files_to_write.update(specs_files)

    for rel_path, content in files_to_write.items():
        full_path = output_dir / rel_path

        if dry_run:
            print(f"  [DRY RUN] Would create: {full_path}")
            created.append(str(rel_path))
            continue

        # Check for collision
        if full_path.exists() and not force:
            response = input(f"  File exists: {full_path}. Overwrite? (y/N): ")
            if response.lower() != 'y':
                skipped.append(str(rel_path))
                continue

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        full_path.write_text(content, encoding='utf-8')
        created.append(str(rel_path))
        print(f"  Created: {full_path}")

    return created, skipped


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

    # Step 2: Validate specification
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

    # Step 3: Read documents
    print("\nReading documents...")
    prd = read_prd(spec_dir / "product-requirements.md")
    sdd = read_sdd(spec_dir / "solution-design.md")
    plan = read_plan(spec_dir / "implementation-plan.md")

    print(f"  PRD: {'Found' if prd else 'Not found'}")
    print(f"  SDD: {'Found' if sdd else 'Not found'}")
    print(f"  PLAN: {'Found' if plan else 'Not found'}")

    # Determine project name
    project_name = prd.get('title', 'Project')
    print(f"\nProject: {project_name}")

    # Step 4: Transform content
    print("\nTransforming content...")
    prompt_content = transform_prompt(prd, sdd, project_name)
    fixplan_content = transform_fixplan(prd, plan, project_name)
    agent_content = transform_agent(sdd, project_name)
    specs_files = transform_specs(prd, sdd, args.output_dir)

    print(f"  PROMPT.md: {len(prompt_content)} bytes")
    print(f"  @fix_plan.md: {len(fixplan_content)} bytes")
    print(f"  @AGENT.md: {len(agent_content)} bytes")
    print(f"  specs/: {len(specs_files)} files")

    # Step 5: Write output
    print(f"\nWriting to: {args.output_dir}")
    if args.dry_run:
        print("  (DRY RUN - no files will be created)")

    created, skipped = write_output(
        args.output_dir,
        prompt_content,
        fixplan_content,
        agent_content,
        specs_files,
        dry_run=args.dry_run,
        force=args.force
    )

    # Step 6: Summary
    print(f"\n{'='*60}")
    print("Export Complete!")
    print(f"{'='*60}")
    print(f"\nFiles created: {len(created)}")
    for f in created:
        print(f"  - {f}")

    if skipped:
        print(f"\nFiles skipped: {len(skipped)}")
        for f in skipped:
            print(f"  - {f}")

    if warnings:
        print(f"\nWarnings: {len(warnings)}")
        for w in warnings:
            print(f"  - {w}")

    print("\nNext Steps:")
    print("  1. Review generated files")
    print("  2. Run: ralph start")
    print("")


if __name__ == "__main__":
    main()
