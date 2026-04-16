#!/usr/bin/env python3
"""
setup-activity-hook.py — installs a PostToolUse hook that logs every tool call
to per-subagent files under the Claude session history directory.

Each subagent gets its own log file keyed by session_id:
  ~/.claude/projects/<encoded-project-path>/bad-logs/<session_id>.log

Log format (tab-separated):
  <ISO timestamp> | <tool_name> | <key input detail>

Usage:
  python3 setup-activity-hook.py [--settings-path PATH] [--project-root PATH] [--remove]
  python3 setup-activity-hook.py --help
"""
import argparse
import json
import os
from pathlib import Path


BAD_HOOK_MARKER = "bad-logs"


def compute_log_dir(project_root: str) -> str:
    """
    Derives the per-project bad-logs directory path.
    Claude stores session history at: ~/.claude/projects/<encoded>/
    where <encoded> is the absolute path with leading / removed and / replaced by -.
    """
    home = str(Path.home())
    encoded = project_root.lstrip("/").replace("/", "-")
    return f"{home}/.claude/projects/{encoded}/bad-logs"


def build_hook_command(log_dir: str, project_root: str) -> str:
    """
    Builds the shell command that runs on every PostToolUse event.

    Directory structure:
      bad-logs/coordinator/<session_id>.log      — coordinator (cwd == project root)
      bad-logs/<story-basename>/<session_id>.log — story subagents (cwd is a worktree)

    The project root is baked in at setup time so the jq expression can compare
    cwd against it to distinguish the coordinator from story subagents.

    Reads stdin once into _BAD_IN, then extracts session_id and agent slug.
    Uses || true so hook failures never block Claude.
    """
    jq_entry = (
        "[now|todate, .tool_name, "
        "(.tool_input.file_path // .tool_input.command // .tool_input.description // "
        ".tool_input.pattern // .tool_input.query // "
        '(.tool_input | to_entries | map(.value | tostring) | first // ""))'
        '] | join(" | ")'
    )
    jq_agent = f'if .cwd == "{project_root}" then "coordinator" else (.cwd // "" | split("/") | last) end'
    return (
        f'_BAD_IN=$(cat); '
        f'_BAD_DIR="{log_dir}"; '
        f'_BAD_SID=$(printf \'%s\' "$_BAD_IN" | jq -r \'.session_id // "unknown"\' 2>/dev/null); '
        f'_BAD_AGENT=$(printf \'%s\' "$_BAD_IN" | jq -r \'{jq_agent}\' 2>/dev/null); '
        f'mkdir -p "$_BAD_DIR/$_BAD_AGENT" 2>/dev/null; '
        f'printf \'%s\' "$_BAD_IN" | jq -r \'{jq_entry}\' >> "$_BAD_DIR/$_BAD_AGENT/$_BAD_SID.log" 2>/dev/null || true'
    )


def load_settings(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: {path} contains invalid JSON: {e}", flush=True)
        raise SystemExit(1)


def save_settings(path: str, settings: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def install_hook(settings: dict, command: str) -> dict:
    """Add BAD activity hook, removing any existing one first (anti-zombie)."""
    hooks = settings.setdefault("hooks", {})
    entries = hooks.get("PostToolUse", [])
    # Remove existing BAD activity hook
    entries = [
        e for e in entries
        if not any(BAD_HOOK_MARKER in h.get("command", "") for h in e.get("hooks", []))
    ]
    entries.append({
        "matcher": "",
        "hooks": [{"type": "command", "command": command}]
    })
    hooks["PostToolUse"] = entries
    settings["hooks"] = hooks
    return settings


def remove_hook(settings: dict) -> dict:
    """Remove BAD activity hook."""
    hooks = settings.get("hooks", {})
    entries = hooks.get("PostToolUse", [])
    entries = [
        e for e in entries
        if not any(BAD_HOOK_MARKER in h.get("command", "") for h in e.get("hooks", []))
    ]
    if entries:
        hooks["PostToolUse"] = entries
    elif "PostToolUse" in hooks:
        del hooks["PostToolUse"]
    if not hooks:
        settings.pop("hooks", None)
    else:
        settings["hooks"] = hooks
    return settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install or remove the BAD activity log hook in .claude/settings.local.json"
    )
    parser.add_argument(
        "--settings-path",
        default=".claude/settings.local.json",
        help="Path to settings.local.json (default: .claude/settings.local.json)",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Absolute project root path (default: current working directory)",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove the BAD activity hook instead of installing it",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root or os.getcwd())
    settings = load_settings(args.settings_path)

    if args.remove:
        settings = remove_hook(settings)
        save_settings(args.settings_path, settings)
        print(f"BAD activity hook removed from {args.settings_path}")
    else:
        log_dir = compute_log_dir(project_root)
        command = build_hook_command(log_dir, project_root)
        settings = install_hook(settings, command)
        save_settings(args.settings_path, settings)
        print(f"BAD activity hook installed")
        print(f"  settings  : {args.settings_path}")
        print(f"  log dir   : {log_dir}/coordinator/<session_id>.log")
        print(f"            : {log_dir}/<story-basename>/<session_id>.log")


if __name__ == "__main__":
    main()
