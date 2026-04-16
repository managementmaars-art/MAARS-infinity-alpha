---
name: ai-governance
description: AI governance and responsible AI planning including EU AI Act classification, NIST AI RMF, and AI ethics frameworks
allowed-tools: Read, Glob, Grep, Write, Edit, Task
---

# AI Governance Planning

Comprehensive guidance for AI governance, regulatory compliance, and responsible AI practices before development begins.

## When to Use This Skill

- Building AI/ML systems that may fall under EU AI Act
- Implementing NIST AI Risk Management Framework
- Establishing responsible AI practices and governance
- Conducting AI risk classification and impact assessments
- Creating AI documentation and transparency reports

## EU AI Act Overview

### Risk-Based Classification

The EU AI Act categorizes AI systems by risk level:

```text
┌─────────────────────────────────────────────────────┐
│ UNACCEPTABLE RISK (Prohibited)                      │
│ • Social scoring by governments                     │
│ • Subliminal manipulation                           │
│ • Exploitation of vulnerabilities                   │
│ • Real-time biometric ID in public (exceptions)     │
├─────────────────────────────────────────────────────┤
│ HIGH RISK (Strict Requirements)                     │
│ • Biometric identification                          │
│ • Critical infrastructure management                │
│ • Education/vocational training access              │
│ • Employment, worker management, recruitment        │
│ • Essential services access (credit, insurance)     │
│ • Law enforcement                                   │
│ • Migration, asylum, border control                 │
│ • Justice and democratic processes                  │
├─────────────────────────────────────────────────────┤
│ LIMITED RISK (Transparency Obligations)             │
│ • Chatbots (must disclose AI interaction)           │
│ • Emotion recognition systems                       │
│ • Biometric categorization                          │
│ • Deepfakes (must label as generated)               │
├─────────────────────────────────────────────────────┤
│ MINIMAL RISK (No Specific Requirements)             │
│ • AI-enabled video games                            │
│ • Spam filters                                      │
│ • Inventory management                              │
└─────────────────────────────────────────────────────┘
```

### High-Risk AI Requirements

| Requirement | Description | Implementation |
|-------------|-------------|----------------|
| **Risk Management** | Continuous risk management system | Risk assessment process |
| **Data Governance** | Training data quality and governance | Data documentation |
| **Technical Documentation** | Detailed system documentation | System spec + model cards |
| **Record Keeping** | Automatic logging of events | Audit trail |
| **Transparency** | Clear instructions for users | User documentation |
| **Human Oversight** | Ability for human intervention | HITL mechanisms |
| **Accuracy, Robustness, Cybersecurity** | Appropriate performance levels | Testing + monitoring |

### Risk Classification Decision Tree

```csharp
public class EuAiActClassifier
{
    public AiRiskCategory Classify(AiSystemDescription system)
    {
        // Check for prohibited practices first
        if (IsProhibited(system))
            return AiRiskCategory.Unacceptable;

        // Check Annex III high-risk categories
        if (IsHighRiskCategory(system))
            return AiRiskCategory.High;

        // Check Annex I product safety legislation
        if (RequiresProductConformity(system))
            return AiRiskCategory.High;

        // Check for transparency obligations
        if (RequiresTransparency(system))
            return AiRiskCategory.Limited;

        return AiRiskCategory.Minimal;
    }

    private bool IsProhibited(AiSystemDescription system)
    {
        return system.UseCases.Any(uc =>
            uc.Type == UseCaseType.SocialScoring ||
            uc.Type == UseCaseType.SubliminalManipulation ||
            uc.Type == UseCaseType.VulnerabilityExploitation ||
            (uc.Type == UseCaseType.RealTimeBiometricId &&
             uc.Context == Context.PublicSpace &&
             !uc.HasLawEnforcementException));
    }

    private bool IsHighRiskCategory(AiSystemDescription system)
    {
        var highRiskCategories = new[]
        {
            Domain.BiometricIdentification,
            Domain.CriticalInfrastructure,
            Domain.EducationAccess,
            Domain.Employment,
            Domain.EssentialServices,
            Domain.LawEnforcement,
            Domain.MigrationAsylum,
            Domain.JusticeProcesses
        };

        return highRiskCategories.Contains(system.Domain);
    }
}

public enum AiRiskCategory
{
    Unacceptable,
    High,
    Limited,
    Minimal
}
```

## NIST AI Risk Management Framework

### The Four Functions

```text
┌─────────────────────────────────────────────────────────────┐
│                         GOVERN                               │
│  Culture, policies, accountability structures               │
│  ↓                                                          │
├─────────────────────────────────────────────────────────────┤
│        MAP              MEASURE           MANAGE            │
│  Context & risks →  Assess risks →   Prioritize &          │
│  identification     & impacts        mitigate               │
└─────────────────────────────────────────────────────────────┘
```

### Govern Function

Establish AI governance structures:

```markdown
## AI Governance Structure

### Roles and Responsibilities
| Role | Responsibilities |
|------|------------------|
| AI Governance Board | Strategic oversight, policy approval |
| AI Ethics Officer | Ethics review, bias assessment |
| AI Risk Manager | Risk identification, mitigation tracking |
| Model Owner | Lifecycle management, performance |
| Technical Lead | Implementation, testing, monitoring |

### Policies Required
- [ ] AI Development Policy
- [ ] Model Risk Management Policy
- [ ] AI Ethics Guidelines
- [ ] Data Quality Standards
- [ ] Human Oversight Requirements
- [ ] Incident Response for AI Failures
```

### Map Function

Understand context and identify risks:

```csharp
public class AiContextMapping
{
    public record AiSystemContext
    {
        public required string SystemName { get; init; }
        public required string Purpose { get; init; }
        public required List<string> Stakeholders { get; init; }
        public required List<string> ImpactedGroups { get; init; }
        public required string DecisionType { get; init; } // Augment vs Automate
        public required bool InvolvesVulnerablePopulations { get; init; }
        public required List<string> PotentialHarms { get; init; }
        public required List<string> PotentialBenefits { get; init; }
        public required List<string> LegalConstraints { get; init; }
    }

    public ContextAssessment Assess(AiSystemContext context)
    {
        var risks = new List<IdentifiedRisk>();

        // Assess stakeholder impacts
        foreach (var group in context.ImpactedGroups)
        {
            risks.Add(new IdentifiedRisk
            {
                Category = "Stakeholder Impact",
                Description = $"Potential impact on {group}",
                Severity = context.InvolvesVulnerablePopulations
                    ? RiskSeverity.High
                    : RiskSeverity.Medium
            });
        }

        // Assess potential harms
        foreach (var harm in context.PotentialHarms)
        {
            risks.Add(new IdentifiedRisk
            {
                Category = "Potential Harm",
                Description = harm,
                Severity = DetermineHarmSeverity(harm)
            });
        }

        return new ContextAssessment
        {
            Context = context,
            IdentifiedRisks = risks,
            RecommendedMitigations = GenerateMitigations(risks)
        };
    }
}
```

### Measure Function

Assess and analyze AI risks:

```markdown
## Risk Assessment Framework

### Trustworthiness Characteristics

| Characteristic | Assessment Questions |
|----------------|---------------------|
| **Valid & Reliable** | Does the system perform as intended? Are results consistent? |
| **Safe** | Can the system cause harm? Are safety controls adequate? |
| **Secure & Resilient** | Is the system protected from attacks? Can it recover? |
| **Accountable & Transparent** | Can we explain decisions? Is there clear ownership? |
| **Explainable & Interpretable** | Can users understand outputs? Can we audit decisions? |
| **Privacy-Enhanced** | Is personal data protected? Is data minimization applied? |
| **Fair (Bias Managed)** | Are outcomes equitable? Is bias detected and mitigated? |

### Measurement Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Accuracy | Correct predictions/total | ≥95% |
| Fairness Gap | Max disparity across groups | ≤5% |
| Explainability | Decisions with explanations | 100% |
| Incident Rate | Failures per 1000 uses | <1 |
| Human Override Rate | Manual interventions | Track |
```

### Manage Function

Prioritize and implement mitigations:

```csharp
public class AiRiskManagement
{
    public record RiskMitigation
    {
        public required string RiskId { get; init; }
        public required string Risk { get; init; }
        public required RiskSeverity Severity { get; init; }
        public required List<string> Controls { get; init; }
        public required string Owner { get; init; }
        public required DateTimeOffset DueDate { get; init; }
        public required MitigationStatus Status { get; init; }
    }

    public RiskTreatmentPlan CreateTreatmentPlan(
        IEnumerable<IdentifiedRisk> risks)
    {
        var prioritized = risks
            .OrderByDescending(r => r.Severity)
            .ThenByDescending(r => r.Likelihood);

        var plan = new RiskTreatmentPlan();

        foreach (var risk in prioritized)
        {
            var treatment = DetermineTreatment(risk);

            switch (treatment)
            {
                case TreatmentType.Avoid:
                    plan.Avoidances.Add(CreateAvoidanceAction(risk));
                    break;
                case TreatmentType.Mitigate:
                    plan.Mitigations.Add(CreateMitigationPlan(risk));
                    break;
                case TreatmentType.Transfer:
                    plan.Transfers.Add(CreateTransferPlan(risk));
                    break;
                case TreatmentType.Accept:
                    plan.Acceptances.Add(CreateAcceptanceRecord(risk));
                    break;
            }
        }

        return plan;
    }
}
```

## Responsible AI Principles

### Core Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Fairness** | Equitable treatment, non-discrimination | Bias testing, fairness metrics |
| **Transparency** | Clear about AI use and limitations | Disclosure, explanations |
| **Accountability** | Clear ownership and responsibility | Governance, audit trails |
| **Privacy** | Protect personal data | Data minimization, consent |
| **Safety** | Prevent harm | Testing, guardrails, monitoring |
| **Human Control** | Meaningful human oversight | HITL, override capabilities |

### Model Documentation (Model Card)

```markdown
# Model Card: [Model Name]

## Model Details
- **Developer**: [Organization]
- **Version**: [X.Y.Z]
- **Type**: [Classification/Regression/Generation/etc.]
- **Framework**: [PyTorch/TensorFlow/etc.]
- **License**: [License]

## Intended Use
- **Primary Use Cases**: [List]
- **Users**: [Target users]
- **Out-of-Scope Uses**: [Prohibited or unsupported uses]

## Training Data
- **Dataset**: [Name and source]
- **Size**: [Number of examples]
- **Features**: [Key features used]
- **Preprocessing**: [Steps applied]
- **Known Limitations**: [Data gaps or biases]

## Evaluation
- **Metrics**: [Accuracy, F1, etc.]
- **Test Data**: [Holdout set description]
- **Results**: [Performance numbers]
- **Fairness Evaluation**: [Disaggregated metrics]

## Ethical Considerations
- **Sensitive Use Cases**: [If applicable]
- **Potential Misuse**: [Risks]
- **Mitigations**: [Controls in place]

## Limitations and Recommendations
- **Known Limitations**: [Model weaknesses]
- **Recommendations**: [Best practices for users]
```

### Algorithmic Impact Assessment

```markdown
## Algorithmic Impact Assessment

### 1. System Description
- **Name**: [System name]
- **Purpose**: [Business objective]
- **Decision Type**: [What decisions it informs/makes]
- **Affected Parties**: [Who is impacted]

### 2. Data Assessment
- **Data Sources**: [Origin of data]
- **Personal Data**: [Types collected]
- **Sensitive Attributes**: [Protected characteristics]
- **Historical Bias Risk**: [Assessment]

### 3. Impact Assessment

#### Positive Impacts
| Impact | Beneficiary | Magnitude |
|--------|-------------|-----------|
| [Impact] | [Group] | [High/Med/Low] |

#### Negative Impacts
| Impact | Affected Group | Magnitude | Mitigation |
|--------|----------------|-----------|------------|
| [Impact] | [Group] | [H/M/L] | [Action] |

### 4. Fairness Assessment
- **Protected Groups Analyzed**: [List]
- **Fairness Metrics Used**: [Demographic parity, etc.]
- **Disparities Found**: [Results]
- **Remediation Plan**: [Actions]

### 5. Human Oversight
- **Oversight Level**: [Full automation / Human-in-the-loop / Human-on-the-loop]
- **Override Mechanism**: [How humans can intervene]
- **Escalation Path**: [When to escalate]

### 6. Monitoring Plan
- **Performance Metrics**: [What to track]
- **Fairness Metrics**: [Ongoing monitoring]
- **Review Frequency**: [Cadence]
- **Trigger Thresholds**: [When to investigate]

### 7. Approval
| Role | Name | Approval | Date |
|------|------|----------|------|
| Model Owner | | [ ] | |
| AI Ethics | | [ ] | |
| Legal | | [ ] | |
| Business | | [ ] | |
```

## AI Governance Checklist

### Pre-Development

- [ ] Classify AI system risk level (EU AI Act)
- [ ] Conduct algorithmic impact assessment
- [ ] Identify regulatory requirements
- [ ] Establish governance structure
- [ ] Define success metrics (including fairness)
- [ ] Document intended use and limitations

### Development

- [ ] Implement bias testing throughout development
- [ ] Create model documentation (model card)
- [ ] Build explainability features
- [ ] Implement human oversight mechanisms
- [ ] Create audit logging
- [ ] Test with diverse stakeholders

### Deployment

- [ ] Final fairness evaluation
- [ ] Transparency disclosures in place
- [ ] Human override mechanisms tested
- [ ] Monitoring dashboards configured
- [ ] Incident response plan ready
- [ ] User documentation complete

### Operations

- [ ] Regular bias monitoring
- [ ] Performance drift detection
- [ ] Periodic fairness audits
- [ ] Model retraining governance
- [ ] Incident tracking and response
- [ ] Stakeholder feedback collection

## Cross-References

- **Bias Assessment**: Research via MCP (perplexity: "AI bias assessment frameworks NIST")
- **Explainability**: Research via MCP (perplexity: "AI explainability XAI techniques")
- **Data Privacy**: `gdpr-compliance` for data protection
- **Ethics**: `ethics-review` for ethical assessment

## Resources

- [EU AI Act Text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)
- [OECD AI Principles](https://oecd.ai/en/ai-principles)
- [IEEE Ethically Aligned Design](https://ethicsinaction.ieee.org/)
