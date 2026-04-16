# Claude Instructions for @skillhq/telegram

## Version and Release Workflow

When using `/commit-and-push` or committing changes:

1. **Always bump the version** in `package.json` before committing:
   - Patch (0.x.Y): Bug fixes
   - Minor (0.X.0): New features (like new commands)
   - Major (X.0.0): Breaking changes

2. **After pushing, always create and push a git tag**:
   ```bash
   git tag v<version>
   git push origin v<version>
   ```

3. **Tag naming**: Use `v` prefix (e.g., `v0.3.0`, `v1.0.0`)

## Commit Message Format

Follow conventional commits style:
- `Add <feature>` for new features
- `Fix <bug>` for bug fixes
- `Update <component>` for changes
- Include `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>` at the end
