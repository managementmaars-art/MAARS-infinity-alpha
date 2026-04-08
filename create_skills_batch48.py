
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Enterprise software and ERP
    ('sap-s4hana', 'SAP S/4HANA - ABAP in Eclipse, CDS views, RAP, Fiori, Business Technology Platform integration'),
    ('sap-fiori-advanced', 'SAP Fiori advanced - UI5, freestyle apps, annotations, OData services, CAP Node.js'),
    ('oracle-fusion-cloud', 'Oracle Fusion Cloud - ERP modules, OTBI, BI Publisher, REST APIs, FBDI, HCM'),
    ('oracle-ebs', 'Oracle E-Business Suite - customizations, APIs, workflow, reporting, concurrent programs, forms'),
    ('microsoft-dynamics-365', 'Microsoft Dynamics 365 - customization, Power Platform, Dataverse, plugins, PCF controls'),
    ('workday-integration', 'Workday integration - Workday Studio, EIB, Prism Analytics, REST API, calculated fields'),
    ('servicenow-advanced', 'ServiceNow advanced - flow designer, ATF, CMDB, ITSM, integration hub, custom apps'),
    ('salesforce-cpq', 'Salesforce CPQ - quote-to-cash, price rules, product bundles, contracts, amendments'),
    ('veeva-crm', 'Veeva CRM - life sciences CRM, CLM, approved email, event management, MyInsights, iRep'),
    ('planview-ppm', 'Planview PPM - portfolio management, resource management, Lean/Agile, OKRs, reporting'),
    ('jira-service-management', 'Jira Service Management - service desk, assets, change management, SLAs, automation'),
    ('freshworks-suite', 'Freshworks suite - Freshdesk, Freshservice, Freshsales, CRM, automations, integrations'),
    ('zendesk-enterprise', 'Zendesk enterprise - ticket routing, omnichannel, CSAT, reporting, integrations, guide'),
    ('intercom-advanced-platform', 'Intercom advanced platform - product tours, series, bots, reporting, team inbox, SDK'),
    ('hubspot-operations-hub', 'HubSpot Operations Hub - data sync, programmable automation, data quality, reporting'),
    ('marketo-engage', 'Marketo Engage - smart campaigns, lead scoring, revenue cycle, email programs, attribution'),
    ('eloqua-marketing', 'Oracle Eloqua - campaign canvas, contact washing, data tools, dynamic content, APIs'),
    ('pardot-account-engagement', 'Pardot/Account Engagement - automation rules, completion actions, engagement programs'),
    ('klaviyo-ecommerce', 'Klaviyo e-commerce - flows, segments, predictive analytics, CDP, SMS, A/B testing'),
    ('iterable-growth', 'Iterable growth marketing - journeys, user events, catalogs, experiments, webhooks'),
    # Specialized cloud and infrastructure
    ('aws-outposts', 'AWS Outposts - on-premises AWS infrastructure, rack setup, connectivity, local data processing'),
    ('azure-stack-hub', 'Azure Stack Hub - disconnected deployments, hybrid cloud, ADFS, value-add RP'),
    ('google-distributed-cloud', 'Google Distributed Cloud - Anthos on-premises, GDC air-gapped, edge locations'),
    ('nutanix-cloud', 'Nutanix cloud - HCI, AOS, AHV, Prism, Flow, Files, Objects, Xi Cloud Services'),
    ('vmware-vsphere-advanced', 'VMware vSphere advanced - vCenter, DRS, HA, vMotion, vSAN, NSX integration'),
    ('openstack-advanced', 'OpenStack advanced - Nova, Neutron, Cinder, Swift, Heat, Keystone, Ironic, Kolla'),
    ('proxmox-ve', 'Proxmox VE - VM management, LXC, Ceph storage, clustering, HA, firewall, backup'),
    ('harvester-hci', 'Harvester HCI - Kubernetes-native virtualization, Rancher integration, storage, networking'),
    ('talos-linux', 'Talos Linux - immutable, API-driven OS for Kubernetes, declarative configuration, security'),
    ('flatcar-container-linux', 'Flatcar Container Linux - immutable OS, auto-updates, systemd, ignition, cloud init'),
    ('bottlerocket-os', 'Bottlerocket OS - AWS container OS, minimal attack surface, atomic updates, API server'),
    ('k0s-kubernetes', 'k0s Kubernetes - zero-friction, single binary, control plane, worker, autopilot upgrades'),
    ('microk8s-advanced', 'MicroK8s advanced - snap deployment, add-ons, HA, clustering, GPU support, Istio'),
    ('openshift-advanced', 'OpenShift advanced - operators, builds, DeploymentConfigs, routes, image streams, OLM'),
    ('rancher-advanced', 'Rancher advanced - Fleet, multi-cluster, catalog, monitoring, logging, cluster provisioning'),
    ('lens-kubernetes', 'Lens Kubernetes IDE - cluster management, resource editor, extensions, metrics, terminals'),
    ('cilium-ebpf-advanced', 'Cilium eBPF advanced - XDP, network policies, Hubble observability, encryption, BGP'),
    ('calico-advanced', 'Calico advanced - BGP peering, IPinIP, VXLAN, eBPF dataplane, policy troubleshooting'),
    ('multus-cni', 'Multus CNI - multiple network interfaces, SRIOV, DPDK, network attachment definitions'),
    ('whereabouts-ipam', 'Whereabouts IPAM - cluster-wide IPAM, IP reconciliation, overlapping CIDRs, storage'),
    # Observability and SRE
    ('opentelemetry-collector', 'OpenTelemetry Collector - pipelines, receivers, processors, exporters, configuration'),
    ('grafana-loki-advanced', 'Grafana Loki advanced - LogQL, streams, chunks, compactor, ruler, multi-tenancy'),
    ('grafana-tempo-advanced', 'Grafana Tempo advanced - TraceQL, metrics-generator, parquet backend, serverless'),
    ('cortex-advanced', 'Cortex advanced - ruler, alertmanager, blocks storage, tenant federation, compaction'),
    ('thanos-advanced', 'Thanos advanced - sidecar, store gateway, compactor, ruler, querier, receive mode'),
    ('m3-metrics', 'M3 metrics - distributed time series, M3DB, M3Query, M3Coordinator, Prometheus remote write'),
    ('openmetrics-standard', 'OpenMetrics standard - exposition format, naming, types, exemplars, push, info metrics'),
    ('pyroscope-profiling', 'Pyroscope profiling - continuous profiling, FlameQL, storage, integrations, Grafana plugin'),
    ('coroot-monitoring', 'Coroot monitoring - application-centric, eBPF, service maps, anomaly detection, SLOs'),
    ('groundcover-monitoring', 'groundcover monitoring - eBPF-based APM, in-cluster, cost attribution, service mesh'),
    ('honeycomb-advanced', 'Honeycomb advanced - BubbleUp, SLOs, derived columns, triggers, boards, environments'),
    ('lightstep-observability', 'Lightstep observability - change intelligence, service health, correlations, percentiles'),
    ('elastic-observability-advanced', 'Elastic observability advanced - profiling, synthetic, universal profiling, SLOs'),
    ('appdynamics-advanced', 'AppDynamics advanced - business transactions, baselines, flow maps, machine agents'),
    ('dynatrace-davis', 'Dynatrace Davis AI - automatic root cause, Smartscape, OneAgent, Davis security, BizOps'),
    ('new-relic-advanced', 'New Relic advanced - NRQL, NR1 platform, custom visualizations, distributed tracing, AI'),
    ('datadog-advanced-platform', 'Datadog advanced platform - Notebooks, SLOs, Error Tracking, Incident Management, RUM'),
    ('instana-advanced', 'Instana advanced - automatic tracing, infrastructure map, AI root cause, pipeline monitoring'),
    ('signoz-self-hosted', 'SigNoz self-hosted - ClickHouse backend, custom dashboards, alerts, team management'),
    ('chronosphere-observability', 'Chronosphere observability - control plane, pipeline, cardinality control, SLOs'),
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
