
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Staffing and workforce solutions technology
    ('staffing-agency-platform', 'Staffing agency technology platform - applicant tracking, temp worker placement, time tracking, billing'),
    ('executive-search-platform', 'Executive search and headhunter platform - candidate sourcing, search management, client portal, placement'),
    ('temp-workforce-platform', 'Temporary workforce management platform - talent pool, rapid deployment, compliance, payroll, reporting'),
    ('employer-of-record-platform', 'Employer of record technology platform - global employment, compliance, payroll, benefits, contracts'),
    ('gig-economy-platform', 'Gig economy workforce platform - task marketplace, worker matching, ratings, payments, compliance'),
    ('hr-outsourcing-platform', 'HR outsourcing technology platform - multi-client HR, onboarding, benefits, compliance, reporting'),
    ('professional-employer-platform', 'Professional employer organization technology - co-employment, benefits pooling, HR, payroll, compliance'),
    ('talent-acquisition-platform', 'Talent acquisition technology platform - sourcing, ATS, interview scheduling, offers, analytics'),
    ('workforce-analytics-platform', 'Workforce analytics technology platform - headcount, turnover, diversity, compensation benchmarking'),
    ('contingent-workforce-platform', 'Contingent workforce management - SOW, IC compliance, VMS, spend analytics, risk management'),
    # Vocational training and trade school technology
    ('vocational-school-platform', 'Vocational and trade school technology platform - enrollment, curriculum, certification, job placement'),
    ('apprenticeship-platform', 'Apprenticeship program management platform - RAPIDS compliance, OJT hours, related instruction, completion'),
    ('trade-certification-platform', 'Trade certification and testing platform - exam management, credential verification, renewal, CEU tracking'),
    ('culinary-school-platform', 'Culinary school management platform - kitchen scheduling, mise en place, externships, certification'),
    ('cosmetology-school-platform', 'Cosmetology school technology platform - hours tracking, state board prep, clinic management, licensing'),
    ('dental-hygiene-school', 'Dental hygiene school technology - clinic scheduling, patient records, competency assessment, board prep'),
    ('welding-school-platform', 'Welding school management platform - equipment tracking, certification prep, safety records, job placement'),
    ('cdl-training-platform', 'CDL and truck driving school platform - behind-the-wheel hours, skills testing, DOT compliance, placement'),
    ('coding-bootcamp-platform', 'Coding bootcamp technology platform - curriculum delivery, project management, career services, outcomes'),
    ('flight-school-platform', 'Flight school management platform - logbook tracking, aircraft scheduling, checkride prep, FAA compliance'),
    # Language and ESL education technology
    ('language-school-platform', 'Language school management platform - level assessment, class scheduling, immersion programs, billing'),
    ('esl-program-platform', 'ESL and English language program technology - placement testing, curriculum, attendance, SEVIS compliance'),
    ('online-language-platform', 'Online language learning platform - live tutoring, group classes, self-paced, speech recognition'),
    ('corporate-language-training', 'Corporate language training platform - employee enrollment, progress tracking, ROI reporting, scheduling'),
    ('language-immersion-platform', 'Language immersion program platform - homestay matching, cultural activities, academic tracking'),
    ('bilingual-education-platform', 'Bilingual education technology platform - dual language programs, assessment, parent communication'),
    ('language-assessment-platform', 'Language proficiency assessment platform - adaptive testing, reporting, certification, benchmarking'),
    ('translation-education-platform', 'Translation and interpretation education platform - skill development, practicum, certification, job board'),
    ('sign-language-platform', 'Sign language instruction technology platform - video instruction, interpreter matching, certification'),
    ('heritage-language-platform', 'Heritage and community language program platform - cultural preservation, curriculum, community engagement'),
    # Music education and arts technology
    ('music-school-platform', 'Music school management platform - lesson scheduling, teacher management, recital planning, billing'),
    ('music-lesson-platform', 'Music lesson marketplace platform - teacher matching, booking, video lessons, progress tracking, payments'),
    ('performing-arts-school', 'Performing arts school technology platform - auditions, class scheduling, production management, billing'),
    ('music-production-education', 'Music production education platform - DAW integration, project submission, peer review, certification'),
    ('orchestra-management-platform', 'Orchestra and ensemble management platform - rehearsal scheduling, touring, scores library, fundraising'),
    ('choir-management-platform', 'Choir and choral organization platform - member management, music library, rehearsal, performance, dues'),
    ('dance-studio-platform', 'Dance studio management platform - class scheduling, costume tracking, recital management, billing'),
    ('theater-company-platform', 'Theater company management platform - production management, auditions, box office, donor management'),
    ('art-school-platform', 'Art school and studio management platform - class enrollment, supply tracking, portfolio management, shows'),
    ('music-festival-platform', 'Music festival management platform - artist booking, stage scheduling, ticketing, vendor management'),
    # Manufactured housing and community technology
    ('manufactured-housing-platform', 'Manufactured housing community platform - lot management, tenant portal, utilities billing, maintenance'),
    ('mobile-home-park-platform', 'Mobile home park management platform - rent collection, lot leases, utility metering, compliance'),
    ('rv-park-platform', 'RV park and campground management platform - site reservations, hookup management, amenities, billing'),
    ('marina-management-platform', 'Marina and boat storage management platform - slip reservations, liveaboard, fuel dock, maintenance'),
    ('campground-management-platform', 'Campground management technology platform - reservation system, site mapping, activities, billing'),
    ('community-land-trust-platform', 'Community land trust technology platform - affordability tracking, ground lease management, resale formula'),
    ('affordable-housing-platform', 'Affordable housing management technology - income certification, rent calculation, compliance, waitlist'),
    ('transitional-housing-platform', 'Transitional housing management platform - resident services, case management, outcome tracking'),
    ('homeless-shelter-platform', 'Homeless shelter operations technology - HMIS integration, bed management, services, case management'),
    ('housing-authority-platform', 'Housing authority technology platform - public housing, Section 8, waitlist, inspections, compliance'),
    # Document and records management technology
    ('document-destruction-platform', 'Document destruction and shredding services platform - chain of custody, certificates of destruction, scheduling'),
    ('records-management-platform', 'Records management and offsite storage platform - box tracking, retrieval, retention schedules, destruction'),
    ('document-scanning-platform', 'Document scanning and digitization platform - batch processing, OCR, indexing, quality control, delivery'),
    ('e-discovery-platform', 'E-discovery technology platform - legal hold, collection, review, production, chain of custody'),
    ('contract-lifecycle-platform', 'Contract lifecycle management platform - drafting, negotiation, approval, execution, obligations, renewal'),
    ('digital-mailroom-platform', 'Digital mailroom technology platform - mail scanning, routing, distribution, workflow, archives'),
    ('forms-automation-platform', 'Forms and document automation platform - template management, conditional logic, e-signature, workflow'),
    ('compliance-document-platform', 'Compliance documentation platform - policy management, version control, attestation, audit trails'),
    ('intellectual-property-platform', 'Intellectual property management platform - patent/trademark tracking, deadlines, licensing, portfolio'),
    ('regulatory-document-platform', 'Regulatory document management platform - submissions, correspondence, approval tracking, compliance'),
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
