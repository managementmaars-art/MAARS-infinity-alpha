# Packaging and CI

Use this file when the user wants something that can be installed, run, or tested like a normal Python project.

## Baseline project shape

- `my_app.py` or a package module
- matching `.tcss`
- `tests/`
- `pyproject.toml`
- optional `.github/workflows/textual-tests.yml`

## Recommended dependencies

Runtime:
- `textual`

Useful dev dependencies:
- `pytest`
- `pytest-asyncio`
- `textual-dev`
- `pytest-textual-snapshot`

Optional:
- syntax extras when the app needs `TextArea` syntax support

## Console entry points

Prefer a `main()` function and a package/script entry in `pyproject.toml`.

## CI guidance

A good default workflow should:
- test multiple Python versions where sensible
- install the project with dev extras
- run pytest
- upload snapshot artefacts if present

Use the bundled generators:
- `python scripts/emit_textual_pyproject.py`
- `python scripts/emit_github_actions_ci.py`

## Packaging checklist

Before finishing:
- entry point works
- tests are runnable with `pytest`
- the README or handoff notes mention `textual run --dev`
- the project structure is understandable without reading a long explanation
