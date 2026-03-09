# Transformer Component Breakdown

A reference table for every component in the transformer — what it does, why it's there, and an analogy.

---

## Component-by-Component Table

| Component | What it does | Why it's there | Analogy |
|---|---|---|---|
| Word embeddings | Maps each token ID to a dense vector | Gives tokens a meaningful numerical representation | A dictionary that maps each word to its "profile" |
| Positional encoding | Adds position signal to each embedding | Attention is order-agnostic — needs position injected | Stamping each page with a page number |
| Multi-head self-attention (encoder) | Each token gathers context from all other tokens, from multiple perspectives | Builds rich contextual representations | 8 specialists reading the same document from different angles |
| Masked self-attention (decoder) | Each token gathers context from past tokens only | Prevents seeing the future during generation | An author re-reading what they've written before writing the next word |
| Cross-attention (decoder) | Decoder attends to encoder output | Connects decoder to source context | A translator glancing at the original while speaking the translation |
| Feed-forward network (FFN) | Two-layer MLP applied to each position | Applies learned transformations to processed context; stores factual knowledge | A specialist interpreting information gathered by the attention mechanism |
| Residual connection | Adds input to sub-layer output | Enables gradient flow through deep networks; eases optimization | A parallel backup route that always carries the original signal |
| Layer normalization | Normalizes activations within each sample | Stabilizes training; prevents activation explosion | A level-setting calibration before passing to the next stage |
| Linear + Softmax (output) | Projects decoder output to vocabulary distribution | Converts hidden state to next-token probabilities | Translating internal thoughts into a specific word choice |

---

## Detailed: Residual Connection

**What:**
```
output = LayerNorm(x + SubLayer(x))
```

The input x passes through the sub-layer, and then the original x is added back.

**Why:**
1. Gradient highway: during backpropagation, the gradient can flow directly through the addition without passing through the sub-layer's parameters at all. Even if the sub-layer's gradient vanishes, the residual connection guarantees gradient flow.
2. Easy learning: the sub-layer only needs to learn a correction delta on top of the identity. It's much easier to learn "add this small amount" than "produce the full output from scratch."
3. Enables depth: with residuals, models can be 96+ layers deep and still train.

---

## Detailed: Layer Normalization

**What:** For a vector x of dimension d:
```
LayerNorm(x) = γ × (x - mean(x)) / std(x) + β
```
Where γ and β are learned scaling/shifting parameters.

**Why:**
- Batch norm (used in CNNs) normalizes across the batch dimension. For variable-length sequences, this is tricky.
- Layer norm normalizes within each sample, across the feature dimension. Works for any sequence length.
- Prevents activations from being too large or too small, keeping the model in a trainable range.

---

## Detailed: Feed-Forward Network

**What:**
```
FFN(x) = max(0, x × W1 + b1) × W2 + b2

Dimensions:
  x:     (N × d_model)        e.g., (100 × 512)
  W1:    (d_model × d_ff)     e.g., (512 × 2048)
  W2:    (d_ff × d_model)     e.g., (2048 × 512)
  output:(N × d_model)        e.g., (100 × 512)
```

Applied independently to each position. The same W1 and W2 are used for all positions in a layer (position-wise).

**Why 4× expansion?**
- The first layer projects up to a wider space where more complex feature combinations can form
- ReLU provides nonlinearity — without it, two linear layers are still just linear
- The second layer projects back down, selecting the most useful features

---

## Detailed: Attention in context of the full layer

Attention and FFN work as a two-stage process within each layer:

| Stage | What it does |
|---|---|
| Attention | "Gather" — collect relevant information from other positions |
| FFN | "Process" — transform the gathered information into useful representations |

Attention is communication between tokens. FFN is computation within each token.

This division is deliberate. Research has shown that removing the FFN entirely and relying on attention alone significantly hurts performance — especially on factual recall tasks.

---

## Summary: What each part is responsible for

| What the model needs to do | Component responsible |
|---|---|
| Know what each word means | Word embeddings |
| Know where each word is | Positional encoding |
| Understand word in context | Multi-head self-attention |
| Remember what was generated | Masked self-attention (decoder) |
| Connect source to target | Cross-attention (decoder) |
| Store facts and apply transformations | Feed-forward network |
| Train stably and deeply | Residual connections + layer norm |
| Output the next word probability | Linear + Softmax |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture deep dive |
| 📄 **Component_Breakdown.md** | ← you are here |

⬅️ **Prev:** [05 Positional Encoding](../05_Positional_Encoding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md)
