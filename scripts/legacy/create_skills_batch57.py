
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # E-commerce technology deep
    ('ecommerce-platform-advanced', 'E-commerce platform advanced - Shopify Plus, Magento 2, BigCommerce, headless commerce, PWA'),
    ('product-catalog-management', 'Product catalog management - PIM systems, Akeneo, attribute modeling, taxonomy, syndication'),
    ('shopping-cart-optimization', 'Shopping cart optimization - checkout UX, cart abandonment, payment methods, trust signals'),
    ('ecommerce-search-advanced', 'E-commerce search advanced - Elasticsearch, Algolia, Solr, faceted search, personalization'),
    ('merchandising-platform', 'Merchandising platform - product recommendations, curated collections, upsell/cross-sell, bundles'),
    ('ecommerce-analytics-advanced', 'E-commerce analytics - funnel analysis, cohort LTV, basket analysis, attribution, RFM'),
    ('marketplace-platform-advanced', 'Marketplace platform advanced - multi-vendor, escrow, dispute resolution, seller onboarding'),
    ('subscription-commerce', 'Subscription commerce - recurring billing, churn prediction, dunning, upgrades, proration'),
    ('b2b-commerce-advanced', 'B2B commerce advanced - quote management, punchout, net terms, contract pricing, ERP integration'),
    ('commerce-personalization', 'Commerce personalization - segment targeting, ML recommendations, behavioral triggers, A/B'),
    # CRM and customer success technology
    ('crm-platform-advanced', 'CRM platform advanced - Salesforce customization, HubSpot advanced, Zoho CRM, custom objects'),
    ('sales-automation-advanced', 'Sales automation advanced - sequences, territory management, deal scoring, forecast AI'),
    ('customer-success-platform', 'Customer success platform - health scoring, playbooks, QBR automation, NPS, expansion signals'),
    ('revenue-operations', 'Revenue operations - RevOps tech stack, attribution, pipeline hygiene, forecast accuracy'),
    ('contact-center-advanced', 'Contact center advanced - ACD, IVR, predictive dialing, omnichannel routing, WFM, QA'),
    ('customer-data-platform-advanced', 'CDP advanced - identity resolution, real-time segmentation, activation, consent management'),
    ('customer-journey-analytics', 'Customer journey analytics - cross-channel attribution, touchpoint analysis, path analysis'),
    ('field-service-management', 'Field service management - scheduling, dispatch, mobile workforce, IoT triggers, SLA tracking'),
    ('partner-relationship-management', 'Partner relationship management - PRM portals, deal registration, MDF, co-selling, tiers'),
    ('customer-feedback-platform', 'Customer feedback platform - NPS, CSAT, CES, text analytics, closed-loop, action management'),
    # Marketing technology deep
    ('marketing-automation-advanced', 'Marketing automation advanced - Marketo, Pardot, Eloqua, lead scoring, nurture programs'),
    ('email-marketing-advanced', 'Email marketing advanced - deliverability, DKIM/SPF/DMARC, segmentation, AMP email, ISP'),
    ('account-based-marketing', 'Account-based marketing - ABM platforms, 6sense, Demandbase, intent data, orchestration'),
    ('seo-advanced-technical', 'SEO advanced technical - Core Web Vitals, crawl budget, JavaScript SEO, log analysis, schema'),
    ('paid-media-advanced', 'Paid media advanced - programmatic, DSP, DMP, bidding algorithms, audience building, ROAS'),
    ('social-media-marketing-tech', 'Social media marketing tech - Meta Ads API, TikTok Ads API, LinkedIn API, scheduling, analytics'),
    ('influencer-marketing-platform', 'Influencer marketing platform - creator discovery, campaign management, fraud detection, ROI'),
    ('marketing-analytics-advanced', 'Marketing analytics advanced - MMM, incrementality testing, attribution modeling, lift studies'),
    ('content-marketing-platform', 'Content marketing platform - content strategy tools, editorial calendar, distribution, repurposing'),
    ('growth-hacking-tech', 'Growth hacking technology - viral loops, referral programs, product-led growth, activation, PLG'),
    # AdTech deep
    ('programmatic-advertising', 'Programmatic advertising - RTB, SSP, DSP, ad exchange, OpenRTB protocol, supply path optimization'),
    ('ad-server-engineering', 'Ad server engineering - ad decisioning, pacing, frequency capping, targeting, VAST, VPAID'),
    ('header-bidding-advanced', 'Header bidding advanced - Prebid.js, OpenRTB, server-side bidding, adapter development'),
    ('ad-fraud-detection', 'Ad fraud detection - IVT, SIVT, bot detection, traffic quality, TAG, IAB standards, IAS'),
    ('identity-resolution-adtech', 'Identity resolution AdTech - cookie deprecation, first-party data, UID2, clean rooms, PETs'),
    ('contextual-advertising', 'Contextual advertising - semantic targeting, brand safety, content classification, NLP-based'),
    ('connected-tv-advertising', 'Connected TV advertising - CTV/OTT, SSAI, dynamic ad insertion, ACR data, measurement'),
    ('retail-media-networks', 'Retail media networks - sponsored products, display, analytics, self-serve, attribution'),
    ('attribution-modeling-advanced', 'Attribution modeling advanced - data-driven attribution, Shapley values, Markov chains, MMM'),
    ('privacy-sandbox-advanced', 'Privacy Sandbox advanced - Topics API, FLEDGE/PA API, Attribution Reporting, CHIPS'),
    # HR technology deep
    ('hris-advanced', 'HRIS advanced - Workday, SAP SuccessFactors, Oracle HCM, custom integrations, data model'),
    ('talent-acquisition-tech', 'Talent acquisition technology - ATS, sourcing tools, assessment platforms, hiring workflow'),
    ('workforce-analytics-advanced', 'Workforce analytics advanced - people analytics, attrition prediction, org network analysis'),
    ('performance-management-tech', 'Performance management technology - OKRs, continuous feedback, 360 reviews, calibration'),
    ('learning-development-platform', 'L&D platform - LMS advanced, skills mapping, AI-personalized learning, certification tracking'),
    ('compensation-analytics', 'Compensation analytics - market pricing, pay equity analysis, total rewards, salary bands'),
    ('employee-experience-platform', 'Employee experience platform - pulse surveys, recognition, wellbeing, DEI dashboards'),
    ('workforce-planning-tech', 'Workforce planning technology - headcount modeling, scenario planning, skill gap analysis'),
    ('payroll-systems-advanced', 'Payroll systems advanced - multi-country payroll, tax engine, compliance, ERP integration'),
    ('hr-chatbot-automation', 'HR chatbot automation - ServiceNow HR, conversational AI, policy Q&A, self-service workflows'),
    # Legal technology
    ('legal-document-automation', 'Legal document automation - contract templates, clause library, variable substitution, e-sign'),
    ('contract-lifecycle-management', 'Contract lifecycle management - CLM platforms, obligation tracking, renewal alerts, AI review'),
    ('legal-research-tech', 'Legal research technology - Westlaw API, LexisNexis, case law analysis, citation graphs, NLP'),
    ('ediscovery-advanced', 'eDiscovery advanced - TAR, predictive coding, Relativity, EDRM workflow, data culling'),
    ('legal-analytics-platform', 'Legal analytics platform - matter management, billing analytics, outside counsel benchmarking'),
    ('regulatory-compliance-tech', 'Regulatory compliance technology - RegTech, surveillance, policy management, horizon scanning'),
    ('intellectual-property-management', 'IP management technology - patent portfolio, trademark docketing, prior art search, PAIR'),
    ('court-technology', 'Court technology - case management systems, e-filing, virtual hearings, public portals'),
    ('legal-billing-advanced', 'Legal billing advanced - matter-based billing, LEDES format, e-billing, rate management'),
    ('compliance-monitoring', 'Compliance monitoring - transaction monitoring, KYC/AML, OFAC screening, regulatory reporting'),
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
