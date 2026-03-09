# RNNs — Cheatsheet

**One-liner:** An RNN is a neural network that processes sequential data by maintaining a hidden state (memory) that is updated at each time step and passed forward to the next.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Sequence | Ordered data where position and history matter (text, time series, audio) |
| Hidden state (h_t) | The RNN's memory — a vector summarizing everything seen so far |
| Time step | One element in the sequence (one word, one frame, one sample) |
| Unrolling | Visualizing the RNN as a chain of copies, one per time step |
| BPTT | Backpropagation Through Time — backprop on the unrolled RNN |
| Vanishing gradient | Gradients shrink as they flow back through many time steps — early steps don't learn |
| LSTM | Long Short-Term Memory — gates control what to remember and forget |
| GRU | Gated Recurrent Unit — simplified LSTM with two gates |
| Cell state (c_t) | LSTM's long-term memory — flows with minimal modification |
| Forget gate | Controls how much of previous cell state to keep |

---

## RNN Formula

```
h_t = tanh( W_h × h_(t-1) + W_x × x_t + b )
y_t = W_y × h_t + b_y   (optional output at each step)
```

---

## LSTM Gates (simplified)

```
Forget gate:  f_t = sigmoid( W_f × [h_(t-1), x_t] + b_f )
Input gate:   i_t = sigmoid( W_i × [h_(t-1), x_t] + b_i )
New memory:   g_t = tanh(    W_g × [h_(t-1), x_t] + b_g )
Cell update:  c_t = f_t × c_(t-1) + i_t × g_t
Output gate:  o_t = sigmoid( W_o × [h_(t-1), x_t] + b_o )
Hidden state: h_t = o_t × tanh(c_t)
```

---

## RNN vs LSTM vs GRU

| | RNN | LSTM | GRU |
|--|-----|------|-----|
| Memory type | Hidden state only | Hidden + cell state | Hidden state only |
| Gates | None | 3 (forget, input, output) | 2 (reset, update) |
| Long-range memory | Poor (vanishing grad) | Excellent | Good |
| Parameters | Fewest | Most | Middle |
| Training speed | Fastest | Slowest | Middle |
| Use when | Very short sequences | Long sequences, important | Good default |

---

## Input/Output Configurations

| Type | Description | Example |
|------|-------------|---------|
| Many-to-one | Sequence → single output | Sentiment: "great movie" → positive |
| Many-to-many (equal) | Each step → output | POS tagging: word → tag per word |
| Many-to-many (unequal) | Sequence → different-length sequence | Translation: English → French |
| One-to-many | Single input → sequence | Image → caption words |

---

## When to Use / Not Use

| Use RNNs/LSTMs when... | Consider alternatives when... |
|------------------------|-------------------------------|
| Sequential data with temporal dependencies | Long sequences (>500 steps) — Transformer is better |
| Time-series prediction | Fixed-length features (tabular) — use MLP |
| Variable-length sequences | Image data — use CNN |
| Text classification, generation (smaller scale) | State-of-the-art NLP — use Transformer |

---

## Golden Rules

1. Always normalize input features for time-series data.
2. Default to LSTM over vanilla RNN — almost always better.
3. Use GRU when you need to train faster with slightly less data.
4. Use gradient clipping (max_norm=1.0) in RNN training — exploding gradients are common.
5. For sequences longer than ~100 steps, consider Transformer architectures instead.
6. Bidirectional RNN (processes sequence forward AND backward) significantly improves performance for tasks where full context is available.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | RNN architecture deep dive |

⬅️ **Prev:** [09 CNNs](../09_CNNs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [11 GANs](../11_GANs/Theory.md)
