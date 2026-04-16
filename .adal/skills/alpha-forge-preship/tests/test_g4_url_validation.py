'''Tests for G4: URL Fork Validator'''

import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.g4_url_validation import validate_org_urls


def test_detects_fork_url():
    '''Test detection of fork URLs.'''
    code = '''
# Reference: https://github.com/terrylica/alpha-forge/issues/42
# See: https://github.com/terrylica/alpha-forge/issues/43
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        
        try:
            issues = validate_org_urls(f.name)
            assert len(issues) == 2
            assert all(issue['type'] == 'FORK_URL' for issue in issues)
        finally:
            os.unlink(f.name)


def test_allows_org_url():
    '''Test that org URLs don't trigger warnings.'''
    code = '''
# Reference: https://github.com/EonLabs-Spartan/alpha-forge/issues/42
# See: https://github.com/EonLabs-Spartan/alpha-forge/issues/43
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        
        try:
            issues = validate_org_urls(f.name)
            assert len(issues) == 0
        finally:
            os.unlink(f.name)


def test_empty_file():
    '''Test validation on empty file.'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("")
        f.flush()
        
        try:
            issues = validate_org_urls(f.name)
            assert len(issues) == 0
        finally:
            os.unlink(f.name)
