# TodoWrite Task Templates

## Single File Mode

```
1. [Preflight] Check asciinema CLI and convert command
2. [Preflight] Offer installation if missing
3. [Discovery] Find .cast files with metadata
4. [Selection] AskUserQuestion: file to convert
5. [Options] AskUserQuestion: conversion options (multi-select)
6. [Location] AskUserQuestion: output location
7. [Convert] Run asciinema convert -f txt
8. [Report] Display compression ratio and output path
9. [Index] Create timestamp index if requested
10. [Next] AskUserQuestion: next steps
```

## Batch Mode (--batch flag)

```
1. [Preflight] Check asciinema CLI and convert command
2. [Preflight] Offer installation if missing
3. [Source] AskUserQuestion: source directory (skip if --source)
4. [Output] AskUserQuestion: output directory (skip if --output-dir)
5. [Batch] Execute batch conversion with progress
6. [Report] Display aggregate compression stats
7. [Next] AskUserQuestion: batch next steps
```
