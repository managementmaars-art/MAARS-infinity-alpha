# Escalation Contacts

## Contact Matrix by Severity

| Severity | Primary Contact | Secondary Contact | Management | Communication |
|----------|----------------|-------------------|------------|---------------|
| **SEV1** | On-call engineer (PagerDuty) | Backend lead + Frontend lead | Engineering Manager + VP Eng | Status page + #incidents |
| **SEV2** | On-call engineer (PagerDuty) | Relevant team lead | Engineering Manager | #incidents |
| **SEV3** | On-call engineer (Slack) | Relevant team lead | _Not required_ | #incidents-low |
| **SEV4** | Team responsible for service | _Not required_ | _Not required_ | Ticket only |

## On-Call Rotation

| Week | Primary | Secondary |
|------|---------|-----------|
| Odd weeks | Engineer A | Engineer B |
| Even weeks | Engineer C | Engineer D |

**On-call schedule:** Managed in PagerDuty
**Rotation cadence:** Weekly, handoff on Monday 09:00 UTC
**Override requests:** Post in #on-call-swap channel

## Service Ownership

| Service / Component | Team | Primary Contact | Slack Channel |
|---------------------|------|-----------------|---------------|
| Backend API (FastAPI) | Backend Team | Backend Tech Lead | #team-backend |
| Frontend (React) | Frontend Team | Frontend Tech Lead | #team-frontend |
| Database (PostgreSQL) | Platform Team | DBA Lead | #team-platform |
| Redis / Caching | Platform Team | Platform Engineer | #team-platform |
| CI/CD Pipeline | Platform Team | DevOps Lead | #team-platform |
| Authentication | Backend Team | Auth Module Owner | #team-backend |
| Infrastructure / Cloud | Platform Team | Infrastructure Lead | #team-platform |
| Third-party integrations | Backend Team | Integration Lead | #team-backend |

## Escalation Paths

### Technical Escalation

```
On-call Engineer
    |
    v
Team Lead (for affected service)
    |
    v
Engineering Manager
    |
    v
VP of Engineering (SEV1 only, if not resolved within 30 minutes)
```

### Data / Security Incidents

```
On-call Engineer
    |
    v
Security Lead
    |
    v
CTO + Legal (if data breach confirmed)
```

### Third-Party / Vendor Issues

```
On-call Engineer
    |
    v
Integration Lead
    |
    v
Vendor support (using premium support channel)
```

## Communication Channels

| Channel | Purpose | Who Posts |
|---------|---------|----------|
| `#incidents` | Active SEV1/SEV2 incident coordination | Incident commander, responders |
| `#incidents-low` | SEV3/SEV4 tracking | On-call engineer |
| `#engineering` | Post-incident summaries | Incident commander |
| `#status-updates` | External-facing status updates | Incident commander |
| PagerDuty | Automated alerting and paging | Monitoring system |

## Contact Information

_Replace placeholders with actual team contacts._

| Role | Name | Slack | PagerDuty | Phone (emergency) |
|------|------|-------|-----------|-------------------|
| On-call (primary) | _See rotation_ | _Via PagerDuty_ | Auto-paged | _Via PagerDuty_ |
| On-call (secondary) | _See rotation_ | _Via PagerDuty_ | Auto-paged | _Via PagerDuty_ |
| Backend Tech Lead | TBD | @backend-lead | @backend-lead | TBD |
| Frontend Tech Lead | TBD | @frontend-lead | @frontend-lead | TBD |
| DBA Lead | TBD | @dba-lead | @dba-lead | TBD |
| DevOps Lead | TBD | @devops-lead | @devops-lead | TBD |
| Engineering Manager | TBD | @eng-manager | @eng-manager | TBD |
| VP of Engineering | TBD | @vp-eng | @vp-eng | TBD |

## When to Page vs. When to Slack

| Signal | Action | Channel |
|--------|--------|---------|
| Service completely down | Page immediately | PagerDuty |
| Error rate > 5% | Page immediately | PagerDuty |
| Error rate 1-5% | Slack notification | #incidents |
| Performance degradation > 2x | Page if sustained > 5 min | PagerDuty |
| Single user report | Investigate, no page | #incidents-low |
| Multiple user reports | Evaluate severity, likely page | PagerDuty or #incidents |
| Scheduled maintenance issue | Slack notification | #incidents-low |
