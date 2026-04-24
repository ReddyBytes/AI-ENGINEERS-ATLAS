# Encoder-Decoder Models — Interview Q&A

## Beginner

**Q1. What is the difference between encoder-only and decoder-only transformer models?**

<details>
<summary>💡 Show Answer</summary>

Encoder-only models (like BERT) process the full input with bidirectional attention — every token can see every other token. They produce contextual representations of the input but don't generate new text. They're trained with masked language modeling — predict masked words from context.

Decoder-only models (like GPT) use causal (masked) attention — each token can only see tokens that came before it. They generate text one token at a time. They're trained on next-token prediction — predict the next word given all previous words.

Encoder-only = understand. Decoder-only = generate.

</details>

---

<br>

**Q2. What is the difference between BERT and GPT at a high level?**

<details>
<summary>💡 Show Answer</summary>

BERT (encoder-only, bidirectional):
- Reads the whole sequence in both directions simultaneously
- Every token is contextualized by all surrounding tokens
- Can't generate text
- Best for: classification, NER, extractive QA, sentence embeddings

GPT (decoder-only, left-to-right):
- Reads sequence left to right only
- Each token only sees past tokens
- Generates text token by token
- Best for: text generation, chatbots, code, few-shot tasks

The key difference is directionality. BERT's bidirectionality makes it better at understanding. GPT's autoregressive structure makes it natural for generation.

</details>

---

<br>

**Q3. What tasks are best suited for encoder-decoder models like T5?**

<details>
<summary>💡 Show Answer</summary>

Encoder-decoder models shine on tasks where you need to:
1. Fully understand an input (encoder processes it bidirectionally)
2. Generate a different output (decoder generates it autoregressively)

Prime examples:
- Machine translation: understand the source language, generate the target
- Summarization: understand the full document, generate a shorter summary
- Question answering (generative): understand the question + context, generate an answer
- Text simplification: understand complex text, generate simpler version

T5 (Text-to-Text Transfer Transformer) frames all NLP tasks as text-to-text, making one model handle translation, summarization, QA, and classification through the same interface.

</details>

---

## Intermediate

**Q4. Why have decoder-only models (GPT family) come to dominate over encoder-decoder models?**

<details>
<summary>💡 Show Answer</summary>

Several reasons:

1. **Scaling efficiency:** next-token prediction is a clean, natural objective that scales well. Training data (next word in any text) is infinite and requires no annotation.

2. **Versatility:** GPT-3 showed that a large enough decoder-only model can do classification, translation, QA, and more through in-context learning — no task-specific architecture needed. Just prompt it.

3. **Instruction fine-tuning:** teaching a decoder to follow instructions (RLHF, FLAN) is natural — the model is already generating text from a prompt.

4. **Simplicity:** one architecture, one training objective, everything scales together.

Encoder-decoder models are still competitive for tasks where training data is labeled (translation pairs, document-summary pairs), but their dominance has faded as decoder-only models at scale proved they could do everything.

</details>

---

<br>

**Q5. What is T5's "text-to-text" approach and why is it significant?**

<details>
<summary>💡 Show Answer</summary>

T5 (Raffel et al., 2020) reframes every NLP task as: input text → output text.

- Classification: input = "sentence: I love this movie", output = "positive"
- Translation: input = "translate English to French: Hello", output = "Bonjour"
- Summarization: input = "summarize: [document]", output = "[summary]"
- QA: input = "question: Who is president? context: [text]", output = "Joe Biden"

Significance: one model, one training procedure, one fine-tuning interface for all tasks. No task-specific heads. No special output layers. Just text → text.

This was influential in moving the field toward instruction fine-tuning — the idea that a model trained to follow task descriptions in natural language can generalize broadly.

</details>

---

<br>

**Q6. How does BART differ from BERT and T5?**

<details>
<summary>💡 Show Answer</summary>

BART (Lewis et al., 2020) is an encoder-decoder model, but its pretraining is different:

- BERT: predict masked tokens (MLM)
- T5: predict span-corrupted text
- BART: reconstruct original text from various corruptions (text infilling, token masking, sentence permutation, deletion)

BART's pretraining makes it especially strong at:
- Sequence-to-sequence generation tasks (summarization, translation)
- Text infilling (completing documents)

BART-large is competitive with T5-large on summarization. The key difference from T5: BART uses a standard encoder-decoder transformer without the T5-specific design choices (relative position encoding, shared QK embeddings, etc.).

</details>

---

## Advanced

**Q7. What is the "prefix LM" setup and how does it blend encoder and decoder capabilities?**

<details>
<summary>💡 Show Answer</summary>

A prefix LM is a decoder-only model where the input (prefix) is processed with bidirectional attention, and the generated output uses causal attention.

For input "Translate to French: Hello" → " Bonjour", the model:
- Processes "Translate to French: Hello" with bidirectional attention (like an encoder)
- Generates " Bonjour" with causal attention (like a decoder)

T5 can be run in this mode. It blurs the line between encoder-only and encoder-decoder:
- It captures the full context of the input without masking
- But it's still a single model, not two separate stacks

PaLM and some other models use this approach for certain tasks. The advantage: more context available when generating, especially useful when the input and output are closely related.

</details>

---

<br>

**Q8. Why is bidirectional context important for encoding and harmful for generation?**

<details>
<summary>💡 Show Answer</summary>

For encoding/understanding: you want the fullest possible context. To understand "bank" in "The river bank was flooded," you need to see "river" (which comes after "bank"). Bidirectionality gives each token access to its full linguistic context.

For generation: you're predicting the next token given previous tokens only. At generation time, future tokens don't exist yet. If a model were trained with bidirectional attention and could see future tokens during training, it would learn to copy from the future rather than actually predicting — no learning happens. The causal mask enforces the autoregressive generation interface.

Summary: bidirectionality helps with understanding (offline tasks). Causality is required for generation (online tasks).

</details>

---

<br>

**Q9. How do you fine-tune a decoder-only model for a classification task?**

<details>
<summary>💡 Show Answer</summary>

Decoder-only models don't have a natural classification head. Two common approaches:

**1. Causal LM fine-tuning (generative):** Format the task as text generation. Train the model to generate the label as text.
- Input: "Classify sentiment: I love this movie\nAnswer:"
- Target output: "positive"
- Loss: next-token prediction on the target tokens only

**2. Last-token classification:** Take the hidden state of the last non-padding token and add a linear classification head. Fine-tune end-to-end.
- Input: "I love this movie"
- Use hidden_state[-1] → linear layer → 2-class output
- Standard cross-entropy loss

Both approaches work. Method 1 is more flexible (zero-shot compatible, extends to many classes easily). Method 2 is more efficient for high-volume binary/multi-class classification. Instruction-tuned models (GPT-4, Claude) almost always use method 1.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Encoder vs decoder vs encoder-decoder comparison |

⬅️ **Prev:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 BERT](../08_BERT/Theory.md)
