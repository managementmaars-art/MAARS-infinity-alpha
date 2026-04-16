"""Comprehensive tests for all Phase 1 quality gates"""
# GitHub Issue: https://github.com/Eon-Labs/alpha-forge/issues/154
import pytest
import tempfile
import os
import sys
from pathlib import Path

parent = Path(__file__).parent.parent
sys.path.insert(0, str(parent))

from gates.g5_rng_determinism import validate_rng_isolation
from gates.g4_url_validation import validate_org_urls
from gates.g8_parameter_validation import ParameterValidator
from gates.g12_manifest_sync import ManifestSyncValidator


class TestG5RNG:
    def test_detects_global_seed(self):
        code = "np.random.seed(42)"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            try:
                issues = validate_rng_isolation(f.name)
                assert len(issues) >= 1
                assert any(i['type'] == 'GLOBAL_RNG_SEED' for i in issues)
            finally:
                os.unlink(f.name)

    def test_clean_code(self):
        code = "value = 42"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            try:
                issues = validate_rng_isolation(f.name)
                assert len(issues) == 0
            finally:
                os.unlink(f.name)


class TestG4URL:
    def test_detects_fork_url(self):
        code = "See terrylica/alpha-forge"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(code)
            f.flush()
            try:
                issues = validate_org_urls(f.name)
                assert len(issues) >= 1
                assert any(i['type'] == 'FORK_URL' for i in issues)
            finally:
                os.unlink(f.name)

    def test_accepts_org_url(self):
        code = "See EonLabs-Spartan/alpha-forge"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(code)
            f.flush()
            try:
                issues = validate_org_urls(f.name)
                assert len(issues) == 0
            finally:
                os.unlink(f.name)


class TestG8Parameter:
    def test_numeric_range_valid(self):
        ParameterValidator.validate_numeric_range(50, 0, 100, "test")

    def test_numeric_range_invalid(self):
        with pytest.raises(ValueError):
            ParameterValidator.validate_numeric_range(150, 0, 100, "test")

    def test_enum_valid(self):
        ParameterValidator.validate_enum("bullish_only", ["bullish_only", "any"], "regime")

    def test_enum_invalid(self):
        with pytest.raises(ValueError):
            ParameterValidator.validate_enum("invalid", ["bullish_only"], "regime")

    def test_column_exists_valid(self):
        ParameterValidator.validate_column_exists("price.close", ["price.open", "price.close"])

    def test_column_missing(self):
        with pytest.raises(ValueError):
            ParameterValidator.validate_column_exists("regime", ["price.open"], "data")


class TestG12Manifest:
    def test_sync_valid(self):
        decorator = {'outputs': {'columns': ['rsi', 'trend']}}
        yaml_manifest = {'outputs': {'columns': ['rsi', 'trend']}}
        issues = ManifestSyncValidator.validate_decorator_yaml_sync(decorator, yaml_manifest)
        assert len(issues) == 0

    def test_sync_mismatch(self):
        decorator = {'outputs': {'columns': ['rsi', 'trend']}}
        yaml_manifest = {'outputs': {'columns': ['rsi']}}
        issues = ManifestSyncValidator.validate_decorator_yaml_sync(decorator, yaml_manifest)
        assert len(issues) > 0
        assert any('mismatch' in str(i).lower() for i in issues)
