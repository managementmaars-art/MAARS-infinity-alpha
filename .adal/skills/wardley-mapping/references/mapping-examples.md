# Wardley Mapping Examples

## Example 1: E-Commerce Platform

### Map

```text
Title: Online Retail Platform
Anchor: Customer needs to purchase products online
Date: 2025-12-26

                    Genesis    Custom     Product    Commodity
                       │          │          │          │
Visible            ┌───┼──────────┼──────────┼──────────┼───┐
                   │   │          │          │          │   │
                   │   │  ● Customer Experience          │   │
                   │   │  │                              │   │
                   │   │  ├──────────────────┐           │   │
                   │   │  │                  │           │   │
                   │   │  ↓                  ↓           │   │
                   │   │  ● Product         ● Shopping  │   │
                   │   │    Recommendations   Cart       │   │
                   │   │    │                 │          │   │
                   │   │    │                 │          │   │
                   │   │    ↓                 ↓          │   │
                   │   │    ●────────────────●──────────→●  │
                   │   │    Personalization  Checkout    │   │
                   │   │    Engine           │           │   │
                   │   │    │                │           │   │
Hidden             │   │    │                ↓           │   │
                   │   │    │                ● Payment──→●  │
                   │   │    │                  Gateway   │   │
                   │   │    │                │           │   │
                   │   │    ↓                ↓           │   │
                   │   │    ●────────────────●──────────→●  │
                   │   │    Customer Data    Cloud       │   │
                   │   │                     Compute     │   │
                   └───┴──────────────────────────────────┘

Legend: ● Current position, → Evolution direction
```

### Analysis

```yaml
e_commerce_analysis:
  anchor:
    user: "Online shopper"
    need: "Purchase products conveniently online"

  components:
    customer_experience:
      evolution: "Custom"
      position: 0.35
      notes: "Differentiating, unique brand experience"

    product_recommendations:
      evolution: "Custom → Product"
      position: 0.40
      movement: "evolving"
      notes: "ML-based, moving toward productized solutions"

    personalization_engine:
      evolution: "Custom"
      position: 0.30
      notes: "Key differentiator, in-house built"
      depends_on: ["customer_data"]

    shopping_cart:
      evolution: "Product"
      position: 0.65
      notes: "Many solutions available, configure don't build"

    checkout:
      evolution: "Product → Commodity"
      position: 0.70
      movement: "evolving"
      notes: "Standard patterns, increasingly commoditized"

    payment_gateway:
      evolution: "Commodity"
      position: 0.85
      notes: "Stripe, Adyen - utility services"

    customer_data:
      evolution: "Custom"
      position: 0.35
      notes: "Proprietary, valuable for personalization"

    cloud_compute:
      evolution: "Commodity"
      position: 0.90
      notes: "AWS, Azure - utility"

  strategic_insights:
    opportunities:
      - "Double down on personalization as differentiator"
      - "Commoditize checkout to reduce cost"
      - "Use customer data to improve recommendations"

    threats:
      - "Amazon's personalization superiority"
      - "Recommendation engines becoming commoditized"

    recommendations:
      - action: "Invest in personalization engine"
        rationale: "Key differentiator, not yet commoditized"

      - action: "Migrate to SaaS checkout"
        rationale: "No competitive advantage in custom checkout"

      - action: "Build customer data platform"
        rationale: "Enables differentiation in personalization"
```

## Example 2: DevOps Platform

### Map

```text
Title: Internal Developer Platform
Anchor: Developers need to deploy applications reliably
Date: 2025-12-26

                    Genesis    Custom     Product    Commodity
                       │          │          │          │
Visible            ┌───┼──────────┼──────────┼──────────┼───┐
                   │   │          │          │          │   │
                   │   │          │  ● Developer        │   │
                   │   │          │    Portal           │   │
                   │   │          │    │                │   │
                   │   │          │    ├──────────┐     │   │
                   │   │          │    │          │     │   │
                   │   │  ● Golden│    │          │     │   │
                   │   │    Paths │    │          │     │   │
                   │   │    │     │    │          │     │   │
                   │   │    │     ↓    ↓          ↓     │   │
                   │   │    │     ●────●──────────●     │   │
                   │   │    │     CI/CD  Container  IaC │   │
                   │   │    │     │      Orchestration  │   │
Hidden             │   │    │     │      │          │   │   │
                   │   │    │     │      │          │   │   │
                   │   │    ↓     ↓      ↓          ↓   │   │
                   │   │    ●─────●──────●──────────●   │   │
                   │   │    Platform  Kubernetes  Cloud │   │
                   │   │    Config    │          │      │   │
                   │   │              │          │      │   │
                   │   │              ↓          ↓      │   │
                   │   │              ●──────────●      │   │
                   │   │              Compute    Network│   │
                   └───┴──────────────────────────────────┘
```

### Analysis

```yaml
devops_analysis:
  strategic_positioning:
    differentiation_zone:
      components: ["Developer Portal", "Golden Paths"]
      strategy: "Build custom, focus on developer experience"
      rationale: "Competitive advantage in developer productivity"

    leverage_zone:
      components: ["CI/CD", "Container Orchestration", "IaC"]
      strategy: "Buy/configure products"
      rationale: "Mature products exist, don't rebuild"

    utility_zone:
      components: ["Kubernetes", "Cloud", "Compute"]
      strategy: "Consume as utility"
      rationale: "Commodity, optimize for cost"

  inertia_points:
    - component: "Platform Config"
      inertia: "Custom scripts accumulated over years"
      resolution: "Migrate to IaC gradually"

  evolution_watch:
    - component: "CI/CD"
      current: "Product"
      trend: "Moving toward commodity/utility (GitHub Actions, etc.)"
      action: "Prepare to migrate when utility options mature"
```

## Example 3: Machine Learning Product

### Map

```text
Title: ML-Powered Document Processing
Anchor: Business users need to extract data from documents
Date: 2025-12-26

                    Genesis    Custom     Product    Commodity
                       │          │          │          │
Visible            ┌───┼──────────┼──────────┼──────────┼───┐
                   │   │          │          │          │   │
                   │   │          │     ● Document      │   │
                   │   │          │       Portal        │   │
                   │   │          │       │             │   │
                   │   │          │       │             │   │
                   │   │   ● Custom│      │             │   │
                   │   │     NLP  │←──────┘             │   │
                   │   │     Models│                    │   │
                   │   │     │     │                    │   │
                   │   │     │     ↓                    │   │
                   │   │     │     ●────────────────────●   │
                   │   │     │     Human Review   OCR      │
                   │   │     │     Workflow            │   │
Hidden             │   │     │     │                   │   │
                   │   │     │     │                   │   │
                   │   │     ↓     ↓                   │   │
                   │   │     ●─────●───────────────────●   │
                   │   │     ML    Training   Document │   │
                   │   │     Pipeline Data     Storage │   │
                   │   │     │                 │       │   │
                   │   │     ↓                 ↓       │   │
                   │   │     ●─────────────────●       │   │
                   │   │     GPU Compute  Cloud      │   │
                   └───┴──────────────────────────────────┘
```

### Strategic Decision

```yaml
ml_strategy:
  key_decision: "Build vs. Buy ML Models"

  analysis:
    custom_nlp_models:
      current_position: "Genesis/Custom (0.25)"
      alternatives:
        - "Azure AI Document Intelligence (Product)"
        - "AWS Textract (Product)"
        - "Google Document AI (Product)"

      considerations:
        build:
          pros:
            - "Tailored to specific document types"
            - "IP ownership"
            - "Potential long-term differentiator"
          cons:
            - "High expertise required"
            - "Slow time to market"
            - "Maintenance burden"

        buy:
          pros:
            - "Fast time to market"
            - "Continuous improvement by vendor"
            - "No ML expertise needed"
          cons:
            - "Less customization"
            - "Vendor lock-in"
            - "No differentiation"

  recommendation:
    decision: "Hybrid approach"
    strategy:
      - "Start with product (Azure AI) for 80% of documents"
      - "Build custom models only for unique document types"
      - "Focus differentiation on human-in-loop workflow"

    rationale: |
      Document AI products are mature enough for most use cases.
      True differentiation is in the workflow, not the ML models.
      Custom models only where product gaps exist.
```

## Common Mapping Patterns

### The Tower Pattern

```yaml
tower_pattern:
  description: "Differentiation built on commodity foundation"

  structure:
    top: "Genesis/Custom differentiators"
    middle: "Product integrations"
    bottom: "Commodity infrastructure"

  example:
    differentiator: "Custom recommendation engine"
    product_layer: "E-commerce platform, CRM"
    commodity: "Cloud compute, databases"

  strategy: "Maximize commoditization at bottom to fund top"
```

### The Legacy Trap

```yaml
legacy_trap:
  description: "Custom-built components that should be commodity"

  symptoms:
    - "Large team maintaining commodity-equivalent"
    - "High cost, slow innovation"
    - "Technical debt accumulation"

  example:
    component: "Custom identity management"
    market_alternatives: ["Auth0", "Azure AD B2C", "Okta"]
    waste: "Team of 5 maintaining what SaaS provides"

  resolution: "Migrate to product/commodity, redeploy team"
```

### The Premature Innovation

```yaml
premature_innovation:
  description: "Treating genesis component as if product/commodity"

  symptoms:
    - "Fixed-scope contracts for unknown work"
    - "Waterfall planning for experimental work"
    - "Outsourcing pioneer work"

  example:
    component: "Novel ML application"
    mistake: "Fixed-price contract with vendor"
    result: "Scope creep, failed project"

  resolution: "Match management approach to evolution stage"
```

---

**Last Updated:** 2025-12-26
