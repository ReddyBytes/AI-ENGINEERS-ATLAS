# Transformer Architecture — Cheatsheet

**One-liner:** The transformer uses stacked encoder layers (bidirectional self-attention) and decoder layers (masked self-attention + cross-attention), with residual connections and layer norm around each sub-layer.

---

## Key Terms

| Term | Definition |
|---|---|
| Encoder | Stack of layers that processes the full input with bidirectional attention |
| Decoder | Stack of layers that generates output autoregressively |
| Self-attention | Attention where each position attends to all positions in the same sequence |
| Cross-attention | Decoder attending to encoder output |
| Masked attention | Attention where future positions are masked out (used in decoder) |
| FFN | Feed-forward network — two linear layers with ReLU; processes each position independently |
| Residual connection | Adds the input to the output of a sub-layer (skip connection) |
| Layer normalization | Normalizes across the feature dimension for a single sample |
| N | Number of encoder/decoder layers (6 in original; 12 in BERT-base; 96 in GPT-3) |

---

## Architecture at a glance

### One encoder layer:
```
Input
  → Multi-Head Self-Attention
  → Add & Layer Norm
  → Feed-Forward Network
  → Add & Layer Norm
  → Output
```

### One decoder layer:
```
Input (generated so far)
  → Masked Multi-Head Self-Attention
  → Add & Layer Norm
  → Multi-Head Cross-Attention (Q from decoder, K/V from encoder)
  → Add & Layer Norm
  → Feed-Forward Network
  → Add & Layer Norm
  → Output
```

---

## Original transformer dimensions ("Attention is All You Need")

| Parameter | Value |
|---|---|
| d_model | 512 |
| N (layers) | 6 encoder + 6 decoder |
| Attention heads | 8 |
| d_k per head | 64 |
| FFN inner dimension | 2048 |
| Vocabulary | ~37k |

---

## What each component does

| Component | Purpose |
|---|---|
| Multi-head self-attention | Gather context from all positions |
| Cross-attention | Connect encoder context to decoder |
| FFN | Apply learned transformations to each position |
| Residual connections | Enable deep training, preserve signal |
| Layer norm | Stabilize training, prevent activation explosion |
| Positional encoding | Inject word order information |

---

## Golden Rules

1. Encoder = understands input (bidirectional). Decoder = generates output (unidirectional + encoder context).
2. Residual connections are essential — without them, training deep transformers fails.
3. The FFN is wider than d_model (4× is standard) — this is where factual knowledge is stored.
4. Cross-attention is only in the decoder — it's the bridge between encoder and decoder.
5. The decoder uses masked self-attention so it can't see future tokens during generation.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture deep dive |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component-by-component breakdown |

⬅️ **Prev:** [05 Positional Encoding](../05_Positional_Encoding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md)
