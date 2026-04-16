# Onboarding

Covers installation, the `caw onboard` interactive loop, environment configuration, and wallet pairing.

## 1. Install caw

Run `./scripts/bootstrap-env.sh --env sandbox --only caw` to install caw. caw → `~/.cobo-agentic-wallet/bin/caw`; add that dir to PATH. TSS Node is downloaded automatically during onboard when needed.

## 2. Onboard

```bash
export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"
caw onboard --env sandbox
```

If the user **already has** an invitation code before starting, pass it on the **first call** so provisioning runs immediately — you skip the “get an invitation code” step below.

```bash
# Invitation code from Cobo — you own the wallet initially, with limited functionality.
# Your owner can pair the wallet later to unlock full functionality (see Pairing below).
caw onboard --env sandbox --invitation-code <CODE>
```

> **CRITICAL:** The shortcut commands above are for the **first call only**. Once you have called `caw onboard` and received a `session_id`, you **MUST** include `--session-id <SESSION_ID>` on **every** subsequent call — even when adding `--invitation-code`. Omitting `--session-id` starts a brand-new session, discarding prior progress and TSS prewarm work.

**How the interactive loop works:**
1. Call `caw onboard` — read `phase`, `prompts`, `needs_input`, `next_action`, and `session_id`.
2. On each follow-up, pass `--session-id` with the **latest** `session_id` from the previous response, and keep the same **`--env`** as the initial call (and `--api-url` if you used it). If the response says the session was not found and a new one was created, use that **new** `session_id`.
3. When `needs_input` is true, pass `--answers` as JSON whose keys match `prompts[].id` (etc., depending on phase).
4. Repeat until onboarding finishes — typically `wallet_status` is `active` and/or `phase` is `wallet_active`. If input is invalid, use `last_error` and resubmit with corrected `--answers`.
5. When bootstrap fails or stops (`phase` is `error`), run the command from `next_action` as given — same `--session-id`, `--env`, and `--api-url` (if any) as your previous calls.

Example follow-up call:

```bash
caw onboard --session-id <SESSION_ID> --env sandbox
```

Use `phase` + `bootstrap_stage` + `wallet_status` to track progress.

See [Error Handling](./error-handling.md#onboarding-errors) for common onboarding errors.

## Environment

| Environment | `--env` value | API URL                                          |
|-------------|---------------|--------------------------------------------------|
| Sandbox | `sandbox` | `https://api-core.agenticwallet.sandbox.cobo.com` |

Set the API URL before any command:

```bash
export AGENT_WALLET_API_URL=https://api-core.agenticwallet.sandbox.cobo.com
```

## Pairing — Transfer Ownership to a Human

Pairing is initiated manually. When the user decides to transfer wallet ownership:

```bash
caw wallet pair \
  --context '{"channel":"<channel>","target":"<target>","session_id":"<session-id>"}'
caw wallet pair-status              # check pairing status
```

`pair` returns a **numeric code** (valid 30 minutes). Tell the user:

> "To pair this wallet, open the Cobo Agentic Wallet app and enter the pairing code."

The user completes the pairing in the **Cobo Agentic Wallet app** by entering the code. Once paired:
- Ownership transfers from Agent → Human
- Agent becomes a delegate, authorized to operate within the owner's configured rules
- Operations outside those rules require the agent to submit a pact for human approval

Use `pair-status` to check state and act accordingly. Poll every **10 seconds**:

| Status | Meaning | Action |
|---|---|---|
| `valid` | Code issued, waiting for user | Share the code with the user; keep polling |
| `claimed` | Pairing complete | Proceed — ownership transferred |
| `expired` | Code timed out (30 min) | Re-run `caw wallet pair` to generate a new code |
| `not_found` | No pairing request on record | Re-run `caw wallet pair` to start a new pairing |

If the user is unreachable before the code expires, stop polling and notify when they return.

**Pair status tracking**: `--context` is **required** for `caw wallet pair`. In an openclaw environment, pass `--context '{"channel":"<channel>", "target":"<target>", "session_id":"<session-id>"}'` — `session_id` is a string from `openclaw sessions --json --agent <agent>`. If not running in openclaw or notification context is unavailable, pass `--context '{"openclaw": false}'`. When the terminal notification is delivered (claimed/expired), continue any established next steps from the conversation context.
