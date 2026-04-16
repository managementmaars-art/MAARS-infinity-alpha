#!/usr/bin/env python
"""ADF validation utility for checking document structure before submission to Jira."""

import json
import sys
from typing import Any, Optional


class ADFValidator:
    """Validates ADF documents for correctness."""

    # Node types and their requirements
    BLOCK_NODES = {
        "heading": {"requires": ["content"], "optional": ["attrs"]},
        "paragraph": {"requires": ["content"]},
        "bulletList": {"requires": ["content"]},
        "orderedList": {"requires": ["content"], "optional": ["attrs"]},
        "taskList": {"requires": ["content"], "optional": ["attrs"]},
        "taskItem": {"requires": ["content"], "optional": ["attrs"]},
        "decisionList": {"requires": ["content"], "optional": ["attrs"]},
        "decisionItem": {"requires": ["content"], "optional": ["attrs"]},
        "listItem": {"requires": ["content"]},
        "codeBlock": {"requires": ["content"], "optional": ["attrs"]},
        "panel": {"requires": ["content", "attrs"]},
        "blockquote": {"requires": ["content"]},
        "expand": {"requires": ["content", "attrs"]},
        "rule": {"requires": []},
        "table": {"requires": ["content"], "optional": ["attrs"]},
        "tableRow": {"requires": ["content"]},
        "tableHeader": {"requires": ["content"]},
        "tableCell": {"requires": ["content"]},
    }

    INLINE_NODES = {
        "text": {"requires": ["text"]},
        "emoji": {"requires": ["attrs"]},
        "mention": {"requires": ["attrs"]},
        "date": {"requires": ["attrs"]},
        "status": {"requires": ["attrs"]},
        "inlineCard": {"requires": ["attrs"]},
        "hardBreak": {"requires": []},
    }

    VALID_MARKS = {
        "strong", "em", "code", "underline", "strike", "link",
        "subsup", "textColor", "backgroundColor", "border",
        "alignment", "indentation", "annotation", "fragment"
    }

    def __init__(self):
        """Initialize validator."""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, adf: Any) -> tuple[bool, list[str], list[str]]:
        """Validate ADF document.

        Args:
            adf: ADF document to validate

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        if not isinstance(adf, dict):
            self.errors.append("Root must be an object/dictionary")
            return False, self.errors, self.warnings

        # Check root properties
        if adf.get("version") != 1:
            self.errors.append("Missing or invalid 'version' (must be 1)")

        if adf.get("type") != "doc":
            self.errors.append("Missing or invalid root 'type' (must be 'doc')")

        if "content" not in adf:
            self.errors.append("Root missing 'content' array")
            return False, self.errors, self.warnings

        if not isinstance(adf["content"], list):
            self.errors.append("Root 'content' must be an array")
            return False, self.errors, self.warnings

        # Validate content
        for i, node in enumerate(adf["content"]):
            self._validate_block_node(node, path=f"content[{i}]")

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_block_node(self, node: Any, path: str = "node") -> None:
        """Validate a block-level node."""
        if not isinstance(node, dict):
            self.errors.append(f"At {path}: Node must be an object")
            return

        node_type = node.get("type")
        if not node_type:
            self.errors.append(f"At {path}: Missing 'type' property")
            return

        if node_type not in self.BLOCK_NODES:
            self.errors.append(f"At {path}: Unknown block node type '{node_type}'")
            return

        # Check required properties
        spec = self.BLOCK_NODES[node_type]
        for required in spec.get("requires", []):
            if required not in node:
                self.errors.append(f"At {path}: {node_type} requires '{required}' property")

        # Validate attributes if present
        if "attrs" in node:
            self._validate_attrs(node["attrs"], node_type, path)

        # Validate content
        if "content" in node:
            if not isinstance(node["content"], list):
                self.errors.append(f"At {path}: 'content' must be an array")
                return

            # Special handling for different node types
            if node_type in ["bulletList", "orderedList"]:
                # Content must be listItem nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict) and child.get("type") != "listItem":
                        self.errors.append(
                            f"At {path}.content[{i}]: {node_type} can only contain listItem nodes"
                        )
                    else:
                        self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type == "taskList":
                # Content must be taskItem nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict) and child.get("type") != "taskItem":
                        self.errors.append(
                            f"At {path}.content[{i}]: taskList can only contain taskItem nodes"
                        )
                    else:
                        self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type == "decisionList":
                # Content must be decisionItem nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict) and child.get("type") != "decisionItem":
                        self.errors.append(
                            f"At {path}.content[{i}]: decisionList can only contain decisionItem nodes"
                        )
                    else:
                        self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type == "table":
                # Content must be tableRow nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict) and child.get("type") != "tableRow":
                        self.errors.append(
                            f"At {path}.content[{i}]: table can only contain tableRow nodes"
                        )
                    else:
                        self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type == "tableRow":
                # Content must be tableHeader or tableCell nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict):
                        child_type = child.get("type")
                        if child_type not in ["tableHeader", "tableCell"]:
                            self.errors.append(
                                f"At {path}.content[{i}]: tableRow can only contain tableHeader or tableCell nodes"
                            )
                        else:
                            self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type in ["panel", "listItem", "tableHeader", "tableCell", "blockquote", "expand"]:
                # These can contain block nodes
                for i, child in enumerate(node["content"]):
                    self._validate_block_node(child, path=f"{path}.content[{i}]")

            elif node_type in ["taskItem", "decisionItem"]:
                # These contain inline nodes
                for i, child in enumerate(node["content"]):
                    self._validate_inline_node(child, path=f"{path}.content[{i}]")

            elif node_type in ["heading", "paragraph"]:
                # These contain inline nodes
                for i, child in enumerate(node["content"]):
                    self._validate_inline_node(child, path=f"{path}.content[{i}]")

            elif node_type == "codeBlock":
                # Content must be text nodes
                for i, child in enumerate(node["content"]):
                    if isinstance(child, dict) and child.get("type") != "text":
                        self.errors.append(
                            f"At {path}.content[{i}]: codeBlock can only contain text nodes"
                        )
                    else:
                        self._validate_inline_node(child, path=f"{path}.content[{i}]")

    def _validate_inline_node(self, node: Any, path: str = "node") -> None:
        """Validate an inline node."""
        if not isinstance(node, dict):
            self.errors.append(f"At {path}: Node must be an object")
            return

        node_type = node.get("type")
        if not node_type:
            self.errors.append(f"At {path}: Missing 'type' property")
            return

        if node_type not in self.INLINE_NODES and node_type != "hardBreak":
            # Check if it's a block node in wrong place
            if node_type in self.BLOCK_NODES:
                self.errors.append(
                    f"At {path}: Block node '{node_type}' cannot be used in inline context"
                )
            else:
                self.errors.append(f"At {path}: Unknown inline node type '{node_type}'")
            return

        # Check required properties
        if node_type in self.INLINE_NODES:
            spec = self.INLINE_NODES[node_type]
            for required in spec.get("requires", []):
                if required not in node:
                    self.errors.append(f"At {path}: {node_type} requires '{required}' property")

        # Validate text node specifically
        if node_type == "text":
            if "text" not in node:
                self.errors.append(f"At {path}: text node requires 'text' property")
            elif not isinstance(node["text"], str):
                self.errors.append(f"At {path}: text node 'text' must be a string")

            # Validate marks
            if "marks" in node:
                self._validate_marks(node["marks"], path)

    def _validate_attrs(self, attrs: Any, node_type: str, path: str) -> None:
        """Validate node attributes."""
        if not isinstance(attrs, dict):
            self.errors.append(f"At {path}: 'attrs' must be an object")
            return

        # Node-specific attribute validation
        if node_type == "heading":
            if "level" in attrs:
                level = attrs["level"]
                if not isinstance(level, int) or level < 1 or level > 6:
                    self.errors.append(f"At {path}: heading level must be 1-6, got {level}")
        elif node_type == "panel":
            if "panelType" in attrs:
                panel_type = attrs["panelType"]
                valid_types = {"info", "note", "tip", "warning", "success", "error", "custom"}
                if panel_type not in valid_types:
                    self.errors.append(
                        f"At {path}: invalid panelType '{panel_type}' (must be one of {valid_types})"
                    )
        elif node_type == "codeBlock":
            if "language" in attrs:
                lang = attrs["language"]
                if not isinstance(lang, str):
                    self.errors.append(f"At {path}: language must be a string")
        elif node_type == "status":
            if "text" not in attrs:
                self.errors.append(f"At {path}: status requires 'text' attribute")
            if "color" in attrs:
                color = attrs["color"]
                valid_colors = {"neutral", "purple", "blue", "red", "yellow", "green"}
                if color not in valid_colors:
                    self.errors.append(
                        f"At {path}: invalid status color '{color}' (must be one of {valid_colors})"
                    )
        elif node_type in ["taskItem", "decisionItem"]:
            if "localId" not in attrs:
                self.warnings.append(f"At {path}: {node_type} should have 'localId' attribute")
            if node_type == "taskItem" and "state" in attrs:
                state = attrs["state"]
                valid_states = {"TODO", "DONE"}
                if state not in valid_states:
                    self.errors.append(
                        f"At {path}: invalid taskItem state '{state}' (must be one of {valid_states})"
                    )
        elif node_type == "expand":
            if "title" not in attrs:
                self.errors.append(f"At {path}: expand requires 'title' attribute")

    def _validate_marks(self, marks: Any, path: str) -> None:
        """Validate text formatting marks."""
        if not isinstance(marks, list):
            self.errors.append(f"At {path}: 'marks' must be an array")
            return

        for i, mark in enumerate(marks):
            if not isinstance(mark, dict):
                self.errors.append(f"At {path}.marks[{i}]: mark must be an object")
                continue

            mark_type = mark.get("type")
            if not mark_type:
                self.errors.append(f"At {path}.marks[{i}]: mark requires 'type' property")
                continue

            if mark_type not in self.VALID_MARKS:
                self.errors.append(f"At {path}.marks[{i}]: unknown mark type '{mark_type}'")


def validate_file(filename: str) -> int:
    """Validate ADF from a JSON file.

    Args:
        filename: Path to JSON file containing ADF

    Returns:
        Exit code (0 for valid, 1 for invalid)
    """
    try:
        with open(filename, "r") as f:
            adf = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return 1

    validator = ADFValidator()
    is_valid, errors, warnings = validator.validate(adf)

    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s):\n")
        for error in errors:
            print(f"  • {error}")
        print()

    if warnings:
        print(f"⚠️  {len(warnings)} warning(s):\n")
        for warning in warnings:
            print(f"  • {warning}")
        print()

    if is_valid:
        print("✅ ADF is valid!")
        return 0
    else:
        return 1


def validate_string(adf_str: str) -> tuple[bool, list[str], list[str]]:
    """Validate ADF from a JSON string.

    Args:
        adf_str: JSON string containing ADF

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    try:
        adf = json.loads(adf_str)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"], []

    validator = ADFValidator()
    return validator.validate(adf)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_adf.py <json_file>")
        print("Validates ADF document structure")
        sys.exit(1)

    exit_code = validate_file(sys.argv[1])
    sys.exit(exit_code)
