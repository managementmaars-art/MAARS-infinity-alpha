'''Tests for G5: RNG Determinism Validator'''

import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.g5_rng_determinism import validate_rng_isolation


def test_detects_global_seed():
    '''Test detection of global np.random.seed() call.'''
    code = '''
import numpy as np

def test_something():
    np.random.seed(42)
    data = np.random.randn(10)
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        
        try:
            issues = validate_rng_isolation(f.name)
            assert len(issues) > 0
            assert any(issue['type'] == 'GLOBAL_RNG_SEED' for issue in issues)
            assert issues[0]['severity'] == 'error'
        finally:
            os.unlink(f.name)


def test_allows_proper_rng_pattern():
    '''Test that proper rng pattern doesn't trigger warnings.'''
    code = '''
import numpy as np

def test_something():
    rng = np.random.default_rng(42)
    data = rng.standard_normal(10)
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        
        try:
            issues = validate_rng_isolation(f.name)
            # default_rng should not trigger errors
            assert not any(issue['type'] == 'GLOBAL_RNG_SEED' for issue in issues)
        finally:
            os.unlink(f.name)


def test_empty_file():
    '''Test validation on empty file.'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        f.flush()
        
        try:
            issues = validate_rng_isolation(f.name)
            assert len(issues) == 0
        finally:
            os.unlink(f.name)
