#!/usr/bin/env python3
"""
Create OneBase frontend projects using cisdigital-generator-app frontend logic.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

FRONTEND_TEMPLATES: Dict[str, str] = {
    "frontend_app": "fe-cisdigital-vite-app-template",
    "frontend_ui": "fe-cisdigital-monorepo-template",
    "frontend_sdk": "fe-cisdigital-ts-lib-template",
}

PROJECT_TYPE_ALIASES = {
    "app": "frontend_app",
    "ui": "frontend_ui",
    "sdk": "frontend_sdk",
}


def _slugify(value: str, default: str = "service") -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or default


def _validate_kebab(value: str, field_name: str) -> None:
    if not KEBAB_CASE_PATTERN.fullmatch(value.strip()):
        raise ValueError(
            f"{field_name} must be kebab-case: lowercase letters, numbers, and hyphens only."
        )


def _resolve_project_type(project_type: str) -> str:
    resolved = PROJECT_TYPE_ALIASES.get(project_type, project_type)
    if resolved not in FRONTEND_TEMPLATES:
        valid = ", ".join(sorted(FRONTEND_TEMPLATES.keys()))
        raise ValueError(f"Unsupported project_type '{project_type}'. Expected one of: {valid}")
    return resolved


def build_payload(
    project_type: str,
    company_name: str,
    product_name: str,
    service_name: str,
    cli_name: str = "onebase-cli",
    frontend_project_type: str | None = None,
) -> Dict[str, str]:
    resolved_type = _resolve_project_type(project_type)
    template_name = FRONTEND_TEMPLATES[resolved_type]

    company_slug = _slugify(company_name, "company")
    product_slug = _slugify(product_name, "product")
    service_slug = _slugify(service_name, "service")
    project_name = f"fe-{company_slug}-{product_slug}-{service_slug}"
    path_prefix = f"{company_slug}/{product_slug}"

    payload: Dict[str, str] = {
        "project_type": resolved_type,
        "company_name": company_name,
        "product_name": product_name,
        "service_name": service_name,
        "package_manager": "pnpm",
        "cli_name": cli_name,
        "template_name": template_name,
        "project_name": project_name,
        "frontend_bundle": f"{project_name}.zip",
        "output_folder": project_name,
        "generated_folder": project_name,
        "archive_basename": project_name,
        "object_name": f"{path_prefix}/{project_name}.zip",
        "company_slug": company_slug,
        "product_slug": product_slug,
        "service_slug": service_slug,
    }
    if frontend_project_type:
        payload["frontend_project_type"] = frontend_project_type
    return payload


def build_command(payload: Dict[str, str]) -> List[str]:
    return [
        payload.get("cli_name", "onebase-cli"),
        "create",
        "-t",
        payload["template_name"],
        "-p",
        payload["project_name"],
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create OneBase frontend project using generator-app rules."
    )
    parser.add_argument(
        "--project-type",
        required=True,
        help="frontend_app | frontend_ui | frontend_sdk (aliases: app/ui/sdk)",
    )
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--frontend-project-type")
    parser.add_argument("--cli-name", default="onebase-cli")
    parser.add_argument("--output-dir", default=".")
    parser.add_argument(
        "--auto-slugify",
        action="store_true",
        help="Allow non-kebab input and convert to slug in payload/project_name.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload and command, do not execute.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.auto_slugify:
        _validate_kebab(args.company_name, "company_name")
        _validate_kebab(args.product_name, "product_name")
        _validate_kebab(args.service_name, "service_name")

    payload = build_payload(
        project_type=args.project_type,
        company_name=args.company_name,
        product_name=args.product_name,
        service_name=args.service_name,
        cli_name=args.cli_name,
        frontend_project_type=args.frontend_project_type,
    )
    command = build_command(payload)

    output_dir = Path(args.output_dir).expanduser().resolve()
    if not output_dir.exists():
        print(f"[ERROR] output_dir does not exist: {output_dir}", file=sys.stderr)
        return 2
    if not output_dir.is_dir():
        print(f"[ERROR] output_dir is not a directory: {output_dir}", file=sys.stderr)
        return 2

    result = {
        "payload": payload,
        "command": command,
        "cwd": str(output_dir),
    }

    if args.dry_run:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    target_dir = output_dir / payload["project_name"]
    if target_dir.exists():
        print(
            f"[ERROR] target project directory already exists: {target_dir}",
            file=sys.stderr,
        )
        return 2

    process = subprocess.run(
        command,
        cwd=str(output_dir),
        capture_output=True,
        text=True,
    )

    if process.stdout:
        print(process.stdout, end="")
    if process.stderr:
        print(process.stderr, end="", file=sys.stderr)

    if process.returncode != 0:
        print(
            f"[ERROR] command failed ({process.returncode}): {' '.join(command)}",
            file=sys.stderr,
        )
        return process.returncode

    if not target_dir.exists():
        print(
            f"[ERROR] command succeeded but project directory missing: {target_dir}",
            file=sys.stderr,
        )
        return 3

    print(json.dumps({"project_path": str(target_dir), "command": command}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(2)
