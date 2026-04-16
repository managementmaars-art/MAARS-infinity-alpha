#!/usr/bin/env python3
import requests
import json
import os
import argparse
import sys
import time
from datetime import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # Handle case where python-dotenv is not installed

# Configuration
# Configuration
# ==============================================================================
# [新手設定區] 請在這裡貼上你的 API Key
# 1. 刪除 None
# 2. 貼上你的 Key，並保留引號
# 例: DEFAULT_API_KEY = "ms-xxxyyyzzzz..."
# ==============================================================================
DEFAULT_API_KEY = None 

DEFAULT_MODEL = "Tongyi-MAI/Z-Image-Turbo"
BASE_URL = "https://api-inference.modelscope.cn/"

def generate_image(prompt, output_path=None, api_key=None, model=None, size="1024x1024"):
    token = api_key or os.environ.get("MODELSCOPE_API_TOKEN") or DEFAULT_API_KEY
    
    if not token:
        print("Error: No API Key provided.")
        print("Please set the MODELSCOPE_API_TOKEN environment variable or pass --api-key.")
        return False
    model_id = model or DEFAULT_MODEL
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = prompt[:20].replace(" ", "_").replace("/", "")
        output_path = f"zimage_{timestamp}_{safe_prompt}.png"
        
    print(f"Generating image with Z-Image ({model_id})...")
    print(f"Prompt: {prompt}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelScope-Async-Mode": "true"  # Required for Z-Image
    }
    
    data = {
        "model": model_id,
        "prompt": prompt,
        "n": 1,
        "size": size
    }
    
    try:
        # 1. Submit Async Task
        submit_url = f"{BASE_URL}v1/images/generations"
        response = requests.post(submit_url, headers=headers, json=data, timeout=60)
        
        if response.status_code != 200:
            print(f"Error submitting task: {response.status_code}")
            print(response.text)
            return False

        task_data = response.json()
        task_id = task_data.get("task_id")
        if not task_id:
            print("Error: No task_id received.")
            return False
            
        print(f"Task submitted successfully (ID: {task_id}). Polling for result...")
        
        # 2. Poll for Status
        # Important header for polling image tasks
        poll_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-ModelScope-Task-Type": "image_generation" 
        }
        
        start_time = time.time()
        timeout_seconds = 300 # 5 minutes timeout
        
        while True:
            if time.time() - start_time > timeout_seconds:
                print("Timeout waiting for image generation.")
                return False
                
            poll_resp = requests.get(
                f"{BASE_URL}v1/tasks/{task_id}",
                headers=poll_headers,
                timeout=30
            )
            
            if poll_resp.status_code != 200:
                print(f"Polling error: {poll_resp.status_code}")
                # Don't break immediately on transient network errors, maybe retry?
                # For now we print and sleep
            else:
                data = poll_resp.json()
                status = data.get("task_status")
                
                if status == "SUCCEED":
                    if "output_images" in data and len(data["output_images"]) > 0:
                        image_url = data["output_images"][0]
                        print(f"Generation successful! Downloading from {image_url}...")
                        
                        # Download Image
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            with open(output_path, "wb") as f:
                                f.write(img_response.content)
                            print(f"Image saved to: {os.path.abspath(output_path)}")
                            return True
                        else:
                            print("Error: Failed to download the generated image file.")
                            return False
                    else:
                        print("Task succeeded but no output image found.")
                        return False
                        
                elif status == "FAILED":
                    print("Generation Failed.")
                    print(f"Details: {data}")
                    return False
                
                elif status in ["PENDING", "RUNNING", "QUEUED", "PROCESSING"]:
                    print(f"Status: {status}...", end="\r")
                else:
                    print(f"Unknown status: {status}")

            time.sleep(2)
            
    except Exception as e:
        print(f"Exception during generation: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images using ModelScope Z-Image API")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--output", "-o", help="Output filename")
    parser.add_argument("--model", "-m", help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--size", "-s", default="1024x1024", help="Image size (default: 1024x1024)")
    parser.add_argument("--api-key", "-k", help="ModelScope API Key")
    
    args = parser.parse_args()
    
    success = generate_image(args.prompt, args.output, model=args.model, size=args.size, api_key=args.api_key)
    if not success:
        sys.exit(1)
