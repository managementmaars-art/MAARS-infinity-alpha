#!/usr/bin/env python3
"""
Form data validation utility for chrome-form-filler skill.

Validates form data before submission:
- Email format validation
- Phone number format checking
- Required field verification
- Sensitive field detection
- Value format suggestions

Usage:
    python validate_form.py --check-email "user@example.com"
    python validate_form.py --check-phone "(555) 123-4567"
    python validate_form.py --detect-sensitive "password" "credit_card"
    python validate_form.py --validate-form form_data.json
"""

import argparse
import json
import re
from typing import Dict, List, Tuple


class FormValidator:
    """Validates form field data for common issues."""

    # Sensitive field patterns (case-insensitive)
    SENSITIVE_PATTERNS = [
        r"password",
        r"pwd",
        r"passwd",
        r"cc",
        r"credit.?card",
        r"card.?number",
        r"cvv",
        r"cvc",
        r"ssn",
        r"social.?security",
        r"bank",
        r"account.?number",
        r"routing",
        r"pin",
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email:
            self.errors.append("Email is empty")
            return False

        # Basic email regex
        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

        if not re.match(email_pattern, email):
            self.errors.append(f"Invalid email format: {email}")
            self.suggestions.append(
                "Email must contain @ and domain (e.g., user@example.com)"
            )
            return False

        # Check for common mistakes
        if email.endswith("@"):
            self.errors.append("Email missing domain after @")
            return False

        if "@" not in email:
            self.errors.append("Email missing @ symbol")
            return False

        # Check for spaces
        if " " in email:
            self.warnings.append("Email contains spaces (likely invalid)")

        return True

    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number format (flexible).

        Args:
            phone: Phone number to validate

        Returns:
            True if appears valid, False otherwise
        """
        if not phone:
            self.errors.append("Phone number is empty")
            return False

        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-\(\)\+\.]", "", phone)

        # Check if remaining characters are digits
        if not cleaned.isdigit():
            self.errors.append(
                f"Phone number contains invalid characters: {phone}"
            )
            self.suggestions.append(
                "Phone should contain only digits and formatting (e.g., (555) 123-4567)"
            )
            return False

        # Check length (7-15 digits is reasonable for most formats)
        if len(cleaned) < 7:
            self.warnings.append(
                f"Phone number seems short ({len(cleaned)} digits)"
            )
        elif len(cleaned) > 15:
            self.warnings.append(
                f"Phone number seems long ({len(cleaned)} digits)"
            )

        return True

    def detect_sensitive_field(self, field_name: str, field_type: str = "") -> bool:
        """
        Detect if field is sensitive and should not be auto-filled.

        Args:
            field_name: Field name or label
            field_type: Input type attribute (e.g., "password")

        Returns:
            True if sensitive, False otherwise
        """
        # Check input type
        if field_type == "password":
            return True

        # Check field name against sensitive patterns
        name_lower = field_name.lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, name_lower):
                return True

        return False

    def validate_required_fields(
        self, field_data: Dict[str, str], required_fields: List[str]
    ) -> bool:
        """
        Verify all required fields have values.

        Args:
            field_data: Dictionary of field names to values
            required_fields: List of required field names

        Returns:
            True if all required fields filled, False otherwise
        """
        missing = []
        for field in required_fields:
            if field not in field_data or not field_data[field]:
                missing.append(field)

        if missing:
            self.errors.append(f"Missing required fields: {', '.join(missing)}")
            return False

        return True

    def suggest_corrections(self, field_name: str, value: str) -> List[str]:
        """
        Suggest corrections for common field mistakes.

        Args:
            field_name: Name of the field
            value: Current value

        Returns:
            List of suggestions
        """
        suggestions = []

        # Email-specific suggestions
        if "email" in field_name.lower():
            if "@" not in value:
                suggestions.append(f"Add '@domain.com' to '{value}'")
            elif value.endswith("@"):
                suggestions.append("Add domain after @ (e.g., example.com)")

        # Phone-specific suggestions
        if "phone" in field_name.lower() or "tel" in field_name.lower():
            # Suggest formatting if just digits
            if value.isdigit():
                if len(value) == 10:
                    formatted = f"({value[:3]}) {value[3:6]}-{value[6:]}"
                    suggestions.append(f"Consider format: {formatted}")

        # URL-specific suggestions
        if "url" in field_name.lower() or "website" in field_name.lower():
            if not value.startswith(("http://", "https://")):
                suggestions.append(f"Add 'https://' prefix: https://{value}")

        return suggestions

    def validate_form_data(
        self, form_data: Dict[str, any], schema: Dict[str, any] = None
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete form data.

        Args:
            form_data: Dictionary of field names to values
            schema: Optional schema with field types and requirements

        Returns:
            Tuple of (is_valid, issues_dict)
        """
        issues = {"errors": [], "warnings": [], "sensitive": [], "suggestions": []}

        if schema:
            # Validate against schema
            required_fields = [
                name for name, spec in schema.items() if spec.get("required", False)
            ]

            # Check required fields
            if not self.validate_required_fields(form_data, required_fields):
                issues["errors"].extend(self.errors)

            # Validate each field
            for field_name, field_spec in schema.items():
                field_type = field_spec.get("type", "text")
                value = form_data.get(field_name, "")

                # Check if sensitive
                if self.detect_sensitive_field(field_name, field_type):
                    issues["sensitive"].append(
                        f"{field_name} (type: {field_type}) is sensitive - DO NOT AUTO-FILL"
                    )
                    continue

                # Type-specific validation
                if field_type == "email" and value:
                    if not self.validate_email(value):
                        issues["errors"].extend(self.errors)
                        issues["suggestions"].extend(self.suggestions)
                        self.errors = []
                        self.suggestions = []

                elif field_type in ("tel", "phone") and value:
                    if not self.validate_phone(value):
                        issues["warnings"].extend(self.warnings)
                        issues["suggestions"].extend(self.suggestions)
                        self.warnings = []
                        self.suggestions = []

                # Get field-specific suggestions
                field_suggestions = self.suggest_corrections(field_name, value)
                if field_suggestions:
                    issues["suggestions"].extend(
                        [f"{field_name}: {s}" for s in field_suggestions]
                    )

        is_valid = len(issues["errors"]) == 0

        return is_valid, issues

    def print_report(self, issues: Dict[str, List[str]]):
        """Print validation report."""
        print("\n=== Form Validation Report ===\n")

        if issues["errors"]:
            print("❌ ERRORS:")
            for error in issues["errors"]:
                print(f"   - {error}")
            print()

        if issues["sensitive"]:
            print("⚠️  SENSITIVE FIELDS (manual fill required):")
            for field in issues["sensitive"]:
                print(f"   - {field}")
            print()

        if issues["warnings"]:
            print("⚠️  WARNINGS:")
            for warning in issues["warnings"]:
                print(f"   - {warning}")
            print()

        if issues["suggestions"]:
            print("💡 SUGGESTIONS:")
            for suggestion in issues["suggestions"]:
                print(f"   - {suggestion}")
            print()

        if not any(issues.values()):
            print("✅ All validations passed!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate form data for chrome-form-filler skill"
    )

    parser.add_argument("--check-email", help="Validate email address")
    parser.add_argument("--check-phone", help="Validate phone number")
    parser.add_argument(
        "--detect-sensitive",
        nargs="+",
        help="Check if field names are sensitive",
    )
    parser.add_argument(
        "--validate-form",
        help="Validate complete form data from JSON file",
    )

    args = parser.parse_args()

    validator = FormValidator()

    if args.check_email:
        print(f"Validating email: {args.check_email}")
        is_valid = validator.validate_email(args.check_email)
        if is_valid:
            print("✅ Email is valid")
        else:
            print("❌ Email validation failed:")
            for error in validator.errors:
                print(f"   - {error}")
            if validator.suggestions:
                print("💡 Suggestions:")
                for suggestion in validator.suggestions:
                    print(f"   - {suggestion}")

    elif args.check_phone:
        print(f"Validating phone: {args.check_phone}")
        is_valid = validator.validate_phone(args.check_phone)
        if is_valid:
            print("✅ Phone number appears valid")
        else:
            print("❌ Phone validation failed:")
            for error in validator.errors:
                print(f"   - {error}")
        if validator.warnings:
            print("⚠️  Warnings:")
            for warning in validator.warnings:
                print(f"   - {warning}")

    elif args.detect_sensitive:
        print("Checking for sensitive fields:")
        for field_name in args.detect_sensitive:
            is_sensitive = validator.detect_sensitive_field(field_name)
            status = "⚠️  SENSITIVE" if is_sensitive else "✅ Safe"
            print(f"   {status}: {field_name}")

    elif args.validate_form:
        with open(args.validate_form) as f:
            data = json.load(f)

        form_data = data.get("data", {})
        schema = data.get("schema", None)

        is_valid, issues = validator.validate_form_data(form_data, schema)
        validator.print_report(issues)

        if is_valid:
            print("✅ Form validation PASSED - safe to submit")
            exit(0)
        else:
            print("❌ Form validation FAILED - resolve errors before submission")
            exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
