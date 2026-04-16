#!/usr/bin/env python3

import requests
import json
import sys
import os

def load_api_key():
    config_path = os.path.expanduser('~/apikey.json')
    
    api_key = os.environ.get('MINIMAX_API_KEY')
    if api_key:
        return api_key
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('MINIMAX_API_KEY')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def text_to_image(prompt, model='image-01', aspect_ratio='1:1', width=None, height=None, n=1, seed=None, response_format='url', output_file=None):
    api_key = load_api_key()
    if not api_key:
        print("Error: API Key not found. Please configure it first.", file=sys.stderr)
        sys.exit(1)

    url = 'https://api.minimaxi.com/v1/image_generation'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': model,
        'prompt': prompt,
        'n': n,
        'response_format': response_format,
        'prompt_optimizer': False,
        'aigc_watermark': False
    }

    if aspect_ratio:
        payload['aspect_ratio'] = aspect_ratio
    
    if width and height:
        payload['width'] = width
        payload['height'] = height
    
    if seed:
        payload['seed'] = seed

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('base_resp', {}).get('status_code') == 0:
            data = result.get('data', {}).get('image_urls', [])
            if data:
                print(f"Image generation successful!")
                print(f"Generated {len(data)} image(s)")
                
                for idx, url in enumerate(data):
                    print(f"\nImage {idx + 1}:")
                    print(f"URL: {url}")
                    
                    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    url_file = os.path.join(script_dir, 'image_urls.txt')
                    with open(url_file, 'a') as f:
                        f.write(f"{url}\n")
                    print(f"URL saved to: {url_file}")
                    
                    if output_file:
                        img_response = requests.get(url, timeout=60)
                        img_response.raise_for_status()
                        filename = output_file if n == 1 else f"{output_file.rsplit('.', 1)[0]}_{idx + 1}.{output_file.rsplit('.', 1)[1]}"
                        with open(filename, 'wb') as f:
                            f.write(img_response.content)
                        print(f"Saved to: {filename}")
                
                return data
            else:
                print("Error: No images generated", file=sys.stderr)
                sys.exit(1)
        else:
            error_msg = result.get('base_resp', {}).get('status_msg', 'Unknown error')
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def image_to_image(prompt, subject_reference, model='image-01', aspect_ratio='1:1', width=None, height=None, n=1, seed=None, response_format='url', output_file=None):
    api_key = load_api_key()
    if not api_key:
        print("Error: API Key not found. Please configure it first.", file=sys.stderr)
        sys.exit(1)

    url = 'https://api.minimaxi.com/v1/image_generation'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': model,
        'prompt': prompt,
        'subject_reference': subject_reference,
        'n': n,
        'response_format': response_format,
        'prompt_optimizer': False,
        'aigc_watermark': False
    }

    if aspect_ratio:
        payload['aspect_ratio'] = aspect_ratio
    
    if width and height:
        payload['width'] = width
        payload['height'] = height
    
    if seed:
        payload['seed'] = seed

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('base_resp', {}).get('status_code') == 0:
            data = result.get('data', {}).get('image_urls', [])
            if data:
                print(f"Image-to-image generation successful!")
                print(f"Generated {len(data)} image(s)")
                
                for idx, url in enumerate(data):
                    print(f"\nImage {idx + 1}:")
                    print(f"URL: {url}")
                    
                    if output_file:
                        img_response = requests.get(url, timeout=60)
                        img_response.raise_for_status()
                        filename = output_file if n == 1 else f"{output_file.rsplit('.', 1)[0]}_{idx + 1}.{output_file.rsplit('.', 1)[1]}"
                        with open(filename, 'wb') as f:
                            f.write(img_response.content)
                        print(f"Saved to: {filename}")
                
                return data
            else:
                print("Error: No images generated", file=sys.stderr)
                sys.exit(1)
        else:
            error_msg = result.get('base_resp', {}).get('status_msg', 'Unknown error')
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 image.py <prompt> [options]", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --model <model>         Model version (default: image-01)", file=sys.stderr)
        print("  --aspect-ratio <ratio>  Image aspect ratio (default: 1:1)", file=sys.stderr)
        print("  --width <pixels>        Image width (512-2048, multiple of 8)", file=sys.stderr)
        print("  --height <pixels>       Image height (512-2048, multiple of 8)", file=sys.stderr)
        print("  --n <count>             Number of images to generate (1-9, default: 1)", file=sys.stderr)
        print("  --seed <number>         Random seed for reproducibility", file=sys.stderr)
        print("  --format <format>       Response format: url, base64 (default: url)", file=sys.stderr)
        print("  --output <file>         Save image to file (png/jpg format)", file=sys.stderr)
        print("  --subject <path>        Subject reference image for I2I (image to image)", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python3 image.py '一只可爱的猫咪在阳光下玩耍'", file=sys.stderr)
        print("  python3 image.py '一只可爱的猫咪在阳光下玩耍' --aspect-ratio 16:9 --n 2", file=sys.stderr)
        print("  python3 image.py '一只可爱的猫咪在阳光下玩耍' --width 1024 --height 768 --output cat.png", file=sys.stderr)
        print("  python3 image.py --subject /path/to/image.jpg '猫咪玩耍'", file=sys.stderr)
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = 'image-01'
    aspect_ratio = '1:1'
    width = None
    height = None
    n = 1
    seed = None
    response_format = 'url'
    output_file = None
    subject_reference = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--aspect-ratio' and i + 1 < len(sys.argv):
            aspect_ratio = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--width' and i + 1 < len(sys.argv):
            width = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--height' and i + 1 < len(sys.argv):
            height = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--n' and i + 1 < len(sys.argv):
            n = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--seed' and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--format' and i + 1 < len(sys.argv):
            response_format = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--subject' and i + 1 < len(sys.argv):
            subject_reference = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if subject_reference:
        if len(sys.argv) < 3:
            print("Error: --subject requires a prompt", file=sys.stderr)
            sys.exit(1)
        prompt = sys.argv[2]
        image_to_image(prompt, subject_reference, model, aspect_ratio, width, height, n, seed, response_format, output_file)
    else:
        text_to_image(prompt, model, aspect_ratio, width, height, n, seed, response_format, output_file)
