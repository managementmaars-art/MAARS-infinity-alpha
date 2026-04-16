# CLI Error Code Reference

## Tier & Quota Errors

| Error | Cause | Fix |
|---|---|---|
| Resource exceeds your tier quota | Service needs more CPU/memory than tier allows | Upgrade tier at [guaracloud.com/docs](https://guaracloud.com/docs) or reduce resource request |
| Build minutes quota exceeded | Monthly build minutes used up | Wait for next billing cycle or upgrade tier |
| Account resource pool exhausted | Total account resources across all services exceeded | Scale down other services or upgrade tier |
| Maximum number of projects reached | Project count limit for tier | Delete unused project or upgrade |
| Maximum number of services reached | Service count limit for project | Delete unused service or upgrade |
| Maximum number of custom domains reached | Domain limit per service | Remove existing domain or upgrade |
| Maximum number of API keys reached | API key limit for tier | Revoke unused key at [app.guaracloud.com](https://app.guaracloud.com) or upgrade |

## Authentication Errors

| Error | Cause | Fix |
|---|---|---|
| Authentication failed. API key is invalid or revoked | Key was deleted or is wrong | Run `guara login` |
| Authentication failed. API key has expired | Key past expiration | Run `guara login` |
| Your API key lacks the required permission scope | Key has read-only scope | Create new key with write scope at [app.guaracloud.com](https://app.guaracloud.com) |
| Not authenticated | No stored credentials | Run `guara login` |
| Account is suspended due to billing issues | Payment failed | Update payment at [app.guaracloud.com](https://app.guaracloud.com) |
| Terms of Service must be accepted | TOS not accepted | Accept at [app.guaracloud.com](https://app.guaracloud.com) |
| Account is scheduled for deletion | User requested deletion | Cancel at [app.guaracloud.com](https://app.guaracloud.com) if unintentional |

## Resource & Access Errors

| Error | Cause | Fix |
|---|---|---|
| Project not found or you do not have access | Wrong slug or no permission | Check with `guara projects list` |
| Service not found or you do not have access | Wrong slug or no permission | Check with `guara services list` |
| Deployment not found | Invalid deployment ID | Check with `guara deployments list` |
| You do not have permission for this action | Insufficient role | Check role with `guara whoami`, contact project owner |
| A build is already in progress | Concurrent build attempt | Wait for current build: `guara deployments list` |
| Payment failed | Stripe charge failed | Update payment method at [app.guaracloud.com](https://app.guaracloud.com) |

## Session Errors (exec/proxy)

| Error | Cause | Fix |
|---|---|---|
| No ready pods available | Service stopped or no healthy pods | Start service: `guara services start` |
| Maximum concurrent sessions reached | Too many open exec/proxy sessions | Close existing sessions |
| Session token has expired | Token timed out | Run the command again |
| Session token has already been used | Token consumed | Run the command again for a new session |
| Session disconnected due to inactivity | Idle timeout | Reconnect by running the command again |

## CLI Errors

| Error | Cause | Fix |
|---|---|---|
| No project specified | No context available | Pass `--project`, set `$GUARA_PROJECT`, or run `guara link` |
| No service specified | No service in context | Pass `--service`, set `$GUARA_SERVICE`, or include service in `.guara.json` |
| Could not reach GuaraCloud API | Network issue or wrong URL | Check connection and `guara config get api-url` |
| No interactive terminal available | Running non-interactively without required flags | Pass `--api-key` for auth, or required flags for the command |
| Too many requests | Rate limit hit | Wait and retry |
| Validation failed | Invalid input fields | Fix the listed fields and retry |
