from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.artifact_service import _preview_from_payload


def test_preview_from_string_payload_truncates():
    payload = "x" * 600
    preview = _preview_from_payload(payload)
    assert len(preview) == 500
    assert preview == payload[:500]


def test_preview_from_dict_payload_serializes():
    preview = _preview_from_payload({"hello": "world", "count": 3})
    assert '"hello": "world"' in preview
    assert '"count": 3' in preview
