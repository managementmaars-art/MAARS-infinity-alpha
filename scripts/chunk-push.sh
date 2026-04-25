#!/usr/bin/env bash
# One-shot chunk-commit + chunk-push for the backlog of vendored skill dirs.
# Runs sequentially so we don't fight the git index lock. Each batch: commit,
# then push. Output is appended to scripts/chunk-push.log so you can tail it.

set -u
cd "$(git rev-parse --show-toplevel)"
LOG="scripts/chunk-push.log"

log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG"; }

wait_lock() {
    while [ -f .git/index.lock ]; do sleep 3; done
}

do_batch() {
    local msg="$1"; shift
    wait_lock
    log "COMMIT: $msg ($#  path(s))"
    if ! git commit -m "$msg" -- "$@" >>"$LOG" 2>&1; then
        log "  commit failed (maybe nothing to commit); continuing"
        return 0
    fi
    log "  commit OK; pushing..."
    if git push origin main >>"$LOG" 2>&1; then
        log "  push OK"
    else
        log "  push FAILED — stopping pipeline"
        return 1
    fi
}

log "=== chunk-push start ==="

do_batch "Vendor .continue .cortex .crush .factory skill mirrors"    .continue .cortex .crush .factory    || exit 1
do_batch "Vendor .goose .iflow .junie .kilocode skill mirrors"       .goose .iflow .junie .kilocode       || exit 1
do_batch "Vendor .kiro .kode .mcpjam .mux skill mirrors"             .kiro .kode .mcpjam .mux             || exit 1
do_batch "Vendor .neovate .openhands .pi .pochi skill mirrors"       .neovate .openhands .pi .pochi       || exit 1
do_batch "Vendor .qoder .qwen .roo .trae skill mirrors"              .qoder .qwen .roo .trae              || exit 1
do_batch "Vendor .vibe .windsurf .zencoder .screenshots"             .vibe .windsurf .zencoder .screenshots || exit 1
do_batch "Update .claude config and memory"                          .claude                              || exit 1
do_batch "Vendor skills/ catalog (legacy install path)"              skills                               || exit 1

# Root-level installer / manifest / log files.
wait_lock
log "COMMIT: root-level installer scripts, manifests, logs"
git add -- \
    MIGRATION.md Makefile SKILL.md START_MAARS.bat build-repo-only-list.js \
    create_skills_batch*.py \
    install-all-skills-auto.ps1 install-all-skills-vscode.js install-all-skills.ps1 install_skills.py \
    mcp-skills-results.txt open-progress-window.ps1 package-lock.json package.json \
    retry-failed-clean.js scrape-skills-top.js session-log.txt setup-session-log.txt \
    setup.sh skills-installed-failed.txt skills-installed-success.txt skills-lock.json \
    skills-progress.json skills-test.txt skills-top.json start_frontend.bat test_result.md \
    yarn.lock .gitignore \
    >>"$LOG" 2>&1 || true
git commit -m "Add root-level installer scripts, skill manifests, and session logs" >>"$LOG" 2>&1 \
    && log "  root commit OK" \
    || { log "  root commit failed or nothing to commit"; }
wait_lock
git push origin main >>"$LOG" 2>&1 \
    && log "  root push OK" \
    || { log "  root push FAILED"; exit 1; }

log "=== chunk-push DONE ==="
