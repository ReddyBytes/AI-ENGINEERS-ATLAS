# Sequence Models Before Transformers — Interview Q&A

## Beginner

**Q1. What is a Recurrent Neural Network (RNN) and how does it process text?**

An RNN processes sequences one element at a time. At each step, it takes the current input (a word embedding) and the previous hidden state, combines them, and produces a new hidden state. This hidden state is the model's running memory of everything it has seen so far.

For the sentence "The cat sat", the RNN processes "The" first, creates a hidden state, then takes "cat" and the previous hidden state to create a new one, and so on. The final hidden state is supposed to capture the meaning of the whole sequence.

The problem is that as sequences get longer, earlier information gets diluted. The hidden state for step 100 contains a faded echo of what was at step 1.

---

**Q2. What is the vanishing gradient problem?**

During training, neural networks adjust their weights by computing gradients — signals that flow backward through the network. In an RNN, these gradients must travel backward through every time step.

At each step, the gradient gets multiplied by the weight matrix. If this matrix has values slightly less than 1, multiplying it 50 times results in a gradient near zero. The model can no longer update the weights for early time steps because the signal has vanished.

The practical consequence: the model can't learn from context that appeared many words ago. It effectively only sees the recent past.

---

**Q3. What is an LSTM and how does it fix the vanishing gradient problem?**

An LSTM (Long Short-Term Memory) adds a second memory track called the cell state, alongside the regular hidden state. The cell state is designed to carry information over long distances without being forced through nonlinear transformations at every step.

Three gates control information flow:
- The forget gate removes irrelevant old information
- The input gate adds new relevant information
- The output gate decides what to expose to the next step

Because information can flow along the cell state with minimal transformation, gradients can also flow backward more cleanly. LSTMs can maintain relevant context over much longer sequences than plain RNNs.

---

## Intermediate

**Q4. What is the seq2seq architecture and what are its limitations?**

Seq2seq (sequence-to-sequence) uses two RNNs or LSTMs: an encoder and a decoder. The encoder reads the input sequence and compresses it into a single fixed-size context vector. The decoder takes this vector and generates the output sequence word by word.

Used for: translation, summarization, question answering.

Key limitation: the fixed-size context vector is a bottleneck. For a 100-word input sentence, the encoder must compress all information into one vector of, say, 512 numbers. Long sentences lose information. This is what motivated attention mechanisms — instead of one fixed vector, the decoder gets to look at all encoder states directly.

---

**Q5. What is gradient clipping and why is it used with RNNs?**

Gradient clipping caps the gradient magnitude at a maximum value during backpropagation. This prevents the exploding gradient problem — the opposite of vanishing gradients — where gradients grow exponentially as they propagate backward.

Without clipping, exploding gradients cause weight updates to be enormous, destabilizing training (loss goes to infinity). Clipping rescales the gradient vector to have norm at most some threshold (typically 1.0 or 5.0) before applying the update.

Gradient clipping is a training-time trick, not an architectural fix. Vanishing gradients aren't solved by clipping — they require architectural changes (LSTM, residual connections, or attention).

---

**Q6. What specific problem did attention mechanisms solve in RNN-based seq2seq models?**

The bottleneck problem. In a seq2seq model, the entire input sequence must be compressed into a single fixed-size vector for the decoder. For long sequences, this is lossy.

Attention gives the decoder a direct window into the encoder's full sequence of hidden states. At each decoder step, it computes a weighted sum of all encoder states, where the weights (attention scores) reflect which encoder positions are most relevant for the current decoder step.

This solves long-range dependencies in translation: when translating word 50, the decoder can directly "look at" encoder position 3 if that's the relevant source word — no compression required.

---

## Advanced

**Q7. Why can't LSTMs scale the way transformers can?**

Three fundamental reasons:

1. **Sequential processing:** each LSTM step depends on the previous step's hidden state. You can't compute step 5 until step 4 is done. This makes LSTMs inherently sequential — poor utilization of parallel hardware like GPUs/TPUs.

2. **O(sequence_length) depth:** information from step 1 must pass through all N steps to reach step N. Even with LSTM gating, this creates a path that can degrade. Transformers have direct connections between any two positions.

3. **Fixed hidden state size:** the bottleneck exists at every step. Modern transformers scale by increasing width and depth independently. LSTMs have no equivalent mechanism.

These limitations mean LSTM training is much slower per token than transformer training, and quality doesn't scale with more compute the same way.

---

**Q8. What is teacher forcing and why is it used in RNN training?**

Teacher forcing is a training technique for seq2seq decoders. Normally, the decoder uses its own previous output as the next input. But during training, if the model makes a mistake at step 3, step 4 gets a wrong input and the error compounds — the model is trying to recover from its own mistakes while learning.

Teacher forcing avoids this: during training, use the true target token as the decoder input, not the model's prediction. This gives cleaner gradients and faster convergence.

The downside is exposure bias: the model never sees its own mistakes during training, so at inference time (where it must use its own outputs) it can struggle. Techniques like scheduled sampling (gradually switching from teacher forcing to model predictions during training) mitigate this.

---

**Q9. How do bidirectional RNNs (BiRNNs) work and when should you use them?**

A bidirectional RNN runs two RNNs on the same sequence: one left-to-right and one right-to-left. The hidden states from both directions are concatenated at each position.

This means each position gets context from both what came before AND what comes after. For "The bank was closed", the word "bank" gets context from "closed" (on the right) which helps disambiguate the meaning.

Use BiRNNs (or BiLSTMs) when:
- The full sequence is available at inference time (classification, NER, POS)
- Context from both directions is needed for accurate labeling

Don't use them for:
- Language generation (you don't have the future when generating)
- Streaming/online processing (right-to-left pass needs the whole sequence first)

Transformers with bidirectional attention (like BERT) have superseded BiLSTMs for virtually all classification and labeling tasks.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Timeline.md](./Timeline.md) | Historical timeline of sequence models |

⬅️ **Prev:** [07 Conditional Random Fields](../../05_NLP_Foundations/07_Conditional_Random_Fields/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md)
