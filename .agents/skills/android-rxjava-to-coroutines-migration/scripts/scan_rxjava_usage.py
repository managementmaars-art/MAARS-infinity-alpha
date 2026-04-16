#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


TYPE_PATTERNS = {
    'Single': re.compile(r'\bSingle<'),
    'Maybe': re.compile(r'\bMaybe<'),
    'Completable': re.compile(r'\bCompletable\b'),
    'Observable': re.compile(r'\bObservable<'),
    'Flowable': re.compile(r'\bFlowable<'),
    'CompositeDisposable': re.compile(r'\bCompositeDisposable\b'),
    'BehaviorSubject': re.compile(r'\bBehaviorSubject<'),
    'PublishSubject': re.compile(r'\bPublishSubject<'),
    'ReplaySubject': re.compile(r'\bReplaySubject<'),
}

OPERATOR_PATTERNS = {
    'subscribeOn': re.compile(r'\.subscribeOn\('),
    'observeOn': re.compile(r'\.observeOn\('),
    'flatMap': re.compile(r'\.flatMap\('),
    'switchMap': re.compile(r'\.switchMap\('),
    'combineLatest': re.compile(r'combineLatest'),
}


def scan(project: Path) -> dict[str, object]:
    files = sorted(path for path in project.rglob('*') if path.suffix in {'.kt', '.java'})
    type_counts = Counter()
    operator_counts = Counter()
    imports: Counter[str] = Counter()
    per_file: list[dict[str, object]] = []

    for path in files:
        text = path.read_text(encoding='utf-8')
        rx_imports = [line.strip() for line in text.splitlines() if line.strip().startswith('import io.reactivex')]
        if not rx_imports:
            continue
        file_types = Counter({name: len(pattern.findall(text)) for name, pattern in TYPE_PATTERNS.items() if pattern.search(text)})
        file_ops = Counter({name: len(pattern.findall(text)) for name, pattern in OPERATOR_PATTERNS.items() if pattern.search(text)})
        type_counts.update(file_types)
        operator_counts.update(file_ops)
        imports.update(rx_imports)
        per_file.append(
            {
                'file': str(path),
                'imports': rx_imports,
                'types': dict(file_types),
                'operators': dict(file_ops),
            }
        )

    return {
        'project': str(project),
        'files_scanned': len(files),
        'imports': dict(imports),
        'type_counts': dict(type_counts),
        'operator_counts': dict(operator_counts),
        'files': per_file,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Scan a project for Android RxJava usage that should migrate to coroutines and Flow.')
    parser.add_argument('project', type=Path)
    parser.add_argument('--json', action='store_true', help='Emit JSON output')
    args = parser.parse_args()

    report = scan(args.project)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps({'project': report['project'], 'type_counts': report['type_counts'], 'operator_counts': report['operator_counts']}, indent=2))
        for item in report['files']:
            print(f"- {item['file']}: types={item['types']} operators={item['operators']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
