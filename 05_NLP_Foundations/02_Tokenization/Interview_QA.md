# Tokenization — Interview Q&A

## Beginner

**Q1. What is tokenization and why do we need it?**

<details>
<summary>💡 Show Answer</summary>

Tokenization is the process of splitting text into smaller units called tokens. Models can't read raw text — they need numbers. Before converting text to numbers, you have to define what the basic units are. Tokenization does that. Without it, there's nothing to convert.

</details>

---

**Q2. What is the difference between word tokenization and subword tokenization?**

<details>
<summary>💡 Show Answer</summary>

Word tokenization splits text on spaces and punctuation — each word becomes one token. It's simple but has a big problem: if a word wasn't in the training vocabulary, the model can't handle it (OOV problem).

Subword tokenization splits words into smaller pieces — fragments that appear frequently. An unknown word like "ChatGPT" might split into ["Chat", "G", "PT"], all of which are known. This eliminates the OOV problem and keeps vocabularies manageable.

</details>

---

**Q3. What is OOV and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

OOV stands for Out-of-Vocabulary. It means a word or token appears in test/production data that was never seen in training. The model has no representation for it.

With word tokenization, OOV words are replaced with a special [UNK] token, which loses all meaning. With subword tokenization, OOV words are split into known subwords, so meaning is partially preserved. OOV is a real-world problem because new words (names, slang, product names) appear constantly.

</details>

---

## Intermediate

**Q4. How does Byte Pair Encoding (BPE) work?**

<details>
<summary>💡 Show Answer</summary>

BPE builds a subword vocabulary by starting with individual characters and merging the most frequent adjacent pairs step by step.

1. Start: each character is its own token
2. Count all adjacent pairs across the training corpus
3. Merge the most frequent pair into one new token
4. Update the corpus with the merged token
5. Repeat until vocabulary size is reached

Example: if "lo" appears very often, it gets merged. Then "low" if "low" is common. The vocabulary learns the most useful subword units for that specific language and domain.

</details>

---

**Q5. Why does the same word sometimes become different numbers of tokens in different models?**

<details>
<summary>💡 Show Answer</summary>

Different models use different tokenizers trained on different corpora. A word that's common in one model's training data might be a single token, while an obscure word splits into many pieces.

For example, "tokenization" might be 1 token in a model trained heavily on NLP text, but 3–4 tokens in a general-purpose model. The vocabulary size also matters: larger vocabularies keep more whole words, smaller vocabularies split more aggressively.

</details>

---

**Q6. What are special tokens and when are they used?**

<details>
<summary>💡 Show Answer</summary>

Special tokens are reserved tokens with a fixed meaning defined during pretraining:

- `[CLS]` — start of a BERT sequence, used for classification
- `[SEP]` — separator between two sentences in BERT
- `[MASK]` — the masked position in masked language modeling
- `[PAD]` — padding to make sequences the same length in a batch
- `<s>` and `</s>` — start and end of sequence in some models

They count toward the token limit, so a "512-token" BERT model actually has fewer than 512 tokens available for your text.

</details>

---

## Advanced

**Q7. How does tokenization affect LLM pricing and performance?**

<details>
<summary>💡 Show Answer</summary>

LLM APIs charge per token. Understanding tokenization lets you optimize cost:

- Shorter prompts = fewer tokens = lower cost
- Code tokenizes differently from English (often more tokens per character)
- Repeating phrases like "You are a helpful assistant" across many calls adds up

For performance: long inputs that exceed the context window get truncated. You must design your prompts and chunking strategies around token counts, not word counts.

</details>

---

**Q8. What is WordPiece and how does it differ from BPE?**

<details>
<summary>💡 Show Answer</summary>

Both are subword tokenization methods but differ in how they pick merges:

- **BPE** merges the most frequent pair of tokens at each step — purely frequency-based
- **WordPiece** (used in BERT) picks the merge that maximizes the likelihood of the training data — it evaluates whether a merge actually helps model the data better

In practice, they produce similar results. WordPiece tends to create slightly more linguistically meaningful splits. BPE is faster to train and more widely used in GPT-family models.

</details>

---

**Q9. How would you build a custom tokenizer for a domain-specific NLP application (e.g., medical or legal text)?**

<details>
<summary>💡 Show Answer</summary>

Domain-specific text has vocabulary that general tokenizers handle poorly. "Acetaminophen" in a medical model might split into 6 tokens, but ideally it's 1.

Approach:
1. Collect a domain-specific corpus (medical literature, legal documents)
2. Train a BPE or SentencePiece tokenizer on this corpus using the `tokenizers` library from HuggingFace
3. Set vocabulary size based on domain size (medical: ~30k-50k is common)
4. Validate that key domain terms are single or two-token items
5. Fine-tune a pretrained model with this new tokenizer, or train from scratch

The trade-off: a custom tokenizer means you lose the pretrained weights of general-purpose models unless you retrain embeddings for the new vocabulary.

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

⬅️ **Prev:** [01 Text Preprocessing](../01_Text_Preprocessing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Bag of Words and TF-IDF](../03_Bag_of_Words_and_TF_IDF/Theory.md)
