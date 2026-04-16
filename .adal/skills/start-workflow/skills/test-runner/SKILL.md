---
name: test-runner
description: "Run project tests: jest unit/integration tests and Playwright E2E for frontend projects, plus agent-browser smoke check. Reports pass/fail/skipped summary and writes results to state.json. Triggers on: /test-runner, run tests, execute tests, jest, playwright, run test suite."
---

# test-runner

IRON LAW: Never skip tests if a test suite is configured. Report actual results — do not assume pass. Always record skip reasons for TG notification.

## Invocation

Called by start-workflow, or standalone:
```
/test-runner
```

## Testing strategy

| Layer | Tool | 触发条件 | 缺失时 |
|-------|------|---------|--------|
| 单元/集成 | Jest | `package.json` 含 `"jest"` | 跳过，TG 提示 |
| 正式 E2E | Playwright | 有前端框架 + `playwright.config.*` | 跳过，TG 提示安装步骤 |
| Smoke check | agent-browser | 有前端框架 + `npm run dev` 可用 | 跳过，TG 提示原因 |

**所有跳过都不阻断 pipeline**，但必须在 state 里记录跳过原因，供 TG 通知使用。

## Execution Flow

### Step 1 — Detect test setup

```bash
# Jest
HAS_JEST=$(grep -q '"jest"' package.json 2>/dev/null && echo yes || echo no)

# Frontend framework
HAS_FRONTEND=$(grep -qE '"react"|"vue"|"next"|"nuxt"|"svelte"|"vite"' package.json 2>/dev/null && echo yes || echo no)

# Playwright config
HAS_PW_CONFIG=$(ls playwright.config.* 2>/dev/null | head -1 | grep -q . && echo yes || echo no)

# Dev server script
HAS_DEV=$(node -e "const p=require('./package.json'); process.exit(p.scripts&&p.scripts.dev?0:1)" 2>/dev/null && echo yes || echo no)
```

### Step 2 — Run jest

If `HAS_JEST=yes`:
```bash
bash "$SKILLS_BASE/test-runner/scripts/run-tests.sh" "$RUN_DIR" "$PROJECT_DIR"
```

If `HAS_JEST=no`: record skip reason:
```python
state['phases']['test-runner']['jest_summary'] = "skipped"
state['phases']['test-runner']['jest_skip_reason'] = "package.json 中未找到 jest 配置"
state['phases']['test-runner']['jest_next_steps'] = "npm install -D jest && npx jest --init"
```

### Step 3 — Playwright E2E

If `HAS_FRONTEND=yes` and `HAS_PW_CONFIG=yes`: run via `run-tests.sh`.

If `HAS_FRONTEND=yes` and `HAS_PW_CONFIG=no`: record skip:
```python
state['phases']['test-runner']['pw_summary'] = "skipped"
state['phases']['test-runner']['pw_skip_reason'] = "检测到前端框架但未找到 playwright.config.*"
state['phases']['test-runner']['pw_next_steps'] = "npm install -D @playwright/test && npx playwright install --with-deps && npx playwright init"
```

If `HAS_FRONTEND=no`: record skip:
```python
state['phases']['test-runner']['pw_summary'] = "skipped"
state['phases']['test-runner']['pw_skip_reason'] = "纯后端项目，无需 E2E"
```

### Step 4 — agent-browser smoke check

If `HAS_FRONTEND=yes` and `HAS_DEV=yes`:
1. Start dev server: `npm run dev &` (capture PID as `DEV_PID`)
2. Use agent-browser to walk through affected UI routes
3. Capture pass/fail per route — write to `state.phases.test-runner.browser_results`
4. Cleanup — always run, even if agent-browser failed:
```bash
# Kill dev server
kill $DEV_PID 2>/dev/null || true

# Kill any Chrome for Testing processes spawned by agent-browser
pkill -f "Google Chrome for Testing" 2>/dev/null || true
pkill -f "chrome-.*--remote-debugging-port" 2>/dev/null || true
```

If `HAS_FRONTEND=yes` and `HAS_DEV=no`: record skip:
```python
state['phases']['test-runner']['browser_summary'] = "skipped"
state['phases']['test-runner']['browser_skip_reason'] = "package.json 中未找到 dev 脚本"
state['phases']['test-runner']['browser_next_steps'] = 'package.json scripts 中添加 "dev" 启动命令'
```

If `HAS_FRONTEND=no`: skip silently (纯后端无需 smoke check).

### Step 5 — Report

Update state:
```python
state['phases']['test-runner']['status'] = 'done'   # or 'error' if a configured suite failed
state['phases']['test-runner']['summary'] = {
    'jest':    jest_summary,       # "3 passed, 0 failed" or "skipped"
    'playwright': pw_summary,      # "2 passed, 0 failed" or "skipped"
    'browser': browser_summary,    # "passed" or "skipped"
}
```

**只有已配置且实际运行的测试套件失败时**才 set `status = error`。跳过不算失败。
