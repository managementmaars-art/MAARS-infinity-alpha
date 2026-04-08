---
name: ai-research-interpretability
description: Mechanistic interpretability with TransformerLens, sparse autoencoders, activation patching, attention analysis, and circuit discovery.
---

# AI Research: Interpretability

## Overview

Mechanistic interpretability reverse-engineers neural networks to understand how they compute. Key tools include TransformerLens for activation access, sparse autoencoders (SAEs) for feature decomposition, and activation patching for causal analysis.

## TransformerLens Setup

```python
# pip install transformer_lens
import transformer_lens
from transformer_lens import HookedTransformer, ActivationCache
import torch
import einops

# Load a model (GPT-2, GPT-Neo, Mistral, Llama, etc.)
model = HookedTransformer.from_pretrained(
    "gpt2",
    center_unembed=True,
    center_writing_weights=True,
    fold_ln=True,          # Fold LayerNorm weights for cleaner analysis
)

# Model architecture info
print(f"Layers: {model.cfg.n_layers}")
print(f"Heads: {model.cfg.n_heads}")
print(f"d_model: {model.cfg.d_model}")
print(f"d_head: {model.cfg.d_head}")
print(f"d_mlp: {model.cfg.d_mlp}")
```

## Activation Cache & Analysis

```python
# Run model and cache all activations
tokens = model.to_tokens("The Eiffel Tower is located in")

logits, cache = model.run_with_cache(tokens)

# Access any activation by name
residual_stream = cache["resid_post", 3]    # Layer 3 residual stream
attn_pattern = cache["pattern", 5]          # Layer 5 attention patterns
mlp_output = cache["mlp_out", 2]           # Layer 2 MLP output

# Access head-specific activations
head_output = cache["result", 4, "attn"]    # Layer 4 attention output
q, k, v = cache["q", 4], cache["k", 4], cache["v", 4]

# Decompose residual stream into components
def decompose_residual(cache: ActivationCache, layer: int, token_pos: int):
    """Show how each component contributes to the residual stream."""
    components = {}

    # Embedding contribution
    components["embed"] = cache["embed"][0, token_pos]

    # Each attention head
    for l in range(layer + 1):
        for h in range(model.cfg.n_heads):
            key = f"L{l}H{h}"
            components[key] = cache["result", l][0, token_pos, h]

        # MLP
        components[f"L{l}MLP"] = cache["mlp_out", l][0, token_pos]

    return components

# Logit lens: project each layer's residual to vocabulary
def logit_lens(cache: ActivationCache, token_pos: int = -1):
    """See what each layer 'predicts' at a given position."""
    for layer in range(model.cfg.n_layers):
        resid = cache["resid_post", layer][0, token_pos]
        # Apply final layer norm and unembed
        resid_normalized = model.ln_final(resid.unsqueeze(0).unsqueeze(0))
        logits = model.unembed(resid_normalized)[0, 0]
        top_tokens = logits.topk(5)
        print(f"Layer {layer}: {[model.to_string(t) for t in top_tokens.indices]}")

logit_lens(cache)
```

## Attention Pattern Analysis

```python
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_attention(cache: ActivationCache, layer: int, head: int, tokens):
    """Plot attention pattern for a specific head."""
    pattern = cache["pattern", layer][0, head].cpu().numpy()
    token_strs = model.to_str_tokens(tokens)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        pattern,
        xticklabels=token_strs,
        yticklabels=token_strs,
        cmap="Blues",
        ax=ax,
    )
    ax.set_title(f"Layer {layer}, Head {head} Attention Pattern")
    plt.tight_layout()
    plt.savefig(f"attn_L{layer}H{head}.png", dpi=150)

# Find "induction heads" (pattern: attend to token following previous occurrence)
def detect_induction_heads(model: HookedTransformer) -> list:
    """Induction heads: copy token after previous occurrence of current token."""
    seq = "A B C D E A B C D E"  # Repeated sequence
    tokens = model.to_tokens(seq)
    _, cache = model.run_with_cache(tokens)

    induction_heads = []
    for layer in range(model.cfg.n_layers):
        for head in range(model.cfg.n_heads):
            pattern = cache["pattern", layer][0, head]
            # Induction heads attend to T-seq_len+1 at position T
            # Check if diagonal shifted by -seq_len is high
            score = pattern.diagonal(-5).mean().item()  # -5 = -half_seq
            if score > 0.4:
                induction_heads.append((layer, head, score))

    return sorted(induction_heads, key=lambda x: -x[2])

induction_heads = detect_induction_heads(model)
print("Induction heads:", induction_heads[:5])
```

## Activation Patching (Causal Analysis)

```python
from functools import partial

def patch_activation(
    value: torch.Tensor,        # Corrupted activation
    hook,
    position: int,              # Token position to patch
    clean_cache: ActivationCache,
    hook_name: str,
):
    """Replace corrupted activation with clean activation at a position."""
    value[:, position] = clean_cache[hook_name][:, position]
    return value

def run_activation_patching(
    model: HookedTransformer,
    clean_prompt: str,
    corrupted_prompt: str,
    answer_token: str,
):
    """Find which components matter for a prediction by patching."""
    clean_tokens = model.to_tokens(clean_prompt)
    corrupted_tokens = model.to_tokens(corrupted_prompt)
    answer_id = model.to_single_token(answer_token)

    # Run clean and get cache
    _, clean_cache = model.run_with_cache(clean_tokens)

    # Baseline: corrupted model performance
    corrupted_logits = model(corrupted_tokens)
    baseline_prob = corrupted_logits[0, -1].softmax(dim=-1)[answer_id].item()

    # Patch each component and measure improvement
    results = {}

    for layer in range(model.cfg.n_layers):
        # Patch attention output
        hook_name = f"blocks.{layer}.hook_attn_out"
        patched_logits = model.run_with_hooks(
            corrupted_tokens,
            fwd_hooks=[(hook_name, partial(
                patch_activation,
                position=-1,
                clean_cache=clean_cache,
                hook_name=hook_name,
            ))],
        )
        patched_prob = patched_logits[0, -1].softmax(dim=-1)[answer_id].item()
        results[f"L{layer}attn"] = patched_prob - baseline_prob

        # Patch MLP output
        hook_name = f"blocks.{layer}.hook_mlp_out"
        patched_logits = model.run_with_hooks(
            corrupted_tokens,
            fwd_hooks=[(hook_name, partial(
                patch_activation,
                position=-1,
                clean_cache=clean_cache,
                hook_name=hook_name,
            ))],
        )
        patched_prob = patched_logits[0, -1].softmax(dim=-1)[answer_id].item()
        results[f"L{layer}mlp"] = patched_prob - baseline_prob

    return results

# IOI (Indirect Object Identification) circuit analysis
results = run_activation_patching(
    model,
    clean_prompt="When Mary and John went to the store, John gave a drink to Mary",
    corrupted_prompt="When Mary and John went to the store, Mary gave a drink to John",
    answer_token=" Mary",
)

# Plot results
import matplotlib.pyplot as plt
components = list(results.keys())
values = [results[c] for c in components]
plt.figure(figsize=(20, 4))
plt.bar(range(len(components)), values)
plt.xticks(range(len(components)), components, rotation=45)
plt.title("Activation Patching Results: Which components matter?")
plt.tight_layout()
plt.savefig("patching_results.png")
```

## Sparse Autoencoders (SAE)

```python
# pip install sae-lens
from sae_lens import SAE, ActivationsStore
import torch

# Load a pre-trained SAE
sae, cfg_dict, _ = SAE.from_pretrained(
    release="gpt2-small-res-jb",
    sae_id="blocks.8.hook_resid_post",
)

# Get activations and encode through SAE
tokens = model.to_tokens("The quick brown fox")
_, cache = model.run_with_cache(tokens)

resid_post = cache["resid_post", 8][0]  # [seq_len, d_model]

# Encode: find active features
feature_acts = sae.encode(resid_post)   # [seq_len, n_features]
reconstructed = sae.decode(feature_acts)

# L0 sparsity: avg features active per token
l0 = (feature_acts > 0).float().sum(dim=-1).mean()
print(f"L0 sparsity: {l0:.1f} features/token")

# Reconstruction MSE
mse = ((resid_post - reconstructed) ** 2).mean()
print(f"Reconstruction MSE: {mse:.4f}")

# Find top features for a token
token_pos = 3  # "fox"
active_features = feature_acts[token_pos].nonzero().squeeze(-1)
top_features = feature_acts[token_pos, active_features].topk(10)

print(f"\nTop features active on token '{model.to_string(tokens[0, token_pos])}':")
for feat_idx, activation in zip(
    active_features[top_features.indices].tolist(),
    top_features.values.tolist()
):
    print(f"  Feature {feat_idx}: {activation:.3f}")

# Build a custom SAE
class SparseAutoencoder(torch.nn.Module):
    def __init__(self, d_model: int, n_features: int, sparsity_coef: float = 1e-3):
        super().__init__()
        self.d_model = d_model
        self.n_features = n_features
        self.sparsity_coef = sparsity_coef

        self.W_enc = torch.nn.Linear(d_model, n_features, bias=True)
        self.W_dec = torch.nn.Linear(n_features, d_model, bias=False)

        # Normalize decoder weights
        with torch.no_grad():
            self.W_dec.weight.data = torch.nn.functional.normalize(
                self.W_dec.weight.data, dim=0
            )

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return torch.nn.functional.relu(self.W_enc(x))

    def decode(self, features: torch.Tensor) -> torch.Tensor:
        return self.W_dec(features)

    def forward(self, x: torch.Tensor) -> tuple:
        features = self.encode(x)
        reconstructed = self.decode(features)

        # Loss = reconstruction + sparsity
        recon_loss = ((x - reconstructed) ** 2).mean()
        sparsity_loss = features.abs().mean()
        total_loss = recon_loss + self.sparsity_coef * sparsity_loss

        return reconstructed, features, total_loss
```

## Neuron Analysis

```python
def analyze_neuron(model: HookedTransformer, layer: int, neuron: int, n_examples: int = 20):
    """Find examples that maximally activate a specific neuron."""
    from transformer_lens.utils import get_act_name

    # Prepare dataset
    from datasets import load_dataset
    dataset = load_dataset("NeelNanda/pile-10k", split="train")
    texts = dataset["text"][:1000]

    max_activations = []

    for text in texts:
        tokens = model.to_tokens(text[:200])
        _, cache = model.run_with_cache(tokens, names_filter=f"blocks.{layer}.mlp.hook_post")
        acts = cache[f"blocks.{layer}.mlp.hook_post"][0, :, neuron]

        for pos in range(acts.shape[0]):
            max_activations.append({
                "activation": acts[pos].item(),
                "token": tokens[0, pos].item(),
                "context": model.to_string(tokens[0, max(0, pos-5):pos+1]),
            })

    max_activations.sort(key=lambda x: -x["activation"])
    return max_activations[:n_examples]

top_examples = analyze_neuron(model, layer=8, neuron=2049)
for ex in top_examples[:5]:
    print(f"Activation: {ex['activation']:.2f} | Context: '{ex['context']}'")
```

## Key Patterns

- **Logit lens** is the fastest way to understand what each layer "knows"
- **Activation patching** identifies the causal circuit for a behavior — patch component, measure effect
- **Induction heads** (L-K and prev-token heads) are universal across models
- **SAEs** decompose polysemantic neurons into interpretable monosemantic features
- **Token position is crucial** — analyses are almost always position-dependent
- **TransformerLens hooks** are the core primitive — use `run_with_hooks` for non-destructive patching

## Models to Use

- **claude-opus-4-5**: Novel circuit discovery, SAE analysis strategy, interpretability paper reproduction
- **claude-sonnet-4-5**: Activation patching experiments, attention analysis, neuron attribution
- **claude-haiku-3-5**: Simple logit lens queries, cache access patterns, visualization scripts
