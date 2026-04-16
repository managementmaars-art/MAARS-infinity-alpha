# Post-Mortem Template

## Instructions

Copy this template for each post-mortem. Fill in all sections. Conduct the post-mortem meeting within 48 hours of the incident for SEV1/SEV2, within 1 week for SEV3.

---

# Post-Mortem: [Incident Title]

**Date:** [YYYY-MM-DD]
**Severity:** [SEV1/SEV2/SEV3/SEV4]
**Duration:** [Total duration]
**Author:** [Name]
**Incident Commander:** [Name]
**Attendees:** [List of post-mortem participants]

## 1. Summary

_One paragraph describing what happened, when, and the impact on users._

**Example:** On January 15, 2024, from 14:30 to 15:15 UTC (45 minutes), the backend API returned 503 errors for approximately 80% of requests. The root cause was database connection pool exhaustion triggered by a new endpoint that failed to release connections. An estimated 2,400 users were affected during the incident window.

## 2. Impact

| Metric | Value |
|--------|-------|
| Duration | _minutes/hours_ |
| Users affected | _count or percentage_ |
| Requests failed | _count or percentage_ |
| Revenue impact | _if applicable_ |
| SLA impact | _if applicable_ |
| Data loss | _yes/no, describe if yes_ |

## 3. Timeline (UTC)

| Time | Event |
|------|-------|
| HH:MM | _First sign of impact (from metrics/logs)_ |
| HH:MM | _Alert fired / issue detected_ |
| HH:MM | _Incident declared, severity assigned_ |
| HH:MM | _Incident commander designated_ |
| HH:MM | _Investigation started_ |
| HH:MM | _Root cause identified_ |
| HH:MM | _Mitigation applied_ |
| HH:MM | _Service recovered_ |
| HH:MM | _Incident declared resolved_ |

## 4. Root Cause

_Describe the fundamental reason the incident occurred. Use the Five Whys technique._

**Five Whys:**
1. Why did [symptom]? Because [cause 1].
2. Why did [cause 1]? Because [cause 2].
3. Why did [cause 2]? Because [cause 3].
4. Why did [cause 3]? Because [cause 4].
5. Why did [cause 4]? Because [root cause].

**Root cause:** _One sentence describing the fundamental issue._

## 5. Contributing Factors

_List all conditions that contributed to the incident occurring or worsening._

- [ ] _Factor 1: Description_
- [ ] _Factor 2: Description_
- [ ] _Factor 3: Description_

## 6. Detection

| Question | Answer |
|----------|--------|
| How was the incident detected? | _Alert / user report / manual check_ |
| Time from impact to detection | _minutes_ |
| Was the right alert in place? | _yes / no_ |
| Did the alert fire promptly? | _yes / no / N/A_ |

## 7. Response

| Question | Answer |
|----------|--------|
| Time from detection to response | _minutes_ |
| Were the right people paged? | _yes / no_ |
| Was the runbook useful? | _yes / no / no runbook existed_ |
| Time from response to mitigation | _minutes_ |
| Was communication clear and timely? | _yes / no_ |

## 8. What Went Well

- _List things that worked effectively during the incident_
- _Example: Alert fired within 2 minutes of impact_
- _Example: Rollback procedure completed in under 5 minutes_

## 9. What Could Be Improved

- _List gaps or problems in the response_
- _Example: No alert for connection pool saturation_
- _Example: Runbook did not mention this failure mode_
- _Example: It took 15 minutes to find the right dashboard_

## 10. Action Items

| # | Action | Owner | Priority | Due Date | Tracking |
|---|--------|-------|----------|----------|----------|
| 1 | _Description_ | _Name_ | P1/P2/P3 | _Date_ | _Ticket link_ |
| 2 | _Description_ | _Name_ | P1/P2/P3 | _Date_ | _Ticket link_ |
| 3 | _Description_ | _Name_ | P1/P2/P3 | _Date_ | _Ticket link_ |

**Action item categories:**
- **Prevent:** Changes to prevent this class of incident from recurring
- **Detect:** Improvements to detect similar issues faster
- **Mitigate:** Changes to reduce time-to-recovery
- **Process:** Improvements to incident response procedures

## 11. Lessons Learned

_Key insights from this incident that the broader team should understand._

1. _Lesson 1_
2. _Lesson 2_
3. _Lesson 3_

---

_Reviewed and approved by: [Engineering Manager Name], [Date]_
