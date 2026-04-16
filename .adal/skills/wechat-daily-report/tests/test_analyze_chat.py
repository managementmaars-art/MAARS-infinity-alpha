import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from scripts.analyze_chat import analyze


class AnalyzeChatTests(unittest.TestCase):
    def test_analyze_refreshes_decrypted_data_by_default(self):
        data = {
            "meta": {
                "name": "测试群",
                "groupId": "room1@chatroom",
                "decrypted_dir": "D:/fake/decrypted",
            },
            "members": [],
            "messages": [],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            stats_path = Path(tmpdir) / "stats.json"
            text_path = Path(tmpdir) / "chat.txt"
            args = Namespace(
                decrypted_dir="D:/fake/decrypted",
                chatroom="测试群",
                date=None,
                start=None,
                end=None,
                skip_refresh=False,
                output_stats=str(stats_path),
                output_text=str(text_path),
            )

            with patch("scripts.analyze_chat.refresh_decrypted_data") as refresh_mock:
                with patch("scripts.analyze_chat.load_chatroom_records", return_value=data):
                    analyze(args)

            refresh_mock.assert_called_once_with("D:/fake/decrypted")

    def test_analyze_writes_name_avatar_map_into_stats(self):
        data = {
            "meta": {
                "name": "测试群",
                "groupId": "room1@chatroom",
                "decrypted_dir": "D:/fake/decrypted",
            },
            "members": [
                {
                    "platformId": "wxid_alice",
                    "accountName": "Alice",
                    "avatar": "https://example.com/alice.jpg",
                }
            ],
            "messages": [
                {
                    "sender": "wxid_alice",
                    "accountName": "Alice",
                    "groupNickname": "Alice",
                    "timestamp": 1712793600,
                    "type": 0,
                    "content": "大家好",
                    "avatar": "https://example.com/alice.jpg",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            stats_path = Path(tmpdir) / "stats.json"
            text_path = Path(tmpdir) / "chat.txt"
            args = Namespace(
                decrypted_dir="D:/fake/decrypted",
                chatroom="测试群",
                date=None,
                start=None,
                end=None,
                skip_refresh=True,
                output_stats=str(stats_path),
                output_text=str(text_path),
            )

            with patch("scripts.analyze_chat.load_chatroom_records", return_value=data):
                analyze(args)

            stats = json.loads(stats_path.read_text(encoding="utf-8"))
            self.assertEqual(
                stats["name_avatar_map"]["Alice"],
                "https://example.com/alice.jpg",
            )


if __name__ == "__main__":
    unittest.main()
