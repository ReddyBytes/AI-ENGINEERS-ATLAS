# Sequence Models Before Transformers — Cheatsheet

**One-liner:** RNNs process sequences step by step and pass a hidden state forward, but they suffer from vanishing gradients and can't handle long-range dependencies at scale.

---

## Key Terms

| Term | Definition |
|---|---|
| RNN | Recurrent Neural Network — processes sequences by maintaining a hidden state |
| Hidden state | The RNN's memory: a vector updated at each time step |
| Vanishing gradient | Gradients shrink to near-zero as they propagate backward through many steps |
| Exploding gradient | Gradients grow unboundedly — solved with gradient clipping |
| LSTM | Long Short-Term Memory — RNN variant with gating to preserve long-range info |
| GRU | Gated Recurrent Unit — simpler LSTM alternative |
| Cell state | LSTM's long-term memory track (separate from hidden state) |
| Seq2seq | Encoder-decoder architecture using RNNs for translation etc. |
| Teacher forcing | Training trick: use true labels as decoder input, not model predictions |

---

## RNN vs LSTM vs Transformer

| Feature | RNN | LSTM | Transformer |
|---|---|---|---|
| Long-range dependencies | Poor | Better | Excellent |
| Training speed | Slow | Slow | Fast (parallel) |
| Gradient issues | Vanishing | Mostly fixed | No recurrence |
| Memory bottleneck | Yes | Reduced | No |
| Parallelizable? | No | No | Yes |
| State of the art? | No | No | Yes |

---

## LSTM gates

| Gate | What it does |
|---|---|
| Forget gate | Decides what to erase from cell state |
| Input gate | Decides what new info to add to cell state |
| Output gate | Decides what part of cell state to expose as hidden state |

---

## The vanishing gradient problem

```
Gradient at step t = gradient at step T × (weight matrix)^(T-t)

If weight < 1: shrinks exponentially → vanishes
If weight > 1: grows exponentially → explodes
```

---

## When are RNNs/LSTMs still used?

| Use case | Why |
|---|---|
| Streaming time-series | Process data as it arrives, step by step |
| Very small datasets | Simple RNNs overfit less than transformers |
| Resource-limited devices | Much smaller than transformer models |
| Speech synthesis (some) | Sequential audio generation |

---

## Golden Rules

1. For any NLP task, use transformers — they outperform LSTMs in virtually every benchmark.
2. The vanishing gradient problem is why deep RNNs don't work — the signal disappears.
3. LSTMs fixed the vanishing gradient but introduced sequential processing bottlenecks.
4. The fixed-size hidden state in RNNs is a hard bottleneck for long documents.
5. Attention was the key insight that broke the sequential bottleneck.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Timeline.md](./Timeline.md) | Historical timeline of sequence models |

⬅️ **Prev:** [07 Conditional Random Fields](../../05_NLP_Foundations/07_Conditional_Random_Fields/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md)
