"""Pytest configuration: set PYTHONPATH to scripts/lib."""
import sys
import os

# Add scripts/lib so that analysis, config, data_sources, utils are importable
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_lib_dir = os.path.join(_scripts_dir, "lib")
sys.path.insert(0, _lib_dir)
