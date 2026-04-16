---
name: zero-trust-architecture
description: Use when designing security architectures, implementing zero trust principles, or evaluating security posture. Covers never trust always verify, microsegmentation, identity-based access, and ZTNA patterns.
allowed-tools: Read, Glob, Grep
---

# Zero Trust Architecture

Comprehensive guide to zero trust security architecture - the "never trust, always verify" approach to modern security.

## When to Use This Skill

- Designing security architecture for new systems
- Migrating from perimeter-based security
- Implementing microsegmentation
- Evaluating identity-based access controls
- Understanding ZTNA (Zero Trust Network Access)
- Assessing security posture

## Core Principles

```text
Zero Trust Pillars:

1. Never Trust, Always Verify
   └── Every request is verified regardless of origin
   └── No implicit trust based on network location
   └── Continuous authentication and authorization

2. Least Privilege Access
   └── Minimum permissions required for the task
   └── Just-in-time access when possible
   └── Just-enough-access for the operation

3. Assume Breach
   └── Design as if attackers are already inside
   └── Minimize blast radius of any compromise
   └── Continuous monitoring and verification

4. Explicit Verification
   └── Verify user identity
   └── Verify device health
   └── Verify request context
   └── Make access decisions at each request
```

## Architecture Components

### Identity Layer

```text
Identity Provider (IdP):
├── Multi-factor authentication (MFA)
├── Single sign-on (SSO)
├── Federated identity
└── Privileged access management (PAM)

User Identity:
- Strong authentication required
- Continuous session validation
- Risk-based authentication
- Context-aware access decisions

Service Identity:
- Machine identity management
- Service accounts with rotation
- Certificate-based authentication
- Workload identity
```

### Device Layer

```text
Device Trust Assessment:
├── Device health attestation
├── Endpoint detection and response (EDR)
├── Mobile device management (MDM)
├── Certificate-based device identity
└── Posture assessment

Device Trust Signals:
- Is the device managed/enrolled?
- Is the OS up to date?
- Is security software running?
- Are there known vulnerabilities?
- Is there anomalous behavior?
```

### Network Layer

```text
Microsegmentation:
┌─────────────────────────────────────────┐
│              Traditional               │
│  ┌──────────────────────────────────┐  │
│  │     Flat Internal Network       │  │
│  │   Trust everything inside       │  │
│  └──────────────────────────────────┘  │
│                  ↓                      │
│          Zero Trust                    │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│  │ Seg │ │ Seg │ │ Seg │ │ Seg │     │
│  │  A  │ │  B  │ │  C  │ │  D  │     │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘     │
│     │       │       │       │         │
│  All traffic verified at each hop     │
└─────────────────────────────────────────┘

Network Controls:
- Software-defined perimeter (SDP)
- Network access control (NAC)
- DNS security
- Encrypted communications (mTLS)
```

### Application Layer

```text
Application Security:
├── API gateway with authentication
├── Service mesh for service-to-service
├── Web application firewall (WAF)
├── Runtime application self-protection (RASP)
└── Secure software supply chain

Access Control:
- Attribute-based access control (ABAC)
- Role-based access control (RBAC)
- Policy-based access control
- Just-in-time access provisioning
```

### Data Layer

```text
Data Protection:
├── Classification and labeling
├── Encryption at rest and in transit
├── Data loss prevention (DLP)
├── Rights management
└── Tokenization/masking

Data Access:
- Need-to-know basis
- Fine-grained access control
- Audit logging for all access
- Data residency compliance
```

## Implementation Patterns

### Pattern 1: Identity-Aware Proxy

```text
                    ┌───────────────────┐
                    │   Identity Proxy   │
                    │  (BeyondCorp-style)│
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  User   │          │  Device │          │ Context │
   │ Identity│          │  Trust  │          │  Eval   │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Access Decision  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Application      │
                    └───────────────────┘

How it works:
1. User requests access to application
2. Proxy checks user identity (authentication)
3. Proxy evaluates device trust score
4. Proxy considers context (location, time, behavior)
5. Policy engine makes access decision
6. If approved, proxy provides access
```

### Pattern 2: Service Mesh Zero Trust

```text
┌─────────────────────────────────────────────────┐
│                   Control Plane                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Policy  │  │   Cert   │  │  Config  │     │
│  │  Engine  │  │ Authority│  │  Store   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼────────────┘
        │             │             │
┌───────▼─────────────▼─────────────▼────────────┐
│                   Data Plane                    │
│  ┌─────────────┐        ┌─────────────┐        │
│  │  Service A  │◄──mTLS──►│  Service B  │        │
│  │  ┌───────┐  │        │  ┌───────┐  │        │
│  │  │ Proxy │  │        │  │ Proxy │  │        │
│  │  └───────┘  │        │  └───────┘  │        │
│  └─────────────┘        └─────────────┘        │
└─────────────────────────────────────────────────┘

Service mesh provides:
- mTLS between all services
- Fine-grained authorization policies
- Service-to-service identity
- Traffic encryption everywhere
- Policy enforcement at the proxy
```

### Pattern 3: ZTNA (Zero Trust Network Access)

```text
Traditional VPN:
User ──► VPN ──► Full Network Access

ZTNA (Zero Trust Network Access):
User ──► ZTNA Broker ──► Specific App Only
              │
        ┌─────▼─────┐
        │ Evaluate: │
        │ - Identity│
        │ - Device  │
        │ - Context │
        │ - Policy  │
        └─────┬─────┘
              │
        Access to ONE application
        (not entire network)

ZTNA Benefits:
- Application-level access, not network-level
- Invisible infrastructure (no exposed IPs)
- Consistent policy regardless of location
- Reduced attack surface
```

## Trust Evaluation

### Continuous Trust Scoring

```text
Trust Score Components:

User Trust:
├── Authentication strength    [0-25 points]
├── Session age/freshness     [0-15 points]
├── Behavioral anomalies      [0-20 points]
└── Historical patterns       [0-10 points]

Device Trust:
├── Device management status   [0-20 points]
├── Security posture          [0-20 points]
├── Patch level               [0-15 points]
└── Certificate validity      [0-10 points]

Context Trust:
├── Network location          [0-15 points]
├── Geolocation               [0-10 points]
├── Time of access            [0-10 points]
└── Request patterns          [0-15 points]

Total Score: 0-185 points

Policy Example:
- Score > 150: Full access
- Score 100-150: Limited access + step-up auth
- Score 50-100: Read-only access
- Score < 50: Block access
```

### Risk-Based Access Decisions

```text
Access Decision Matrix:

                    │ Low-Risk Resource │ High-Risk Resource
────────────────────┼───────────────────┼────────────────────
High Trust Score    │ Allow             │ Allow
Medium Trust Score  │ Allow             │ MFA Challenge
Low Trust Score     │ MFA Challenge     │ Block + Alert

Dynamic Factors:
- Time-based: Unusual access hours?
- Location-based: Unusual geography?
- Behavior-based: Unusual patterns?
- Resource-based: Sensitive data access?
```

## Implementation Roadmap

### Phase 1: Visibility and Identity

```text
Duration: 3-6 months

Steps:
1. Inventory all users, devices, applications
2. Implement strong identity management
3. Enable MFA everywhere
4. Deploy comprehensive logging
5. Establish baseline behaviors

Success Criteria:
□ 100% user MFA coverage
□ Complete asset inventory
□ Centralized authentication
□ Security event visibility
```

### Phase 2: Device Trust

```text
Duration: 3-6 months

Steps:
1. Implement device management (MDM/UEM)
2. Deploy endpoint security (EDR)
3. Establish device trust policies
4. Enable device health attestation
5. Enforce device compliance

Success Criteria:
□ All devices managed/enrolled
□ Device posture assessment active
□ Non-compliant devices blocked
□ Certificate-based device identity
```

### Phase 3: Microsegmentation

```text
Duration: 6-12 months

Steps:
1. Map application dependencies
2. Define segmentation policies
3. Implement network controls
4. Deploy software-defined perimeter
5. Enable east-west traffic inspection

Success Criteria:
□ Critical apps microsegmented
□ East-west traffic encrypted
□ Lateral movement restricted
□ Segment-level monitoring
```

### Phase 4: Adaptive Access

```text
Duration: 3-6 months

Steps:
1. Implement risk scoring
2. Deploy policy decision points
3. Enable continuous authentication
4. Implement just-in-time access
5. Automate access decisions

Success Criteria:
□ Risk-based access decisions
□ Context-aware policies
□ Automated access reviews
□ Just-in-time privileged access
```

## Anti-Patterns

```text
Zero Trust Anti-Patterns:

1. "Zero Trust In Name Only"
   ❌ Adding MFA and calling it zero trust
   ✓ Comprehensive identity + device + network + data controls

2. "Perimeter Replacement"
   ❌ Replacing VPN with ZTNA without other controls
   ✓ ZTNA as part of comprehensive architecture

3. "Trust The Internal Network"
   ❌ Applying zero trust only at the edge
   ✓ Verify all traffic, including internal

4. "One-Time Verification"
   ❌ Verify at login, trust for session duration
   ✓ Continuous verification throughout session

5. "Security Theater"
   ❌ Complex controls that users bypass
   ✓ Frictionless security that's hard to bypass
```

## Technology Options

```text
Identity & Access:
- Azure AD / Entra ID
- Okta
- Ping Identity
- Google Identity

ZTNA Solutions:
- Zscaler Private Access
- Cloudflare Access
- Palo Alto Prisma Access
- Tailscale

Service Mesh:
- Istio
- Linkerd
- Consul Connect
- AWS App Mesh

Device Management:
- Microsoft Intune
- Jamf
- VMware Workspace ONE
- Google Endpoint Management
```

## Related Skills

- `api-security` - OAuth, OIDC, JWT patterns
- `mtls-service-mesh` - Service-to-service security
- `secrets-management` - Credential and secret handling
- `observability-patterns` - Security monitoring and detection
