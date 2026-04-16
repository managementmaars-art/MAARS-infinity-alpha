# TodoWrite Task Templates

## Template A - Set Up Go Proxy

```
1. [Preflight] Verify Go 1.21+ installed: go version
2. [Execute] Build Go proxy to /usr/local/bin/claude-proxy
3. [Execute] Create launchd plist at /Library/LaunchDaemons/com.terryli.claude-proxy.plist
4. [Execute] Load launchd: sudo launchctl load -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist
5. [Execute] Add to ~/.zshenv: export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"
6. [Execute] Add to ~/.zshenv: export ANTHROPIC_API_KEY="proxy-managed"
7. [Verify] Health: curl -s http://127.0.0.1:8082/health
8. [Verify] Restart Claude Code
```

## Template B - Add New Provider

```
1. [Preflight] Verify provider supports /v1/messages
2. [Execute] Edit launchd plist, add to EnvironmentVariables:
   - PROVIDER_API_KEY
   - PROVIDER_BASE_URL
3. [Execute] Reload: sudo launchctl unload -w ... && sudo launchctl load -w ...
4. [Verify] Test: curl http://127.0.0.1:8082/health
```

## Template C - Diagnose Proxy Auth Failure

```
1. Check running: sudo launchctl list | grep claude-proxy
2. Check port: lsof -i :8082
3. Check .zshenv: grep ANTHROPIC ~/.zshenv
4. Check logs: tail -50 /Users/terryli/.claude/logs/proxy-stdout.log
5. Health check: curl http://127.0.0.1:8082/health
```

## Template D - Disable Proxy

```
1. Comment out ANTHROPIC_BASE_URL in ~/.zshenv
2. Unload: sudo launchctl unload -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist
3. Restart Claude Code
```
