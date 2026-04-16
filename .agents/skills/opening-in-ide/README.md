# opening-in-ide

Open a file or folder in JetBrains Rider, JetBrains WebStorm, Visual Studio Code, Cursor, or Windsurf from an agent workflow, using the nearest workspace or project context when available.

The launchers are non-blocking (fire-and-forget) so terminal-based agents can continue immediately after the IDE opens.

## Contents

- `SKILL.md`: Agent-facing skill instructions and metadata
- `scripts/list-installed-ides.sh`: Linux/macOS supported-IDE detection
- `scripts/list-installed-ides.ps1`: Windows PowerShell supported-IDE detection
- `scripts/open-in-rider.sh`: Linux/macOS Rider launcher
- `scripts/open-in-rider.ps1`: Windows PowerShell Rider launcher
- `scripts/open-in-webstorm.sh`: Linux/macOS WebStorm launcher
- `scripts/open-in-webstorm.ps1`: Windows PowerShell WebStorm launcher
- `scripts/open-in-code.sh`: Linux/macOS VS Code launcher
- `scripts/open-in-code.ps1`: Windows PowerShell VS Code launcher
- `scripts/open-in-cursor.sh`: Linux/macOS Cursor launcher
- `scripts/open-in-cursor.ps1`: Windows PowerShell Cursor launcher
- `scripts/open-in-windsurf.sh`: Linux/macOS Windsurf launcher
- `scripts/open-in-windsurf.ps1`: Windows PowerShell Windsurf launcher
- `scripts/lib/*`: shared Bash and PowerShell launcher helpers
- `evals/evals.json`: agent-facing trigger and behavior evals
- `evals/run-harness.py`: non-launching eval-quality harness
- `tests/scenarios.md`: Behavior and edge-case test scenarios
- `tests/run-harness.py`: Runnable isolated validation harness
- `tests/README.md`: Test coverage and harness usage notes

## Prerequisites

- One or more supported IDEs installed:
  - JetBrains Rider with `rider` on Unix-like systems, or `rider`, `rider.bat`, or `rider64.exe` on Windows
  - JetBrains WebStorm with `webstorm` on Unix-like systems, or `webstorm`, `webstorm.bat`, or `webstorm64.exe` on Windows
  - Visual Studio Code with `code` on Unix-like systems, or `code` or `code.cmd` on Windows
  - Cursor with `cursor` on Unix-like systems, or `cursor` or `cursor.cmd` on Windows
  - Windsurf with `windsurf` on Unix-like systems, or `windsurf` or `windsurf.cmd` on Windows

## Generic IDE selection

When a request says "open in IDE" without naming an IDE:

1. Detect installed supported IDEs with the platform-appropriate `list-installed-ides` script.
2. If none are installed, return a clear error.
3. If exactly one is installed, use it directly.
4. If multiple are installed, ask the user which installed IDE to use.

When a request explicitly asks for Rider, WebStorm, VS Code, Cursor, or Windsurf, use only that IDE and return a clear error if its CLI is unavailable.

## Usage

Detect supported IDEs on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/list-installed-ides.sh
```

Open in Rider on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/open-in-rider.sh <path> [--line <n>]
```

Open in VS Code on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/open-in-code.sh <path> [--line <n>]
```

Open in WebStorm on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/open-in-webstorm.sh <path> [--line <n>]
```

Open in Cursor on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/open-in-cursor.sh <path> [--line <n>]
```

Open in Windsurf on Linux/macOS:

```bash
./skills/opening-in-ide/scripts/open-in-windsurf.sh <path> [--line <n>]
```

Detect supported IDEs on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/list-installed-ides.ps1
```

Open in Rider on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/open-in-rider.ps1 <path> [--line <n>]
```

Open in VS Code on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/open-in-code.ps1 <path> [--line <n>]
```

Open in WebStorm on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/open-in-webstorm.ps1 <path> [--line <n>]
```

Open in Cursor on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/open-in-cursor.ps1 <path> [--line <n>]
```

Open in Windsurf on Windows (PowerShell):

```powershell
./skills/opening-in-ide/scripts/open-in-windsurf.ps1 <path> [--line <n>]
```

Examples:

```bash
./skills/opening-in-ide/scripts/list-installed-ides.sh
./skills/opening-in-ide/scripts/open-in-rider.sh src/MyFile.cs
./skills/opening-in-ide/scripts/open-in-rider.sh src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-webstorm.sh src/app.ts --line 42
./skills/opening-in-ide/scripts/open-in-code.sh src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-cursor.sh src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-windsurf.sh .
./skills/opening-in-ide/scripts/open-in-code.sh .
```

```powershell
./skills/opening-in-ide/scripts/list-installed-ides.ps1
./skills/opening-in-ide/scripts/open-in-rider.ps1 src/MyFile.cs
./skills/opening-in-ide/scripts/open-in-rider.ps1 src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-webstorm.ps1 src/app.ts --line 42
./skills/opening-in-ide/scripts/open-in-code.ps1 src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-cursor.ps1 src/MyFile.cs --line 120
./skills/opening-in-ide/scripts/open-in-windsurf.ps1 .
./skills/opening-in-ide/scripts/open-in-code.ps1 .
```

## Selection behavior

### Rider

1. Search upward from the target path for nearest `*.sln`
2. If no solution exists, search for nearest `*.csproj`
3. If neither exists, open the target directly

When multiple `.sln`/`.csproj` files exist in a directory:

- Prefer the one whose basename matches the directory name
- Otherwise choose alphabetically

### VS Code

1. Search upward from the target path for nearest `*.code-workspace`
2. If no workspace exists, search for nearest `*.sln` and use that file's directory as context
3. If no solution exists, search for nearest `*.csproj` and use that file's directory as context
4. If neither exists, open the target directly
5. When opening a file at a line, use `--goto`

When multiple `.code-workspace`/`.sln`/`.csproj` files exist in a directory:

- Prefer the one whose basename matches the directory name
- Otherwise choose alphabetically

### WebStorm

1. Search upward from the target path for nearest `.idea` directory
2. If no `.idea` exists, search upward for nearest JavaScript or TypeScript project root such as `package.json`, `pnpm-workspace.yaml`, `yarn.lock`, `package-lock.json`, `bun.lock`, `bun.lockb`, `tsconfig.json`, or `jsconfig.json`
3. If neither exists, open the target directly
4. When opening a file at a line, use JetBrains `--line`
5. When opening a file without an explicit line number, still pass `--line 1` intentionally as a WebStorm workaround because some WebStorm builds can fail to open the file otherwise
5. When opening a file without an explicit line in project context, fall back to line `1` so the file tab opens reliably

### Cursor and Windsurf

1. Follow the same context-selection rules as VS Code
2. Use `--goto` for file-and-line opens
3. Keep workspace behavior identical across the VS Code family

## Troubleshooting

- `Rider CLI not found on PATH`: configure Rider launcher in IDE settings and restart shell
- `WebStorm CLI not found on PATH`: configure the WebStorm launcher in IDE settings and restart shell
- `VS Code CLI not found on PATH`: install the `code` shell command and restart shell
- `Cursor CLI not found on PATH`: install or enable the `cursor` shell command and restart shell
- `Windsurf CLI not found on PATH`: install or enable the `windsurf` shell command and restart shell
- `path does not exist`: verify the provided file/folder path
- `--line must be a positive integer`: pass values like `1`, `120`, `999`

## Tests

Human-readable scenarios live in `skills/opening-in-ide/tests/scenarios.md`.

Agent-facing eval cases live in `skills/opening-in-ide/evals/evals.json`.

To validate eval quality without launching any IDE commands:

```bash
python3 skills/opening-in-ide/evals/run-harness.py
```

To run the isolated script harness:

```bash
python3 skills/opening-in-ide/tests/run-harness.py
```

See `skills/opening-in-ide/tests/README.md` for coverage and harness details.
