#!/usr/bin/env python3
"""
Text Translator Tool
Translate text between languages using free APIs.
Based on: https://github.com/ssut/py-googletrans

Usage:
    python text_translator.py "Hello world" --to zh
    python text_translator.py --file document.txt --to es
    python text_translator.py "Bonjour" --to en --detect

Requirements:
    pip install googletrans==4.0.0-rc1
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from googletrans import Translator, LANGUAGES
except ImportError:
    # Fallback to simple HTTP-based translation
    LANGUAGES = {
        'en': 'english', 'zh-cn': 'chinese', 'es': 'spanish',
        'fr': 'french', 'de': 'german', 'ja': 'japanese',
        'ko': 'korean', 'ru': 'russian', 'pt': 'portuguese',
        'it': 'italian', 'ar': 'arabic', 'hi': 'hindi'
    }
    Translator = None


class SimpleTranslator:
    """Simple translator using MyMemory API (free, no key required)."""
    
    def __init__(self):
        try:
            import requests
            self.requests = requests
        except ImportError:
            print("Error: requests package required", file=sys.stderr)
            sys.exit(1)
    
    def translate(self, text: str, dest: str, src: str = 'auto') -> object:
        """Translate text using MyMemory API."""
        url = "https://api.mymemory.translated.net/get"
        
        # Map language codes
        lang_pair = f"{src}|{dest}" if src != 'auto' else f"en|{dest}"
        
        params = {
            'q': text,
            'langpair': lang_pair
        }
        
        try:
            response = self.requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('responseStatus') == 200:
                translated = data['responseData']['translatedText']
                
                class Result:
                    def __init__(self, text, src, dest):
                        self.text = text
                        self.src = src
                        self.dest = dest
                
                return Result(translated, src, dest)
            else:
                raise Exception(data.get('responseDetails', 'Translation failed'))
        except Exception as e:
            raise Exception(f"Translation error: {e}")
    
    def detect(self, text: str) -> object:
        """Detect language (simplified)."""
        class Detection:
            def __init__(self):
                self.lang = 'en'
                self.confidence = 0.5
        return Detection()


def get_translator():
    """Get translator instance."""
    if Translator:
        return Translator()
    return SimpleTranslator()


def translate_text(text: str, dest: str, src: str = 'auto') -> dict:
    """Translate text and return result."""
    translator = get_translator()
    
    result = translator.translate(text, dest=dest, src=src)
    
    return {
        'original': text,
        'translated': result.text,
        'source_lang': result.src,
        'target_lang': result.dest
    }


def translate_file(filepath: str, dest: str, src: str = 'auto', 
                   output: str = None, format: str = 'text') -> str:
    """Translate file content."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    translator = get_translator()
    
    if format == 'json':
        # Translate JSON values
        data = json.loads(content)
        translated_data = translate_json(data, translator, dest, src)
        result = json.dumps(translated_data, ensure_ascii=False, indent=2)
    else:
        # Translate plain text (line by line for better results)
        lines = content.split('\n')
        translated_lines = []
        
        for line in lines:
            if line.strip():
                try:
                    result = translator.translate(line, dest=dest, src=src)
                    translated_lines.append(result.text)
                except:
                    translated_lines.append(line)
            else:
                translated_lines.append(line)
        
        result = '\n'.join(translated_lines)
    
    # Save output
    if not output:
        output = str(path.stem) + f'_{dest}' + path.suffix
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return output


def translate_json(data, translator, dest: str, src: str = 'auto'):
    """Recursively translate JSON string values."""
    if isinstance(data, dict):
        return {k: translate_json(v, translator, dest, src) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_json(item, translator, dest, src) for item in data]
    elif isinstance(data, str) and data.strip():
        try:
            result = translator.translate(data, dest=dest, src=src)
            return result.text
        except:
            return data
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Translate text between languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Languages: en, zh-cn, es, fr, de, ja, ko, ru, pt, it, ar, hi, etc.

Examples:
  %(prog)s "Hello world" --to zh-cn
  %(prog)s "Bonjour" --to en
  %(prog)s --file document.txt --to es
  %(prog)s --file strings.json --to ja --format json
  %(prog)s --list-languages
        """
    )
    
    parser.add_argument('text', nargs='?', help='Text to translate')
    parser.add_argument('--to', '-t', dest='target', help='Target language code')
    parser.add_argument('--from', '-f', dest='source', default='auto', 
                       help='Source language (default: auto-detect)')
    parser.add_argument('--file', help='File to translate')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='File format for translation')
    parser.add_argument('--detect', '-d', action='store_true', 
                       help='Detect language only')
    parser.add_argument('--list-languages', '-l', action='store_true',
                       help='List available languages')
    
    args = parser.parse_args()
    
    if args.list_languages:
        print("Available languages:")
        for code, name in sorted(LANGUAGES.items()):
            print(f"  {code:8} {name}")
        return
    
    if args.detect and args.text:
        translator = get_translator()
        detection = translator.detect(args.text)
        lang_name = LANGUAGES.get(detection.lang, detection.lang)
        print(f"Detected: {detection.lang} ({lang_name})")
        print(f"Confidence: {detection.confidence:.1%}")
        return
    
    if args.file:
        if not args.target:
            parser.error("--to is required for file translation")
        
        output = translate_file(
            args.file, args.target, args.source, 
            args.output, args.format
        )
        print(f"✓ Translated file saved to: {output}")
        return
    
    if not args.text:
        parser.error("Please provide text to translate or use --file")
    
    if not args.target:
        parser.error("--to is required")
    
    result = translate_text(args.text, args.target, args.source)
    
    print(f"Original ({result['source_lang']}): {result['original']}")
    print(f"Translated ({result['target_lang']}): {result['translated']}")


if __name__ == "__main__":
    main()
