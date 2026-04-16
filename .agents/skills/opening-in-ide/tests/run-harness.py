#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "opening-in-ide"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
BASE_PATH = "/usr/bin:/bin"
CLI_LOGS = {
    "rider": "rider.log",
    "webstorm": "webstorm.log",
    "code": "code.log",
    "cursor": "cursor.log",
    "windsurf": "windsurf.log",
}


@dataclass
class Result:
    name: str
    ok: bool
    details: dict[str, object]


class Harness:
    def __init__(self) -> None:
        self.base = Path(tempfile.mkdtemp(prefix="opening-in-ide-tests-", dir="/tmp"))
        self.fixture = self.base / "fixture"
        self.bin_dir = self.base / "bin"
        self.logs = self.base / "logs"
        self.results: list[Result] = []

        self.fixture.mkdir()
        self.bin_dir.mkdir()
        self.logs.mkdir()

        for log_name in CLI_LOGS.values():
            (self.logs / log_name).write_text("", encoding="utf-8")

        for command_name, log_name in CLI_LOGS.items():
            self._write_fake_cli(command_name, log_name)

        self._build_fixture_tree()

    def _write_fake_cli(self, command_name: str, log_name: str) -> None:
        path = self.bin_dir / command_name
        path.write_text(
            textwrap.dedent(
                f"""#!/usr/bin/env bash
                set -euo pipefail
                printf '%s\\n' \"$*\" >> \"{(self.logs / log_name).as_posix()}\"
                """
            ),
            encoding="utf-8",
        )
        path.chmod(0o755)

    def _build_fixture_tree(self) -> None:
        self.root = self.fixture / "repo"
        (self.root / "src").mkdir(parents=True)
        (self.root / "src" / "MyFile.cs").write_text("// file\n", encoding="utf-8")
        (self.root / "README.md").write_text("# readme\n", encoding="utf-8")
        (self.root / "repo.sln").write_text("\n", encoding="utf-8")
        (self.root / "project.csproj").write_text("<Project />\n", encoding="utf-8")
        (self.root / "repo.code-workspace").write_text("{}\n", encoding="utf-8")

        self.fallback = self.fixture / "fallback"
        (self.fallback / "nested" / "deeper").mkdir(parents=True)
        (self.fallback / "nested" / "deeper" / "Lib.cs").write_text("// lib\n", encoding="utf-8")
        (self.fallback / "Lib.csproj").write_text("<Project />\n", encoding="utf-8")

        self.nosln = self.fixture / "nosln"
        (self.nosln / "docs").mkdir(parents=True)
        (self.nosln / "docs" / "readme.md").write_text("x\n", encoding="utf-8")

        self.multi = self.fixture / "multi" / "src"
        self.multi.mkdir(parents=True)
        (self.multi / "Program.cs").write_text("// program\n", encoding="utf-8")
        (self.multi / "App.sln").write_text("\n", encoding="utf-8")
        (self.multi / "src.sln").write_text("\n", encoding="utf-8")

        self.webstorm_idea = self.fixture / "webstorm-idea"
        (self.webstorm_idea / ".idea").mkdir(parents=True)
        (self.webstorm_idea / "package.json").write_text("{}\n", encoding="utf-8")
        (self.webstorm_idea / "src").mkdir()
        (self.webstorm_idea / "src" / "index.ts").write_text("console.log('idea');\n", encoding="utf-8")

        self.webstorm_pkg = self.fixture / "webstorm-pkg"
        (self.webstorm_pkg / "src").mkdir(parents=True)
        (self.webstorm_pkg / "package.json").write_text("{}\n", encoding="utf-8")
        (self.webstorm_pkg / "tsconfig.json").write_text("{}\n", encoding="utf-8")
        (self.webstorm_pkg / "src" / "app.ts").write_text("console.log('pkg');\n", encoding="utf-8")

        self.missing_path = self.fixture / "does-not-exist.cs"

    def script(self, name: str) -> Path:
        return SCRIPTS_DIR / name

    def run(self, command: list[str], extra_path: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{extra_path}:{BASE_PATH}" if extra_path else BASE_PATH
        return subprocess.run(command, text=True, capture_output=True, env=env)

    def run_bash(self, script_name: str, *args: object, extra_path: Path | None = None) -> subprocess.CompletedProcess[str]:
        return self.run(["bash", str(self.script(script_name)), *map(str, args)], extra_path=extra_path)

    def run_pwsh(self, script_name: str, *args: object, extra_path: Path | None = None) -> subprocess.CompletedProcess[str]:
        return self.run(["pwsh", "-NoProfile", "-File", str(self.script(script_name)), *map(str, args)], extra_path=extra_path)

    def read_log(self, cli_name: str) -> list[str]:
        path = self.logs / CLI_LOGS[cli_name]
        time.sleep(0.2)
        return [line for line in path.read_text(encoding="utf-8").splitlines() if line]

    def clear_logs(self) -> None:
        for log_name in CLI_LOGS.values():
            (self.logs / log_name).write_text("", encoding="utf-8")

    def record(self, name: str, ok: bool, **details: object) -> None:
        self.results.append(Result(name=name, ok=ok, details=details))

    def make_single_cli_dir(self, command_name: str) -> Path:
        target_dir = self.base / f"only-{command_name}"
        target_dir.mkdir(exist_ok=True)
        shutil.copy2(self.bin_dir / command_name, target_dir / command_name)
        (target_dir / command_name).chmod(0o755)
        return target_dir

    def assert_detect(self, runner: str, extra_path: Path | None, expected: list[str], label: str) -> None:
        if runner == "bash":
            res = self.run_bash("list-installed-ides.sh", extra_path=extra_path)
        else:
            res = self.run_pwsh("list-installed-ides.ps1", extra_path=extra_path)

        self.record(
            label,
            res.returncode == 0 and res.stdout.splitlines() == expected,
            code=res.returncode,
            stdout=res.stdout.splitlines(),
            stderr=res.stderr.strip(),
        )

    def assert_launch(
        self,
        runner: str,
        script_name: str,
        cli_name: str,
        expected_log: str,
        label: str,
        *args: object,
        extra_path: Path | None,
    ) -> None:
        self.clear_logs()
        if runner == "bash":
            res = self.run_bash(script_name, *args, extra_path=extra_path)
        else:
            res = self.run_pwsh(script_name, *args, extra_path=extra_path)
        cli_log = self.read_log(cli_name)
        self.record(
            label,
            res.returncode == 0 and cli_log[-1] == expected_log,
            code=res.returncode,
            log=cli_log,
            stderr=res.stderr.strip(),
        )

    def assert_failure(
        self,
        runner: str,
        script_name: str,
        expected_code: int,
        expected_stderr: str,
        label: str,
        *args: object,
        extra_path: Path | None = None,
    ) -> None:
        if runner == "bash":
            res = self.run_bash(script_name, *args, extra_path=extra_path)
        else:
            res = self.run_pwsh(script_name, *args, extra_path=extra_path)

        self.record(
            label,
            res.returncode == expected_code and expected_stderr in res.stderr,
            code=res.returncode,
            stderr=res.stderr.strip(),
        )

    def run_all(self) -> dict[str, object]:
        target = self.root / "src" / "MyFile.cs"
        direct_target = self.nosln / "docs" / "readme.md"
        fallback_target = self.fallback / "nested" / "deeper" / "Lib.cs"
        multi_target = self.multi / "Program.cs"
        webstorm_idea_target = self.webstorm_idea / "src" / "index.ts"
        webstorm_pkg_target = self.webstorm_pkg / "src" / "app.ts"

        only_rider = self.make_single_cli_dir("rider")
        only_webstorm = self.make_single_cli_dir("webstorm")
        only_cursor = self.make_single_cli_dir("cursor")
        only_windsurf = self.make_single_cli_dir("windsurf")

        self.assert_detect("bash", None, [], "bash detect none")
        self.assert_detect("bash", self.bin_dir, ["rider", "webstorm", "code", "cursor", "windsurf"], "bash detect all")
        self.assert_detect("bash", only_rider, ["rider"], "bash detect rider only")
        self.assert_detect("bash", only_webstorm, ["webstorm"], "bash detect webstorm only")
        self.assert_detect("bash", only_cursor, ["cursor"], "bash detect cursor only")

        self.assert_detect("pwsh", None, [], "pwsh detect none")
        self.assert_detect("pwsh", self.bin_dir, ["rider", "webstorm", "code", "cursor", "windsurf"], "pwsh detect all")
        self.assert_detect("pwsh", only_windsurf, ["windsurf"], "pwsh detect windsurf only")

        self.assert_launch("bash", "open-in-rider.sh", "rider", f"{self.root / 'repo.sln'} {target}", "bash rider nearest sln", target, extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-rider.sh", "rider", f"{self.root / 'repo.sln'} --line 120 {target}", "bash rider line open", target, "--line", "120", extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-rider.sh", "rider", f"{self.fallback / 'Lib.csproj'} {fallback_target}", "bash rider csproj fallback", fallback_target, extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-rider.sh", "rider", f"{self.multi / 'src.sln'} {multi_target}", "bash rider best sln match", multi_target, extra_path=self.bin_dir)
        self.assert_failure("bash", "open-in-rider.sh", 127, "Rider CLI not found", "bash rider missing cli", target)
        self.assert_failure("bash", "open-in-rider.sh", 2, "--line must be a positive integer", "bash rider invalid line", target, "--line", "abc", extra_path=self.bin_dir)

        self.assert_launch("bash", "open-in-webstorm.sh", "webstorm", f"{self.webstorm_pkg} --line 1 {webstorm_pkg_target}", "bash webstorm package context", webstorm_pkg_target, extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-webstorm.sh", "webstorm", f"{self.webstorm_idea} --line 9 {webstorm_idea_target}", "bash webstorm idea context line open", webstorm_idea_target, "--line", "9", extra_path=self.bin_dir)
        self.assert_failure("bash", "open-in-webstorm.sh", 127, "WebStorm CLI not found", "bash webstorm missing cli", webstorm_pkg_target)

        self.assert_launch("bash", "open-in-code.sh", "code", f"{self.root / 'repo.code-workspace'} {target}", "bash code workspace context", target, extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-code.sh", "code", f"{self.root / 'repo.code-workspace'} --goto {target}:120", "bash code goto line", target, "--line", "120", extra_path=self.bin_dir)
        self.assert_failure("bash", "open-in-code.sh", 127, "VS Code CLI not found", "bash code missing cli", target)

        self.assert_launch("bash", "open-in-cursor.sh", "cursor", f"{self.root / 'repo.code-workspace'} --goto {target}:77", "bash cursor goto line", target, "--line", "77", extra_path=self.bin_dir)
        self.assert_failure("bash", "open-in-cursor.sh", 2, "path does not exist", "bash cursor invalid path", self.missing_path, extra_path=self.bin_dir)

        (self.root / "repo.code-workspace").unlink()
        self.assert_launch("bash", "open-in-windsurf.sh", "windsurf", f"{self.root} {target}", "bash windsurf sln dir fallback", target, extra_path=self.bin_dir)
        (self.root / "repo.sln").unlink()
        self.assert_launch("bash", "open-in-windsurf.sh", "windsurf", f"{self.root} {target}", "bash windsurf csproj dir fallback", target, extra_path=self.bin_dir)
        self.assert_launch("bash", "open-in-windsurf.sh", "windsurf", f"{direct_target}", "bash windsurf direct open", direct_target, extra_path=self.bin_dir)
        self.assert_failure("bash", "open-in-windsurf.sh", 127, "Windsurf CLI not found", "bash windsurf missing cli", target)

        (self.root / "repo.code-workspace").write_text("{}\n", encoding="utf-8")
        (self.root / "repo.sln").write_text("\n", encoding="utf-8")

        self.assert_launch("pwsh", "open-in-rider.ps1", "rider", f"{self.root / 'repo.sln'} {target}", "pwsh rider nearest sln", target, extra_path=self.bin_dir)
        self.assert_launch("pwsh", "open-in-webstorm.ps1", "webstorm", f"{self.webstorm_idea} --line 1 {webstorm_idea_target}", "pwsh webstorm idea context", webstorm_idea_target, extra_path=self.bin_dir)
        self.assert_launch("pwsh", "open-in-code.ps1", "code", f"{self.root / 'repo.code-workspace'} {target}", "pwsh code workspace context", target, extra_path=self.bin_dir)
        self.assert_launch("pwsh", "open-in-cursor.ps1", "cursor", f"{self.root / 'repo.code-workspace'} --goto {target}:41", "pwsh cursor goto line", target, "--line", "41", extra_path=self.bin_dir)
        self.assert_launch("pwsh", "open-in-windsurf.ps1", "windsurf", f"{self.root / 'repo.code-workspace'} {target}", "pwsh windsurf workspace context", target, extra_path=self.bin_dir)
        self.assert_failure("pwsh", "open-in-webstorm.ps1", 127, "WebStorm CLI not found", "pwsh webstorm missing cli", webstorm_pkg_target)
        self.assert_failure("pwsh", "open-in-cursor.ps1", 127, "Cursor CLI not found", "pwsh cursor missing cli", target)
        self.assert_failure("pwsh", "open-in-windsurf.ps1", 2, "path does not exist", "pwsh windsurf invalid path", self.missing_path, extra_path=self.bin_dir)

        failures = [asdict(result) for result in self.results if not result.ok]
        return {
            "base": str(self.base),
            "passed": len(self.results) - len(failures),
            "failed": len(failures),
            "failures": failures,
        }


def main() -> int:
    harness = Harness()
    summary = harness.run_all()
    print(json.dumps(summary, indent=2))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
