# Worker Pitfalls: Platform-Specific Gotchas

Inject relevant sections into worker prompts based on the task's target language/platform.

---

## Bash

**Subshell variable scoping** -- Variables set inside a pipe subshell do not propagate.
```bash
# BROKEN: count stays 0 (while runs in subshell)
count=0; cat file.txt | while read line; do count=$((count+1)); done
# FIX: redirect instead of pipe
while read line; do count=$((count+1)); done < file.txt
```

**macOS vs GNU tools** -- BSD sed/awk/head flags differ from GNU.
```bash
# BROKEN on macOS:
sed -i 's/old/new/' file.txt
# FIX (macOS): sed -i '' 's/old/new/' file.txt
```

**rm alias hangs workers** -- Some systems alias `rm` to `rm -i`, blocking on confirmation.
```bash
# FIX: bypass aliases
/bin/rm -f somefile
```

**Silent pipe failures** -- Pipeline exit code is the last command's. Earlier failures are hidden.
```bash
# FIX: enable pipefail at top of script
set -o pipefail
```

**Unquoted variables** -- Word splitting breaks paths with spaces.
```bash
# BROKEN: cat "my" and "report.txt" separately
file="my report.txt"; cat $file
# FIX: always double-quote: cat "$file"
```

---

## Go

**Build tag placement** -- `//go:build` must be first line, blank line before `package`.
```go
// BROKEN:
package main
//go:build linux
// FIX:
//go:build linux

package main
```

**Module path vs imports** -- Import paths must match the module path in go.mod exactly.
```
go.mod: module github.com/user/repo
BROKEN: import "github.com/user/repo/v2/pkg"  (module is not v2)
FIX:    import "github.com/user/repo/pkg"
```

**Test naming** -- Files must end `_test.go`. Functions must be `TestXxx` (capital after Test).
```
BROKEN: auth_tests.go, func testAuth(t *testing.T)
FIX:    auth_test.go,  func TestAuth(t *testing.T)
```

**Unused imports fail build** -- Go refuses to compile with unused imports.
```go
// FIX: remove unused imports, or blank-import for side effects:
import _ "github.com/lib/pq"
```

**Unused variables fail build** -- Declared-but-unused locals are a compile error.
```go
// BROKEN: result declared, only err used
result, err := doSomething()
// FIX: blank identifier
_, err := doSomething()
```

---

## Git

**Worktree isolation** -- Changes in a worktree are invisible to main tree until merged. Workers in `/tmp/swarm-epic-1/` do not affect `/repo/`.

**Detached HEAD** -- Worktrees created without `-b` start detached; commits may be lost.
```bash
# BROKEN: git worktree add /tmp/task1 HEAD
# FIX:    git worktree add /tmp/task1 -b swarm/task1
```

**Never commit from a worker** -- Concurrent `git add`/`git commit` corrupts the index. Workers write files only. The team lead is the sole committer.

---

## Skills / Docs

**Source of truth** -- Edit skills in `skills/` in this repo, NOT `~/.claude/skills/` (installed copies are overwritten on update).

**Reference linkage** -- Every file under `skills/<name>/references/` must be linked from that skill's SKILL.md. `heal.sh --strict` enforces this.

**No symlinks** -- The plugin-load-test rejects symlinks. Copy files instead of symlinking.

**Skill count sync** -- Adding or removing a skill directory requires `scripts/sync-skill-counts.sh`. CI fails otherwise.
