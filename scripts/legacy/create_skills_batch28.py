
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Security tools and techniques deep
    ('nessus-scanning', 'Nessus vulnerability scanner - policies, plugins, scan templates, reports, compliance'),
    ('openvas-gvm', 'OpenVAS/GVM - vulnerability management, targets, configs, tasks, reports, NASL scripts'),
    ('nikto-web', 'Nikto web scanner - options, tuning, plugins, evasion, output formats, false positives'),
    ('sqlmap-advanced', 'SQLMap advanced - tampers, techniques, DBMS, batch, wizard, crawl, dump, OS shell'),
    ('hydra-brute', 'Hydra brute force - services, wordlists, modules, rate limiting, success criteria, resume'),
    ('hashcat-advanced', 'Hashcat advanced - attack modes, rules, masks, brain, OpenCL, benchmarks, restore'),
    ('john-ripper', 'John the Ripper - formats, wordlists, rules, incremental, MPI, jumbo, cracking modes'),
    ('aircrack-ng', 'Aircrack-ng suite - capture, WEP, WPA, PMKID, deauth, injection, monitor mode'),
    ('volatility-forensics', 'Volatility memory forensics - plugins, profiles, artifacts, carving, process, network'),
    ('autopsy-forensics', 'Autopsy digital forensics - modules, ingest, timeline, hash analysis, tagging, reports'),
    ('ghidra-advanced', 'Ghidra advanced - scripts, decompiler, analysis, PCode, plugins, collaboration'),
    ('ida-pro', 'IDA Pro - disassembly, decompiler, scripting, plugins, FLIRT, kernel, cross-references'),
    ('binary-ninja', 'Binary Ninja - lifting, MLIL, HLIL, plugins, scripting, collaboration, linear sweep'),
    ('radare2', 'Radare2 - commands, analysis, debugging, patching, scripting r2pipe, visual mode'),
    ('angr-symbolic', 'angr symbolic execution - CFG, path exploration, hooking, SimProcedures, concolic'),
    ('frida-hooking', 'Frida dynamic instrumentation - hooks, stalker, interceptors, memory, iOS, Android'),
    ('gdb-advanced', 'GDB advanced - Python scripting, TUI, reverse debugging, fork, thread, LLDB'),
    ('lldb-advanced', 'LLDB advanced - scripting, SBFrame, watchpoints, type system, debugserver, crashlogs'),
    ('strace-ltrace', 'strace/ltrace - syscall tracing, signal handling, attach, output, performance analysis'),
    ('perf-linux', 'Linux perf - events, sampling, tracing, flamegraphs, hardware counters, BPF'),
    ('bpftrace-ebpf', 'bpftrace - probes, maps, builtins, output, histograms, kernel tracing, use cases'),
    ('osquery-detection', 'osquery - queries, packs, scheduled queries, fleet, real-time, FIM, alerts'),
    ('yara-rules', 'YARA rules - strings, conditions, modules, metadata, performance, private rules'),
    ('snort-ids', 'Snort IDS - rules, preprocessors, output, DAQ, Barnyard2, SO rules, PulledPork'),
    ('suricata-ids', 'Suricata IDS - rules, EVE JSON, fast.log, Lua scripts, datasets, rule tuning'),
    ('zeek-network', 'Zeek network analysis - scripts, logs, frameworks, policy, intelligence, cluster'),
    ('ossec-hids', 'OSSEC HIDS - agents, rules, decoders, active response, email alerts, rootkit detection'),
    ('wazuh-advanced', 'Wazuh SIEM advanced - rules, decoders, active response, modules, integrations, dashboards'),
    ('splunk-siem', 'Splunk SIEM - SPL, dashboards, alerts, lookups, field extractions, Phantom, ES'),
    ('elastic-siem', 'Elastic SIEM - detection rules, ML jobs, timelines, cases, threat intel, alerts'),
    # Cloud security deep
    ('aws-security-advanced', 'AWS security advanced - GuardDuty, Security Hub, Inspector, Macie, Detective, SSM'),
    ('gcp-security', 'GCP security - Security Command Center, Chronicle, Asset Inventory, Binary Authorization'),
    ('azure-security-center', 'Azure Security Center/Defender - policies, initiatives, recommendations, workflow'),
    ('cloud-custodian', 'Cloud Custodian - policies, actions, filters, real-time, metrics, off-hours, tags'),
    ('prowler-aws', 'Prowler - AWS/GCP/Azure security checks, CIS, GDPR, HIPAA, quick wins, remediations'),
    ('steampipe-iac', 'Steampipe - SQL for cloud APIs, plugins, mods, dashboards, benchmarks, snapshots'),
    ('cloudmapper', 'CloudMapper - AWS visualization, audit, collect, webserver, anomaly detection'),
    ('pacu-aws', 'Pacu AWS exploitation - modules, session, bypass, privilege escalation, data exfiltration'),
    ('scout-suite', 'Scout Suite - multi-cloud security auditing, providers, ruleset, exceptions, report'),
    # Container/K8s security
    ('falco-advanced', 'Falco advanced - rules, macros, lists, plugins, outputs, gRPC, Helm deployment'),
    ('trivy-advanced', 'Trivy advanced - scanning, SBOM, secrets, config, Java, client-server, GitHub Actions'),
    ('grype-advanced', 'Grype - vulnerability scanner, SBOM input, DB management, output formats, CI'),
    ('kyverno-policies', 'Kyverno - policy engine, validate, mutate, generate, cleanup, test, CLI'),
    ('opa-kubernetes', 'OPA Kubernetes - Gatekeeper, constraint templates, policies, audit, gator, testing'),
    ('kubescape', 'Kubescape - K8s security posture, NSA guidelines, MITRE, risk scoring, CI integration'),
    ('kube-bench', 'kube-bench - CIS benchmarks, checks, remediation, config, JSON output, non-k8s'),
    ('kube-hunter', 'kube-hunter - active hunting, passive, report, remote, network, Azure, in-cluster'),
    ('aqua-security', 'Aqua Security - image scanning, runtime protection, network policies, drift prevention'),
    ('sysdig-falco', 'Sysdig - system calls, captures, advisors, inspect, Falco integration, troubleshooting'),
    # IAM / Identity security
    ('aws-iam-deep', 'AWS IAM deep - policy simulation, conditions, permission boundaries, trust policies'),
    ('gcp-iam-deep', 'GCP IAM deep - custom roles, resource hierarchy, policy binding, workload identity'),
    ('azure-rbac', 'Azure RBAC - role definitions, assignments, custom roles, PIM, access reviews'),
    ('hashicorp-vault-advanced', 'HashiCorp Vault advanced - auth methods, secrets engines, PKI, dynamic creds, DR'),
    ('cyberark-pam', 'CyberArk PAM - PSM, CPM, PVWA, credential vaulting, session recording, REST API'),
    ('beyond-trust', 'BeyondTrust - privileged access, session management, password safe, endpoint privilege'),
    ('delinea-pam', 'Delinea Secret Server - vaulting, workflow, SSH proxying, discovery, API, DevOps'),
    ('ping-identity', 'Ping Identity - PingFederate, PingAccess, DaVinci, directory, adaptive auth, SSO'),
    ('sailpoint-iam', 'SailPoint IdentityNow - governance, access requests, certifications, roles, policies'),
    ('saviynt-igaas', 'Saviynt - IGA, PAM, application access, cloud, analytics, workflow, provisioning'),
    # Network security deep
    ('palo-alto-ngfw', 'Palo Alto Networks - zones, policies, app-ID, user-ID, decryption, WildFire, Panorama'),
    ('fortinet-fortigate', 'FortiGate - FortiOS, policies, UTM, SD-WAN, HA, FortiManager, FortiAnalyzer'),
    ('checkpoint-firewall', 'Check Point - SmartConsole, rule base, NAT, VPN, ClusterXL, management API'),
    ('cisco-asa', 'Cisco ASA - ACLs, NAT, VPN, clustering, failover, ASDM, CLI, packet capture'),
    ('f5-big-ip', 'F5 BIG-IP - LTM, GTM, ASM, APM, iRules, iApps, TMSH, REST, clustering'),
    ('imperva-waf', 'Imperva WAF/CDN - security policies, custom rules, API protection, bot management'),
    ('cloudflare-security', 'Cloudflare security - WAF, DDoS, bot management, Zero Trust, CASB, Magic Transit'),
    ('akamai-security', 'Akamai security - Kona Site Defender, Bot Manager, API Gateway, Prolexic'),
    # Compliance frameworks
    ('soc2-implementation', 'SOC 2 implementation - trust services criteria, controls, evidence, auditors, tooling'),
    ('iso27001-implementation', 'ISO 27001 implementation - ISMS, risk assessment, controls, SoA, audits, PDCA'),
    ('hipaa-security-rule', 'HIPAA Security Rule - administrative, physical, technical safeguards, BAA, auditing'),
    ('pci-dss-advanced', 'PCI DSS advanced - CDE scoping, SAQ, QSA, pen testing, tokenization, P2PE'),
    ('nist-csf', 'NIST Cybersecurity Framework - identify, protect, detect, respond, recover, tiers, profiles'),
    ('gdpr-technical', 'GDPR technical implementation - consent, data mapping, privacy by design, DSAR, retention'),
    ('fedramp-advanced', 'FedRAMP advanced - authorization packages, ConMon, 3PAO, boundary, POA&M'),
    ('cis-benchmarks', 'CIS Benchmarks - hardening, scoring, remediation, Windows, Linux, cloud, containers'),
    ('disa-stig', 'DISA STIG - checklists, findings, CAT levels, POAM, remediation, automation, scanning'),
    # Penetration testing methodology
    ('oscp-techniques', 'OSCP techniques - enumeration, exploitation, post-exploitation, buffer overflows, AD'),
    ('web-app-pentest', 'Web app pentest - OWASP, recon, authentication, authorization, injection, logic bugs'),
    ('network-pentest', 'Network pentest - discovery, enumeration, exploitation, pivoting, tunneling, persistence'),
    ('mobile-pentest', 'Mobile pentest - iOS/Android, static analysis, dynamic, traffic interception, runtime'),
    ('cloud-pentest', 'Cloud pentest - AWS/GCP/Azure, IAM, metadata, SSRF, misconfigs, lateral movement'),
    ('red-team-advanced', 'Red team advanced - C2 frameworks, evasion, persistence, exfiltration, phishing, OPSEC'),
    ('phishing-simulation', 'Phishing simulation - GoPhish, pretexting, landing pages, tracking, reporting, training'),
    ('social-engineering', 'Social engineering - pretexting, vishing, physical, OSINT, spear phishing, simulation'),
    ('osint-advanced', 'OSINT advanced - Maltego, Shodan, Censys, social media, dark web, pivoting, reporting'),
    ('threat-hunting-techniques', 'Threat hunting techniques - hypothesis, data sources, analytics, tooling, playbooks'),
    # Application security
    ('sast-advanced', 'SAST advanced - custom rules, triage, suppression, integration, remediation, SARIF'),
    ('dast-advanced', 'DAST advanced - ZAP, HCL AppScan, authenticated, API, business logic, reporting'),
    ('iast-runtime', 'IAST runtime - Contrast, Seeker, agents, analysis, accuracy, coverage, integration'),
    ('rasp-runtime', 'RASP - runtime application self-protection, agents, policies, blocking, monitoring'),
    ('software-composition', 'SCA - dependency scanning, license, reachability, fix prioritization, VEX'),
    ('fuzzing-techniques', 'Fuzzing techniques - AFL++, libFuzzer, coverage, corpus, sanitizers, harnesses'),
    ('code-injection-prevention', 'Code injection prevention - input validation, encoding, parameterized queries, WAF'),
    ('cryptography-implementation', 'Cryptography implementation - key sizes, modes, padding, rotation, HSM, FIPS'),
    ('secrets-detection', 'Secrets detection - truffleHog, gitleaks, detect-secrets, baseline, rotation, response'),
    # Data/database security
    ('database-encryption', 'Database encryption - TDE, column-level, key management, backup encryption, HSM'),
    ('database-auditing', 'Database auditing - activity monitoring, access logging, DAM, SIEM integration'),
    ('data-masking', 'Data masking - static, dynamic, tokenization, format-preserving, policies, testing'),
    ('dlp-implementation', 'DLP implementation - content inspection, policies, endpoints, cloud, email, remediation'),
    ('zero-trust-implementation', 'Zero trust implementation - identity, device, network, application, data, analytics'),
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
