#!/usr/bin/env python3
"""
Marketplace 插件验证脚本

用法:
    python validate_plugin.py [路径]

验证 plugin.json 和 marketplace.json 配置的正确性。
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ValidationResult:
    """验证结果"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def add_error(self, message: str):
        """添加错误"""
        self.errors.append(message)

    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)

    def add_info(self, message: str):
        """添加信息"""
        self.info.append(message)

    def is_valid(self) -> bool:
        """是否有效"""
        return len(self.errors) == 0

    def print_report(self):
        """打印报告"""
        if self.info:
            print("\n信息:")
            for info in self.info:
                print(f"  \u2139\ufe0f  {info}")

        if self.warnings:
            print("\n警告:")
            for warning in self.warnings:
                print(f"  \u26a0\ufe0f  {warning}")

        if self.errors:
            print("\n错误:")
            for error in self.errors:
                print(f"  \u274c  {error}")
        else:
            print("\u2705 验证通过！")


def validate_json_file(path: Path, result: ValidationResult) -> Dict[str, Any] | None:
    """验证 JSON 文件格式"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        result.add_error(f"文件不存在: {path}")
        return None
    except json.JSONDecodeError as e:
        result.add_error(f"JSON 格式错误 ({path}): {e}")
        return None


def validate_plugin_name(name: str, result: ValidationResult):
    """验证插件名称格式"""
    if not name:
        result.add_error("plugin.json: name 字段不能为空")
        return

    # 检查 kebab-case 格式
    if not all(c.islower() or c.isdigit() or c in "-_" for c in name):
        result.add_warning(f"plugin.json: name '{name}' 应使用 kebab-case 格式（小写字母、数字、连字符）")

    if name.startswith("-") or name.endswith("-"):
        result.add_error(f"plugin.json: name '{name}' 不能以连字符开头或结尾")


def validate_version(version: str, result: ValidationResult):
    """验证版本号格式"""
    if not version:
        result.add_error("plugin.json: version 字段不能为空")
        return

    parts = version.split(".")
    if len(parts) != 3:
        result.add_error(f"plugin.json: version '{version}' 应为 MAJOR.MINOR.PATCH 格式")
        return

    try:
        major, minor, patch = parts
        if not major.isdigit() or not minor.isdigit() or not patch.isdigit():
            result.add_error(f"plugin.json: version '{version}' 各部分应为数字")
    except ValueError:
        result.add_error(f"plugin.json: version '{version}' 格式错误")


def validate_author(author: Any, result: ValidationResult):
    """验证作者信息"""
    if not author:
        result.add_error("plugin.json: author 字段不能为空")
        return

    if not isinstance(author, dict):
        result.add_error("plugin.json: author 必须是对象")
        return

    if "name" not in author or not author["name"]:
        result.add_error("plugin.json: author.name 字段不能为空")


def validate_plugin_json(data: Dict[str, Any], base_path: Path, result: ValidationResult):
    """验证 plugin.json 内容"""
    # 必需字段
    required_fields = ["name", "version", "description", "author"]
    for field in required_fields:
        if field not in data:
            result.add_error(f"plugin.json: 缺少必需字段 '{field}'")

    # 验证 name
    if "name" in data:
        validate_plugin_name(data["name"], result)

    # 验证 version
    if "version" in data:
        validate_version(data["version"], result)

    # 验证 author
    if "author" in data:
        validate_author(data["author"], result)

    # 验证组件路径
    component_fields = {
        "skills": list,
        "agents": list,
        "commands": list,
    }

    for field, expected_type in component_fields.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                result.add_error(f"plugin.json: {field} 应为数组")
                continue

            for path in data[field]:
                component_path = base_path / path.lstrip("./")
                if not component_path.exists():
                    result.add_warning(f"plugin.json: {field} 路径不存在: {path}")
                elif not component_path.is_dir():
                    result.add_warning(f"plugin.json: {field} 路径不是目录: {path}")

    # 验证 hooks 路径
    if "hooks" in data:
        hooks_path = base_path / data["hooks"].lstrip("./")
        if not hooks_path.exists():
            result.add_warning(f"plugin.json: hooks 路径不存在: {data['hooks']}")
        else:
            # 验证 hooks.json 格式
            hooks_data = validate_json_file(hooks_path, result)
            if hooks_data:
                if "hooks" not in hooks_data:
                    result.add_warning(f"{data['hooks']}: 缺少 'hooks' 字段")

    # 验证 mcpServers 路径
    if "mcpServers" in data:
        mcp_path = base_path / data["mcpServers"].lstrip("./")
        if not mcp_path.exists():
            result.add_warning(f"plugin.json: mcpServers 路径不存在: {data['mcpServers']}")
        else:
            # 验证 .mcp.json 格式
            mcp_data = validate_json_file(mcp_path, result)
            if mcp_data:
                if "mcpServers" not in mcp_data:
                    result.add_warning(f"{data['mcpServers']}: 缺少 'mcpServers' 字段")


def validate_marketplace_json(data: Dict[str, Any], base_path: Path, result: ValidationResult):
    """验证 marketplace.json 内容"""
    # 必需字段
    required_fields = ["name", "owner", "plugins"]
    for field in required_fields:
        if field not in data:
            result.add_error(f"marketplace.json: 缺少必需字段 '{field}'")

    # 验证 owner
    if "owner" in data:
        if not isinstance(data["owner"], dict):
            result.add_error("marketplace.json: owner 必须是对象")
        elif "name" not in data["owner"] or not data["owner"]["name"]:
            result.add_error("marketplace.json: owner.name 字段不能为空")

    # 验证 plugins
    if "plugins" in data:
        if not isinstance(data["plugins"], list):
            result.add_error("marketplace.json: plugins 必须是数组")
            return

        if len(data["plugins"]) == 0:
            result.add_warning("marketplace.json: plugins 数组为空")

        for i, plugin in enumerate(data["plugins"]):
            if not isinstance(plugin, dict):
                result.add_error(f"marketplace.json: plugins[{i}] 必须是对象")
                continue

            if "name" not in plugin:
                result.add_error(f"marketplace.json: plugins[{i}] 缺少 'name' 字段")
            if "source" not in plugin:
                result.add_error(f"marketplace.json: plugins[{i}] 缺少 'source' 字段")


def validate_skill_files(skills_dirs: List[Path], result: ValidationResult):
    """验证 Skill 文件"""
    for skills_dir in skills_dirs:
        if not skills_dir.exists():
            continue

        for skill_path in skills_dir.glob("*/SKILL.md"):
            # 验证 YAML frontmatter
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if not content.startswith("---"):
                    result.add_warning(f"Skill 文件缺少 YAML frontmatter: {skill_path}")
                    continue

                # 提取 frontmatter
                try:
                    frontmatter_end = content.index("---", 3)
                    frontmatter = content[3:frontmatter_end].strip()

                    # 简单检查 name 和 description
                    if "name:" not in frontmatter:
                        result.add_warning(f"Skill 缺少 name 字段: {skill_path}")
                    if "description:" not in frontmatter:
                        result.add_warning(f"Skill 缺少 description 字段: {skill_path}")
                except ValueError:
                    result.add_warning(f"Skill frontmatter 格式错误: {skill_path}")

            except Exception as e:
                result.add_warning(f"无法读取 Skill 文件 {skill_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="验证 Claude Code Marketplace 插件配置")
    parser.add_argument("path", nargs="?", default=".", help="插件根目录路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")

    args = parser.parse_args()

    base_path = Path(args.path).resolve()

    if not base_path.exists():
        print(f"错误: 路径不存在: {base_path}")
        return 1

    result = ValidationResult()

    print(f"验证插件: {base_path}")
    print("=" * 50)

    # 查找 plugin.json
    plugin_json_path = base_path / ".claude-plugin" / "plugin.json"
    if plugin_json_path.exists():
        result.add_info(f"找到 plugin.json")
        plugin_data = validate_json_file(plugin_json_path, result)
        if plugin_data:
            validate_plugin_json(plugin_data, base_path, result)

            # 收集 skills 目录用于验证
            skills_dirs = []
            if "skills" in plugin_data:
                for skills_path in plugin_data["skills"]:
                    skills_dir = base_path / skills_path.lstrip("./")
                    if skills_dir.exists():
                        skills_dirs.append(skills_dir)

            # 验证 Skill 文件
            if skills_dirs and args.verbose:
                validate_skill_files(skills_dirs, result)
    else:
        result.add_error("未找到 .claude-plugin/plugin.json")

    # 查找 marketplace.json
    marketplace_json_path = base_path / ".claude-plugin" / "marketplace.json"
    if marketplace_json_path.exists():
        result.add_info(f"找到 marketplace.json")
        marketplace_data = validate_json_file(marketplace_json_path, result)
        if marketplace_data:
            validate_marketplace_json(marketplace_data, base_path, result)
    else:
        result.add_warning("未找到 .claude-plugin/marketplace.json")

    # 检查 README
    readme_path = base_path / "README.md"
    if not readme_path.exists():
        result.add_warning("缺少 README.md")

    # 打印报告
    result.print_report()

    return 0 if result.is_valid() else 1


if __name__ == "__main__":
    sys.exit(main())
