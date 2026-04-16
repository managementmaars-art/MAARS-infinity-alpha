---
name: cli-anything
description: Reference guide for CLI-Anything, which auto-generates production-ready agent-controllable CLI harnesses for any GUI application via a 7-phase pipeline. Use when the user asks about CLI-Anything, wants to generate a CLI for a GUI app, asks how to install or invoke cli-anything commands, wants usage examples for any of the 11 supported apps (GIMP, Blender, LibreOffice, Inkscape, Audacity, OBS, Kdenlive, Shotcut, Zoom, Draw.io, AnyGen), or mentions HARNESS.md, agent harness, or cli-anything-gimp. Do not use for building CLIs from scratch without the CLI-Anything tool.
allowed-tools:
  - Read
---

# CLI-Anything Reference

Auto-generates production-ready, agent-controllable CLI interfaces for any GUI application with accessible source code. A 7-phase pipeline maps GUI actions to backend APIs and emits Click-based harnesses with `--json` output mode, interactive REPL, and pytest test suites.

**Source**: <https://github.com/HKUDS/CLI-Anything>
**License**: MIT | **Python**: 3.10+ | **Tests**: 1,508 passing across 11 apps

---

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Installation

### Method 1: Claude Code Marketplace (recommended)

```
/plugin marketplace add HKUDS/CLI-Anything
/plugin install cli-anything
```

### Method 2: Manual Claude Code

```bash
git clone https://github.com/HKUDS/CLI-Anything.git
cp -r CLI-Anything/cli-anything-plugin ~/.claude/plugins/cli-anything
# Reload in Claude Code:
/reload-plugins
```

### Method 3: OpenCode — global

```bash
git clone https://github.com/HKUDS/CLI-Anything.git
cp CLI-Anything/opencode-commands/*.md ~/.config/opencode/commands/
cp CLI-Anything/cli-anything-plugin/HARNESS.md ~/.config/opencode/commands/
```

### Method 4: OpenCode — project-level

```bash
cp CLI-Anything/opencode-commands/*.md .opencode/commands/
cp CLI-Anything/cli-anything-plugin/HARNESS.md .opencode/commands/
```

---

## Generating a New CLI Harness

```bash
# From local source path
/cli-anything ./gimp

# From GitHub URL (auto-cloned)
/cli-anything https://github.com/blender/blender

# Claude Code variant (plugin command)
/cli-anything ./inkscape

# OpenCode variant
/cli-anything ./libreoffice
```

---

## All Commands

| Command                                                | Platform    | Purpose                               |
| ------------------------------------------------------ | ----------- | ------------------------------------- |
| `/cli-anything <path-or-url>`                          | Claude Code | Build full 7-phase harness            |
| `/cli-anything:refine <path> [focus]`                  | Claude Code | Expand with gap analysis              |
| `/cli-anything:test <path-or-url>`                     | Claude Code | Run tests + update TEST.md            |
| `/cli-anything:validate <path-or-url>`                 | Claude Code | Verify HARNESS.md standards           |
| `/cli-anything:list [--path dir] [--depth n] [--json]` | Claude Code | Discover installed CLI-Anything tools |
| `/cli-anything ./gimp`                                 | OpenCode    | Build harness                         |
| `/cli-anything-refine ./gimp`                          | OpenCode    | Refine harness                        |
| `/cli-anything-test ./gimp`                            | OpenCode    | Run tests                             |
| `/cli-anything-validate ./gimp`                        | OpenCode    | Validate standards                    |
| `/cli-anything-list`                                   | OpenCode    | List installed tools                  |

### Refinement with Focus

```bash
# Broad gap analysis
/cli-anything:refine ./gimp

# Targeted domain expansion
/cli-anything:refine ./gimp "batch processing and filters"
/cli-anything:refine ./blender "rendering pipeline and animations"
/cli-anything:refine ./libreoffice "spreadsheet formulas and macros"
```

---

## Installing a Generated CLI

```bash
cd <software>/agent-harness
pip install -e .

# Verify PATH entry created
which cli-anything-gimp
cli-anything-gimp --help
```

---

## Using Generated CLIs

All generated CLIs share a consistent interface pattern.

### GIMP Example

```bash
# Help
cli-anything-gimp --help

# Create project
cli-anything-gimp project new --width 1920 --height 1080 -o poster.json

# Machine-readable JSON output (for agent consumption)
cli-anything-gimp --json layer add -n "Background" --type solid --color "#1a1a2e"

# Interactive REPL
cli-anything-gimp

# Stateful workflow with --project flag
cli-anything-gimp --project poster.json layer add -n "Logo" --type group
cli-anything-gimp --project poster.json export render output.png --format png
```

### LibreOffice Example

```bash
# New document
cli-anything-libreoffice document new -o report.json --type writer

# Populate document
cli-anything-libreoffice --project report.json writer add-heading -t "Q1 Report" --level 1
cli-anything-libreoffice --project report.json writer add-table --rows 4 --cols 3

# Export
cli-anything-libreoffice --project report.json export render output.pdf -p pdf --overwrite

# JSON output
cli-anything-libreoffice --json document info --project report.json
```

### Blender Example

```bash
cli-anything-blender scene new -o scene.json
cli-anything-blender --project scene.json object add --type mesh --mesh-type CUBE
cli-anything-blender --project scene.json render image output.png --engine CYCLES
cli-anything-blender --json scene info --project scene.json
```

### Inkscape Example

```bash
cli-anything-inkscape document new --width 800 --height 600 -o design.json
cli-anything-inkscape --project design.json shape add rect --x 10 --y 10 --w 200 --h 100
cli-anything-inkscape --project design.json export render output.svg
cli-anything-inkscape --json document info --project design.json
```

---

## Output Modes

Every command supports two output modes:

| Mode                     | Usage                                    | Audience           |
| ------------------------ | ---------------------------------------- | ------------------ |
| Human-readable (default) | `cli-anything-gimp layer add ...`        | Terminal / humans  |
| Machine-readable JSON    | `cli-anything-gimp --json layer add ...` | AI agents, scripts |

The `--json` flag is always the first argument, before any subcommands.

---

## Interactive REPL

Enter by running the CLI with no subcommands:

```bash
cli-anything-gimp
cli-anything-blender
cli-anything-libreoffice
```

REPL features:

- 50-level undo/redo stack
- Persistent command history
- ANSI 256-color output (software-specific accent colors)
- Table rendering, progress indicators
- All subcommands available interactively

---

## Running Tests

```bash
# Standard pytest run
cd <software>/agent-harness
python3 -m pytest cli_anything/<software>/tests/ -v

# Validate the installed binary is invoked (not just the module)
CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/<software>/tests/ -v -s

# Coverage
python3 -m pytest cli_anything/<software>/tests/ --cov=cli_anything/<software>

# Per-software examples
cd gimp/agent-harness && python3 -m pytest cli_anything/gimp/tests/ -v
cd blender/agent-harness && python3 -m pytest cli_anything/blender/tests/ -v
cd libreoffice/agent-harness && python3 -m pytest cli_anything/libreoffice/tests/ -v
```

---

## Environment Variables

| Variable                         | Purpose                                                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `CLI_ANYTHING_FORCE_INSTALLED=1` | Forces tests to use the real installed binary (validates `which cli-anything-<software>` resolves correctly, not just module import) |

---

## Supported Applications (11 total, 1,508 tests)

| Application | Category          | Entry Point                |
| ----------- | ----------------- | -------------------------- |
| GIMP        | Creative (raster) | `cli-anything-gimp`        |
| Blender     | Creative (3D)     | `cli-anything-blender`     |
| Inkscape    | Creative (vector) | `cli-anything-inkscape`    |
| Audacity    | Media (audio)     | `cli-anything-audacity`    |
| LibreOffice | Productivity      | `cli-anything-libreoffice` |
| OBS Studio  | Media (streaming) | `cli-anything-obs-studio`  |
| Kdenlive    | Media (video)     | `cli-anything-kdenlive`    |
| Shotcut     | Media (video)     | `cli-anything-shotcut`     |
| Zoom        | Communication     | `cli-anything-zoom`        |
| Draw.io     | Diagramming       | `cli-anything-drawio`      |
| AnyGen      | AI Content        | `cli-anything-anygen`      |

---

## The 7-Phase Pipeline (HARNESS.md)

What `/cli-anything` triggers under the hood:

| Phase | Name                    | What happens                                                                                         |
| ----- | ----------------------- | ---------------------------------------------------------------------------------------------------- |
| 1     | Source Acquisition      | Accept local path or GitHub URL; clone if needed                                                     |
| 2     | Codebase Analysis       | Map GUI actions → backend APIs; inventory existing CLI tools; document data model                    |
| 3     | CLI Architecture Design | Choose interaction model (stateful REPL + subcommand); define command groups; plan `--json` output   |
| 4     | Implementation          | Build Click-based CLI with `cli_anything.<software>` namespace; implement REPL via shared `ReplSkin` |
| 5     | Test Planning           | Write `TEST.md` with planned test inventory before code                                              |
| 6     | Test Implementation     | Unit tests (synthetic data) + E2E tests (real software output) + subprocess tests                    |
| 7     | PyPI Publishing         | `setup.py` with `find_namespace_packages()`; console_scripts entry points                            |

**Fundamental Rule**: The CLI MUST delegate rendering to the real software — never reimplement functionality in Python. The target software is a hard dependency.

---

## Generated Harness Structure

Each generated CLI follows this layout (PEP 420 namespace packages):

```
<software>/agent-harness/
├── setup.py                          # find_namespace_packages(), entry_points
├── <SOFTWARE>.md                     # Software-specific SOP
└── cli_anything/                     # NO __init__.py (namespace package)
    └── <software>/
        ├── __init__.py
        ├── __main__.py
        ├── <software>_cli.py         # Main Click entry point
        ├── core/                     # Domain modules (project, session, export, ...)
        ├── utils/
        │   └── repl_skin.py          # Shared REPL UI (copied from plugin)
        └── tests/
            ├── TEST.md               # Test inventory (written in phase 5)
            ├── test_core.py          # Unit tests
            └── test_full_e2e.py      # E2E + subprocess tests
```

**Why namespace packages**: `cli_anything/` has no `__init__.py`, enabling multiple separately-installed CLIs to coexist under the same `cli_anything.*` namespace without conflict.

---

## Output Verification Standards

Tests verify real output using magic bytes and content analysis:

| Output Type          | Verification                        |
| -------------------- | ----------------------------------- |
| PDF                  | `%PDF-` magic bytes + non-zero size |
| OOXML (.docx, .xlsx) | ZIP structure validation            |
| CSV                  | Data row count + column check       |
| Images               | Pillow pixel value analysis         |
| Audio                | RMS level check (non-silent)        |

---

## Prerequisites Checklist

Before running `/cli-anything <path>`:

- [ ] Python 3.10+ installed
- [ ] Target software installed (hard dependency — it will be called for rendering)
- [ ] Source code accessible (local path or public GitHub URL)
- [ ] `click>=8.0.0` available (installed via `pip install -e .`)
- [ ] `Pillow>=10.0.0`, `prompt-toolkit>=3.0.0` available
- [ ] `pytest` available for running tests

---

## Key Files Reference

| File                                           | Purpose                                    |
| ---------------------------------------------- | ------------------------------------------ |
| `cli-anything-plugin/HARNESS.md`               | Complete methodology document (30K chars)  |
| `cli-anything-plugin/QUICKSTART.md`            | Quick start guide                          |
| `cli-anything-plugin/repl_skin.py`             | Shared REPL UI class (18K, ANSI 256-color) |
| `cli-anything-plugin/commands/cli-anything.md` | `/cli-anything` slash command definition   |
| `cli-anything-plugin/commands/refine.md`       | `/cli-anything:refine` command             |
| `cli-anything-plugin/commands/test.md`         | `/cli-anything:test` command               |
| `cli-anything-plugin/commands/validate.md`     | `/cli-anything:validate` command           |
| `cli-anything-plugin/commands/list.md`         | `/cli-anything:list` command               |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
