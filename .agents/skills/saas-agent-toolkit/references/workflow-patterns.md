# Workflow Patterns

## Pattern A: Support Triage (Zendesk/Intercom)

1. Trigger: new ticket webhook.
2. Search: find similar tickets and customer history.
3. Summarize: issue, prior attempts, current status.
4. Draft: response draft plus missing-info checklist.
5. Update: set priority/tags/owner for low-risk actions.
6. Notify: send summary to assignee.
7. Approve: route refund/compensation actions to approver.

## Pattern B: Sales Follow-Up (HubSpot/Salesforce)

1. Trigger: call note/transcript arrives.
2. Summarize: pain points, budget, timeline, decision process.
3. Update: write `next_step`, `stage`, and follow-up task to CRM.
4. Draft: follow-up email variants.
5. Notify: remind account owner to review/send.
6. Approve: gate price/contract exceptions.

## Pattern C: Incident Assistant (PagerDuty + Datadog + Jira + Slack)

1. Trigger: production alert.
2. Search: gather logs, recent deployments, related pull requests.
3. Summarize: impact, timeline, likely root cause.
4. Draft: internal/external status update drafts.
5. Update: create incident issue and sync status.
6. Notify: alert incident commander and stakeholder channel.
7. Approve: require approval for public status-page updates.
