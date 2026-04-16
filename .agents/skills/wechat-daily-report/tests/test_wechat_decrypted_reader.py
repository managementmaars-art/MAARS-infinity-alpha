import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.wechat_decrypted_reader import list_chatrooms, load_chatroom_records


def create_contact_db(base_dir, contacts):
    contact_dir = Path(base_dir) / "contact"
    contact_dir.mkdir(parents=True, exist_ok=True)
    contact_db = contact_dir / "contact.db"
    conn = sqlite3.connect(contact_db)
    try:
        conn.execute(
            """
            CREATE TABLE contact (
                username TEXT PRIMARY KEY,
                nick_name TEXT,
                remark TEXT,
                big_head_url TEXT,
                small_head_url TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO contact (username, nick_name, remark, big_head_url, small_head_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            contacts,
        )
        conn.commit()
    finally:
        conn.close()


def create_message_db(base_dir, username_rows, chatroom_username, message_rows):
    message_dir = Path(base_dir) / "message"
    message_dir.mkdir(parents=True, exist_ok=True)
    message_db = message_dir / "message_0.db"
    conn = sqlite3.connect(message_db)
    try:
        conn.execute("CREATE TABLE Name2Id (user_name TEXT)")
        conn.executemany("INSERT INTO Name2Id (user_name) VALUES (?)", username_rows)

        table_hash = hashlib.md5(chatroom_username.encode("utf-8")).hexdigest()
        conn.execute(
            f"""
            CREATE TABLE [Msg_{table_hash}] (
                local_id INTEGER,
                local_type INTEGER,
                create_time INTEGER,
                real_sender_id INTEGER,
                message_content BLOB,
                WCDB_CT_message_content INTEGER
            )
            """
        )
        conn.executemany(
            f"""
            INSERT INTO [Msg_{table_hash}]
            (local_id, local_type, create_time, real_sender_id, message_content, WCDB_CT_message_content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            message_rows,
        )
        conn.commit()
    finally:
        conn.close()


class WechatDecryptedReaderTests(unittest.TestCase):
    def test_list_chatrooms_reports_group_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            create_contact_db(
                tmpdir,
                [
                    ("room1@chatroom", "测试群", "", "", ""),
                    ("wxid_alice", "Alice", "", "", ""),
                ],
            )
            create_message_db(
                tmpdir,
                [("room1@chatroom",)],
                "room1@chatroom",
                [
                    (1, 1, 1712793600, 0, "hi", 0),
                    (2, 1, 1712797200, 0, "there", 0),
                ],
            )

            groups = list_chatrooms(tmpdir)

            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]["username"], "room1@chatroom")
            self.assertEqual(groups[0]["display_name"], "测试群")
            self.assertEqual(groups[0]["message_count"], 2)

    def test_load_chatroom_records_returns_analyze_ready_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            create_contact_db(
                tmpdir,
                [
                    ("room1@chatroom", "测试群", "", "", ""),
                    ("wxid_alice", "Alice", "", "https://example.com/alice-big.jpg", "https://example.com/alice-small.jpg"),
                    ("wxid_bob", "Bob", "", "https://example.com/bob-big.jpg", "https://example.com/bob-small.jpg"),
                ],
            )
            create_message_db(
                tmpdir,
                [("wxid_alice",), ("wxid_bob",), ("room1@chatroom",)],
                "room1@chatroom",
                [
                    (1, 1, 1712793600, None, "wxid_alice:\n大家好", 0),
                    (2, 47, 1712793660, 2, "", 0),
                    (3, 10000, 1712793720, 0, "你已加入群聊", 0),
                    (
                        4,
                        244813135921,
                        1712793780,
                        2,
                        """wxid_bob:\n<?xml version="1.0"?>
<msg>
  <appmsg>
    <title>没人赌这个财报么</title>
    <type>57</type>
    <refermsg>
      <type>3</type>
      <displayname>Alice</displayname>
      <content><![CDATA[<?xml version="1.0"?><msg><img /></msg>]]></content>
    </refermsg>
  </appmsg>
</msg>""",
                        0,
                    ),
                    (
                        5,
                        49,
                        1712793840,
                        1,
                        """wxid_alice:\n<?xml version="1.0"?>
<msg>
  <appmsg>
    <title>小米明天不涨吗</title>
    <type>5</type>
  </appmsg>
</msg>""",
                        0,
                    ),
                ],
            )

            data = load_chatroom_records(tmpdir, "测试群")

            self.assertEqual(data["meta"]["name"], "测试群")
            self.assertEqual(data["meta"]["groupId"], "room1@chatroom")
            self.assertEqual(len(data["members"]), 2)
            self.assertEqual(data["members"][0]["avatar"], "https://example.com/alice-small.jpg")
            self.assertEqual(data["messages"][0]["sender"], "wxid_alice")
            self.assertEqual(data["messages"][0]["accountName"], "Alice")
            self.assertEqual(data["messages"][0]["type"], 0)
            self.assertEqual(data["messages"][0]["content"], "大家好")
            self.assertEqual(data["messages"][0]["avatar"], "https://example.com/alice-small.jpg")
            self.assertEqual(data["messages"][1]["type"], 5)
            self.assertEqual(data["messages"][1]["avatar"], "https://example.com/bob-small.jpg")
            self.assertEqual(data["messages"][2]["type"], 99)
            self.assertEqual(data["messages"][3]["type"], 0)
            self.assertEqual(data["messages"][3]["content"], "回复 Alice发的图片说：没人赌这个财报么")
            self.assertEqual(data["messages"][4]["type"], 0)
            self.assertEqual(data["messages"][4]["content"], "分享链接《小米明天不涨吗》")

    def test_load_chatroom_records_filters_by_date(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            create_contact_db(
                tmpdir,
                [
                    ("room1@chatroom", "测试群", "", "", ""),
                    ("wxid_alice", "Alice", "", "", ""),
                ],
            )
            create_message_db(
                tmpdir,
                [("wxid_alice",), ("room1@chatroom",)],
                "room1@chatroom",
                [
                    (1, 1, 1712707200, 1, "昨天消息", 0),
                    (2, 1, 1712793600, 1, "今天消息", 0),
                ],
            )

            data = load_chatroom_records(tmpdir, "room1@chatroom", date="2024-04-11")

            self.assertEqual(len(data["messages"]), 1)
            self.assertEqual(data["messages"][0]["content"], "今天消息")


if __name__ == "__main__":
    unittest.main()
