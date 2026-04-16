---
name: wardley-map
description: Create a Wardley Map for a business or technology context. Use for visualizing value chains and strategic positioning.
allowed-tools: Read, Glob, Grep, Write, Skill, Task, mcp__perplexity__search, mcp__perplexity__reason
argument-hint: <context> [--focus <area>] [--depth overview|standard|detailed]
---

# Create Wardley Map

Create a Wardley Map to visualize value chains and component evolution for strategic planning.

## Workflow

### Step 1: Parse Arguments

- **context** (required): The domain to map
- **focus** (optional): Specific area within domain
- **depth** (optional): overview | standard | detailed

### Step 2: Research Context

Use MCP servers to understand the domain:

1. Research current industry landscape for the context
2. Identify common components and patterns
3. Understand evolution state of key technologies

### Step 3: Spawn Strategy Mapmaker Agent

Invoke the `strategy-mapmaker` agent with:

```text
Create a Wardley Map for: [context]
Focus area: [focus if provided, or "full scope"]
Detail level: [depth or "standard"]

Requirements:
1. Start with user need identification
2. Build complete value chain
3. Position all components on evolution axis
4. Identify movement and inertia
5. Document strategic observations
6. Provide OWM notation for rendering
```

### Step 4: Validate Output

Ensure the map includes:

- [ ] Clear user need as anchor
- [ ] Components positioned on both axes
- [ ] Dependencies mapped
- [ ] Evolution stages justified
- [ ] Movement indicators where relevant
- [ ] Strategic observations
- [ ] OWM notation for visualization

### Step 5: Return Results

Present the complete Wardley Map with:

1. Visual representation (Mermaid or ASCII)
2. OWM notation for online rendering
3. Component analysis table
4. Strategic observations
5. Recommended next steps

## Examples

### Basic Usage

```text
/wardley-map "e-commerce platform"
```

Creates a standard-depth Wardley Map for an e-commerce platform.

### Focused Map

```text
/wardley-map "CI/CD pipeline" focus="deployment-automation"
```

Creates a map focused on the deployment automation aspect.

### Detailed Analysis

```text
/wardley-map "cloud migration strategy" depth="detailed"
```

Creates a detailed map with comprehensive component analysis.

## Output Format

The command produces:

1. **Map Overview**: Purpose, scope, user need
2. **Visual Map**: Rendered diagram or OWM notation
3. **Component Table**: All components with positions
4. **Strategic Analysis**: Opportunities, threats, plays
5. **Next Steps**: Actionable recommendations

## Related Commands

- `/strategic-analysis`: Deep strategic analysis of a mapped domain
- `/doctrine-assessment`: Assess organizational doctrine

## Related Skills

- `wardley-map-creation`: Core mapping methodology
- `value-chain-mapping`: Value chain decomposition
- `evolution-analysis`: Evolution stage assessment
