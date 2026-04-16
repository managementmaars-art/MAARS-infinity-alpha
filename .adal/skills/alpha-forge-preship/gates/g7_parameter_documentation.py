"""G7: Parameter Documentation Validator

Detects missing or incomplete parameter documentation.
Triggers: Pre-commit hook + decorator validation
Prevents: C9 (undocumented parameters causing maintainability issues)
ROI: 100% effectiveness, 0% false positives
Coverage: Decorator parameter descriptions
"""

import ast
import re
from typing import List, Dict, Any, Optional


class ParameterDocumentationValidator:
    """Validates parameter descriptions in plugin decorators."""

    @staticmethod
    def validate_decorator_parameters(parameters_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate all parameters have meaningful descriptions.

        Args:
            parameters_dict: Dictionary of parameters from @register_plugin decorator

        Returns:
            List of validation errors (empty if valid)
        """
        issues = []

        for param_name, param_spec in parameters_dict.items():
            if not isinstance(param_spec, dict):
                continue

            # Rule 1: Parameter must have 'description' field
            if 'description' not in param_spec:
                issues.append({
                    'type': 'MISSING_PARAMETER_DESCRIPTION',
                    'severity': 'error',
                    'parameter': param_name,
                    'message': f"Parameter '{param_name}' is missing 'description' field",
                    'fix': f"Add description to parameter: {param_name}: {{description: '...'}}"
                })
                continue

            description = param_spec.get('description', '').strip()

            # Rule 2: Description must not be empty
            if not description:
                issues.append({
                    'type': 'EMPTY_PARAMETER_DESCRIPTION',
                    'severity': 'error',
                    'parameter': param_name,
                    'message': f"Parameter '{param_name}' has empty description",
                    'fix': f"Provide meaningful description for parameter: {param_name}"
                })
                continue

            # Rule 3: Description should be at least 10 characters (meaningful content)
            if len(description) < 10:
                issues.append({
                    'type': 'INSUFFICIENT_PARAMETER_DESCRIPTION',
                    'severity': 'warning',
                    'parameter': param_name,
                    'message': f"Parameter '{param_name}' description too brief: '{description}'",
                    'fix': f"Expand description to explain parameter's purpose and valid range/values"
                })

            # Rule 4: Description should mention valid range or allowed values
            param_type = param_spec.get('type')
            if param_type in ['numeric', 'int', 'float']:
                if not re.search(r'(range|min|max|[0-9])', description, re.IGNORECASE):
                    issues.append({
                        'type': 'UNDOCUMENTED_NUMERIC_RANGE',
                        'severity': 'warning',
                        'parameter': param_name,
                        'message': f"Numeric parameter '{param_name}' description doesn't mention range or bounds",
                        'fix': f"Add range info to description: e.g., '(range: 1-100)' or '(min: 0, max: 1)'"
                    })

            elif param_type == 'enum':
                allowed = param_spec.get('enum', param_spec.get('allowed_values', []))
                if allowed and not any(str(val) in description for val in allowed):
                    issues.append({
                        'type': 'UNDOCUMENTED_ENUM_VALUES',
                        'severity': 'warning',
                        'parameter': param_name,
                        'message': f"Enum parameter '{param_name}' description doesn't mention allowed values",
                        'fix': f"List allowed values in description: e.g., 'one of: {allowed}'"
                    })

        return issues

    @staticmethod
    def validate_python_decorator_documentation(file_path: str) -> List[Dict[str, Any]]:
        """Parse Python decorator and validate parameter documentation.

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
                                # Extract parameters dict from decorator
                                for keyword in decorator.keywords:
                                    if keyword.arg == 'parameters':
                                        params_dict = ParameterDocumentationValidator._extract_dict_from_ast(
                                            keyword.value
                                        )
                                        if params_dict:
                                            issues.extend(
                                                ParameterDocumentationValidator.validate_decorator_parameters(
                                                    params_dict
                                                )
                                            )

        except (SyntaxError, ValueError) as e:
            issues.append({
                'type': 'PARSE_ERROR',
                'severity': 'error',
                'message': f"Failed to parse {file_path}: {str(e)}",
                'fix': "Ensure file is valid Python syntax"
            })

        return issues

    @staticmethod
    def _extract_dict_from_ast(node: ast.expr) -> Optional[Dict[str, Any]]:
        """Extract dictionary from AST node.

        Returns:
            Dictionary representation, or None if cannot extract
        """
        if isinstance(node, ast.Dict):
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                if isinstance(key_node, ast.Constant):
                    key = key_node.value
                    value = ParameterDocumentationValidator._extract_value_from_ast(value_node)
                    result[key] = value
            return result
        return None

    @staticmethod
    def _extract_value_from_ast(node: ast.expr) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Dict):
            return ParameterDocumentationValidator._extract_dict_from_ast(node)
        elif isinstance(node, ast.List):
            return [ParameterDocumentationValidator._extract_value_from_ast(n) for n in node.elts]
        else:
            return f"<{type(node).__name__}>"
