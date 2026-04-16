#!/usr/bin/env python3
"""
小米摄像头图片获取脚本
通过 HTTP API 直接获取摄像头图片
使用 Python 标准库，无需外部依赖
"""

import argparse
import hashlib
import http.cookiejar
import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 图片 API 基础 URL
IMAGE_API_BASE = "http://micam.appsvc.net"


class MilocoCameraClient:
    """Miloco 摄像头客户端"""

    def __init__(
        self,
        base_url: str,
        username: str = "admin",
        password: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        # Cookie 管理
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )

    def login(self) -> bool:
        """登录获取 token (access_token cookie)"""
        if not self.password:
            self.password = os.environ.get("MILOCO_PASSWORD", "")

        # 密码需要 MD5 加密
        password_md5 = hashlib.md5(self.password.encode()).hexdigest()

        login_url = f"{self.base_url}/api/auth/login"
        payload = json.dumps({
            "username": self.username,
            "password": password_md5
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                login_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            resp = self.opener.open(req)
            data = json.loads(resp.read().decode("utf-8"))

            # code=0 表示登录成功
            if data.get("code") == 0:
                # 从 Cookie 中获取 access_token
                for cookie in self.cookie_jar:
                    if cookie.name == "access_token":
                        self.token = cookie.value
                        logger.info("登录成功")
                        return True
                logger.error("登录响应中没有 access_token cookie")
                return False
            logger.error("登录失败: %s", data)
            return False
        except urllib.error.HTTPError as e:
            logger.error("登录失败: %s %s", e.code, e.read().decode("utf-8"))
            return False
        except Exception as e:
            logger.error("登录请求失败: %s", e)
            return False

    def get_camera_list(self) -> list:
        """获取摄像头列表"""
        if not self.token:
            logger.error("未登录")
            return []

        url = f"{self.base_url}/api/miot/camera_list"

        try:
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                method="GET"
            )
            resp = self.opener.open(req)
            data = json.loads(resp.read().decode("utf-8"))
            cameras = data.get("data", [])
            logger.info("获取到 %d 个摄像头", len(cameras))
            return cameras
        except Exception as e:
            logger.error("请求失败: %s", e)
            return []

    def get_camera_image(
        self,
        camera_id: str,
        output_dir: str = ".",
        filename: Optional[str] = None,
        retry_on_auth_fail: bool = True,
    ) -> bool:
        """
        获取摄像头图片

        Args:
            camera_id: 摄像头设备ID (did)
            output_dir: 输出目录
            filename: 自定义文件名（不含扩展名），默认使用 日期_did_时分秒 格式
            retry_on_auth_fail: 认证失败时是否重试登录

        Returns:
            是否成功获取图片
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 构建图片 API URL
        image_url = f"{IMAGE_API_BASE}/api/miot/camera/{camera_id}/image"

        logger.info("获取摄像头图片: camera_id=%s", camera_id)

        try:
            req = urllib.request.Request(
                image_url,
                headers={
                    "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
                    "Accept": "*/*",
                },
                method="GET"
            )
            resp = self.opener.open(req)

            # 获取图片数据
            image_data = resp.read()

            if not image_data:
                logger.error("获取到空图片数据")
                return False

            # 确定文件名：日期_did_时分秒 格式
            if not filename:
                now = datetime.now()
                filename = f"{now.strftime('%Y%m%d')}_{camera_id}_{now.strftime('%H%M%S')}"

            # 根据内容类型确定扩展名
            content_type = resp.headers.get("Content-Type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            else:
                ext = ".jpg"

            # 保存图片
            output_file = output_path / f"{filename}{ext}"
            output_file.write_bytes(image_data)

            logger.info("图片已保存: %s (%d bytes)", output_file, len(image_data))
            return True

        except urllib.error.HTTPError as e:
            # 检查是否认证失败
            if e.code in (401, 403):
                logger.warning("认证失败 (status=%d)，尝试重新登录...", e.code)
                if retry_on_auth_fail:
                    if self.login():
                        return self.get_camera_image(
                            camera_id=camera_id,
                            output_dir=output_dir,
                            filename=filename,
                            retry_on_auth_fail=False,
                        )
                logger.error("重新登录后仍然失败")
                return False
            logger.error("获取图片失败: status=%d, %s", e.code, e.read().decode("utf-8"))
            return False
        except Exception as e:
            logger.error("获取图片失败: %s", e, exc_info=True)
            return False


def cleanup_old_images(output_dir: str, max_age_days: int = 1):
    """
    清理过期的图片文件

    Args:
        output_dir: 输出目录
        max_age_days: 最大保留时间（天），默认1天
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        return

    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    deleted_count = 0

    for file in output_path.iterdir():
        if file.is_file() and file.suffix.lower() in (".jpg", ".jpeg", ".png"):
            # 获取文件修改时间
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if mtime < cutoff_time:
                try:
                    file.unlink()
                    deleted_count += 1
                    logger.debug("已删除过期图片: %s", file)
                except Exception as e:
                    logger.warning("删除文件失败 %s: %s", file, e)

    if deleted_count > 0:
        logger.info("已清理 %d 个过期图片（超过 %d 天）", deleted_count, max_age_days)


def main():
    parser = argparse.ArgumentParser(
        description="小米摄像头图片获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有摄像头
  python3 camera_client.py --server http://localhost:8000 --password YOUR_PASSWORD --list

  # 获取摄像头图片
  python3 camera_client.py --server http://localhost:8000 --password YOUR_PASSWORD \\
      --camera-id "1036201996" --output ./images

  # 持续获取图片，每30秒一次
  python3 camera_client.py --server http://localhost:8000 --password YOUR_PASSWORD \\
      --camera-id "1036201996" --output ./images --loop

  # 持续获取图片，每60秒一次，自动清理1天以上的图片
  python3 camera_client.py --server http://localhost:8000 --password YOUR_PASSWORD \\
      --camera-id "1036201996" --output ./images --loop --interval 60 --cleanup

  # 持续获取图片，自动清理3天以上的图片
  python3 camera_client.py --server http://localhost:8000 --password YOUR_PASSWORD \\
      --camera-id "1036201996" --output ./images --loop --cleanup --cleanup-days 3

环境变量:
  MILOCO_PASSWORD  服务器密码 (可替代 --password 参数)
        """
    )

    parser.add_argument(
        "--server", "-s",
        help="Miloco 服务器地址"
    )
    parser.add_argument(
        "--username", "-u",
        default="admin",
        help="用户名 (默认: admin)"
    )
    parser.add_argument(
        "--password", "-p",
        help="密码 (也可通过 MILOCO_PASSWORD 环境变量设置)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有摄像头"
    )
    parser.add_argument(
        "--camera-id", "-c",
        help="摄像头设备ID (did)"
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="输出目录 (默认: 当前目录)"
    )
    parser.add_argument(
        "--filename", "-f",
        help="自定义文件名（不含扩展名）"
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="持续获取图片"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="循环获取间隔秒数 (默认: 30)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="自动清理超过指定天数的图片"
    )
    parser.add_argument(
        "--cleanup-days",
        type=int,
        default=1,
        help="清理多少天前的图片 (默认: 1)"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试日志"
    )

    # 无参数时显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # 检查必选参数
    if not args.server or not args.password:
        parser.error("--server 和 --password 是必选参数")

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    client = MilocoCameraClient(
        base_url=args.server,
        username=args.username,
        password=args.password,
    )

    # 登录
    if not client.login():
        sys.exit(1)

    # 列出摄像头
    if args.list:
        cameras = client.get_camera_list()
        print("\n摄像头列表:")
        print("-" * 80)
        for cam in cameras:
            print(f"  ID: {cam.get('did')}")
            print(f"  名称: {cam.get('name')}")
            print(f"  在线: {'是' if cam.get('online') else '否'}")
            print(f"  位置: {cam.get('home_name', '')} - {cam.get('room_name', '')}")
            print("-" * 80)
        sys.exit(0)

    # 获取摄像头图片
    if args.camera_id:
        # 单次获取
        if not args.loop:
            success = client.get_camera_image(
                camera_id=args.camera_id,
                output_dir=args.output,
                filename=args.filename,
            )
            sys.exit(0 if success else 1)

        # 循环获取
        logger.info("开始循环获取图片，间隔 %d 秒，按 Ctrl+C 停止", args.interval)
        if args.cleanup:
            logger.info("已启用自动清理，将删除 %d 天前的图片", args.cleanup_days)

        try:
            while True:
                # 获取图片
                client.get_camera_image(
                    camera_id=args.camera_id,
                    output_dir=args.output,
                    filename=args.filename,
                )

                # 清理过期图片
                if args.cleanup:
                    cleanup_old_images(args.output, args.cleanup_days)

                # 等待下次获取
                logger.info("等待 %d 秒后继续...", args.interval)
                time.sleep(args.interval)

        except KeyboardInterrupt:
            logger.info("用户中断，退出程序")
            sys.exit(0)

    # 没有指定操作
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
