import json
import tempfile
import unittest
from pathlib import Path

from scripts.generate_report import load_name_avatar_map


class GenerateReportTests(unittest.TestCase):
    def test_load_name_avatar_map_skips_directory_source_chat_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stats = {
                "meta": {
                    "source_chat_path": tmpdir,
                    "source_chatroom": "room1@chatroom",
                }
            }
            stats_path = str(Path(tmpdir) / "stats.json")
            Path(stats_path).write_text(json.dumps(stats), encoding="utf-8")

            avatar_map = load_name_avatar_map(stats, stats_path)

            self.assertEqual(avatar_map, {})


if __name__ == "__main__":
    unittest.main()
