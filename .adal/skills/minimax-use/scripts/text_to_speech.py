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

VALID_EMOTIONS = ['happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised', 'calm', 'fluent', 'whisper']
EMOTION_NAMES = {
    'happy': '高兴',
    'sad': '悲伤',
    'angry': '愤怒',
    'fearful': '害怕',
    'disgusted': '厌恶',
    'surprised': '惊讶',
    'calm': '中性',
    'fluent': '生动',
    'whisper': '低语'
}

def text_to_speech(text, model='speech-2.8-hd', output_file=None, voice_id='female-shaonv', emotion=None):
    api_key = load_api_key()
    if not api_key:
        print("Error: API Key not found. Please configure it first.", file=sys.stderr)
        sys.exit(1)

    url = 'https://api.minimaxi.com/v1/t2a_v2'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    voice_setting = {
        'voice_id': voice_id,
        'speed': 1.0,
        'vol': 1.0,
        'pitch': 0
    }
    
    if emotion and emotion in VALID_EMOTIONS:
        voice_setting['emotion'] = emotion

    payload = {
        'model': model,
        'text': text,
        'stream': False,
        'voice_setting': voice_setting,
        'audio_setting': {
            'sample_rate': 32000,
            'format': 'mp3',
            'bitrate': 128000
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('base_resp', {}).get('status_code') == 0:
            data = result.get('data')
            if data and data.get('audio'):
                if output_file:
                    import binascii
                    audio_data = binascii.unhexlify(data['audio'])
                    with open(output_file, 'wb') as f:
                        f.write(audio_data)
                    print(f"Audio saved to: {output_file}")
                else:
                    print(json.dumps({'audio_hex': data['audio']}, indent=2, ensure_ascii=False))
            else:
                print("Error: No audio data in response", file=sys.stderr)
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

def list_voices():
    voices = {
        "中文 (普通话)": [
            {"voice_id": "male-qn-qingse", "name": "青涩青年音色"},
            {"voice_id": "male-qn-jingying", "name": "精英青年音色"},
            {"voice_id": "male-qn-badao", "name": "霸道青年音色"},
            {"voice_id": "male-qn-daxuesheng", "name": "青年大学生音色"},
            {"voice_id": "female-shaonv", "name": "少女音色"},
            {"voice_id": "female-yujie", "name": "御姐音色"},
            {"voice_id": "female-chengshu", "name": "成熟女性音色"},
            {"voice_id": "female-tianmei", "name": "甜美女性音色"},
            {"voice_id": "Chinese (Mandarin)_Reliable_Executive", "name": "沉稳高管"},
            {"voice_id": "Chinese (Mandarin)_News_Anchor", "name": "新闻女声"},
            {"voice_id": "Chinese (Mandarin)_Mature_Woman", "name": "傲娇御姐"},
            {"voice_id": "Chinese (Mandarin)_Unrestrained_Young_Man", "name": "不羁青年"},
            {"voice_id": "Chinese (Mandarin)_Gentleman", "name": "温润男声"},
            {"voice_id": "Chinese (Mandarin)_Sweet_Lady", "name": "甜美女声"},
            {"voice_id": "Chinese (Mandarin)_Radio_Host", "name": "电台男主播"},
            {"voice_id": "Chinese (Mandarin)_Lyrical_Voice", "name": "抒情男声"}
        ],
        "英文": [
            {"voice_id": "English_Trustworthy_Man", "name": "Trustworthy Man"},
            {"voice_id": "English_Graceful_Lady", "name": "Graceful Lady"},
            {"voice_id": "Sweet_Girl", "name": "Sweet Girl"}
        ],
        "日文": [
            {"voice_id": "Japanese_IntellectualSenior", "name": "Intellectual Senior"},
            {"voice_id": "Japanese_GentleButler", "name": "Gentle Butler"}
        ],
        "韩文": [
            {"voice_id": "Korean_SweetGirl", "name": "Sweet Girl"},
            {"voice_id": "Korean_ElegantPrincess", "name": "Elegant Princess"}
        ]
    }
    
    print("可用音色列表：\n")
    for lang, voice_list in voices.items():
        print(f"{lang}:")
        for voice in voice_list:
            print(f"  {voice['voice_id']}: {voice['name']}")
        print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 text_to_speech.py <text> [options]", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --model <model>         Model version (default: speech-2.8-hd)", file=sys.stderr)
        print("  --output <file>         Save audio to file (mp3 format)", file=sys.stderr)
        print("  --voice <voice_id>      Voice ID (default: female-shaonv)", file=sys.stderr)
        print("  --emotion <emotion>     Emotion: happy, sad, angry, fearful, disgusted,", file=sys.stderr)
        print("                          surprised, calm, fluent, whisper", file=sys.stderr)
        print("  --list-voices           List available voices", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python3 text_to_speech.py '你好世界' --output audio.mp3", file=sys.stderr)
        print("  python3 text_to_speech.py '今天真开心' --emotion happy --output happy.mp3", file=sys.stderr)
        print("  python3 text_to_speech.py --list-voices", file=sys.stderr)
        sys.exit(1)
    
    if '--list-voices' in sys.argv:
        list_voices()
        sys.exit(0)
    
    text = sys.argv[1]
    model = 'speech-2.8-hd'
    output_file = None
    voice_id = 'female-shaonv'
    emotion = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--model' and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--voice' and i + 1 < len(sys.argv):
            voice_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--emotion' and i + 1 < len(sys.argv):
            emotion = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if emotion and emotion not in VALID_EMOTIONS:
        print(f"Error: Invalid emotion '{emotion}'. Valid options: {', '.join(VALID_EMOTIONS)}", file=sys.stderr)
        sys.exit(1)
    
    text_to_speech(text, model, output_file, voice_id, emotion)
