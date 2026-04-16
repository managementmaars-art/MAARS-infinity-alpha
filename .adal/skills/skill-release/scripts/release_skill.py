#!/usr/bin/env python3
"""
Skill Release Script - Sync skills from .agents/skills/ to skills/ and publish

Usage:
    python release_skill.py [--dry-run] [--skill SKILL_NAME]

Options:
    --dry-run        Show what would be done without making changes
    --skill NAME     Only process the specified skill

Workflow:
    1. Scan .agents/skills/ for skills
    2. Compare with skills/ directory
    3. Copy changed skills and bump version (patch)
    4. Run git add, commit, push
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def compute_dir_hash(dir_path: Path) -> str:
    """Compute a hash of all files in a directory for change detection."""
    hasher = hashlib.sha256()
    for file_path in sorted(dir_path.rglob("*")):
        if file_path.is_file() and not file_path.name.startswith("."):
            relative = file_path.relative_to(dir_path)
            hasher.update(str(relative).encode())
            hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def get_skill_version(skill_dir: Path) -> str:
    """Get skill version from package.json or return default."""
    package_json = skill_dir / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            return data.get("version", "1.0.0")
        except (json.JSONDecodeError, KeyError):
            pass
    return "1.0.0"


def copy_skill(
    source: Path, dest: Path, dry_run: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Copy skill from source to destination.

    Returns:
        (was_copied, version)
    """
    if not source.exists():
        print(f"  ❌ Source not found: {source}")
        return False, None

    source_hash = compute_dir_hash(source)
    dest_hash = compute_dir_hash(dest) if dest.exists() else None
    source_version = get_skill_version(source)

    if dest_hash == source_hash:
        dest_version = get_skill_version(dest) if dest.exists() else "1.0.0"
        print(f"  ✓ No changes (v{dest_version})")
        return False, None

    if dry_run:
        print(f"  [DRY-RUN] Would copy to {dest}")
        print(f"  [DRY-RUN] Version: v{source_version}")
        return True, source_version

    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(source, dest)

    legacy_version_file = dest / "version.txt"
    if legacy_version_file.exists():
        legacy_version_file.unlink()

    print(f"  ✅ Copied v{source_version}")
    return True, source_version


def run_git_commands(dry_run: bool = False) -> bool:
    """Run git add, commit, push."""
    commands = [
        ["git", "add", "."],
        ["git", "commit", "-m", "chore: release skills"],
        ["git", "push"],
    ]

    for cmd in commands:
        print(f"  Running: {' '.join(cmd)}")
        if dry_run:
            print(f"  [DRY-RUN] Skipping")
            continue

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # git commit may fail if nothing to commit
            if "commit" in cmd and "nothing to commit" in result.stdout:
                print(f"  ℹ️ Nothing to commit")
                continue
            print(f"  ❌ Command failed: {result.stderr}")
            return False
        print(f"  ✓ Success")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Release skills from .agents/skills/ to skills/"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--skill", type=str, help="Only process specified skill")
    args = parser.parse_args()

    # Determine paths
    project_root = Path.cwd()
    source_dir = project_root / ".agents" / "skills"
    dest_dir = project_root / "skills"

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        sys.exit(1)

    if not dest_dir.exists():
        print(f"❌ Destination directory not found: {dest_dir}")
        sys.exit(1)

    print(f"📁 Source: {source_dir}")
    print(f"📁 Destination: {dest_dir}")
    print(f"🔧 Dry run: {args.dry_run}")
    print()

    # Find skills in source directory (exclude skill-release itself)
    source_skills = [
        d
        for d in source_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists() and d.name not in ["skill-release", "performance-evaluation", "tapd-idle"]
    ]

    if args.skill:
        source_skills = [s for s in source_skills if s.name == args.skill]
        if not source_skills:
            print(f"❌ Skill not found: {args.skill}")
            sys.exit(1)

    print(f"🔍 Found {len(source_skills)} skill(s) to process")
    print()

    # Process each skill
    changed_skills = []
    for skill in sorted(source_skills, key=lambda x: x.name):
        print(f"📦 Processing: {skill.name}")
        dest_skill = dest_dir / skill.name
        copied, version = copy_skill(skill, dest_skill, args.dry_run)
        if copied:
            changed_skills.append((skill.name, version))
        print()

    # Summary
    if changed_skills:
        print("=" * 50)
        print("📋 Summary of changes:")
        for name, version in changed_skills:
            print(f"  • {name} → v{version}")
        print()

        # Git operations
        print("🔄 Git operations:")
        if args.dry_run:
            print("  [DRY-RUN] Would run git add, commit, push")
        else:
            run_git_commands(args.dry_run)
    else:
        print("✅ No changes detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
