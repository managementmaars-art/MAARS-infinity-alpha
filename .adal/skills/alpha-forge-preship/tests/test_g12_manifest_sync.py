'''Tests for G12: Manifest Sync Validator'''

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from gates.g12_manifest_sync import ManifestSyncValidator


def test_detects_output_mismatch():
    '''Test detection of output column mismatches.'''
    validator = ManifestSyncValidator()
    
    decorator_meta = {
        'outputs': {'columns': ['rsi', 'regime'], 'format': 'panel'}
    }
    yaml_manifest = {
        'outputs': {'columns': ['rsi', 'regime', 'extra'], 'format': 'panel'}
    }
    
    mismatches = validator.validate_decorator_yaml_sync(decorator_meta, yaml_manifest)
    assert any(m['type'] == 'OUTPUT_COLUMNS_MISMATCH' for m in mismatches)


def test_no_mismatches_for_consistent_metadata():
    '''Test that consistent metadata passes validation.'''
    validator = ManifestSyncValidator()
    
    decorator_meta = {
        'outputs': {'columns': ['rsi', 'regime'], 'format': 'panel'},
        'warmup_formula': 'atr_period * 3',
        'requires_history': True,
    }
    yaml_manifest = {
        'outputs': {'columns': ['rsi', 'regime'], 'format': 'panel'},
        'warmup_formula': 'atr_period * 3',
    }
    
    mismatches = validator.validate_decorator_yaml_sync(decorator_meta, yaml_manifest)
    errors = [m for m in mismatches if m['severity'] == 'error']
    assert len(errors) == 0
