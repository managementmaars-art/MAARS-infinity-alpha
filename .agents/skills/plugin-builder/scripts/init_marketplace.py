#!/usr/bin/env python3
"""
Marketplace 初始化脚本

用法:
    python init_marketplace.py [目录路径]

如果不指定路径，将在当前目录创建 marketplace 结构。
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def get_user_input():
    """获取用户输入"""
    print("\n=== Claude Code Marketplace 初始化 ===\n")

    # 基本信息
    plugin_name = input("插件名称 (kebab-case, 如: my-awesome-plugins): ").strip() or "my-plugins"
    description = input("插件描述: ").strip() or "我的 Claude Code 插件集合"

    # 作者信息
    author_name = input("作者名称: ").strip() or "Unknown"
    author_email = input("作者邮箱 (可选): ").strip() or None
    author_url = input("作者主页 (可选): ").strip() or None

    # 仓库信息
    repo_owner = input("仓库所有者/用户名: ").strip() or "username"
    repo_name = input("仓库名称: ").strip() or plugin_name
    homepage = input("项目主页 (可选): ").strip() or None
    repository = input("仓库 URL (可选): ").strip() or None

    # 许可证
    license_type = input("许可证 (默认: MIT): ").strip() or "MIT"

    # 组件选择
    print("\n选择要包含的组件 (用逗号分隔，如: 1,2,3):")
    print("  1. Skills")
    print("  2. Agents")
    print("  3. Commands")
    print("  4. Hooks")
    print("  5. MCP Servers")

    components = input("组件 (默认: 1): ").strip() or "1"
    component_list = [c.strip() for c in components.split(",")]

    has_skills = "1" in component_list
    has_agents = "2" in component_list
    has_commands = "3" in component_list
    has_hooks = "4" in component_list
    has_mcp = "5" in component_list

    # Marketplace 名称
    marketplace_name = input(f"\nMarketplace 名称 (默认: {repo_name}-marketplace): ").strip() or f"{repo_name}-marketplace"

    return {
        "plugin_name": plugin_name,
        "description": description,
        "author_name": author_name,
        "author_email": author_email,
        "author_url": author_url,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "homepage": homepage,
        "repository": repository,
        "license": license_type,
        "has_skills": has_skills,
        "has_agents": has_agents,
        "has_commands": has_commands,
        "has_hooks": has_hooks,
        "has_mcp": has_mcp,
        "marketplace_name": marketplace_name,
    }


def create_plugin_json(data, base_path):
    """创建 plugin.json"""
    plugin_data = {
        "name": data["plugin_name"],
        "version": "1.0.0",
        "description": data["description"],
        "author": {
            "name": data["author_name"],
        },
        "license": data["license"],
    }

    # 可选字段
    if data["author_email"]:
        plugin_data["author"]["email"] = data["author_email"]
    if data["author_url"]:
        plugin_data["author"]["url"] = data["author_url"]
    if data["homepage"]:
        plugin_data["homepage"] = data["homepage"]
    if data["repository"]:
        plugin_data["repository"] = data["repository"]

    # 注意：Claude Code 使用自动发现机制，默认目录（skills/、agents/、commands/）
    # 会被自动识别，无需在 plugin.json 中显式声明路径。

    plugin_path = base_path / ".claude-plugin" / "plugin.json"
    plugin_path.parent.mkdir(parents=True, exist_ok=True)

    with open(plugin_path, "w", encoding="utf-8") as f:
        json.dump(plugin_data, f, indent=2, ensure_ascii=False)

    print(f"  创建: {plugin_path}")


def create_marketplace_json(data, base_path):
    """创建 marketplace.json"""
    marketplace_data = {
        "name": data["marketplace_name"],
        "owner": {
            "name": data["repo_owner"],
        },
        "plugins": [
            {
                "name": data["plugin_name"],
                "source": "./",
                "description": data["description"],
                "author": {
                    "name": data["author_name"],
                },
                "license": data["license"],
            }
        ],
    }

    # 可选字段
    if data["repository"]:
        marketplace_data["plugins"][0]["repository"] = data["repository"]
    if data["homepage"]:
        marketplace_data["plugins"][0]["homepage"] = data["homepage"]

    marketplace_path = base_path / ".claude-plugin" / "marketplace.json"
    marketplace_path.parent.mkdir(parents=True, exist_ok=True)

    with open(marketplace_path, "w", encoding="utf-8") as f:
        json.dump(marketplace_data, f, indent=2, ensure_ascii=False)

    print(f"  创建: {marketplace_path}")


def create_directories(data, base_path):
    """创建组件目录"""
    dirs_to_create = []

    if data["has_skills"]:
        dirs_to_create.append("skills")
    if data["has_agents"]:
        dirs_to_create.append("agents")
    if data["has_commands"]:
        dirs_to_create.append("commands")
    if data["has_hooks"]:
        dirs_to_create.append("hooks")
    if data["has_mcp"]:
        # MCP 不需要目录，只需要配置文件
        pass

    for dir_name in dirs_to_create:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        # 创建 .gitkeep 文件
        (dir_path / ".gitkeep").touch()

        print(f"  创建: {dir_path}/")


def create_hooks_json(base_path):
    """创建 hooks.json 模板"""
    hooks_data = {
        "hooks": {
            "PreToolUse": [],
            "PostToolUse": [],
            "PreResponse": [],
            "PostResponse": [],
        }
    }

    hooks_path = base_path / "hooks" / "hooks.json"
    hooks_path.parent.mkdir(parents=True, exist_ok=True)

    with open(hooks_path, "w", encoding="utf-8") as f:
        json.dump(hooks_data, f, indent=2, ensure_ascii=False)

    print(f"  创建: {hooks_path}")


def create_mcp_json(base_path):
    """创建 .mcp.json 模板"""
    mcp_data = {
        "mcpServers": {}
    }

    mcp_path = base_path / ".mcp.json"

    with open(mcp_path, "w", encoding="utf-8") as f:
        json.dump(mcp_data, f, indent=2, ensure_ascii=False)

    print(f"  创建: {mcp_path}")


def create_readme(data, base_path):
    """创建 README.md"""
    repo_url = data["repository"] or f"https://github.com/{data['repo_owner']}/{data['repo_name']}"

    readme_content = f"""# {data['plugin_name']}

{data['description']}

## 安装

### 添加 Marketplace

```bash
/plugin marketplace add {data['repo_owner']}/{data['repo_name']}
```

### 安装插件

```bash
/plugin install {data['plugin_name']}@{data['repo_name']}
```

## 内容

"""

    components = []
    if data["has_skills"]:
        components.append("- **Skills**: 自定义技能")
    if data["has_agents"]:
        components.append("- **Agents**: AI 代理")
    if data["has_commands"]:
        components.append("- **Commands**: 斜杠命令")
    if data["has_hooks"]:
        components.append("- **Hooks**: 事件钩子")
    if data["has_mcp"]:
        components.append("- **MCP**: MCP 服务器")

    if components:
        readme_content += "\n".join(components) + "\n\n"

    readme_content += f"""## 作者

- **{data['author_name']}**

## 许可证

{data['license']}

---

*本仓库使用 [Claude Code](https://claude.ai/code) 插件系统管理。*
"""

    readme_path = base_path / "README.md"

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"  创建: {readme_path}")


def create_gitignore(base_path):
    """创建 .gitignore"""
    gitignore_content = """# Claude Code
.claude/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# OS
Thumbs.db
"""

    gitignore_path = base_path / ".gitignore"

    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gitignore_content)

    print(f"  创建: {gitignore_path}")


def main():
    parser = argparse.ArgumentParser(description="初始化 Claude Code Marketplace 结构")
    parser.add_argument("path", nargs="?", default=".", help="目标目录路径")
    parser.add_argument("--non-interactive", action="store_true", help="非交互模式（使用默认值）")

    args = parser.parse_args()

    base_path = Path(args.path).resolve()

    if base_path.exists() and list(base_path.iterdir()):
        response = input(f"目录 {base_path} 不为空，是否继续？(y/N): ").strip().lower()
        if response != "y":
            print("已取消")
            return

    # 获取用户输入
    if args.non_interactive:
        data = {
            "plugin_name": "my-plugins",
            "description": "我的 Claude Code 插件集合",
            "author_name": "Unknown",
            "author_email": None,
            "author_url": None,
            "repo_owner": "username",
            "repo_name": "my-plugins",
            "homepage": None,
            "repository": None,
            "license": "MIT",
            "has_skills": True,
            "has_agents": False,
            "has_commands": False,
            "has_hooks": False,
            "has_mcp": False,
            "marketplace_name": "my-plugins-marketplace",
        }
    else:
        data = get_user_input()

    # 创建目录
    base_path.mkdir(parents=True, exist_ok=True)

    print(f"\n在 {base_path} 创建 marketplace 结构:\n")

    # 创建配置文件
    create_plugin_json(data, base_path)
    create_marketplace_json(data, base_path)

    # 创建组件目录
    create_directories(data, base_path)

    # 创建特定配置文件
    if data["has_hooks"]:
        create_hooks_json(base_path)
    if data["has_mcp"]:
        create_mcp_json(base_path)

    # 创建文档
    create_readme(data, base_path)
    create_gitignore(base_path)

    print("\n=== 初始化完成 ===\n")

    # 显示后续步骤
    print("后续步骤:")
    print(f"  1. cd {base_path}")
    print("  2. 添加你的 skills/agents/commands 到相应目录")
    print("  3. 验证配置: python ~/.claude/skills/marketplace-builder/scripts/validate_plugin.py .")
    print("  4. 初始化 Git 仓库: git init")
    print("  5. 提交: git add . && git commit -m 'Initial marketplace setup'")
    print(f"  6. 推送到远程: git remote add origin {data['repository'] or 'YOUR_REPO_URL'}")
    print("     git push -u origin main")


if __name__ == "__main__":
    main()
