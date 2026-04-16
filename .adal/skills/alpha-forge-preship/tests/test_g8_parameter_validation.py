"""Tests for G8: Parameter Validation"""
import pytest
import sys
import os
from pathlib import Path

parent = Path(__file__).parent.parent
sys.path.insert(0, str(parent))

from gates.g8_parameter_validation import ParameterValidator


class TestG8:
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

    def test_column_valid(self):
        ParameterValidator.validate_column_exists("price.close", ["price.open", "price.close"])

    def test_column_invalid(self):
        with pytest.raises(ValueError):
            ParameterValidator.validate_column_exists("regime", ["price.open"], "data")
