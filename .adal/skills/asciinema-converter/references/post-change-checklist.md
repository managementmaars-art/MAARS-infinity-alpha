# Post-Change Checklist

After modifying this skill:

## Single File Mode

1. [ ] Preflight check detects asciinema version correctly
2. [ ] Discovery uses heredoc wrapper for bash compatibility
3. [ ] Compression calculation handles macOS stat syntax
4. [ ] All AskUserQuestion phases are present
5. [ ] TodoWrite template matches actual workflow

## Batch Mode

1. [ ] `--batch` flag triggers batch workflow (phases 7-10)
2. [ ] `--source` skips Phase 7 (source selection)
3. [ ] `--output-dir` skips Phase 8 (output organization)
4. [ ] `--skip-existing` prevents re-conversion of existing files
5. [ ] Aggregate compression ratio calculated correctly
6. [ ] iTerm2 filename format documented
