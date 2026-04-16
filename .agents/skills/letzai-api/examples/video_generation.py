"""
LetzAI Video Generation Examples

This module demonstrates how to generate videos using the LetzAI API
with various models and configurations.
"""

import os
import time
import requests
from typing import Optional, Dict, Any

API_BASE_URL = "https://api.letz.ai"
API_KEY = os.environ.get("LETZAI_API_KEY", "YOUR_API_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def poll_status(
    endpoint: str,
    job_id: str,
    interval_seconds: float = 3.0,
    max_attempts: int = 120
) -> Dict[str, Any]:
    """
    Poll for job completion.
    
    Args:
        endpoint: API endpoint (e.g., 'images', 'videos')
        job_id: The job ID to poll
        interval_seconds: Time between polls (default: 3s for images, 2-3s for videos)
        max_attempts: Maximum number of polling attempts
        
    Returns:
        The completed job data
        
    Raises:
        TimeoutError: If job doesn't complete within max_attempts
        RuntimeError: If job fails
    """
    url = f"{API_BASE_URL}/{endpoint}/{job_id}"
    
    for attempt in range(max_attempts):
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        status = data.get("status", "")
        print(f"Attempt {attempt + 1}: Status = {status}")
        
        if status == "ready":
            return data
        
        if status == "failed":
            error_msg = data.get("error", "Unknown error")
            raise RuntimeError(f"Job failed: {error_msg}")
        
        time.sleep(interval_seconds)
    
    raise TimeoutError(f"Job {job_id} did not complete within {max_attempts} attempts")


def poll_image_status(image_id: str) -> Dict[str, Any]:
    """Poll for image completion (3s interval)."""
    return poll_status("images", image_id, interval_seconds=3.0)


def poll_video_status(video_id: str) -> Dict[str, Any]:
    """Poll for video completion (2.5s interval)."""
    return poll_status("videos", video_id, interval_seconds=2.5)


# =============================================================================
# Image Generation (needed for video source)
# =============================================================================

def generate_source_image(prompt: str) -> Dict[str, Any]:
    """
    Generate a source image for video creation.
    
    Args:
        prompt: Text description of the image
        
    Returns:
        The completed image data including ID and URLs
    """
    print("=== Generating Source Image ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/images",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "baseModel": "gemini-3-pro-image-preview",
            "mode": "2k"
        }
    )
    response.raise_for_status()
    
    data = response.json()
    image_id = data["id"]
    print(f"Image generation started. ID: {image_id}")
    
    result = poll_image_status(image_id)
    print(f"\nImage ready!")
    print(f"URL: {result['imageVersions']['original']}")
    
    return result


# =============================================================================
# Video Generation Examples
# =============================================================================

def generate_video_from_url(
    prompt: str,
    image_url: str,
    mode: str = "default",
    duration: int = 5
) -> Dict[str, Any]:
    """
    Example 1: Generate video from an image URL.
    
    Args:
        prompt: Text description of the video motion
        image_url: URL of the source image
        mode: Video model ('default', 'veo31', 'kling26', 'wan25')
        duration: Video duration in seconds
        
    Returns:
        The completed video data
    """
    print(f"=== Video Generation from URL ({mode}) ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/videos",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "imageUrl": image_url,
            "settings": {
                "mode": mode,
                "duration": duration
            }
        }
    )
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]
    print(f"Video generation started. ID: {video_id}")
    
    result = poll_video_status(video_id)
    print(f"\nVideo ready!")
    print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
    print(f"Credits used: {result.get('creditsUsed', 'N/A')}")
    
    return result


def generate_video_from_image_id(
    prompt: str,
    image_completion_id: str,
    mode: str = "kling26",
    duration: int = 5
) -> Dict[str, Any]:
    """
    Example 2: Generate video from a previously generated image ID.
    
    This is more efficient if you've already generated an image with LetzAI.
    
    Args:
        prompt: Text description of the video motion
        image_completion_id: ID from previous image generation
        mode: Video model
        duration: Video duration in seconds
        
    Returns:
        The completed video data
    """
    print(f"=== Video Generation from Image ID ({mode}) ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/videos",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "originalImageCompletionId": image_completion_id,
            "settings": {
                "mode": mode,
                "duration": duration
            }
        }
    )
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]
    print(f"Video generation started. ID: {video_id}")
    
    result = poll_video_status(video_id)
    print(f"\nVideo ready!")
    print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
    
    return result


def generate_video_veo31(
    prompt: str,
    image_url: str
) -> Dict[str, Any]:
    """
    Example 3: Generate high-quality video with VEO 3.1.
    
    VEO 3.1 produces the highest quality videos at 8 seconds duration.
    
    Args:
        prompt: Text description of the video motion
        image_url: URL of the source image
        
    Returns:
        The completed video data
    """
    print("=== VEO 3.1 Video Generation ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/videos",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "imageUrl": image_url,
            "settings": {
                "mode": "veo31"
                # VEO 3.1 has fixed 8-second duration
            }
        }
    )
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]
    print(f"VEO 3.1 generation started. ID: {video_id}")
    print("Note: VEO 3.1 may take longer to generate...")
    
    # VEO can take longer, increase polling time
    result = poll_status("videos", video_id, interval_seconds=5.0, max_attempts=120)
    print(f"\nVideo ready!")
    print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
    print(f"Credits used: {result.get('creditsUsed', 'N/A')} (VEO 3.1 uses 1500-6000 credits)")
    
    return result


def generate_video_kling(
    prompt: str,
    image_url: str,
    duration: int = 10
) -> Dict[str, Any]:
    """
    Example 4: Generate video with Kling 2.6.
    
    Kling 2.6 offers a good balance of quality and duration (5-10 seconds).
    
    Args:
        prompt: Text description of the video motion
        image_url: URL of the source image
        duration: Video duration (5-10 seconds)
        
    Returns:
        The completed video data
    """
    print("=== Kling 2.6 Video Generation ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/videos",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "imageUrl": image_url,
            "settings": {
                "mode": "kling26",
                "duration": min(max(duration, 5), 10)  # Clamp to 5-10
            }
        }
    )
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]
    print(f"Kling 2.6 generation started. ID: {video_id}")
    
    result = poll_video_status(video_id)
    print(f"\nVideo ready!")
    print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
    
    return result


def generate_video_wan(
    prompt: str,
    image_url: str,
    duration: int = 5
) -> Dict[str, Any]:
    """
    Example 5: Generate video with Wan 2.5.
    
    Wan 2.5 is good for smooth motion effects.
    
    Args:
        prompt: Text description of the video motion
        image_url: URL of the source image
        duration: Video duration (5-10 seconds)
        
    Returns:
        The completed video data
    """
    print("=== Wan 2.5 Video Generation ===\n")
    
    response = requests.post(
        f"{API_BASE_URL}/videos",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "imageUrl": image_url,
            "settings": {
                "mode": "wan25",
                "duration": duration
            }
        }
    )
    response.raise_for_status()
    
    data = response.json()
    video_id = data["id"]
    print(f"Wan 2.5 generation started. ID: {video_id}")
    
    result = poll_video_status(video_id)
    print(f"\nVideo ready!")
    print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
    
    return result


# =============================================================================
# Complete Workflow Examples
# =============================================================================

def complete_image_to_video_workflow():
    """
    Example 6: Complete workflow - generate image then video.
    
    This demonstrates the full workflow of:
    1. Generating a source image
    2. Creating a video from that image
    """
    print("=" * 60)
    print("COMPLETE IMAGE-TO-VIDEO WORKFLOW")
    print("=" * 60 + "\n")
    
    # Step 1: Generate source image
    image_result = generate_source_image(
        "A majestic lion standing on a rock at sunset, golden savanna in background"
    )
    image_id = image_result["id"]
    
    print("\n" + "-" * 40 + "\n")
    
    # Step 2: Generate video from the image
    video_result = generate_video_from_image_id(
        prompt="The lion slowly turns its head and looks at the camera, wind blowing through its mane",
        image_completion_id=image_id,
        mode="kling26",
        duration=5
    )
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"Source Image: {image_result['imageVersions']['original']}")
    print(f"Video: {video_result['videoPaths'].get('mp4', 'N/A')}")
    
    return {
        "image": image_result,
        "video": video_result
    }


def compare_video_models(image_url: str):
    """
    Example 7: Compare different video models.
    
    Generates videos with different models from the same source image.
    
    Args:
        image_url: URL of the source image
    """
    print("=" * 60)
    print("COMPARING VIDEO MODELS")
    print("=" * 60 + "\n")
    
    prompt = "Gentle camera pan with subtle motion, cinematic"
    
    models = [
        {"mode": "default", "duration": 4},
        {"mode": "kling26", "duration": 5},
        # Uncomment for VEO (expensive):
        # {"mode": "veo31"},
    ]
    
    results = {}
    
    for config in models:
        mode = config["mode"]
        print(f"\n--- Testing {mode} ---\n")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/videos",
                headers=HEADERS,
                json={
                    "prompt": prompt,
                    "imageUrl": image_url,
                    "settings": config
                }
            )
            response.raise_for_status()
            
            data = response.json()
            video_id = data["id"]
            
            result = poll_video_status(video_id)
            results[mode] = {
                "url": result["videoPaths"].get("mp4", "N/A"),
                "credits": result.get("creditsUsed", "N/A")
            }
            
        except Exception as e:
            print(f"Error with {mode}: {e}")
            results[mode] = {"error": str(e)}
    
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    for mode, data in results.items():
        print(f"\n{mode}:")
        if "error" in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  URL: {data['url']}")
            print(f"  Credits: {data['credits']}")
    
    return results


# =============================================================================
# Error Handling Example
# =============================================================================

def generate_video_with_error_handling(
    prompt: str,
    image_url: str,
    mode: str = "default"
) -> Optional[Dict[str, Any]]:
    """
    Example 8: Video generation with comprehensive error handling.
    
    Args:
        prompt: Text description of the video motion
        image_url: URL of the source image
        mode: Video model
        
    Returns:
        The completed video data, or None if failed
    """
    print("=== Video Generation with Error Handling ===\n")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/videos",
            headers=HEADERS,
            json={
                "prompt": prompt,
                "imageUrl": image_url,
                "settings": {"mode": mode}
            }
        )
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise ValueError("Invalid API key. Check your credentials at letz.ai/subscription")
        elif response.status_code == 402:
            raise ValueError("Insufficient credits. Top up at letz.ai/subscription")
        elif response.status_code == 400:
            error_data = response.json()
            raise ValueError(f"Invalid parameters: {error_data.get('error', 'Unknown')}")
        elif response.status_code == 429:
            raise ValueError("Rate limited. Please wait before making more requests.")
        
        response.raise_for_status()
        
        data = response.json()
        video_id = data["id"]
        print(f"Video generation started. ID: {video_id}")
        
        result = poll_video_status(video_id)
        print(f"\nVideo ready!")
        print(f"MP4 URL: {result['videoPaths'].get('mp4', 'N/A')}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to LetzAI API. Check your internet connection.")
        return None
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Try again later.")
        return None
        
    except ValueError as e:
        print(f"Error: {e}")
        return None
        
    except RuntimeError as e:
        print(f"Generation failed: {e}")
        return None
        
    except TimeoutError as e:
        print(f"Timeout: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run example demonstrations."""
    
    # First, generate a source image
    print("First, we need a source image for video generation...\n")
    
    try:
        image_result = generate_source_image(
            "A serene mountain lake at dawn with mist rising from the water"
        )
        image_url = image_result["imageVersions"]["original"]
        
        print("\n" + "=" * 60 + "\n")
        
        # Generate a video from the image
        generate_video_from_url(
            prompt="Gentle ripples spread across the lake as morning light intensifies",
            image_url=image_url,
            mode="default",
            duration=4
        )
        
        # Uncomment to run other examples:
        # generate_video_kling(prompt="...", image_url=image_url)
        # generate_video_veo31(prompt="...", image_url=image_url)
        # complete_image_to_video_workflow()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
