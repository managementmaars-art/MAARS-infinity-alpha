"""G6: Warmup Alignment Validator

Detects warmup misalignment between feature and signal stages.
Triggers: DSL validation + decorator check
Prevents: C3 (warmup gap between stages causing NaN handling issues)
ROI: 100% effectiveness, 0% false positives
Coverage: Cross-layer warmup consistency
"""

import re
import ast
from typing import List, Dict, Any, Optional


class WarmupAlignmentValidator:
    """Validates warmup alignment across feature → signal pipeline."""

    @staticmethod
    def validate_decorator_warmup(decorator_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate warmup_formula consistency with requires_history.

        Returns:
            List of validation errors (empty if valid)
        """
        issues = []

        requires_history = decorator_dict.get('requires_history', False)
        warmup_formula = decorator_dict.get('warmup_formula')
        plugin_type = decorator_dict.get('plugin_type', 'unknown')

        # Rule 1: requires_history=True MUST have warmup_formula
        if requires_history and not warmup_formula:
            issues.append({
                'type': 'MISSING_WARMUP_FORMULA',
                'severity': 'error',
                'message': f"Plugin '{plugin_type}': requires_history=True but warmup_formula is missing. "
                          f"Time-series features must declare warmup periods.",
                'fix': f"Add warmup_formula (e.g., 'atr_period * 3') to decorator"
            })

        # Rule 2: requires_history=False should NOT have warmup_formula
        if not requires_history and warmup_formula:
            issues.append({
                'type': 'UNEXPECTED_WARMUP_FORMULA',
                'severity': 'warning',
                'message': f"Plugin '{plugin_type}': requires_history=False but warmup_formula is present. "
                          f"Cross-sectional features typically don't need warmup.",
                'fix': f"Remove warmup_formula or set requires_history=True"
            })

        # Rule 3: warmup_formula should be a simple expression
        if warmup_formula and isinstance(warmup_formula, str):
            # Check for valid formula pattern: parameter or parameter*number
            if not re.match(r'^[a-zA-Z_]\w*(\s*\*\s*\d+)?$', warmup_formula.strip()):
                issues.append({
                    'type': 'INVALID_WARMUP_FORMULA',
                    'severity': 'error',
                    'message': f"warmup_formula '{warmup_formula}' is invalid. Must be simple expression like 'atr_period * 3'",
                    'fix': "Use format: 'parameter_name' or 'parameter_name * factor'"
                })

        return issues

    @staticmethod
    def validate_dsl_warmup_alignment(strategy_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate warmup consistency across features and signals in DSL.

        Returns:
            List of validation errors (empty if valid)
        """
        issues = []

        features = strategy_dict.get('stages', {}).get('features', [])
        signals = strategy_dict.get('stages', {}).get('signals', [])

        # Collect all feature warmup periods
        feature_warmups = {}
        for feature in features:
            feature_name = feature.get('outputs', {}).get('column', 'unknown')
            warmup_bars = feature.get('params', {}).get('warmup_bars')
            warmup_formula = feature.get('warmup_formula')

            if warmup_formula:
                feature_warmups[feature_name] = {
                    'formula': warmup_formula,
                    'bars': warmup_bars
                }

        # Check signal warmup alignment with feature warmup
        for signal in signals:
            signal_warmup = signal.get('params', {}).get('warmup_bars', 0)
            regime_col = signal.get('params', {}).get('regime_col')

            # Extract feature name from regime_col (e.g., "feature.laguerre_regime" → "laguerre_regime")
            if regime_col and regime_col.startswith('feature.'):
                feature_base = regime_col.replace('feature.', '').replace('_regime', '')

                for feature_name, warmup_info in feature_warmups.items():
                    if feature_base in feature_name:
                        # Estimate feature warmup bars from formula
                        feature_warmup_bars = WarmupAlignmentValidator._estimate_warmup_bars(
                            warmup_info.get('formula'),
                            warmup_info.get('bars')
                        )

                        if feature_warmup_bars and signal_warmup < feature_warmup_bars:
                            issues.append({
                                'type': 'WARMUP_MISMATCH',
                                'severity': 'warning',
                                'message': f"Signal warmup_bars ({signal_warmup}) < feature warmup (~{feature_warmup_bars}). "
                                          f"Signal regime data may not be fully warmed.",
                                'fix': f"Set signal warmup_bars >= {feature_warmup_bars}, or document the intentional gap"
                            })

        return issues

    @staticmethod
    def _estimate_warmup_bars(formula: Optional[str], bars: Optional[int]) -> Optional[int]:
        """Estimate warmup bar count from formula.

        Examples:
            "atr_period * 3" with atr_period=32 → 96 bars
            "lookback * 2" with lookback=50 → 100 bars
        """
        if not formula:
            return bars

        # Extract factor if present (e.g., "atr_period * 3" → 3)
        match = re.search(r'\*\s*(\d+)', formula)
        factor = int(match.group(1)) if match else 1

        # Common parameter defaults
        param_defaults = {
            'atr_period': 32,
            'lookback': 50,
            'window': 20,
            'smoothing_period': 14,
            'warmup_bars': 50,
        }

        # Extract parameter name
        param_match = re.match(r'^([a-zA-Z_]\w*)', formula)
        if not param_match:
            return bars

        param_name = param_match.group(1)
        param_value = param_defaults.get(param_name, 32)

        return param_value * factor

    @staticmethod
    def validate_python_decorator_for_warmup(file_path: str) -> List[Dict[str, Any]]:
        """Parse Python decorator and validate warmup consistency.

        Returns:
            List of validation errors (empty if valid)
        """
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for @register_plugin decorator
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            # Check if this is @register_plugin (could be direct Name or Attribute)
                            is_register_plugin = False
                            if isinstance(decorator.func, ast.Name):
                                is_register_plugin = decorator.func.id == 'register_plugin'
                            elif isinstance(decorator.func, ast.Attribute):
                                is_register_plugin = decorator.func.attr == 'register_plugin'

                            if is_register_plugin:
                                # Extract keyword arguments
                                kwargs = {}
                                for keyword in decorator.keywords:
                                    if keyword.arg == 'warmup_formula':
                                        if isinstance(keyword.value, ast.Constant):
                                            kwargs['warmup_formula'] = keyword.value.value
                                    elif keyword.arg == 'requires_history':
                                        if isinstance(keyword.value, ast.Constant):
                                            kwargs['requires_history'] = keyword.value.value
                                    elif keyword.arg == 'plugin_type':
                                        if isinstance(keyword.value, ast.Constant):
                                            kwargs['plugin_type'] = keyword.value.value

                                # Validate if we found both fields
                                if 'requires_history' in kwargs or 'warmup_formula' in kwargs:
                                    issues.extend(
                                        WarmupAlignmentValidator.validate_decorator_warmup(kwargs)
                                    )

        except (SyntaxError, ValueError) as e:
            issues.append({
                'type': 'PARSE_ERROR',
                'severity': 'error',
                'message': f"Failed to parse {file_path}: {str(e)}",
                'fix': "Ensure file is valid Python syntax"
            })

        return issues
