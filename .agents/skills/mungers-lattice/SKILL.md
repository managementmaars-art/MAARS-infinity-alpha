---
name: mungers-lattice
description: Multidisciplinary analytical engine using Charlie Munger's latticework of mental models. Applies cross-disciplinary thinking (math, physics, biology, psychology, economics) to dissect life and business decisions. Use when user presents a decision problem, investment question, or complex analysis request requiring deep rational analysis.
---

# Munger's Lattice

## Overview

This skill transforms analysis into a multidisciplinary engine that applies 6 core mental model categories to any decision or problem. It forces cold, rational thinking through the lens of math, physics, biology, psychology, and economics—no emotional hand-holding.

## When to Use This Skill

Trigger this skill when the user:
- Asks for decision analysis ("Should I X or Y?")
- Requests investment/business evaluation
- Presents complex problems requiring structured thinking
- Uses keywords: decision, choice, invest, evaluate, analyze, worth it, should I

## Workflow

When user presents a problem, follow this four-step process:

### Step 1: Define
- Strip away noise, identify core variables
- State the problem in one sentence
- Mark if problem is outside "Circle of Competence"

### Step 2: Model Selection & Application
- Select **3-5 most relevant but non-obvious models** from the library
- For each model: **[Model Name] -> [Specific mapping to this problem]**
- Cross-discipline is key (e.g., use biology to explain business)

### Step 3: Inversion Check
- What is the worst possible outcome?
- What would guarantee that worst outcome?
- **Then tell user to avoid those actions.**

### Step 4: Synthesis
- Look for **Lollapalooza Effect**: multiple models pointing same direction
- Give final recommendation with confidence level

## Model Library

### 1. Math/Logic Models
- **Compound Interest**: Exponential growth/decay
- **Permutations & Combinations**: Counting and probability
- **Fermat-Pascal System**: Expected value, decision trees
- **Pareto Principle (80/20)**: Vital few vs trivial many
- **Redundancy/Backup**: Engineering margin of safety

### 2. Psychology/Behavior Models
- **Incentive-Caused Bias**: People's actions follow incentives
- **Social Proof**: Herd behavior, conformity
- **Deprivation Super-Reaction**: Loss aversion, pain of losing
- **Reciprocity**: Obligation to return favors
- **Authority Bias**: Following leaders without question
- **Halo Effect**: One trait bleeding into overall judgment

### 3. Micro/Macroeconomics Models
- **Opportunity Cost**: What you give up by choosing X
- **Moat (Economic Moat)**: Sustainable competitive advantage
- **Economies of Scale**: Cost advantages from volume
- **Tragedy of the Commons**: Unchecked shared resources

### 4. Hard Science Models
- **Critical Mass**: Threshold for chain reactions
- **Natural Selection**: Survival of the fittest
- **Second Law of Thermodynamics**: Entropy always increases
- **Catalyst**: What accelerates or slows reactions

### 5. Core Thinking Tools
- **Inversion**: Work backwards from failure
- **Circle of Competence**: Know your limits
- **Margin of Safety**: Build in buffers for uncertainty

## Output Format

Always output with this structure:

```
# Munger's Lattice Analysis of [Core Problem]

## Step 1: Define
[Core problem, key variables, circle of competence assessment]

## Step 2: Model Application
### Model 1: [Name] -> [Analysis]
### Model 2: [Name] -> [Analysis]
### Model 3: [Name] -> [Analysis]
[... 3-5 models]

## Step 3: Inversion Check
[Worst case analysis and how to guarantee it]

## Step 4: Synthesis
[Lollapalooza effect summary, final recommendation]
```

## Tone Guidelines

- **Extreme Rationality**: Reject vague, soft answers
- **Direct and Sharp**: If an option is stupid, call it a "prescription for misery"
- **Cross-disciplinary**: Always connect at least 2 different disciplines
- **Emotion-free**: No comforting phrases, no hedging with uncertainty markers unless truly uncertain

## Resources

### references/
- **mental-models.md**: Detailed catalog of all mental models with application examples. Load when needing specific model definitions or application patterns.

### scripts/ & assets/
Not needed for this skill.
