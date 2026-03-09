# BERT — Interview Q&A

## Beginner

**Q1. What is BERT and what makes it different from previous NLP models?**

BERT (Bidirectional Encoder Representations from Transformers) is a pretrained encoder-only transformer model released by Google in 2018.

What made it different:

1. **Bidirectional:** Every token attends to all other tokens simultaneously — left and right context. Previous models (GPT) were left-to-right only. ELMo used two separate LSTMs that couldn't communicate.

2. **Deep pretraining:** Trained on Wikipedia + BookCorpus (~3.3B words) with masked language modeling — a more challenging and richer objective than simple next-word prediction.

3. **Transfer learning:** One pretrained model, fine-tuned for dozens of tasks with small additional training. BERT set new state-of-the-art records on 11 NLP benchmarks simultaneously on release.

---

**Q2. What is Masked Language Modeling (MLM)?**

MLM is BERT's main pretraining objective. Randomly select 15% of tokens and replace them with [MASK]. Train the model to predict the original tokens using the full bidirectional context.

For "The cat [MASK] on the mat", the model must predict "sat" from both "The cat" (left) and "on the mat" (right).

This forces the model to build deep bidirectional understanding — it can't just rely on left context like GPT does. The difficulty of predicting masked tokens from both directions drives BERT to learn rich syntactic and semantic representations.

---

**Q3. What is the [CLS] token and how is it used for classification?**

BERT prepends a special [CLS] (classification) token to every input. After passing through all transformer layers, this token's final hidden state captures a summary representation of the whole sentence.

For classification:
1. Pass "[CLS] Your text [SEP]" through BERT
2. Take the hidden state of the [CLS] position (shape: 768-dimensional vector)
3. Pass through a linear layer → num_classes output
4. Apply softmax, compute cross-entropy loss
5. Fine-tune the whole model

The [CLS] token "communicates" with all other tokens through attention across all layers, so it builds a sentence-level understanding.

---

## Intermediate

**Q4. How does BERT fine-tuning work? What is actually changed during fine-tuning?**

During fine-tuning:
1. Load BERT's pretrained weights
2. Add a task-specific head (linear layer on top of [CLS] or per-token hidden states)
3. Train on your labeled dataset with a small learning rate (typically 2e-5 to 5e-5)

What changes:
- The task-specific head weights are randomly initialized and trained from scratch
- All of BERT's pretrained weights are also updated (not frozen) — BERT's representations adapt to your domain

Why update all layers? Because BERT's representations, while general, become more task-specific when fine-tuned. The lower layers tend to keep general linguistic patterns; the upper layers adapt more to the task.

Training is typically 3–5 epochs on a few thousand labeled examples. BERT reaches competitive performance even with as few as a few hundred examples on some tasks.

---

**Q5. What are the three types of embeddings BERT adds together for input?**

BERT's input embeddings are the sum of three components:

1. **Token embeddings:** A learned vector for each wordpiece token in the vocabulary. Standard lookup table.

2. **Segment embeddings:** Either embedding A or embedding B, indicating which sentence the token belongs to. Used for the NSP objective and sentence-pair tasks.

3. **Positional embeddings:** Learned absolute position embeddings (unlike the sine/cosine encoding in the original transformer). One embedding per position, up to max sequence length (512 for BERT-base).

All three are the same dimensionality (768) and are added element-wise before the first transformer layer.

---

**Q6. What is Next Sentence Prediction (NSP) and why was it later abandoned?**

NSP is BERT's secondary pretraining task. Given two sentences A and B, predict whether B is the actual next sentence from the corpus (50% of the time) or a random sentence (50% of the time).

The motivation: tasks like question answering and NLI require understanding relationships between sentence pairs. NSP was supposed to teach the model to understand inter-sentence coherence.

Why it was abandoned in RoBERTa: Ablation studies showed NSP barely helped and sometimes hurt performance. The task was too easy — models could solve it by looking for topic consistency without understanding deep reasoning. RoBERTa removed NSP, trained longer, and with more data — and outperformed BERT on all benchmarks.

---

## Advanced

**Q7. How does BERT handle the [MASK] token at fine-tuning time if the model never sees [MASK] during inference?**

This is a real mismatch called the "pretrain-finetune discrepancy." During pretraining, [MASK] tokens appear frequently. During fine-tuning and inference, they don't appear at all.

BERT partially addresses this: of the 15% of tokens selected for masking, only 80% are actually replaced with [MASK]. 10% are replaced with a random token, and 10% are left unchanged. This means BERT can't simply memorize "output something whenever I see [MASK]" — it has to understand every token's context.

In practice, this mismatch is accepted as a minor limitation. The pretrained representations are rich enough that fine-tuning adapts them without issue. Later models like XLNet proposed autoregressive alternatives that eliminate the mismatch, but BERT's practical performance remains competitive.

---

**Q8. What is the computational bottleneck when serving BERT in production at scale?**

Transformer inference is O(n²) in the sequence length due to self-attention. For BERT-base with 512 token input: 512² = 262,144 attention calculations per layer × 12 layers. This adds up.

Practical bottlenecks and solutions:

1. **Latency:** BERT-base takes ~50–100ms per inference on CPU. For low-latency serving: use DistilBERT (2× faster), quantize (int8, ~4× faster), or use ONNX/TensorRT runtime.

2. **Memory:** BERT-base is ~440MB. Multiple replicas for parallel serving multiplies this. Quantization reduces to ~110MB.

3. **Batch efficiency:** BERT processes variable-length sequences padded to the same length. Long padding wastes compute. Solutions: dynamic padding (pad to max length in each mini-batch), sequence bucketing (group similar-length sequences together).

4. **GPU throughput:** For high-throughput serving, batching is critical. BERT on a GPU with batch size 32 can handle hundreds of requests/second.

---

**Q9. How does BERT compare to GPT-3 for NLP tasks, and when would you choose BERT?**

GPT-3 has 175B parameters vs BERT-large's 340M — roughly 500× bigger. For most tasks, GPT-3 has better raw capability.

But choose BERT when:

1. **Latency is critical:** BERT inference is milliseconds. GPT-3 API calls are slower and have variable latency.
2. **Cost is a concern:** BERT runs locally. GPT-3 API costs per token.
3. **Specific fine-tuning is possible:** If you have 1000+ labeled examples, fine-tuned BERT often beats GPT-3 few-shot on that specific task.
4. **Embeddings are needed:** For search, clustering, deduplication — BERT embeddings are faster and cheaper to compute than GPT embeddings.
5. **Private data:** Fine-tuning BERT on-premise keeps data private. GPT-3 requires sending data to the API.
6. **Regulatory requirements:** On-premise BERT deployment is easier to certify for HIPAA, GDPR, etc.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 GPT](../09_GPT/Theory.md)