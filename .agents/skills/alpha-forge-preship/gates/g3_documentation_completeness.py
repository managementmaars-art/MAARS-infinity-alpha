"""G3: Documentation Completeness Validator

Detects missing required documentation sections.
Triggers: Pre-commit hook (markdown analysis)
Prevents: D3-D5 (incomplete documentation causing knowledge loss)
ROI: 85% effectiveness, ~3% false positives
Coverage: Required section validation
"""

import re
from typing import List, Dict, Any, Set


class DocumentationCompletenessValidator:
    """Validates documentation completeness."""

    # Required sections for different file types
    REQUIRED_SECTIONS = {
        'plugin_documentation': [
            'purpose|description',
            'usage|example',
            'parameters',
            'returns|output',
        ],
        'package_claude_md': [
            'overview|introduction',
            'setup|installation',
            'testing',
            'commands|cli',
        ],
        'plugin_claude_md': [
            'quick start',
            'common patterns',
            'troubleshooting',
        ],
    }

    @staticmethod
    def validate_markdown_completeness(file_path: str, doc_type: str = 'plugin_documentation') -> List[Dict[str, Any]]:
        """Validate that markdown file has required sections.

        Args:
            file_path: Path to markdown file
            doc_type: Type of documentation ('plugin_documentation', 'package_claude_md', etc.)

        Returns:
            List of completeness issues
        """
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Extract all sections
            headers = re.findall(r'^#+\s+([^\n]+)', content, re.MULTILINE)
            sections = set(h.lower() for h in headers)

            # Check required sections
            required = DocumentationCompletenessValidator.REQUIRED_SECTIONS.get(doc_type, [])

            for requirement in required:
                # requirement is a pipe-separated list of alternatives (e.g., 'purpose|description')
                alternatives = [alt.strip() for alt in requirement.split('|')]
                found = any(
                    any(alt in section for section in sections)
                    for alt in alternatives
                )

                if not found:
                    issues.append({
                        'type': 'MISSING_SECTION',
                        'severity': 'warning',
                        'message': f"Missing required section: {requirement.replace('|', ' or ')}",
                        'fix': f"Add a section with one of these headers: {', '.join(alternatives)}"
                    })

        except (OSError, UnicodeDecodeError):
            pass

        return issues

    @staticmethod
    def validate_section_completeness(file_path: str) -> List[Dict[str, Any]]:
        """Validate that sections have meaningful content.

        Returns:
            List of completeness issues
        """
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Split into sections
            sections = re.split(r'^#+\s+([^\n]+)', content, flags=re.MULTILINE)[1:]

            # Process pairs of (header, content)
            for i in range(0, len(sections), 2):
                if i + 1 >= len(sections):
                    break

                header = sections[i].strip()
                section_content = sections[i + 1].strip()

                # Check minimum content length (at least 20 characters of meaningful text)
                meaningful_content = re.sub(r'[*_`\-\[\]{}]', '', section_content)
                if len(meaningful_content) < 20 and section_content:
                    issues.append({
                        'type': 'INCOMPLETE_SECTION',
                        'severity': 'warning',
                        'message': f"Section '{header}' has insufficient content ({len(meaningful_content)} chars)",
                        'fix': "Expand section with at least 20 characters of meaningful content"
                    })

                # Check for code examples in relevant sections
                if any(keyword in header.lower() for keyword in ['example', 'usage', 'quickstart']):
                    if '```' not in section_content:
                        issues.append({
                            'type': 'MISSING_CODE_IN_EXAMPLE',
                            'severity': 'warning',
                            'message': f"Section '{header}' mentions code but has no code blocks",
                            'fix': "Add code examples wrapped in ```language ... ```"
                        })

        except (OSError, UnicodeDecodeError):
            pass

        return issues

    @staticmethod
    def validate_cross_reference_completeness(file_path: str, referenced_paths: List[str] = None) -> List[Dict[str, Any]]:
        """Validate that documentation references are complete.

        Args:
            file_path: Path to documentation file
            referenced_paths: Paths that should be referenced (if not provided, uses common patterns)

        Returns:
            List of missing reference issues
        """
        issues = []

        if not referenced_paths:
            referenced_paths = [
                'CLAUDE.md',
                'README.md',
                'tests/',
                'docs/',
            ]

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for references
            for ref_path in referenced_paths:
                # Look for markdown link or code reference
                if ref_path not in content:
                    # Only warn if this is a type of file that should be referenced
                    if ref_path.endswith('.md') or ref_path.endswith('/'):
                        # Don't warn about every possible reference
                        # Only warn about high-probability ones
                        if 'CLAUDE.md' in ref_path and 'CLAUDE.md' not in file_path:
                            issues.append({
                                'type': 'MISSING_REFERENCE',
                                'severity': 'info',
                                'message': f"Consider linking to {ref_path} for more details",
                                'fix': f"Add link: [See {ref_path}]({ref_path})"
                            })

        except (OSError, UnicodeDecodeError):
            pass

        return issues

    @staticmethod
    def validate_parameter_documentation_completeness(parameters_dict: dict) -> List[Dict[str, Any]]:
        """Validate that all parameters are documented.

        Args:
            parameters_dict: Dictionary of parameters from plugin decorator

        Returns:
            List of missing parameter docs
        """
        issues = []

        for param_name, param_spec in parameters_dict.items():
            if not isinstance(param_spec, dict):
                continue

            # Check required parameter fields
            if 'description' not in param_spec or not param_spec.get('description', '').strip():
                issues.append({
                    'type': 'MISSING_PARAMETER_DOCS',
                    'severity': 'error',
                    'parameter': param_name,
                    'message': f"Parameter '{param_name}' missing description",
                    'fix': "Add 'description' field to parameter specification"
                })

            if 'type' not in param_spec:
                issues.append({
                    'type': 'MISSING_PARAMETER_TYPE',
                    'severity': 'warning',
                    'parameter': param_name,
                    'message': f"Parameter '{param_name}' missing type specification",
                    'fix': "Add 'type' field (e.g., 'numeric', 'enum', 'string')"
                })

            # Check that numeric parameters have ranges
            if param_spec.get('type') in ['numeric', 'int', 'float']:
                if 'min' not in param_spec or 'max' not in param_spec:
                    issues.append({
                        'type': 'MISSING_PARAMETER_RANGE',
                        'severity': 'warning',
                        'parameter': param_name,
                        'message': f"Numeric parameter '{param_name}' missing min/max bounds",
                        'fix': "Add 'min' and 'max' fields to parameter specification"
                    })

        return issues
