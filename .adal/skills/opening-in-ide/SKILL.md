---
name: opening-in-ide
description: Opens a file or folder in a supported IDE using the nearest workspace or project context when available. Use when the user asks to open code in Rider, WebStorm, VS Code, Cursor, Windsurf, or a generic IDE from the CLI.
license: MIT
compatibility: Intended for OpenCode/Codex-style agents on Linux, macOS, or Windows. Requires Bash or PowerShell plus supported IDE CLIs on PATH (`rider`, `webstorm`, `code`, `cursor`, `windsurf` on Unix-like systems; `rider`, `rider.bat`, `rider64.exe`, `webstorm`, `webstorm.bat`, `webstorm64.exe`, `code`, `code.cmd`, `cursor`, `cursor.cmd`, `windsurf`, or `windsurf.cmd` on Windows).
metadata:
  author: David Orolin
  version: "1.0.2"
---

## Purpose

Use this skill when the user wants to open a file or project in a supported IDE from the CLI, while preserving solution, project, or workspace context when possible.

## Behavior

1. Accept a file or directory path (default `.`) and an optional line number.
2. When the user names a specific supported IDE, use the matching launcher only.
3. When the user asks for a generic IDE:
   - Run the installed-IDE detection script for the current platform.
   - If no supported IDE is installed, report that none of the supported IDEs are available.
   - If exactly one supported IDE is installed, use it without asking.
   - If multiple supported IDEs are installed, ask the user which one to use.
   - Prefer an interactive multi-choice prompt when the runtime supports it.
   - Populate the choices from the detected installed IDEs instead of hardcoding a fixed set.
   - If the runtime does not support interactive choices, ask a single concise text question listing the available installed IDEs.
   - Do not guess when multiple valid installed IDEs are available and the user did not specify one.
4. If the user explicitly requests an IDE that is not installed, return a clear error and do not fall back to another IDE.
5. Launch the chosen IDE in non-blocking mode (fire-and-forget) so the terminal session is not held open.

## IDE-specific behavior

### Rider

1. Walk upward from the target location to find the nearest directory containing one or more `*.sln` files.
2. If a solution is found, open Rider with the solution and target path.
3. If no solution is found, fall back to the nearest `*.csproj`.
4. If neither is found, open the target directly.
5. When multiple matching files exist in one directory, prefer the file whose basename matches the directory name; otherwise choose alphabetically.

### WebStorm

1. Walk upward from the target location to find the nearest directory containing `.idea`.
2. If `.idea` is found, open WebStorm with that directory as context.
3. If no `.idea` exists, fall back to the nearest JavaScript or TypeScript project root containing one of: `package.json`, `pnpm-workspace.yaml`, `yarn.lock`, `package-lock.json`, `bun.lock`, `bun.lockb`, `tsconfig.json`, or `jsconfig.json`.
4. If no project root is found, open the target directly.
5. When opening a file at a line, use JetBrains `--line` behavior.
6. When opening a file without an explicit line number, still pass `--line 1` intentionally as a WebStorm workaround because some WebStorm builds can fail to open the file otherwise.
6. If WebStorm fails to open a requested file when only project context is provided, retry by anchoring the file open to line `1`.

### VS Code Family

1. Walk upward from the target location to find the nearest directory containing one or more `*.code-workspace` files.
2. If a workspace is found, open the chosen editor with that workspace as context.
3. If no workspace is found, fall back to the nearest `*.sln` and use that file's directory as context.
4. If no solution is found, fall back to the nearest `*.csproj` and use that file's directory as context.
5. If neither is found, open the target directly.
6. When opening a file at a line, use `--goto` behavior.
7. When multiple matching files exist in one directory, prefer the file whose basename matches the directory name; otherwise choose alphabetically.

## Scripts

Use:

- Linux/macOS IDE detection: `./skills/opening-in-ide/scripts/list-installed-ides.sh`
- Windows IDE detection: `./skills/opening-in-ide/scripts/list-installed-ides.ps1`
- Linux/macOS Rider launcher: `./skills/opening-in-ide/scripts/open-in-rider.sh <path> [--line <n>]`
- Windows Rider launcher: `./skills/opening-in-ide/scripts/open-in-rider.ps1 <path> [--line <n>]`
- Linux/macOS WebStorm launcher: `./skills/opening-in-ide/scripts/open-in-webstorm.sh <path> [--line <n>]`
- Windows WebStorm launcher: `./skills/opening-in-ide/scripts/open-in-webstorm.ps1 <path> [--line <n>]`
- Linux/macOS VS Code launcher: `./skills/opening-in-ide/scripts/open-in-code.sh <path> [--line <n>]`
- Windows VS Code launcher: `./skills/opening-in-ide/scripts/open-in-code.ps1 <path> [--line <n>]`
- Linux/macOS Cursor launcher: `./skills/opening-in-ide/scripts/open-in-cursor.sh <path> [--line <n>]`
- Windows Cursor launcher: `./skills/opening-in-ide/scripts/open-in-cursor.ps1 <path> [--line <n>]`
- Linux/macOS Windsurf launcher: `./skills/opening-in-ide/scripts/open-in-windsurf.sh <path> [--line <n>]`
- Windows Windsurf launcher: `./skills/opening-in-ide/scripts/open-in-windsurf.ps1 <path> [--line <n>]`

Examples:

- `./skills/opening-in-ide/scripts/list-installed-ides.sh`
- `./skills/opening-in-ide/scripts/open-in-rider.sh src/MyFile.cs --line 120`
- `./skills/opening-in-ide/scripts/open-in-webstorm.sh src/app.ts --line 42`
- `./skills/opening-in-ide/scripts/open-in-code.sh src/MyFile.cs --line 120`
- `./skills/opening-in-ide/scripts/open-in-cursor.sh src/MyFile.cs --line 120`
- `./skills/opening-in-ide/scripts/open-in-windsurf.sh src/MyFile.cs --line 120`
- `./skills/opening-in-ide/scripts/open-in-rider.ps1 .`
- `./skills/opening-in-ide/scripts/open-in-webstorm.ps1 .`
- `./skills/opening-in-ide/scripts/open-in-code.ps1 .`
- `./skills/opening-in-ide/scripts/open-in-cursor.ps1 .`
- `./skills/opening-in-ide/scripts/open-in-windsurf.ps1 .`

## Notes

- Current supported IDE identifiers are `rider`, `webstorm`, `code`, `cursor`, and `windsurf`.
- The detection scripts print one installed IDE per line and succeed even when none are installed.
- Rider requires CLI availability on `PATH` (`rider` on Unix-like systems; `rider`, `rider.bat`, or `rider64.exe` on Windows).
- WebStorm requires CLI availability on `PATH` (`webstorm` on Unix-like systems; `webstorm`, `webstorm.bat`, or `webstorm64.exe` on Windows).
- VS Code requires CLI availability on `PATH` (`code` on Unix-like systems; `code` or `code.cmd` on Windows).
- Cursor requires CLI availability on `PATH` (`cursor` on Unix-like systems; `cursor` or `cursor.cmd` on Windows).
- Windsurf requires CLI availability on `PATH` (`windsurf` on Unix-like systems; `windsurf` or `windsurf.cmd` on Windows).
- When more IDEs are added later, keep the generic-selection flow data-driven: detect installed IDEs, present only valid installed options, and preserve the same interactive-choice-then-fallback behavior.
