# Tree Search Protocol

Detailed rules for expanding the idea tree in Phase 1 of the Idea Tournament. The tree structure ensures diverse idea generation by systematically varying one axis per level.

## The Three Axes

Each level of the tree varies a different axis. This constraint prevents "similar but different" ideas — each branch explores a fundamentally different dimension of variation.

### Technique Axis (Level 1)

**What varies**: The core technical approach to the problem.

**Good variation**: Each technique represents a fundamentally different paradigm.
- Example for "efficient LLM inference": Pruning (remove weights), Quantization (reduce precision), Distillation (train smaller model)
- These are genuinely different approaches with different assumptions and trade-offs

**Bad variation**: Variations within the same paradigm.
- "Structured pruning", "Unstructured pruning", "Dynamic pruning" — all pruning
- Save these for Level 3 (formulation variants within a technique)

**How to generate**: Ask "What are the 3 fundamentally different ways to approach this problem?" Verify each technique is genuinely distinct — they should rely on different principles, not just different parameters.

### Domain Axis (Level 2)

**What varies**: The application context or data domain where the technique is applied.

**Good variation**: Each domain introduces meaningfully different constraints.
- Example for "pruning for efficient LLM inference": Edge devices (memory-constrained), Multi-modal models (heterogeneous layers), Long-context applications (attention-dominated compute)
- Each domain changes which aspects of pruning matter most

**Bad variation**: Domains that are functionally identical for this technique.
- "Text classification" vs "sentiment analysis" — same technical challenge
- Domains should create different technical demands

**How to generate**: Ask "In what contexts would this technique face fundamentally different challenges?" List 2-3 domains per Level 1 node.

### Formulation Axis (Level 3)

**What varies**: The specific problem formulation — inputs, outputs, constraints, evaluation criteria.

**Good variation**: Each formulation defines a different concrete problem.
- Example for "pruning on edge devices": Latency-constrained (optimize for speed), Memory-constrained (optimize for model size), Accuracy-preserving (optimize for minimal quality loss)
- Each formulation leads to different optimization targets and evaluation metrics

**Bad variation**: Formulations that are equivalent in practice.
- "Minimize latency" vs "Maximize throughput" on the same single-device setup — same optimization

**How to generate**: Ask "What are the different ways to precisely state what success looks like?" Generate 1-2 formulations per Level 2 node.

## Expansion Rules

### Per-Node Cycle: Propose → Review → Refine

**Step 1 — Propose**:
Write a 2-3 sentence description of the idea. Include:
- What the technique does (in this domain, under this formulation)
- Why it might work (the key insight or hypothesis)
- How it differs from the parent node

**Step 2 — Review** (evaluate critically):
Evaluate three questions:
1. Is this genuinely different from sibling nodes? (If not, merge or replace)
2. Is it at least plausible? (If clearly impossible, prune)
3. Is the description specific enough to act on? (If vague, refine)

**Step 3 — Refine**:
Based on the review, sharpen the description. Remove vague language ("might be useful", "could potentially"). Make the novelty claim specific ("uses X to solve Y, which previous approaches Z cannot handle because...").

### Target: Up to N_I=21 Leaf Candidates

The paper sets N_I=21 as the maximum number of candidate ideas during tree search. This value balances diversity against tournament cost: a 3-level tree with 3 technique × 3 domain × ~2-3 formulation branches naturally produces 18-27 leaves, and 21 is the empirically validated upper bound from the paper's experiments (higher N_I showed diminishing returns in Elo ranking stability). Practical guidance for tournament quality:
- **<10 candidates**: Not enough diversity. Tournament results are unreliable — too few comparisons.
- **15-21 candidates**: Good diversity with manageable tournament size (4-5 rounds of Swiss pairing). Aim for this range.
- **>21 candidates**: Exceeds the paper's N_I limit. Prune more aggressively to stay within 21.

If your tree produces fewer than 15 leaves after pruning, expand Level 2 or Level 3 further. If more than 21, prune to stay within the N_I limit.

## Pruning Criteria

Prune after each level expansion. A branch should be pruned ONLY if:

### Clearly Infeasible
- Requires resources fundamentally unavailable (e.g., proprietary data, hardware you can't access)
- Contradicts well-established theoretical or physical constraints
- Violates known mathematical impossibility results

### Duplicate
- Effectively identical to another branch after review (same technique + domain + formulation despite different wording)
- When merging duplicates, keep the more precisely stated version

### Known Failure (from evo-memory)
- Appears in M_I unsuccessful directions as a **fundamental failure** (not implementation failure)
- Implementation failures may be worth retrying — do NOT prune these

### Do NOT Prune
- Ideas that seem unlikely but are not provably impossible
- Ideas outside your current expertise (unfamiliarity ≠ infeasibility)
- Ideas that challenge conventional wisdom (these are often the most interesting)
- Ideas rated low on any single dimension (the tournament evaluates holistically)

## Diversity Metrics

After tree expansion, check diversity before proceeding to the tournament:

### Inter-Branch Diversity
Are Level 1 branches genuinely different techniques?
- Test: Could you explain each Level 1 branch to a colleague in one sentence, and would they recognize them as different approaches?
- If two branches could be described with the same sentence → merge them

### Intra-Branch Diversity
Within each Level 1 branch, are Level 2 nodes exploring different domains?
- Test: Do the domains create different technical challenges for the technique?
- If two domains would use the exact same implementation → merge them

### Leaf Diversity
Across all leaf nodes, is there variety in formulations?
- Test: Would the evaluation metrics be different for different leaves?
- If two leaves would be evaluated identically → they're the same problem

## Example Tree: Efficient LLM Inference

```
Level 0 (Seed): Efficient LLM inference

Level 1 (Technique):
├── T1: Structured Pruning
├── T2: Mixed-Precision Quantization
└── T3: Knowledge Distillation

Level 2 (Domain):
├── T1-D1: Pruning for edge deployment
├── T1-D2: Pruning for multi-modal LLMs
├── T1-D3: Pruning for long-context models
├── T2-D1: Quantization for mobile devices
├── T2-D2: Quantization for batch inference servers
├── T2-D3: Quantization for streaming applications
├── T3-D1: Distillation for domain-specific models
├── T3-D2: Distillation preserving reasoning ability
└── T3-D3: Distillation for multi-lingual models

Level 3 (Formulation):
├── T1-D1-F1: Edge pruning with latency target
├── T1-D1-F2: Edge pruning with memory target
├── T1-D2-F1: Multi-modal pruning preserving cross-modal alignment
├── T1-D2-F2: Multi-modal pruning with modality-specific ratios
├── T1-D3-F1: Context-aware pruning for 100K+ token inputs
├── T2-D1-F1: 4-bit quantization maintaining instruction following
├── T2-D1-F2: Mixed 4/8-bit with per-layer sensitivity
├── T2-D2-F1: Batch-optimized quantization for throughput
├── T2-D3-F1: Streaming quantization with dynamic precision
├── T2-D3-F2: Streaming quantization with latency-accuracy trade-off
├── T3-D1-F1: Domain distillation with unlabeled data only
├── T3-D1-F2: Few-shot domain distillation
├── T3-D2-F1: Reasoning-preserving distillation via chain-of-thought
├── T3-D2-F2: Reasoning distillation with verifier feedback
├── T3-D3-F1: Multi-lingual distillation with shared representations
└── T3-D3-F2: Cross-lingual distillation from English teacher
```

16 leaf nodes — within the target range (≤N_I=21). Each leaf represents a distinct, well-defined research problem.
