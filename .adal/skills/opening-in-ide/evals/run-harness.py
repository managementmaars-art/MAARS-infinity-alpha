#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = ROOT / "evals" / "evals.json"


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: dict


class EvalHarness:
    def __init__(self) -> None:
        self.results: list[CheckResult] = []
        self.evals_doc = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
        self.skill_md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.readme_md = (ROOT / "README.md").read_text(encoding="utf-8")
        self.scenarios_md = (ROOT / "tests" / "scenarios.md").read_text(encoding="utf-8")

    def record(self, name: str, ok: bool, **details: object) -> None:
        self.results.append(CheckResult(name=name, ok=ok, details=details))

    def run(self) -> dict:
        self.check_basic_shape()
        self.check_unique_ids_and_prompts()
        self.check_file_references_exist()
        self.check_assertion_quality()
        self.check_required_coverage()
        self.check_docs_alignment()
        failures = [asdict(result) for result in self.results if not result.ok]
        return {
            "evals_file": str(EVALS_PATH),
            "passed": len(self.results) - len(failures),
            "failed": len(failures),
            "failures": failures,
        }

    def check_basic_shape(self) -> None:
        evals = self.evals_doc.get("evals")
        self.record(
            "basic shape",
            self.evals_doc.get("skill_name") == "opening-in-ide" and isinstance(evals, list) and len(evals) >= 5,
            skill_name=self.evals_doc.get("skill_name"),
            eval_count=len(evals) if isinstance(evals, list) else None,
        )

    def check_unique_ids_and_prompts(self) -> None:
        evals = self.evals_doc["evals"]
        ids = [entry.get("id") for entry in evals]
        prompts = [entry.get("prompt") for entry in evals]
        self.record("unique ids", len(ids) == len(set(ids)), ids=ids)
        self.record("unique prompts", len(prompts) == len(set(prompts)), prompts=prompts)

    def check_file_references_exist(self) -> None:
        missing: list[str] = []
        for entry in self.evals_doc["evals"]:
            for rel_path in entry.get("files", []):
                if not (ROOT / rel_path).exists():
                    missing.append(f"eval {entry.get('id')}: {rel_path}")
        self.record("referenced files exist", not missing, missing=missing)

    def check_assertion_quality(self) -> None:
        weak: list[dict] = []
        for entry in self.evals_doc["evals"]:
            assertions = entry.get("assertions", [])
            if not isinstance(assertions, list) or len(assertions) < 2:
                weak.append({"id": entry.get("id"), "reason": "too few assertions"})
                continue
            for assertion in assertions:
                if not isinstance(assertion, str) or len(assertion.strip()) < 20:
                    weak.append({"id": entry.get("id"), "reason": f"weak assertion: {assertion!r}"})
        self.record("assertion quality", not weak, issues=weak)

    def check_required_coverage(self) -> None:
        prompts = [entry["prompt"].lower() for entry in self.evals_doc["evals"]]
        coverage = {
            "generic_ide": any(" in an ide" in prompt for prompt in prompts),
            "webstorm": any("webstorm" in prompt for prompt in prompts),
            "vs_code": any("vs code" in prompt for prompt in prompts),
            "rider_missing": any("rider" in prompt and "not installed" in prompt for prompt in prompts),
            "negative_case": any("hello world" in prompt or "python" in prompt for prompt in prompts),
        }
        self.record("coverage", all(coverage.values()), coverage=coverage)

    def check_docs_alignment(self) -> None:
        checks = {
            "skill mentions generic detection": "Run the installed-IDE detection script" in self.skill_md,
            "skill mentions webstorm workaround": "--line 1" in self.skill_md,
            "readme lists evals": "evals/evals.json" in self.readme_md,
            "scenarios mention workaround": bool(re.search(r"WebStorm.*--line 1|--line 1.*WebStorm", self.scenarios_md, re.IGNORECASE | re.DOTALL)),
        }
        self.record("docs alignment", all(checks.values()), checks=checks)


def main() -> int:
    harness = EvalHarness()
    summary = harness.run()
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
