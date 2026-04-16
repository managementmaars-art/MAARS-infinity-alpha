#!/usr/bin/env bash
# FILE-SIZE-OK
# Refetch canonical-names.json from upstream sources.
# Run when you want to update to newer OTel/OCSF/CloudEvents versions.
#
# Sources (Apache-2.0, redistributable):
#   - OpenTelemetry semantic-conventions (v1.29.0)
#   - OCSF schema dictionary (main branch)
#   - CloudEvents spec formats (main branch)

set -euo pipefail

OTEL_VERSION="${OTEL_VERSION:-1.29.0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$(mktemp -d /tmp/canonical-build.XXXXXX)"
trap 'rm -rf "$WORK_DIR"' EXIT

cd "$WORK_DIR"

echo "→ Fetching CloudEvents schema..."
curl -sfL "https://raw.githubusercontent.com/cloudevents/spec/main/cloudevents/formats/cloudevents.json" -o cloudevents.json
echo "  ✓ $(wc -c < cloudevents.json) bytes"

echo "→ Fetching OCSF dictionary..."
curl -sfL "https://raw.githubusercontent.com/ocsf/ocsf-schema/main/dictionary.json" -o ocsf.json
echo "  ✓ $(wc -c < ocsf.json) bytes"

echo "→ Fetching OpenTelemetry semantic-conventions v${OTEL_VERSION}..."
curl -sfL "https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/v${OTEL_VERSION}.tar.gz" -o otel.tar.gz
tar xzf otel.tar.gz
echo "  ✓ $(find "semantic-conventions-${OTEL_VERSION}/model" -name 'registry.yaml' | wc -l | tr -d ' ') registry files"

echo "→ Building unified canonical-names.json..."
uv run --python 3.13 --with pyyaml python3 - <<PY
import json
from pathlib import Path
import yaml

OUT = []
otel_root = Path("semantic-conventions-${OTEL_VERSION}/model")

# OpenTelemetry
for reg in otel_root.rglob("registry.yaml"):
    namespace = reg.parent.name
    try:
        data = yaml.safe_load(reg.read_text())
        for group in data.get("groups", []):
            for attr in group.get("attributes", []):
                if "id" not in attr:
                    continue
                OUT.append({
                    "name": attr["id"],
                    "source": "otel",
                    "namespace": namespace,
                    "brief": (attr.get("brief") or "").strip()[:200],
                    "stability": attr.get("stability", "unknown"),
                })
    except Exception as e:
        print(f"  ! {reg}: {e}")

# OCSF
ocsf_data = json.loads(Path("ocsf.json").read_text())
for name, info in ocsf_data.get("attributes", {}).items():
    OUT.append({
        "name": name,
        "source": "ocsf",
        "namespace": info.get("group", "unknown"),
        "brief": (info.get("description") or "").strip()[:200],
        "stability": "stable",
    })

# CloudEvents
ce = json.loads(Path("cloudevents.json").read_text())
for name, info in ce.get("properties", {}).items():
    OUT.append({
        "name": name,
        "source": "cloudevents",
        "namespace": "envelope",
        "brief": (info.get("description") or "").strip()[:200],
        "stability": "stable",
    })

# Dedupe + sort
seen = set()
unique = []
for entry in sorted(OUT, key=lambda x: (x["source"], x["name"])):
    key = (entry["source"], entry["name"])
    if key not in seen:
        seen.add(key)
        unique.append(entry)

out_path = Path("${SCRIPT_DIR}/canonical-names.json")
out_path.write_text(json.dumps(unique, indent=2))
print(f"  ✓ {len(unique)} attributes → {out_path}")
print(f"  ✓ {out_path.stat().st_size:,} bytes")
PY

echo
echo "✓ Done. Review the diff and commit canonical-names.json if it changed."
