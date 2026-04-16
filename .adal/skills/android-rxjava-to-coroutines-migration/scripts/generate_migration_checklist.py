#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scan_rxjava_usage import scan


TYPE_REPLACEMENTS = {
    'Single': 'Replace with a main-safe suspend function that returns a single value.',
    'Maybe': 'Replace with a suspend function that returns a nullable value when absence is valid.',
    'Completable': 'Replace with a suspend function that performs work without returning a value.',
    'Observable': 'Replace with Flow when the stream is cold or with SharedFlow/StateFlow for hot streams.',
    'Flowable': 'Replace with Flow and verify backpressure assumptions explicitly.',
    'CompositeDisposable': 'Replace with lifecycle-aware coroutine scopes and Job ownership.',
    'BehaviorSubject': 'Replace with MutableStateFlow when state replay is required.',
    'PublishSubject': 'Replace with MutableSharedFlow for one-off events or broadcast-style flows.',
    'ReplaySubject': 'Replace with MutableSharedFlow(replay = n) when replay semantics are required.',
}

OPERATOR_REPLACEMENTS = {
    'subscribeOn': 'Move threading to repository or upstream coroutine context with withContext or flowOn.',
    'observeOn': 'Move UI collection to lifecycle-aware scopes and expose main-safe APIs.',
    'flatMap': 'Review whether flatMapMerge, flatMapConcat, or a suspend boundary preserves behavior.',
    'switchMap': 'Review flatMapLatest when latest-only behavior is required.',
    'combineLatest': 'Review Flow combine semantics and initial emission expectations.',
}


def build_checklist(project: Path) -> dict[str, object]:
    report = scan(project)
    checklist: list[str] = [
        'Inventory all RxJava imports before changing public APIs.',
        'Migrate repository and data-source surfaces before updating ViewModels or UI collection.',
        'Keep lifecycle ownership explicit when replacing disposables with coroutine scopes.',
    ]
    for name in sorted(report['type_counts']):
        checklist.append(TYPE_REPLACEMENTS.get(name, f'Review migration strategy for {name}.'))
    for name in sorted(report['operator_counts']):
        checklist.append(OPERATOR_REPLACEMENTS.get(name, f'Review operator semantics for {name} manually.'))
    return {'project': str(project), 'checklist': checklist, 'scan': report}


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate a coroutine migration checklist from scanned RxJava usage.')
    parser.add_argument('project', type=Path)
    parser.add_argument('--json', action='store_true', help='Emit JSON output')
    args = parser.parse_args()

    report = build_checklist(args.project)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Migration checklist for {report['project']}:")
        for item in report['checklist']:
            print(f"- {item}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
