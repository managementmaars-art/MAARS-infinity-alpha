#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests", "pillow"]
# ///

"""
AI Video Generator - 生成 AI 视频
支持 Veo 3.1 (文生视频) 和 Sora 2 Pro (图生视频)
"""

import os
import sys
import time
import argparse
from pathlib import Path

import requests
from PIL import Image

# 配置
BASE_URL = "https://internal.infquest.com/api/aihubmix/v1"

# 模型映射
MODEL_MAP = {
    "veo-3.1": "veo-3.1-generate-preview",
    "sora-2-pro": "sora-2-pro",
}

# 支持图片输入的模型
IMAGE_SUPPORTED_MODELS = ["sora-2-pro"]


def parse_size(size: str) -> tuple[int, int] | None:
    """解析尺寸字符串，如 '1280x720' -> (1280, 720)"""
    if "x" in size.lower():
        parts = size.lower().split("x")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            pass
    return None


def resize_image(image_path: str, target_size: tuple[int, int]) -> str | None:
    """缩放图片到目标尺寸，返回临时文件路径"""
    try:
        img = Image.open(image_path)
        current_size = img.size  # (width, height)

        print(f"[Check] Image size: {current_size[0]}x{current_size[1]}, target: {target_size[0]}x{target_size[1]}")

        if current_size == target_size:
            print("[Check] Image size matches, no resize needed")
            return None

        print("[Resize] Resizing image to match target size...")
        resized = img.resize(target_size, Image.Resampling.LANCZOS)

        # 保存到临时文件
        path = Path(image_path)
        temp_path = path.parent / f"resized_{int(time.time())}{path.suffix}"
        resized.save(temp_path, quality=95)
        print(f"[Resize] Image resized to {target_size[0]}x{target_size[1]}: {temp_path}")
        return str(temp_path)
    except Exception as e:
        print(f"[Warning] Failed to resize image: {e}")
        return None


def get_mime_type(file_path: str) -> str:
    """根据文件扩展名获取 MIME 类型"""
    ext = Path(file_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    return mime_map.get(ext, "image/jpeg")


def create_video_task(api_key: str, model: str, prompt: str, size: str, seconds: str, image_path: str | None = None) -> str:
    """创建视频生成任务，返回 video_id"""
    headers = {"Authorization": f"Bearer {api_key}"}

    if image_path and model in IMAGE_SUPPORTED_MODELS:
        # 使用 multipart/form-data 上传图片，需指定 MIME 类型
        mime_type = get_mime_type(image_path)
        filename = Path(image_path).name
        with open(image_path, "rb") as f:
            files = {"input_reference": (filename, f, mime_type)}
            data = {"model": model, "prompt": prompt, "size": size, "seconds": seconds}
            response = requests.post(f"{BASE_URL}/videos", headers=headers, data=data, files=files)
    else:
        # 纯 JSON 请求
        headers["Content-Type"] = "application/json"
        json_data = {"model": model, "prompt": prompt, "size": size, "seconds": seconds}
        response = requests.post(f"{BASE_URL}/videos", headers=headers, json=json_data)

    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create task: {response.text}")

    return response.json()["id"]


def wait_for_completion(api_key: str, video_id: str, max_wait: int = 1200, poll_interval: int = 10) -> None:
    """轮询等待视频生成完成"""
    headers = {"Authorization": f"Bearer {api_key}"}
    start_time = time.time()
    last_status = ""

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/videos/{video_id}", headers=headers)

        if response.status_code != 200:
            print(f"[Warning] Failed to get status: {response.text}")
            time.sleep(poll_interval)
            continue

        data = response.json()
        status = data.get("status", "").lower()
        elapsed = int(time.time() - start_time)

        if status != last_status:
            print(f"[Status] {status} ({elapsed}s elapsed)")
            last_status = status

        if status in ("completed", "done", "success"):
            return

        if status in ("failed", "error"):
            error = data.get("error", {})
            error_msg = error if isinstance(error, str) else str(error)
            raise Exception(f"Video generation failed: {error_msg}")

        time.sleep(poll_interval)

    raise Exception("Video generation timed out (20 minutes)")


def download_video(api_key: str, video_id: str, output_path: str) -> None:
    """下载生成的视频"""
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{BASE_URL}/videos/{video_id}/content", headers=headers, stream=True, allow_redirects=True)

    if response.status_code != 200:
        raise Exception(f"Download failed with status {response.status_code}")

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="AI Video Generator")
    parser.add_argument("model", nargs="?", default="veo-3.1", help="Model: veo-3.1 / sora-2-pro")
    parser.add_argument("prompt", nargs="?", default="A cat sitting on a windowsill", help="Video description")
    parser.add_argument("size", nargs="?", default="720P", help="Resolution: 720P/1080P or 1280x720/720x1280")
    parser.add_argument("seconds", nargs="?", default="8", help="Duration in seconds")
    parser.add_argument("output_dir", nargs="?", default=".", help="Output directory")
    parser.add_argument("input_image", nargs="?", default="", help="Input image path (optional, Sora only)")
    args = parser.parse_args()

    # 获取 API Key
    api_key = os.environ.get("MAX_API_KEY")
    if not api_key:
        print("Error: Missing MAX_API_KEY environment variable")
        sys.exit(1)

    # 解析模型
    model_id = MODEL_MAP.get(args.model, args.model)

    print("[VideoGen] Starting video generation...")
    print(f"[Config] Model: {model_id}")
    print(f"[Config] Prompt: {args.prompt}")
    print(f"[Config] Size: {args.size}")
    print(f"[Config] Duration: {args.seconds}s")
    if args.input_image:
        print(f"[Config] Input image: {args.input_image}")
    print()

    temp_image = None
    image_to_upload = None

    try:
        # 处理输入图片
        if args.input_image and model_id in IMAGE_SUPPORTED_MODELS:
            if not Path(args.input_image).exists():
                print(f"Error: Input image not found: {args.input_image}")
                sys.exit(1)

            # 检查是否需要缩放
            target_size = parse_size(args.size)
            if target_size:
                temp_image = resize_image(args.input_image, target_size)
                image_to_upload = temp_image if temp_image else args.input_image
            else:
                image_to_upload = args.input_image
        elif args.input_image and model_id not in IMAGE_SUPPORTED_MODELS:
            print(f"[Warning] Model {model_id} does not support image input, ignoring input image")

        # Step 1: 创建任务
        print("[Step 1] Creating video generation task...")
        video_id = create_video_task(api_key, model_id, args.prompt, args.size, args.seconds, image_to_upload)
        print(f"[Step 1] Task created: {video_id}")
        print()

        # Step 2: 等待完成
        print("[Step 2] Waiting for video generation...")
        start_time = time.time()
        wait_for_completion(api_key, video_id)
        print("[Step 2] Video generation completed!")
        print()

        # Step 3: 下载视频
        print("[Step 3] Downloading video...")
        timestamp = int(time.time() * 1000)
        filename = f"generated_video_{timestamp}.mp4"
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        filepath = output_dir / filename
        download_video(api_key, video_id, str(filepath))

        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        total_time = int(time.time() - start_time)

        print(f"[Step 3] Video downloaded: {filepath}")
        print()
        print("=" * 50)
        print(f"Video saved: {filepath}")
        print(f"File size: {file_size_mb:.2f} MB")
        print(f"Total time: {total_time}s")
        print("=" * 50)

    finally:
        # 清理临时文件
        if temp_image and Path(temp_image).exists():
            Path(temp_image).unlink()
            print(f"[Cleanup] Removed temp file: {temp_image}")


if __name__ == "__main__":
    main()
