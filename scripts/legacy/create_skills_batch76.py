
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Political campaign and civic technology
    ('political-campaign-platform', 'Political campaign management platform - voter data, canvassing, fundraising, volunteer coordination, analytics'),
    ('voter-registration-platform', 'Voter registration technology platform - online registration, eligibility verification, data updates, reporting'),
    ('election-management-platform', 'Election administration technology platform - ballot management, poll worker scheduling, results reporting'),
    ('lobbying-platform', 'Lobbying and government affairs technology platform - legislator tracking, bill monitoring, contact management'),
    ('pac-management-platform', 'Political action committee management platform - donation tracking, FEC compliance, disbursements, reporting'),
    ('civic-engagement-platform', 'Civic engagement technology platform - constituent communication, issue advocacy, petition, volunteer'),
    ('government-relations-platform', 'Government relations technology platform - stakeholder mapping, policy tracking, regulatory monitoring'),
    ('petition-platform', 'Online petition and advocacy platform - campaign creation, signature collection, delivery, analytics'),
    ('political-polling-platform', 'Political polling and survey technology platform - sampling, weighting, crosstabs, trend tracking, reporting'),
    ('redistricting-platform', 'Redistricting and political mapping technology platform - district analysis, demographic data, compliance'),
    # Government contracting and procurement technology
    ('government-contracting-platform', 'Government contracting technology platform - SAM registration, proposal management, compliance, invoicing'),
    ('federal-procurement-platform', 'Federal procurement and acquisition platform - solicitation management, vendor evaluation, award, reporting'),
    ('subcontracting-platform', 'Government subcontracting management platform - small business compliance, flow-downs, reporting, payments'),
    ('contract-compliance-gov', 'Government contract compliance platform - FAR/DFARS tracking, certification, audit preparation, reporting'),
    ('proposal-management-platform', 'Proposal management technology platform - RFP response, content library, team collaboration, submissions'),
    ('gsa-schedule-platform', 'GSA schedule and multiple award contract platform - catalog management, order processing, reporting, compliance'),
    ('cost-accounting-gov', 'Government cost accounting technology platform - DCAA compliance, indirect rates, timekeeping, billing'),
    ('cage-sam-platform', 'CAGE code and SAM.gov management platform - registration maintenance, certification tracking, expiration alerts'),
    ('military-contracting-platform', 'Defense and military contracting platform - DD forms, security clearance tracking, ITAR compliance'),
    ('state-local-contracting', 'State and local government contracting platform - bid tracking, vendor registration, compliance, payments'),
    # Corporate PR and communications technology
    ('pr-agency-platform', 'Public relations agency management platform - media list, pitch tracking, coverage reporting, client portal'),
    ('media-monitoring-platform', 'Media monitoring and press clipping platform - coverage tracking, sentiment analysis, share of voice, alerts'),
    ('press-release-platform', 'Press release distribution and management platform - newswire integration, media list, tracking, analytics'),
    ('crisis-communications-platform', 'Crisis communications management platform - response playbooks, stakeholder alerts, media management'),
    ('influencer-pr-platform', 'Influencer relations and PR technology platform - influencer database, outreach, campaign tracking, ROI'),
    ('corporate-communications-platform', 'Corporate communications technology platform - internal comms, executive messaging, town halls, newsletters'),
    ('brand-reputation-platform', 'Brand reputation management technology platform - review monitoring, response management, sentiment trends'),
    ('thought-leadership-platform', 'Thought leadership content technology platform - expert positioning, article management, speaking, media'),
    ('analyst-relations-platform', 'Analyst relations technology platform - analyst database, briefing management, report tracking, coverage'),
    ('awards-submission-platform', 'Industry awards and recognition management platform - submission tracking, judging, deadline management'),
    # Market research and insights technology
    ('market-research-platform', 'Market research technology platform - survey design, panel management, data collection, analysis, reporting'),
    ('consumer-insights-platform', 'Consumer insights technology platform - qualitative/quantitative research, segmentation, trend analysis'),
    ('focus-group-platform', 'Focus group and qualitative research platform - participant recruiting, session management, transcription, analysis'),
    ('panel-management-platform', 'Research panel management technology platform - member recruitment, profiling, survey routing, incentives'),
    ('competitive-intelligence-platform', 'Competitive intelligence technology platform - market monitoring, competitor tracking, win/loss analysis'),
    ('brand-tracking-platform', 'Brand tracking and health monitoring platform - awareness, consideration, preference, NPS, longitudinal study'),
    ('ethnographic-research-platform', 'Ethnographic research technology platform - field research tools, observation recording, analysis, reporting'),
    ('concept-testing-platform', 'Product concept testing technology platform - survey design, monadic/sequential testing, conjoint analysis'),
    ('pricing-research-platform', 'Pricing research technology platform - van Westendorp, Gabor-Granger, conjoint, price sensitivity analysis'),
    ('ux-research-platform', 'UX research management platform - study planning, participant scheduling, session recording, synthesis'),
    # Executive coaching and leadership development technology
    ('executive-coaching-platform', 'Executive coaching technology platform - client management, session notes, assessments, goal tracking, billing'),
    ('leadership-assessment-platform', 'Leadership assessment technology platform - 360 feedback, personality assessments, development planning'),
    ('coaching-marketplace-platform', 'Coaching marketplace technology platform - coach profiles, matching, scheduling, video sessions, payments'),
    ('mentoring-program-platform', 'Corporate mentoring program technology platform - mentor-mentee matching, goal setting, progress tracking'),
    ('talent-development-platform', 'Talent development technology platform - competency frameworks, IDP management, succession planning'),
    ('organizational-development-tech', 'Organizational development technology platform - change management, culture assessment, intervention tracking'),
    ('team-effectiveness-platform', 'Team effectiveness technology platform - team assessments, dynamics analysis, development planning'),
    ('high-potential-program-tech', 'High potential program technology platform - identification, development tracks, exposure opportunities, tracking'),
    ('peer-advisory-platform', 'Peer advisory group and mastermind technology platform - group management, meeting facilitation, accountability'),
    ('board-development-platform', 'Board development and governance technology platform - director assessments, committee management, education'),
    # Healthcare staffing and clinical talent technology
    ('healthcare-staffing-platform', 'Healthcare staffing agency technology platform - clinician database, credential verification, shift filling, billing'),
    ('travel-nurse-platform', 'Travel nursing agency technology platform - assignment management, housing, compliance, pay packages, onboarding'),
    ('locum-tenens-platform', 'Locum tenens physician placement platform - credentialing, malpractice, licensing, assignment management'),
    ('per-diem-staffing-platform', 'Per diem healthcare staffing platform - shift marketplace, self-scheduling, credential management, payments'),
    ('allied-health-staffing', 'Allied health staffing technology platform - therapy, imaging, lab staffing, credential tracking, billing'),
    ('nursing-registry-platform', 'Nursing registry management platform - nurse pool, competency verification, shift dispatch, billing'),
    ('home-health-staffing', 'Home health agency staffing platform - caregiver matching, scheduling, visit verification, compliance, billing'),
    ('clinical-contractor-platform', 'Clinical contract staff management platform - IC compliance, credentialing, time tracking, payments'),
    ('medical-interpreter-platform', 'Medical interpreter services platform - language matching, scheduling, remote interpretation, billing'),
    ('healthcare-credential-platform', 'Healthcare credentialing technology platform - provider enrollment, license verification, CAQH, privileging'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
