
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Fintech and financial services deep
    ('open-banking-platform', 'Open banking platform - PSD2, CDR, FDX, consent management, account aggregation, payment initiation'),
    ('core-banking-modernization', 'Core banking modernization - API-first banking, microservices migration, ledger design, event-driven'),
    ('payments-rails-advanced', 'Payments rails advanced - SWIFT, SEPA, ACH, FedNow, RTP, instant payments, correspondent banking'),
    ('digital-wallet-platform', 'Digital wallet platform - e-money, stored value, P2P payments, tokenization, QR payments'),
    ('lending-platform-advanced', 'Lending platform advanced - credit decisioning, loan origination, servicing, collections, CECL'),
    ('wealth-tech-advanced', 'Wealth tech advanced - portfolio management, rebalancing, tax-loss harvesting, robo-advisory, GIPS'),
    ('insurance-policy-engine', 'Insurance policy engine - rating engine, underwriting rules, policy admin, claims adjudication, reinsurance'),
    ('regtech-transaction-monitoring', 'RegTech transaction monitoring - AML patterns, SAR filing, typologies, network analysis, SWIFT MT'),
    ('cbdc-platform-advanced', 'CBDC platform advanced - programmable money, offline payments, privacy-preserving, interoperability'),
    ('decentralized-finance-protocol', 'DeFi protocol development - AMM design, liquidity pools, yield farming, flash loans, governance'),
    # Real estate technology deep
    ('proptech-platform-advanced', 'Proptech platform advanced - MLS integration, IDX feeds, property valuation, AVM, RETS protocol'),
    ('real-estate-transaction-tech', 'Real estate transaction tech - e-closing, title insurance, escrow systems, ALTA, recording'),
    ('property-management-platform', 'Property management platform - lease management, maintenance, tenant portal, accounting, CAM'),
    ('real-estate-data-analytics', 'Real estate data analytics - market analytics, comp analysis, absorption rate, cap rates, NOI modeling'),
    ('construction-tech-platform', 'Construction tech platform - BIM integration, Procore, project management, RFI/submittal, punch list'),
    ('smart-building-platform', 'Smart building platform - BAS integration, energy management, occupancy analytics, HVAC control'),
    ('real-estate-investment-tech', 'Real estate investment tech - deal sourcing, underwriting models, waterfall, LP/GP, equity crowdfunding'),
    ('facility-management-advanced', 'Facility management advanced - CMMS, preventive maintenance, space utilization, CAFM, ISO 41001'),
    ('urban-planning-tech', 'Urban planning technology - GIS zoning, permitting, impact analysis, traffic modeling, UrbanSim'),
    ('home-services-platform', 'Home services platform - service marketplace, booking, job management, payments, reviews'),
    # Telecommunications technology deep
    ('telecom-network-management', 'Telecom network management - OSS/BSS, NETCONF, topology discovery, fault management, NMS'),
    ('voip-advanced-platform', 'VoIP advanced platform - SIP protocol, SBC, WebRTC gateway, media servers, transcoding, NG911'),
    ('telecom-billing-advanced', 'Telecom billing advanced - mediation, CDR processing, convergent billing, roaming settlement, TAP'),
    ('mobile-core-network', 'Mobile core network - EPC, 5G core, HSS/UDM, PCRF/PCF, AMF, SMF, UPF, network slicing'),
    ('telecom-fraud-detection', 'Telecom fraud detection - IRSF, PBX fraud, CLI spoofing, Wangiri, subscription fraud, real-time blocking'),
    ('network-analytics-platform', 'Network analytics platform - network telemetry, quality of service, anomaly detection, predictive maintenance'),
    ('unified-communications', 'Unified communications - UCaaS, Microsoft Teams integration, Zoom platform, contact center CCaaS'),
    ('iot-connectivity-platform', 'IoT connectivity platform - device management, MVNO, eSIM, LwM2M, connectivity management'),
    ('telecom-api-platform', 'Telecom API platform - GSMA Open APIs, NumberVerify, SIM Swap, WebRTC, CPaaS building blocks'),
    ('spectrum-management', 'Spectrum management - frequency allocation, interference analysis, CBRS, dynamic spectrum, DSA'),
    # Defense and national security technology
    ('c2-systems-advanced', 'C2 systems advanced - command and control software, MIL-STD, situational awareness, STANAG protocols'),
    ('military-simulation', 'Military simulation - constructive simulation, LVC, HLA, DIS protocol, training systems, VBS'),
    ('geoint-systems', 'GEOINT systems - imagery analysis, exploitation, motion detection, terrain analysis, NGA standards'),
    ('sigint-processing', 'SIGINT processing - signals collection, frequency analysis, protocol identification, data fusion'),
    ('cyber-operations-platform', 'Cyber operations platform - SOC tools integration, threat hunting, SIEM correlation, playbook automation'),
    ('logistics-military-advanced', 'Military logistics advanced - supply chain, maintenance tracking, RFID asset management, AIT'),
    ('defense-embedded-systems', 'Defense embedded systems - DO-254, DO-178C, JSF++, safety-critical, avionics certification'),
    ('electronic-warfare-systems', 'Electronic warfare systems - jamming, countermeasures, spectrum dominance, EW systems architecture'),
    ('unmanned-systems-platform', 'Unmanned systems platform - UAS GCS, STANAG 4586, payload integration, autonomous behaviors'),
    ('identity-management-gov-advanced', 'Identity management government advanced - PIV/CAC, FICAM, PKI, biometrics, clearance systems'),
    # Specialized AI and ML platforms
    ('multimodal-foundation-models', 'Multimodal foundation model development - vision-language, video, audio, cross-modal alignment'),
    ('ai-infrastructure-platform', 'AI infrastructure platform - GPU cluster management, job scheduling, storage, networking, MLperf'),
    ('synthetic-data-platform', 'Synthetic data platform - generative data, privacy-preserving, domain randomization, data augmentation'),
    ('ai-safety-platform', 'AI safety platform - red teaming automation, constitutional AI, RLHF pipelines, eval harness'),
    ('continual-learning-platform', 'Continual learning platform - catastrophic forgetting prevention, EWC, replay buffers, meta-learning'),
    ('federated-learning-platform', 'Federated learning platform - secure aggregation, differential privacy, heterogeneous data, FedProx'),
    ('knowledge-distillation-platform', 'Knowledge distillation platform - teacher-student training, lottery ticket hypothesis, pruning'),
    ('ai-hardware-optimization', 'AI hardware optimization - custom ASIC design, TPU programming, neuromorphic computing, in-memory compute'),
    ('autonomous-agent-platform', 'Autonomous agent platform - tool use, long-horizon planning, multi-agent coordination, memory systems'),
    ('llm-application-platform', 'LLM application platform - RAG pipelines, prompt management, evaluation, caching, routing, guardrails'),
    # Advanced robotics and automation
    ('industrial-automation-advanced', 'Industrial automation advanced - PLC programming, robot programming, vision systems, SCADA integration'),
    ('robot-programming-advanced', 'Robot programming advanced - ROS2 navigation, motion planning, MoveIt2, trajectory optimization'),
    ('collaborative-robot-programming', 'Collaborative robot programming - force control, impedance control, kinesthetic teaching, safety'),
    ('drone-fleet-management', 'Drone fleet management - UTM integration, geofencing, path planning, telemetry, beyond visual line'),
    ('autonomous-mobile-robot', 'Autonomous mobile robot - SLAM, navigation stack, fleet management, warehouse automation'),
    ('manipulation-robotics-advanced', 'Manipulation robotics advanced - grasp planning, deformable objects, bimanual coordination, tactile'),
    ('soft-robotics-advanced', 'Soft robotics advanced - pneumatic actuators, continuum robots, bio-inspired design, control systems'),
    ('human-robot-interaction', 'Human-robot interaction - intent recognition, safety monitoring, social robots, shared autonomy'),
    ('robot-learning-platform', 'Robot learning platform - sim-to-real, imitation learning, reinforcement learning, world models'),
    ('space-robotics-advanced', 'Space robotics advanced - orbital mechanics, EVA tools, planetary rovers, teleop with latency'),
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
