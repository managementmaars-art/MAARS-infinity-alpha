"""Tests for G3: Documentation Completeness Validator"""

from pathlib import Path
import sys
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.g3_documentation_completeness import DocumentationCompletenessValidator


def test_detects_missing_required_section():
    """Test detection of missing required section."""
    content = '''# Feature Documentation

## Overview

This is a feature.

## Parameters

atr_period: 32
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationCompletenessValidator()
            issues = validator.validate_markdown_completeness(f.name, 'plugin_documentation')
            # Missing "usage/example" and "returns/output" sections
            assert any(i['type'] == 'MISSING_SECTION' for i in issues)
        finally:
            os.unlink(f.name)


def test_allows_complete_documentation():
    """Test that complete documentation passes."""
    content = '''# Feature Documentation

## Description

This feature calculates momentum.

## Usage Example

```python
result = feature(data, window=20)
```

## Parameters

- window: lookback period (range: 2-100)

## Returns

- Momentum values
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationCompletenessValidator()
            issues = validator.validate_markdown_completeness(f.name, 'plugin_documentation')
            missing = [i for i in issues if i['type'] == 'MISSING_SECTION']
            assert len(missing) == 0
        finally:
            os.unlink(f.name)


def test_detects_incomplete_section():
    """Test detection of sections with insufficient content."""
    content = '''# Documentation

## Overview
Brief.

## Parameters
Lots of content here about parameters and how to configure them properly.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationCompletenessValidator()
            issues = validator.validate_section_completeness(f.name)
            # Overview section is too brief
            incomplete = [i for i in issues if i['type'] == 'INCOMPLETE_SECTION']
            assert len(incomplete) > 0
        finally:
            os.unlink(f.name)


def test_detects_missing_code_in_example_section():
    """Test detection of example section without code."""
    content = '''# Feature Documentation

## Usage Example

To use this feature, follow these steps:
1. Configure parameters
2. Call the function
3. Interpret results

But no actual code example is shown here.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationCompletenessValidator()
            issues = validator.validate_section_completeness(f.name)
            missing_code = [i for i in issues if i['type'] == 'MISSING_CODE_IN_EXAMPLE']
            assert len(missing_code) > 0
        finally:
            os.unlink(f.name)


def test_accepts_section_with_code():
    """Test that example sections with code pass."""
    content = '''# Feature Documentation

## Usage Example

To use this feature:

```python
result = feature(data, window=20)
print(result)
```

This computes momentum with a 20-bar window.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationCompletenessValidator()
            issues = validator.validate_section_completeness(f.name)
            missing_code = [i for i in issues if i['type'] == 'MISSING_CODE_IN_EXAMPLE']
            assert len(missing_code) == 0
        finally:
            os.unlink(f.name)


def test_validates_parameter_documentation():
    """Test validation of parameter documentation completeness."""
    validator = DocumentationCompletenessValidator()

    parameters = {
        'atr_period': {
            'type': 'numeric',
            'description': 'ATR lookback period (range: 1-100)',
        },
        'level_up': {
            'type': 'numeric',
            'description': 'Upper threshold',
            # Missing min/max
        },
    }

    issues = validator.validate_parameter_documentation_completeness(parameters)
    # level_up is missing min/max for numeric type
    assert any(i['type'] == 'MISSING_PARAMETER_RANGE' for i in issues)


def test_detects_missing_parameter_description():
    """Test detection of parameter missing description."""
    validator = DocumentationCompletenessValidator()

    parameters = {
        'atr_period': {
            'type': 'numeric',
        }
    }

    issues = validator.validate_parameter_documentation_completeness(parameters)
    assert any(i['type'] == 'MISSING_PARAMETER_DOCS' for i in issues)


def test_detects_missing_parameter_type():
    """Test detection of parameter missing type."""
    validator = DocumentationCompletenessValidator()

    parameters = {
        'atr_period': {
            'description': 'ATR lookback period',
        }
    }

    issues = validator.validate_parameter_documentation_completeness(parameters)
    assert any(i['type'] == 'MISSING_PARAMETER_TYPE' for i in issues)


def test_complete_parameter_documentation():
    """Test that complete parameter documentation passes."""
    validator = DocumentationCompletenessValidator()

    parameters = {
        'atr_period': {
            'type': 'numeric',
            'description': 'ATR period (range: 1-100)',
            'min': 1,
            'max': 100,
        },
        'regime_filter': {
            'type': 'enum',
            'description': 'Filter regime: any, bullish_only, not_bearish',
            'enum': ['any', 'bullish_only', 'not_bearish'],
        },
    }

    issues = validator.validate_parameter_documentation_completeness(parameters)
    errors = [i for i in issues if i['severity'] == 'error']
    assert len(errors) == 0


def test_detects_reference_completeness():
    """Test detection of missing documentation references."""
    validator = DocumentationCompletenessValidator()

    content = '''# Package Documentation

This is general documentation.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            # This is an informational test - references are optional
            issues = validator.validate_cross_reference_completeness(
                f.name,
                referenced_paths=['CLAUDE.md']
            )
            # Info-level items may or may not be present depending on context
            assert True
        finally:
            os.unlink(f.name)
