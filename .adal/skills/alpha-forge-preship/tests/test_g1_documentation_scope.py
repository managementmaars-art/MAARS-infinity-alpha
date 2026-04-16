"""Tests for G1: Documentation Scope Validator"""

from pathlib import Path
import sys
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.g1_documentation_scope import DocumentationScopeValidator


def test_detects_plugin_content_in_project_file():
    """Test detection of plugin-specific content patterns."""
    import re
    content = '''# Alpha Forge Agents

## Laguerre RSI Configuration

To configure the laguerre_rsi_regime feature:
- Set parameters: atr_period=32, level_up=0.85, level_down=0.10
- Output columns: laguerre_rsi, laguerre_regime
- Warmup formula: atr_period * 3

This is 10+ lines of laguerre-specific configuration that belongs in a plugin-specific CLAUDE.md file.
'''

    validator = DocumentationScopeValidator()
    # Test direct plugin pattern detection
    found_plugin_content = False

    # Check for plugin-specific patterns in the content
    for pattern in validator.PLUGIN_PATTERNS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if len(matches) > 0:
            found_plugin_content = True
            break

    assert found_plugin_content


def test_allows_project_wide_content():
    """Test that project-wide content passes."""
    content = '''# Alpha Forge

## Architecture

Alpha Forge uses a modular architecture with plugin-based orchestration.

## Quick Start

Run `uv run alpha_forge run examples/01_basics/01_minimal.yaml` to test.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='README.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationScopeValidator()
            issues = validator.validate_file_scope(f.name)
            scope_issues = [i for i in issues if 'SCOPE' in i['type']]
            assert len(scope_issues) == 0
        finally:
            os.unlink(f.name)


def test_detects_excessive_plugin_section():
    """Test detection of excessive plugin documentation section."""
    content = '''# AGENTS.md

## Gen800 WL1D Signal Configuration

The gen800_wl1d_regime signal is configured with the following parameters:
- regime_col: feature.laguerre_regime
- regime_filter: bullish_only (options: any, bullish_only, not_bearish)
- wickless_threshold: 0.001 (range: 0.0-1.0)
- warmup_bars: 96 (bars)

This detects wickless DOWN bars in bullish regime.

The signal generates trading signals based on:
1. Range bar detection
2. Regime gate filtering
3. Wickless bar identification

This is over 10 lines of gen800-specific content.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='AGENTS.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationScopeValidator()
            issues = validator.validate_file_scope(f.name)
            excessive = [i for i in issues if i['type'] == 'EXCESSIVE_PLUGIN_SECTION']
            assert len(excessive) > 0
        finally:
            os.unlink(f.name)


def test_detects_duplication_across_files():
    """Test detection of documentation duplication."""
    content1 = '''# Package Guide

The rangebar_cache plugin provides real-time range bar data from ClickHouse.

To use it, configure with:
- date_range: Start and end dates
- source: "cache" for ClickHouse or "local" for Binance
- n_bars: Fixed bar count mode
'''

    content2 = '''# Setup Guide

The rangebar_cache plugin provides real-time range bar data from ClickHouse.

To use it, configure with:
- date_range: Start and end dates
- source: "cache" for ClickHouse or "local" for Binance
- n_bars: Fixed bar count mode
'''

    files = []
    try:
        for i, content in enumerate([content1, content2]):
            f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
            f.write(content)
            f.flush()
            f.close()
            files.append(f.name)

        validator = DocumentationScopeValidator()
        issues = validator.validate_cross_file_duplication(files)
        assert any(i['type'] == 'DOCUMENTATION_DUPLICATION' for i in issues)

    finally:
        for f in files:
            os.unlink(f)


def test_allows_unique_documentation():
    """Test that unique documentation across files is allowed."""
    content1 = '''# Feature Documentation

The momentum feature calculates price rate of change over a window period.
'''

    content2 = '''# Signal Documentation

The breakout signal detects price breakouts from recent highs/lows.
'''

    files = []
    try:
        for i, content in enumerate([content1, content2]):
            f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
            f.write(content)
            f.flush()
            f.close()
            files.append(f.name)

        validator = DocumentationScopeValidator()
        issues = validator.validate_cross_file_duplication(files)
        duplication = [i for i in issues if i['type'] == 'DOCUMENTATION_DUPLICATION']
        assert len(duplication) == 0

    finally:
        for f in files:
            os.unlink(f)


def test_ignores_non_scope_files():
    """Test that non-scope files are not checked."""
    content = '''# Custom Documentation

This file is not in the project scope list, so plugin content is allowed.
@register_plugin decorator with laguerre_rsi configuration.
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='CUSTOM.md', delete=False) as f:
        f.write(content)
        f.flush()

        try:
            validator = DocumentationScopeValidator()
            issues = validator.validate_file_scope(f.name)
            # Should be empty since CUSTOM.md is not in scope
            assert len(issues) == 0
        finally:
            os.unlink(f.name)
