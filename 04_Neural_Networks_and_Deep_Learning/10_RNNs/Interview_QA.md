# RNNs — Interview Q&A

## Beginner

**Q1: What is the key difference between an RNN and a standard MLP?**

<details>
<summary>💡 Show Answer</summary>

An MLP processes each input independently — it has no memory of previous inputs. An RNN maintains a hidden state — a vector that is updated at each time step and carries information forward. When processing the word "it" in a sentence, an MLP has no access to the previous words. An RNN can use its hidden state to remember "what was mentioned earlier" and use that context to process the current word. This makes RNNs suitable for sequential data: text, time series, audio, and video.

</details>

---

**Q2: What is the hidden state in an RNN?**

<details>
<summary>💡 Show Answer</summary>

The hidden state h_t is a vector of numbers that summarizes the information seen so far in the sequence. At each time step, it is computed from two inputs: the current input x_t and the previous hidden state h_(t-1). The formula is: `h_t = tanh(W_h × h_(t-1) + W_x × x_t + b)`. Think of it as a fixed-size note the RNN carries with it as it reads the sequence. It can only hold so much information — which is why very long sequences are difficult.

</details>

---

**Q3: What is the vanishing gradient problem in RNNs?**

<details>
<summary>💡 Show Answer</summary>

When training an RNN with backpropagation through time (BPTT), the gradient must flow backward through every time step. At each step, the gradient is multiplied by the weight matrix (specifically its derivative). If these multiplied values are consistently less than 1 — which is common with tanh activations — the gradient shrinks exponentially. After 50 steps, the gradient reaching the first step is essentially 0. The RNN cannot learn long-range dependencies — it "forgets" information from many steps ago. This is why vanilla RNNs struggle with even moderately long sequences.

</details>

---

## Intermediate

**Q4: How does an LSTM solve the vanishing gradient problem?**

<details>
<summary>💡 Show Answer</summary>

An LSTM adds a cell state c_t — a second memory vector that flows through time with minimal transformation. The forget gate controls what fraction of the previous cell state to keep (sigmoid output between 0 and 1, and multiplied element-wise). When the forget gate outputs values near 1, the cell state passes through nearly unchanged — gradients flow through the multiplication of 1.0 values instead of shrinking values. This is called the "constant error carousel." During backpropagation, gradients can flow through the cell state pathway with little attenuation over hundreds of steps, allowing LSTMs to learn long-range dependencies.

</details>

---

**Q5: What is bidirectional RNN and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

A standard RNN processes a sequence from left to right — at time t, it only has access to past context (time 1 to t). A bidirectional RNN runs two RNNs over the same sequence: one left-to-right, one right-to-left. Their hidden states are concatenated at each position, giving each position access to both past and future context. Use bidirectional RNNs when the full sequence is available and you need both directions: sentiment analysis, named entity recognition, speech recognition. Do not use bidirectional RNNs for generation tasks (you cannot know future tokens when generating text one step at a time).

</details>

---

**Q6: What is the difference between LSTM and GRU?**

<details>
<summary>💡 Show Answer</summary>

Both use gating mechanisms to control information flow. An LSTM has three gates (forget, input, output) and two state vectors (h_t and c_t). A GRU has two gates (reset and update) and one state vector (h_t). GRU merges the cell state and hidden state into one, and uses the update gate to balance between old and new information. Empirically, GRU and LSTM perform similarly on most tasks. GRU has fewer parameters — roughly 25% fewer — making it faster to train, especially with limited data. LSTM tends to have a slight edge on very long sequences where the separate cell state helps maintain long-term memory.

</details>

---

## Advanced

**Q7: What is Backpropagation Through Time (BPTT) and what are its practical challenges?**

<details>
<summary>💡 Show Answer</summary>

BPTT is the application of backpropagation to an unrolled RNN. An RNN processing a sequence of length T is equivalent to a T-layer network where all layers share weights. To compute gradients, we unroll the RNN — create T copies of the same network connected in sequence — and apply standard backpropagation. Gradients are then summed across all time steps to update the shared weights. Practical challenges: (1) Memory: storing all activations for T steps for the backward pass requires O(T) memory — expensive for long sequences. (2) Vanishing/exploding gradients over many steps. (3) Speed: sequential computation — you cannot parallelize across time steps. Truncated BPTT (splitting sequences into chunks and only backpropagating within each chunk) is commonly used to limit these issues.

</details>

---

**Q8: Why have Transformers largely replaced RNNs for NLP tasks?**

<details>
<summary>💡 Show Answer</summary>

Transformers (introduced 2017) address the fundamental weaknesses of RNNs. First, parallelism: RNNs must process tokens sequentially — you cannot compute h_t until you have h_(t-1). Transformers process all tokens simultaneously using self-attention, enabling massive GPU parallelism. Second, long-range dependencies: self-attention directly connects any two positions in a sequence in O(1) operations regardless of distance. RNNs must propagate information through every intermediate step. Third, training scale: because transformers parallelize better, they can be trained on vastly larger datasets with more compute. The result: GPT, BERT, and all modern LLMs are transformer-based. RNNs remain useful for streaming/online processing where you receive one token at a time, low-latency applications, and some time-series tasks.

</details>

---

**Q9: What is a Seq2Seq model and how does the encoder-decoder architecture work?**

<details>
<summary>💡 Show Answer</summary>

A Seq2Seq (sequence-to-sequence) model translates a variable-length input sequence to a variable-length output sequence — used in machine translation, summarization, and question answering. Architecture: The encoder is an RNN/LSTM that reads the input sequence and compresses it into a context vector — the final hidden state. This context vector is supposed to capture the entire meaning of the input. The decoder is a separate RNN/LSTM initialized with the context vector. It generates the output one token at a time, conditioning each step on the context vector and all previously generated tokens. The key weakness: the entire input is compressed into a single fixed-size vector — this bottleneck loses information for long sequences. The **attention mechanism** (Bahdanau et al., 2014) solves this by letting the decoder look at all encoder hidden states, not just the last one — this was the breakthrough that enabled high-quality translation and eventually inspired the Transformer.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | RNN architecture deep dive |

⬅️ **Prev:** [09 CNNs](../09_CNNs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [11 GANs](../11_GANs/Theory.md)
